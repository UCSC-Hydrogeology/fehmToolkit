import logging
from pathlib import Path
import re
from typing import Union
import warnings

from fehmtk.config import BoundariesConfig, RunConfig
from fehmtk.fehm_objects import Grid, Node
from fehmtk.file_interface import read_grid, write_compact_node_data

logger = logging.getLogger(__name__)


def generate_flow_boundaries(config_file: Path):
    logger.info(f'Reading configuration file: {config_file}')
    config = RunConfig.from_yaml(config_file)
    if config.files_config.flow is None:
        raise ValueError(f'Flow file missing from files_config in RunConfig at {config_file}')

    _validate_boundaries_config(config.boundaries_config)

    logger.info('Parsing grid into memory')
    grid = read_grid(
        config.files_config.grid,
        outside_zone_file=config.files_config.outside_zone,
        material_zone_file=config.files_config.material_zone,
        storage_file=config.files_config.storage,
        read_elements=False,
    )

    logger.info('Generating flow data')
    flow_by_node = generate_flow_data_by_node_number(config.boundaries_config, grid)
    write_compact_node_data(
        flow_by_node,
        output_file=config.files_config.flow,
        header='flow\n',
        footer='0\n',
    )

    warn_if_file_not_referenced(input_file=config.files_config.input, referenced_file=config.files_config.flow)


def generate_flow_data_by_node_number(config: BoundariesConfig, grid: Grid) -> dict[int, float]:
    flow_data_by_number = {}
    for flow_config in config.flow_configs:
        model = flow_config.boundary_model
        nodes = _gather_nodes(grid, flow_config.outside_zones, flow_config.material_zones)
        for node in nodes:
            skd = '0'
            eflow = -model.params['input_fluid_temp_degC']
            aiped = abs(node.volume * model.params['aiped_to_volume_ratio'])
            flow_data_by_number[node.number] = (skd, eflow, aiped)
    return flow_data_by_number


def _gather_nodes(grid: Grid, outside_zones: list[Union[str, int]], material_zones: list[Union[str, int]]) -> set[Node]:
    nodes = set()
    for zone in outside_zones:
        nodes.update(grid.get_nodes_in_outside_zone(zone))
    for zone in material_zones:
        nodes.update(grid.get_nodes_in_material_zone(zone))
    return nodes


def warn_if_file_not_referenced(*, input_file: Path, referenced_file: Path):
    content = input_file.read_text()
    match = re.search(rf'(\s){referenced_file.name}(\s)', content)
    if not match:
        warnings.warn(f'Generated file {referenced_file.name} IS NOT REFERENCED in {input_file.name}.')


def _validate_boundaries_config(config: BoundariesConfig):
    if config is None:
        raise ValueError('No boundaries_config in config file.')

    for flow_config in config.flow_configs:
        model = flow_config.boundary_model
        if model.kind not in ('open_flow'):
            raise NotImplementedError(f'Boundary model kind ({model.kind}) not supported.')

        if not flow_config.material_zones and not flow_config.outside_zones:
            raise ValueError('No zones specified (outside or material), at least one zone is required.')
