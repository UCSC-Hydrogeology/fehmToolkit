import logging
from pathlib import Path
from typing import Iterable

from fehm_toolkit.config import ModelConfig, RockPropertiesConfig, RunConfig
from fehm_toolkit.fehm_objects import Node, Grid, Zone
from fehm_toolkit.file_interface import read_grid, write_compact_node_data
from fehm_toolkit.property_models import get_rock_property_model

logger = logging.getLogger(__name__)

PROPERTY_KINDS = ('grain_density', 'specific_heat', 'porosity', 'conductivity', 'permeability', 'compressibility')


def generate_rock_properties(config_file: Path):
    logger.info(f'Reading configuration file: {config_file}')
    config = RunConfig.from_yaml(config_file)

    logger.info('Parsing grid into memory')
    grid = read_grid(
        config.files_config.grid,
        outside_zone_file=config.files_config.outside_zone,
        material_zone_file=config.files_config.material_zone,
        read_elements=False,
    )

    property_lookups = compute_rock_properties(grid, config.rock_properties_config)

    logger.info('Writing property file (rock): %s', config.files_config.rock_properties)
    output_by_node = {
        node.number: (
            property_lookups['grain_density'][node.number],
            property_lookups['specific_heat'][node.number],
            property_lookups['porosity'][node.number],
        )
        for node in grid.nodes
    }
    write_compact_node_data(output_by_node, config.files_config.rock_properties, header='rock\n', footer='\n')

    for property_kind, header, output_file in (
        ('conductivity', 'cond\n', config.files_config.conductivity),
        ('permeability', 'perm\n', config.files_config.permeability),
        ('compressibility', 'ppor\n   1\n', config.files_config.pore_pressure),
    ):
        logger.info('Writing property file (%s): %s', header, output_file)
        write_compact_node_data(property_lookups[property_kind], output_file, header=header, footer='\n')


def compute_rock_properties(grid: Grid, rock_properties_config: RockPropertiesConfig) -> dict[str, dict[int, float]]:
    _validate_config_all_zones_exist(rock_properties_config, zones=grid.material_zones)

    model_lookup_by_zone_and_property = rock_properties_config.create_model_lookup_by_zone_and_property()
    property_lookups = {}
    for zone in rock_properties_config.zone_assignment_order:
        logger.info('Computing properties for zone (%d)', zone)
        model_config_by_property_kind = model_lookup_by_zone_and_property[zone]
        zone_properties = _compute_rock_properties_for_zone(
            model_config_by_property_kind,
            nodes=grid.get_nodes_in_material_zone(zone),
        )
        property_lookups = _update_with_zone_properties(property_lookups, zone_properties)

    _validate_all_nodes_covered(property_lookups, grid.n_nodes)
    return property_lookups


def _compute_rock_properties_for_zone(
    model_config_by_property_kind: dict[str, ModelConfig],
    nodes: Iterable[Node],
) -> dict[str, dict[int, float]]:
    zone_properties = {}
    for property_kind, model_config in model_config_by_property_kind.items():
        rock_property_model = get_rock_property_model(property_kind, model_config.kind)

        zone_properties[property_kind] = {
            node.number: rock_property_model(node.depth, model_config_by_property_kind, property_kind)
            for node in nodes
        }
    return zone_properties


def _update_with_zone_properties(property_lookups: dict, zone_properties: dict) -> dict:
    combined = {}
    for property_kind in PROPERTY_KINDS:
        property_lookup = property_lookups.get(property_kind, {}).copy()
        property_lookup.update(zone_properties[property_kind])
        combined[property_kind] = property_lookup
    return combined


def _validate_config_all_zones_exist(config: RockPropertiesConfig, zones: tuple[Zone]):
    model_lookup_by_zone_and_property = config.create_model_lookup_by_zone_and_property()
    config_zones = model_lookup_by_zone_and_property.keys()

    assignment_zones = set(config.zone_assignment_order)
    mismatched_assignment_zones = config_zones ^ assignment_zones
    if mismatched_assignment_zones:
        raise ValueError(f'Zones in zone_assignment_order do not match those in config {mismatched_assignment_zones}')

    mismatched_zones = config_zones - {zone.number for zone in zones}
    if mismatched_zones:
        raise ValueError(f'Config zones do not exist in grid {mismatched_zones}')

    for zone, zone_config in model_lookup_by_zone_and_property.items():
        mismatched_property_kinds = zone_config.keys() ^ PROPERTY_KINDS
        if mismatched_property_kinds:
            raise ValueError(f'Mismatched property kinds in zone {zone}: {mismatched_property_kinds}')


def _validate_all_nodes_covered(property_lookups: dict, n_nodes: int):
    for property_kind, values_by_node in property_lookups.items():
        expected_nodes = set(range(1, n_nodes + 1))
        missing_nodes = expected_nodes - values_by_node.keys()
        if missing_nodes:
            raise ValueError(f'Computed {property_kind} missing values for nodes: {missing_nodes}')
