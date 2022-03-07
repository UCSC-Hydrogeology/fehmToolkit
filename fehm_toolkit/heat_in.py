import argparse
from collections import defaultdict
from itertools import groupby
import logging
from pathlib import Path
from typing import Callable, Dict

from .config.heat_in import read_legacy_config
from .fehm_objects import Grid, Node

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
    write_boundary_heatflux(heatflux_by_node, output_file)


def compute_boundary_heatflux(grid: Grid, config: dict[int, float]):
    heatflux_config = config['heatflux']
    heatflux_models = get_heatflux_models_by_kind()

    try:
        model = heatflux_models[heatflux_config['model_kind']]
    except KeyError:
        raise NotImplementedError(f'No model defined for kind "{heatflux_config["model_kind"]}"')

    input_nodes = grid.get_nodes_in_outside_zone(HEATFLUX_INPUT_ZONE)
    return {node.number: model(node, heatflux_config['model_params']) for node in input_nodes}


def get_heatflux_models_by_kind() -> Dict[str, Callable]:
    return {'crustal_age': _crustal_age_heatflux}


def _crustal_age_heatflux(node: Node, params: dict) -> float:
    distance_from_boundary = params['crustal_age_sign'] * node.x
    distance_from_ridge = params['boundary_distance_to_ridge_m'] + distance_from_boundary
    age = 1 / (params['spread_rate_mm_per_year'] * 1E3) * distance_from_ridge
    heatflux_per_area = params['coefficient_MW'] / age ** 0.5
    return -abs(node.outside_area.z * heatflux_per_area)


def write_boundary_heatflux(heatflux_by_node: dict[int, float], output_file: Path):
    nodes_by_heatflux = _group_nodes_by_formatted_heatflux(heatflux_by_node)
    ordered_heatflux_entries = _get_grouped_heatflux_entries(nodes_by_heatflux)
    _write_heatflux_file(ordered_heatflux_entries, output_file)


def _write_heatflux_file(heatflux_entries: tuple[int, int, str], output_file: Path):
    with open(output_file, 'w') as f:
        f.write(HEATFLUX_HEADER)
        for min_node, max_node, heatflux in heatflux_entries:
            f.write(_format_heatflux_entry(min_node, max_node, heatflux))
        f.write(HEATFLUX_FOOTER)


def _group_nodes_by_formatted_heatflux(heatflux_by_node: dict[int, float]) -> dict[str, list[int]]:
    nodes_by_heatflux = defaultdict(list)
    for node, heatflux in heatflux_by_node.items():
        formatted_heatflux = _format_heatflux(heatflux)
        nodes_by_heatflux[formatted_heatflux].append(node)
    return nodes_by_heatflux


def _get_grouped_heatflux_entries(nodes_by_heatflux: dict[str, list[int]]) -> list[tuple[int, int, str]]:
    heatflux_entries = []
    for heatflux, nodes in nodes_by_heatflux.items():
        for min_node, max_node in _consecutive_groups(sorted(nodes)):
            heatflux_entries.append((min_node, max_node, heatflux))
    return sorted(heatflux_entries, key=lambda entry: entry[0])  # sort by min_node


def _format_heatflux_entry(min_node: int, max_node: int, heatflux: str) -> str:
    r""" Format heatflux entry as a string.
    >>> _format_heatflux_entry(1, 10, '2.00000E02')
    '1\t10\t1\t2.00000E02\t0.\n'
    >>> _format_heatflux_entry(4, 5, '-3.56738E-04')
    '4\t5\t1\t-3.56738E-04\t0.\n'
    """
    return f'{min_node}\t{max_node}\t1\t{heatflux}\t0.\n'


def _consecutive_groups(x: list[int]) -> list[tuple[int]]:
    """ Iterate over consecutive groups found in list of integers.
    >>> list(_consecutive_groups([1, 2, 4]))
    [(1, 2), (4, 4)]
    >>> list(_consecutive_groups([4, 5, 6, 9, 10, 15, 16]))
    [(4, 6), (9, 10), (15, 16)]
    """
    def _value_minus_index(enum: tuple[int, int]) -> int:
        index = enum[0]
        value = enum[1]
        return index - value

    for k, g in groupby(enumerate(x), key=_value_minus_index):
        g = list(g)
        group_start = g[0][1]
        group_end = g[-1][1]
        yield group_start, group_end


def _format_heatflux(heatflux: float) -> str:
    """ Format heatflux value for output to boundary condition file.
    >>> _format_heatflux(-0.0397631)
    '-3.97631E-02'
    >>> _format_heatflux(200)
    '2.00000E+02'
    """
    return f"{heatflux:.5E}"


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
