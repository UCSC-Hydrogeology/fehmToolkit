import logging
from pathlib import Path
from typing import Optional, Sequence
import warnings

import pandas as pd

from fehmtk.config import RunConfig
from fehmtk.fehm_objects import Node, Grid, Zone
from fehmtk.file_interface import read_grid, read_restart

logger = logging.getLogger(__name__)


def compare_runs(config_file: Path, compare_config_file: Path, output_file: Path, nodes: Optional[Sequence] = None):
    _summarize_run(config_file, compare_config_file=compare_config_file, output_file=output_file, nodes=nodes)


def summarize_run(config_file: Path, output_file: Path, nodes: Optional[Sequence] = None):
    _summarize_run(config_file, output_file=output_file, nodes=nodes)


def _summarize_run(
    config_file: Path,
    *,
    output_file: Path,
    nodes: Optional[Sequence] = None,
    compare_config_file: Optional[Path] = None,
):
    logger.info('Reading configuration file: %s', config_file)
    config = RunConfig.from_yaml(config_file)

    if not nodes:
        logger.info('Reading monitored nodes from input file: %s', config.files_config.input)
        nodes = read_monitored_nodes_from_input(config.files_config.input)
    nodes = sorted(nodes)

    logger.info('Parsing grid into memory from files in %s', config_file)
    grid = read_grid(
        config.files_config.grid,
        outside_zone_file=config.files_config.outside_zone,
        material_zone_file=config.files_config.material_zone,
        read_elements=False,
    )

    monitored = (
        pd.DataFrame(data=[_dict_from_node(grid.node(i)) for i in nodes])
    )
    logger.info('Reading state from restart file: %s', config.files_config.final_conditions)
    state, metadata = read_restart(config.files_config.final_conditions)

    if compare_config_file:
        logger.info('Reading configuration file: %s', compare_config_file)
        compare_config_file = RunConfig.from_yaml(compare_config_file)
        _validate_same_grids(grid, compare_config_file)

        logger.info('Reading state from restart file: %s', compare_config_file.files_config.final_conditions)
        other_state, other_metadata = read_restart(compare_config_file.files_config.final_conditions)
        state = state - other_state

    monitored_indexes = [i - 1 for i in nodes]
    monitored['temperature'] = [state.temperature[i] for i in monitored_indexes]
    monitored['pressure'] = [state.pressure[i] for i in monitored_indexes]
    monitored['saturation'] = [state.saturation[i] for i in monitored_indexes]
    monitored['material_zones'] = _get_zones_for_nodes(nodes, grid.material_zones)
    monitored['outside_zones'] = _get_zones_for_nodes(nodes, grid.outside_zones)

    logger.info('Writing output to: %s', output_file)
    monitored.to_csv(output_file, index=False)


def _dict_from_node(node: Node) -> dict:
    return {'node': node.number, 'x': node.x, 'y': node.y, 'z': node.z, 'depth': node.depth}


def _get_zones_for_nodes(nodes: list[int], zones: set[Zone]) -> list[int]:
    zone_lookup = {zone.number: set(zone.data) for zone in zones}
    return [
        [zone_number for zone_number, zone_nodes in zone_lookup.items() if node in zone_nodes]
        for node in nodes
    ]


def _validate_same_grids(grid: Grid, other_config: RunConfig):
    logger.info('Parsing grid into memory from files in compare config')
    other_grid = read_grid(
        other_config.files_config.grid,
        outside_zone_file=other_config.files_config.outside_zone,
        material_zone_file=other_config.files_config.material_zone,
        read_elements=False,
    )
    if grid.n_nodes != other_grid.n_nodes:
        raise ValueError(f'Grids have differing number of nodes: {grid.n_nodes} != {other_grid.n_nodes}')
    for zone in grid.material_zones:
        try:
            other_zone = other_grid.get_material_zone(zone.number)
        except KeyError:
            warnings.warn('Material zone not present in other grid: %d', zone.number)
            continue

        if zone.data != other_zone.data:
            raise ValueError(f'Grids have differing nodes in material zone: {zone.number}')
    for zone in grid.outside_zones:
        try:
            other_zone = other_grid.get_outside_zone(zone.number)
        except KeyError:
            warnings.warn('Outside zone not present in other grid: %d', zone.number)
            continue

        if zone.data != other_grid.get_outside_zone(zone.number).data:
            raise ValueError(f'Grids have differing nodes in outside zone: {zone.number}')


def read_monitored_nodes_from_input(input_file: Path) -> set[int]:
    all_nodes = set()
    with open(input_file) as f:
        for line in f:
            if line.strip() == 'node':
                n_nodes = int(next(f).strip())
                nodes = [int(node) for node in next(f).strip().split()]
                if len(nodes) != n_nodes:
                    warnings.warn('n_nodes (%d) does not match nodes read ({len(nodes)}) in %s', n_nodes, input_file)
                all_nodes.update(nodes)
    return all_nodes
