import argparse
import logging
from pathlib import Path

from .fehm_runs import create_config_for_legacy_run, create_run_from_mesh
from .preprocessors import (
    generate_hydrostatic_pressure,
    generate_input_heat_flux,
    generate_rock_properties,
)
from .file_manipulation import append_zones


def entry_point():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s (%(levelname)s) %(message)s")

    parser = argparse.ArgumentParser(prog='fehmtk', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    subparsers = parser.add_subparsers(help='FEHM toolkit commands')

    run_from_mesh = subparsers.add_parser(
        'create_run_from_mesh',
        help='Create a new run directory from a LaGriT mesh',
        description=(
            'Create a run directory by copying files from a mesh direcotry. File name roots are replaced '
            'if run_root is set, otherwise file names are persisted.'
        ),
    )
    run_from_mesh.add_argument('mesh_directory', type=Path, help='Mesh directory containing source files')
    run_from_mesh.add_argument('target_directory', type=Path, help='Destination run directory to be created')
    run_from_mesh.add_argument('water_properties_file', type=Path, help='NIST lookup table (.out/.wpi)')
    run_from_mesh.add_argument(
        '--append_outside_zones',
        type=int_or_string,
        nargs='+',
        help='Outside zones to append to material zone file',
        default=('top', 'bottom'),
    )
    run_from_mesh.add_argument('--run_root', type=str, help='Common root to be used to name run files')
    run_from_mesh.add_argument('--grid_file', type=Path, help='Main grid (.fehm[n]) file')
    run_from_mesh.add_argument('--store_file', type=Path, help='FEHM storage coefficients (.stor) file')
    run_from_mesh.add_argument('--material_zone_file', type=Path, help='Material (_material.zone) file')
    run_from_mesh.add_argument('--outside_zone_file', type=Path, help='Boundary (_outside.zone) file')
    run_from_mesh.add_argument('--area_file', type=Path, help='Boundary area (.area) file')
    run_from_mesh.set_defaults(func=create_run_from_mesh)

    run_from_run = subparsers.add_parser(
        'create_run_from_run',
        help='Create a run directory from a previous run',
        description=(
            'Create a run directory by copying files from an existing run. Model time is reset to 0. '
            'File name roots are replaced if run_root is set, otherwise file names are persisted. '
            'Optionally replace some or all node pressures, controlled by mutually exclusive optional arguments.'
        ),
    )
    run_from_run.add_argument('config_file', type=Path, help='Run configuration (config.yaml) file')
    run_from_run.add_argument('target_directory', type=Path, help='Destination run directory to be created')
    run_from_run.add_argument('--run_root', type=str, help='Common root to be used to name run files')
    run_from_run_exclusive = run_from_run.add_mutually_exclusive_group()
    run_from_run_exclusive.add_argument('--reset_initial_pressure_outside_zones', type=int_or_string, nargs='+', help=(
        'Space-separated list of zone names or numbers; pressure in target initial conditions are reset to '
        ' initial_conditions (per config_file), for nodes in specified zones'
    ))
    run_from_run_exclusive.add_argument('--override_pressure_file', type=Path, help=(
        'Pressure (.iap/.icp) file; pressure in target initial conditions are set to these, for all nodes'
    ))

    create_config = subparsers.add_parser(
        'create_config_for_legacy_run',
        help='Create config.yaml file from legacy configuration files (e.g. .hfi/.rpi/.ipi)',
    )
    create_config.add_argument('directory', type=Path, help='Directory with legacy configuration files')
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

    rock_properties = subparsers.add_parser(
        'generate_rock_properties',
        help='Generate rock properties for run based on configuration'
    )
    rock_properties.add_argument('config_file', type=Path, help='Run configuration (config.yaml) file')
    rock_properties.set_defaults(func=generate_rock_properties)

    heat_in = subparsers.add_parser(
        'generate_input_heat_flux',
        help='Generate input heat flux based on run configuration'
    )
    heat_in.add_argument('config_file', type=Path, help='Run configuration (.yaml/.hfi) file')
    heat_in.add_argument('--plot_result', action='store_true', help='Flag to plot the heat flux')
    heat_in.set_defaults(func=generate_input_heat_flux)

    pressure = subparsers.add_parser(
        'generate_hydrostatic_pressure',
        help='Generate hydrostatic pressures for run by bootstrapping down the column',
    )
    pressure.add_argument('config_file', type=Path, help='Run configuration (config.yaml) file')
    pressure.add_argument('output_file', type=Path, help='Pressure output (.iap/.icp) to be written')
    pressure.set_defaults(func=generate_hydrostatic_pressure)

    zones = subparsers.add_parser(
        'append_zones',
        help='Append zones from one zone file to another, overwriting the target',
    )
    zones.add_argument('source_file', type=Path, help='Source file for new zones to add')
    zones.add_argument('target_file', type=Path, help='Target file that new zones will be added to')
    zones.add_argument('zones', type=int_or_string, nargs='+', help='Space-separated list of zone names or numbers')
    zones.set_defaults(func=append_zones)

    args = vars(parser.parse_args())

    if 'func' not in args:
        parser.print_help()
        return

    func = args.pop('func')
    func(**args)


def int_or_string(arg):
    try:
        return int(arg)  # try convert to int
    except ValueError:
        return arg
