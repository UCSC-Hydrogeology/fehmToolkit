import argparse
import logging
from pathlib import Path
from typing import Callable

from .config.heat_in import read_legacy_config
from .fehm_objects import Grid, Node
from .file_interface import write_compact_node_data

logger = logging.getLogger(__name__)

HEATFLUX_INPUT_ZONE = 'bottom'
HEATFLUX_HEADER = 'hflx\n'
HEATFLUX_FOOTER = '0\n'


def generate_input_heatflux_file(
    *,
    config_file: Path,
    fehm_file: Path,
    outside_zone_file: Path,
    area_file: Path,
    output_file: Path,
):
    config = read_legacy_config(config_file)  # TODO(dustin): add support for other config file formats
    grid = Grid.from_files(fehm_file, outside_zone_file=outside_zone_file, area_file=area_file)
    heatflux_by_node = compute_boundary_heatflux(grid, config)
    write_compact_node_data(heatflux_by_node, output_file, header=HEATFLUX_HEADER, footer=HEATFLUX_FOOTER)


def compute_boundary_heatflux(grid: Grid, config: dict[int, float]):
    heatflux_config = config['heatflux']
    heatflux_models = get_heatflux_models_by_kind()

    try:
        model = heatflux_models[heatflux_config['model_kind']]
    except KeyError:
        raise NotImplementedError(f'No model defined for kind "{heatflux_config["model_kind"]}"')

    input_nodes = grid.get_nodes_in_outside_zone(HEATFLUX_INPUT_ZONE)
    return {node.number: model(node, heatflux_config['model_params']) for node in input_nodes}


def get_heatflux_models_by_kind() -> dict[str, Callable]:
    return {'crustal_age': _crustal_age_heatflux}


def _crustal_age_heatflux(node: Node, params: dict) -> float:
    distance_from_boundary = params['crustal_age_sign'] * node.x
    distance_from_ridge = params['boundary_distance_to_ridge_m'] + distance_from_boundary
    age = 1 / (params['spread_rate_mm_per_year'] * 1E3) * distance_from_ridge
    heatflux_per_area = params['coefficient_MW'] / age ** 0.5
    return -abs(node.outside_area.z * heatflux_per_area)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)s (%(levelname)s) %(message)s")

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--fehm_file', type=Path, help='Path to main grid (.fehm) file.')
    parser.add_argument('--outside_zone_file', type=Path, help='Path to boundary (_outside.zone) file.')
    parser.add_argument('--area_file', type=Path, help='Path to boundary area (.area) file.')
    parser.add_argument('--config_file', type=Path, help='Path to configuration (.yaml/.hfi) file.')
    parser.add_argument('--output_file', type=Path, help='Path for heatflux output to be written.')
    args = parser.parse_args()

    generate_input_heatflux_file(
        config_file=args.config_file,
        fehm_file=args.fehm_file,
        outside_zone_file=args.outside_zone_file,
        area_file=args.area_file,
        output_file=args.output_file,
    )
