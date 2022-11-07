from decimal import Decimal
import logging
from pathlib import Path

from matplotlib import cm, colors, pyplot as plt
import pandas as pd
from scipy.spatial import Voronoi, voronoi_plot_2d

from fehmtk.config import HeatFluxConfig, RunConfig
from fehmtk.fehm_objects import Grid
from fehmtk.file_interface import read_grid, write_compact_node_data

from .heat_flux_models import get_heatflux_models_by_kind

logger = logging.getLogger(__name__)


def generate_heat_flux_boundaries(config_file: Path, plot: bool = False):
    logger.info(f'Reading configuration file: {config_file}')
    config = RunConfig.from_yaml(config_file)
    if not config.files_config.heat_flux:
        raise ValueError(f'No heat_flux file defined in {config_file}, required for output.')

    logger.info('Parsing grid into memory')
    grid = read_grid(
        config.files_config.grid,
        outside_zone_file=config.files_config.outside_zone,
        area_file=config.files_config.area,
        read_elements=False,
    )

    logger.info('Computing boundary heat flux')
    heatflux_by_node = compute_boundary_heatflux(grid, config.heat_flux_config)

    logger.info(f'Writing heat flux to disk: {config.files_config.heat_flux}')
    write_compact_node_data(
        {node_number: (heatflux, '0.') for node_number, heatflux in heatflux_by_node.items()},
        output_file=config.files_config.heat_flux,
        header='hflx\n',
        footer='0\n',
    )
    if plot:
        plot_heatflux(heatflux_by_node, grid)


def compute_boundary_heatflux(grid: Grid, heat_flux_config: HeatFluxConfig) -> dict[int, Decimal]:
    heatflux_models = get_heatflux_models_by_kind()

    try:
        model = heatflux_models[heat_flux_config.heat_flux_model.kind]
    except KeyError:
        raise NotImplementedError(f'No model defined for kind {heat_flux_config.heat_flux_model.kind}')

    input_nodes = grid.get_nodes_in_outside_zone('bottom')
    return {node.number: model(node, heat_flux_config.heat_flux_model.params) for node in input_nodes}


def plot_heatflux(heatflux_by_node: dict[int, Decimal], grid: Grid):
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
