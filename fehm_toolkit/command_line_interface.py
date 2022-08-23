import argparse
import logging
from pathlib import Path

from .fehm_runs import create_config_for_legacy_run, create_run_from_mesh


def entry_point():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s (%(levelname)s) %(message)s")

    parser = argparse.ArgumentParser(prog='fehmtk', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    subparsers = parser.add_subparsers(help='FEHM toolkit commands')

    create_run = subparsers.add_parser('create_run_from_mesh', help='Generate a new run directory from a LaGriT mesh')
    create_run.add_argument('mesh_directory', type=Path, help='Path to mesh directory containing source files')
    create_run.add_argument('run_directory', type=Path, help='Path to destination run directory to be created')
    create_run.add_argument('water_properties_file', type=Path, help='Path to NIST lookup table (.out/.wpi)')
    create_run.add_argument('--run_root', type=str, help='Common root to be used to name run files')
    create_run.add_argument('--grid_file', type=Path, help='Path to main grid (.fehm[n]) file')
    create_run.add_argument('--store_file', type=Path, help='Path to FEHM storage coefficients (.stor) file')
    create_run.add_argument('--material_zone_file', type=Path, help='Path to material (_material.zone) file')
    create_run.add_argument('--outside_zone_file', type=Path, help='Path to boundary (_outside.zone) file')
    create_run.add_argument('--area_file', type=Path, help='Path to boundary area (.area) file')
    create_run.set_defaults(func=create_run_from_mesh)

    create_config = subparsers.add_parser(
        'create_config_for_legacy_run',
        help='Generate a config.yaml file from legacy configuration files (e.g. .hfi/.rpi/.ipi)',
    )
    create_config.add_argument('directory', type=Path, help='Path to directory with legacy configuration files')
    create_config.add_argument('--hfi_file', type=Path, help='Legacy heat flux configuration file')
    create_config.add_argument('--rpi_file', type=Path, help='Legacy rock properties configuration file')
    create_config.add_argument('--ipi_file', type=Path, help='Legacy pressure configuration file')
    create_config.add_argument('--material_zone_file', type=Path, help='Material_zone file')
    create_config.add_argument('--outside_zone_file', type=Path, help='Outside_zone file')
    create_config.add_argument('--area_file', type=Path, help='Area file')
    create_config.add_argument('--rock_properties_file', type=Path, help='Rock_properties file')
    create_config.add_argument('--conductivity_file', type=Path, help='Conductivity file')
    create_config.add_argument('--pore_pressure_file', type=Path, help='Pore_pressure file')
    create_config.add_argument('--permeability_file', type=Path, help='Permeability file')
    create_config.add_argument('--files_file', type=Path, help='Files file')
    create_config.add_argument('--grid_file', type=Path, help='Grid file')
    create_config.add_argument('--input_file', type=Path, help='Input file')
    create_config.add_argument('--output_file', type=Path, help='Output file')
    create_config.add_argument('--store_file', type=Path, help='Store file')
    create_config.add_argument('--history_file', type=Path, help='History file')
    create_config.add_argument('--water_properties_file', type=Path, help='Water_properties file')
    create_config.add_argument('--check_file', type=Path, help='Check file')
    create_config.add_argument('--error_file', type=Path, help='Error file')
    create_config.add_argument('--final_conditions_file', type=Path, help='Final_conditions file')
    create_config.add_argument('--flow_file', type=Path, help='Flow file')
    create_config.add_argument('--heat_flux_file', type=Path, help='Heat flux file')
    create_config.add_argument('--initial_conditions_file', type=Path, help='Initial_conditions file')
    create_config.set_defaults(func=create_config_for_legacy_run)

    args = vars(parser.parse_args())
    func = args.pop('func')
    func(**args)
