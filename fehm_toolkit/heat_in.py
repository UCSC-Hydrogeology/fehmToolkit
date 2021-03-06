import argparse
import logging
from pathlib import Path
from typing import Callable

from matplotlib import cm, colors, pyplot as plt
import pandas as pd
from scipy.spatial import Voronoi, voronoi_plot_2d

from .config import HeatFluxConfig, RunConfig
from .fehm_objects import Grid, Node
from .file_interface import read_grid, write_compact_node_data
from .file_interface.legacy_config import read_legacy_hfi_config

logger = logging.getLogger(__name__)


def generate_input_heatflux_file(
    *,
    config_file: Path,
    fehm_file: Path,
    outside_zone_file: Path,
    area_file: Path,
    output_file: Path,
    plot_result: bool = False,
):
    logger.info(f'Reading configuration file: {config_file}')
    try:
        config = RunConfig.from_yaml(config_file)
        heat_flux_config = config.heat_flux_config
    except Exception:  # TODO(Dustin): build sepearate tool to combine legacy configs, assume yaml format in utilities.
        logger.info('Invalid yaml, trying legacy reader.')
        heat_flux_config = read_legacy_hfi_config(config_file)

    logger.info('Parsing grid into memory')
    grid = read_grid(fehm_file, outside_zone_file=outside_zone_file, area_file=area_file, read_elements=False)

    logger.info('Computing boundary heat flux')
    heatflux_by_node = compute_boundary_heatflux(grid, heat_flux_config)

    logger.info(f'Writing heat flux to disk: {output_file}')
    write_compact_node_data(
        heatflux_by_node,
        output_file,
        header='hflx\n',
        footer='0\n',
        style='heatflux',
    )
    if plot_result:
        plot_heatflux(heatflux_by_node, grid)


def compute_boundary_heatflux(grid: Grid, heat_flux_config: HeatFluxConfig) -> dict[int, float]:
    heatflux_models = get_heatflux_models_by_kind()

    try:
        model = heatflux_models[heat_flux_config.heat_flux_model.kind]
    except KeyError:
        raise NotImplementedError(f'No model defined for kind {heat_flux_config.heat_flux_model.kind}')

    input_nodes = grid.get_nodes_in_outside_zone('bottom')
    return {node.number: model(node, heat_flux_config.heat_flux_model.params) for node in input_nodes}


def plot_heatflux(heatflux_by_node: dict[int, float], grid: Grid):
    entries = []
    for node_number, heatflux_MW in heatflux_by_node.items():
        node = grid.node(node_number)
        entries.append({
            'x': node.x / 1E3,  # convert m -> km
            'y': node.y / 1E3,  # convert m -> km
            'heatflux_mW': 1E9 * heatflux_MW / node.outside_area.z,  # convert to MW -> mW
        })
    plot_data = pd.DataFrame(entries)

    axis_2d = _get_2d_axis_or_none(plot_data)
    if axis_2d:
        _plot_heatflux_2d(plot_data, plot_axis='x' if axis_2d == 'y' else 'y')
        return

    _plot_heaflux_3d(plot_data)


def _plot_heatflux_2d(plot_data: pd.DataFrame, plot_axis: str):
    fig, ax = plt.subplots(figsize=(8, 5))
    plot_data.plot(x=plot_axis, y='heatflux_mW', marker='o', legend=False, ax=ax)
    ax.set_xlabel(rf'{plot_axis} ($km$)')
    ax.set_ylabel(r'Heat flux ($mW/m^2$)')
    ax.set_title('Bottom boundary heat flux')
    plt.show()


def _plot_heaflux_3d(plot_data: pd.DataFrame):
    vor = Voronoi(plot_data[['x', 'y']].values)
    heatflux_mW = plot_data['heatflux_mW'].values

    norm = colors.Normalize(vmin=min(heatflux_mW), vmax=max(heatflux_mW), clip=True)
    mapper = cm.ScalarMappable(norm=norm, cmap=cm.Reds)

    fig, ax = plt.subplots(figsize=(8, 8))
    voronoi_plot_2d(vor, show_points=False, show_vertices=False, line_width=0.3, ax=ax)
    for region_index, region_heatflux_mW in zip(vor.point_region, heatflux_mW):
        region = vor.regions[region_index]
        if -1 in region:
            continue

        polygon = [vor.vertices[i] for i in region]
        ax.fill(*zip(*polygon), color=mapper.to_rgba(region_heatflux_mW))

    ax.set_aspect('equal')
    ax.set_xlabel(r'x ($km$)')
    ax.set_ylabel(r'y ($km$)')
    ax.set_title(r'Bottom boundary heat flux ($mW/m^2$)')
    plt.colorbar(mapper, ax=ax)
    plt.show()


def _get_2d_axis_or_none(plot_data: pd.DataFrame) -> str:
    if not plot_data.x.var():
        return 'x'

    if not plot_data.y.var():
        return 'y'

    return None


def get_heatflux_models_by_kind() -> dict[str, Callable]:
    return {
        'crustal_age': _crustal_age_heatflux,
        'constant_MW_per_m2': _constant_MW_per_m2,
    }


def _crustal_age_heatflux(node: Node, params: dict) -> float:
    distance_from_boundary_m = params['crustal_age_sign'] * node.x
    distance_from_ridge_m = params['boundary_distance_to_ridge_m'] + distance_from_boundary_m
    age_ma = 1 / (params['spread_rate_mm_per_year'] * 1E3) * distance_from_ridge_m
    heatflux_per_m2 = params['coefficient_MW'] / age_ma ** 0.5
    return -abs(node.outside_area.z * heatflux_per_m2)


def _constant_MW_per_m2(node: Node, params: dict) -> float:
    return -abs(node.outside_area.z * params['constant'])


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)s (%(levelname)s) %(message)s")

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--fehm_file', type=Path, help='Path to main grid (.fehm) file.')
    parser.add_argument('--outside_zone_file', type=Path, help='Path to boundary (_outside.zone) file.')
    parser.add_argument('--area_file', type=Path, help='Path to boundary area (.area) file.')
    parser.add_argument('--config_file', type=Path, help='Path to configuration (.yaml/.hfi) file.')
    parser.add_argument('--output_file', type=Path, help='Path for heatflux output to be written.')
    parser.add_argument('--plot_result', action='store_true', help='Flag to optionally plot the heatflux.')
    args = parser.parse_args()

    generate_input_heatflux_file(
        config_file=args.config_file,
        fehm_file=args.fehm_file,
        outside_zone_file=args.outside_zone_file,
        area_file=args.area_file,
        output_file=args.output_file,
        plot_result=args.plot_result,
    )
