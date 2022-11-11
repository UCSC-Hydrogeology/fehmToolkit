import logging
from pathlib import Path
import re
from typing import Union
import warnings

from fehmtk.config import BoundaryConfig, FlowConfig, HeatFluxConfig, RunConfig
from fehmtk.fehm_objects import Grid, Node
from fehmtk.file_interface import read_grid, write_compact_node_data

from .boundary_models import get_boundary_model

logger = logging.getLogger(__name__)


def generate_flow_boundaries(config_file: Path):
    logger.info(f'Reading configuration file: {config_file}')
    config = RunConfig.from_yaml(config_file)
    if config.files_config.flow is None:
        raise ValueError(f'Flow file missing from files_config in RunConfig at {config_file}')

    _validate_config(config.flow_config)

    logger.info('Parsing grid into memory')
    grid = read_grid(
        config.files_config.grid,
        outside_zone_file=config.files_config.outside_zone,
        material_zone_file=config.files_config.material_zone,
        storage_file=config.files_config.storage,
        read_elements=False,
    )

    logger.info('Generating flow data')
    flow_by_node = generate_boundary_data_by_node_number(
        grid,
        boundary_configs=config.flow_config.boundary_configs,
        boundary_kind='flow',
    )
    write_compact_node_data(
        flow_by_node,
        output_file=config.files_config.flow,
        header='flow\n',
        footer='0\n',
    )

    warn_if_file_not_referenced(input_file=config.files_config.input, referenced_file=config.files_config.flow)


def generate_boundary_data_by_node_number(
    grid: Grid,
    *,
    boundary_configs: list[BoundaryConfig],
    boundary_kind: str,
) -> dict[int, float]:
    flow_data_by_number = {}
    for boundary_config in boundary_configs:
        model = get_boundary_model(boundary_kind, boundary_config.boundary_model.kind)
        nodes = _gather_nodes(grid, boundary_config.outside_zones, boundary_config.material_zones)
        for node in nodes:
            flow_data_by_number[node.number] = model(node, boundary_config.boundary_model.params)

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


def _validate_config(config: Union[FlowConfig, HeatFluxConfig]):
    if config is None:
        raise ValueError('No relevant boundary config (flow, heat_flux) found in config file.')

    for boundary_config in config.boundary_configs:
        if not boundary_config.material_zones and not boundary_config.outside_zones:
            raise ValueError('No zones specified (outside or material), at least one zone is required.')
