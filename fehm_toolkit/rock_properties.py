import argparse
import logging
from pathlib import Path
from typing import Iterable

from .config import read_legacy_rpi_config
from .fehm_objects import Grid, Node
from .file_interface import read_grid, write_compact_node_data
from .property_models import get_rock_property_model

logger = logging.getLogger(__name__)

PROPERTY_KINDS = ('grain_density', 'specific_heat', 'porosity', 'conductivity', 'permeability', 'compressibility')


def generate_rock_properties_files(
    *,
    config_file: Path,
    fehm_file: Path,
    outside_zone_file: Path,
    material_zone_file: Path,
    cond_output_file: Path,
    perm_output_file: Path,
    ppor_output_file: Path,
    rock_output_file: Path,
):
    logger.info(f'Reading configuration file: {config_file}')
    config = read_legacy_rpi_config(config_file)  # TODO(dustin): add support for other config file formats
    rock_properties_config = config['rock_properties']

    logger.info('Parsing grid into memory')
    grid = read_grid(
        fehm_file,
        outside_zone_file=outside_zone_file,
        material_zone_file=material_zone_file,
        read_elements=False,
    )
    _validate_config_all_zones_covered(rock_properties_config, zones=grid.material_zones)

    property_lookups = {}
    for zone, zone_config in rock_properties_config.items():
        logger.info('Computing properties for zone (%d)', zone)
        zone_properties = compute_rock_properties(zone_config, nodes=grid.get_nodes_in_material_zone(zone))
        property_lookups = _update_with_zone_properties(property_lookups, zone_properties)

    _validate_all_nodes_covered(property_lookups, grid.n_nodes)

    logger.info('Writing property file (rock): %s', rock_output_file)
    output_by_node = {
        node.number: (
            property_lookups['grain_density'][node.number],
            property_lookups['specific_heat'][node.number],
            property_lookups['porosity'][node.number],
        )
        for node in grid.nodes
    }
    write_compact_node_data(output_by_node, rock_output_file, header='rock\n', footer='\n')

    for property_kind, header, output_file in (
        ('conductivity', 'cond\n', cond_output_file),
        ('permeability', 'perm\n', perm_output_file),
        ('compressibility', 'ppor\n   1\n', ppor_output_file),
    ):
        logger.info('Writing property file (%s): %s', header, output_file)
        write_compact_node_data(property_lookups[property_kind], output_file, header=header, footer='\n')


def compute_rock_properties(rock_properties_config: dict, nodes: Iterable[Node]) -> dict[str, dict[int, float]]:
    zone_properties = {}
    for property_kind, property_config in rock_properties_config.items():
        rock_property_model = get_rock_property_model(property_kind, property_config['model_kind'])

        zone_properties[property_kind] = {
            node.number: rock_property_model(node.depth, rock_properties_config, property_kind)
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


def _validate_config_all_zones_covered(config: dict, zones: tuple[int]):
    config_zones = config.keys()
    mismatched_zones = config_zones ^ zones  # ^ is the symmetric difference operator for sets
    if mismatched_zones:
        raise ValueError(f'Config zones do not match zones in grid {mismatched_zones}')

    for zone, zone_config in config.items():
        mismatched_property_kinds = zone_config.keys() ^ PROPERTY_KINDS
        if mismatched_property_kinds:
            raise ValueError(f'Mismatched property kinds in zone {zone}: {mismatched_property_kinds}')


def _validate_all_nodes_covered(property_lookups: dict, n_nodes: int):
    for property_kind, values_by_node in property_lookups.items():
        expected_nodes = set(range(1, n_nodes + 1))
        missing_nodes = expected_nodes - values_by_node.keys()
        if missing_nodes:
            raise ValueError(f'Computed {property_kind} missing values for nodes: {missing_nodes}')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)s (%(levelname)s) %(message)s")

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--fehm_file', type=Path, help='Path to main grid (.fehm) file.')
    parser.add_argument('--outside_zone_file', type=Path, help='Path to boundary (_outside.zone) file.')
    parser.add_argument('--material_zone_file', type=Path, help='Path to material zone (_material.zone) file.')
    parser.add_argument('--config_file', type=Path, help='Path to configuration (.yaml/.hfi) file.')
    parser.add_argument('--cond_output_file', type=Path, help='Path for COND output to be written.')
    parser.add_argument('--perm_output_file', type=Path, help='Path for PERM output to be written.')
    parser.add_argument('--ppor_output_file', type=Path, help='Path for PPOR output to be written.')
    parser.add_argument('--rock_output_file', type=Path, help='Path for ROCK output to be written.')
    args = parser.parse_args()

    generate_rock_properties_files(
        config_file=args.config_file,
        fehm_file=args.fehm_file,
        outside_zone_file=args.outside_zone_file,
        material_zone_file=args.material_zone_file,
        cond_output_file=args.cond_output_file,
        perm_output_file=args.perm_output_file,
        ppor_output_file=args.ppor_output_file,
        rock_output_file=args.rock_output_file,
    )
