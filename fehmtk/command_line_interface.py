import argparse
import logging
from pathlib import Path

from .config import RunConfig
from .fehm_runs import create_config_for_legacy_run, create_run_from_mesh, create_run_from_run
from .preprocessors import (
    generate_flow_boundaries,
    generate_hydrostatic_pressure,
    generate_heat_flux_boundaries,
    generate_rock_properties,
)
from .postprocessors import (
    check_history,
    compare_runs,
    summarize_run,
)
from .file_manipulation import append_zones


def entry_point():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s (%(levelname)s) %(message)s")
    parser = argparse.ArgumentParser(prog='fehmtk', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    add_fehmtk_subparsers(parser)

    args = vars(parser.parse_args())

    if '_func' not in args:
        parser.print_help()
        return

    _func = args.pop('_func')
    _name = args.pop('_name')
    config_file = args.get('config_file')
    if config_file:
        config = RunConfig.from_yaml(config_file)
        command_defaults = (config.command_defaults or {}).get(_name, {})
        for keyword, default_value in command_defaults.items():
            if args.get(keyword) is None:
                args[keyword] = default_value

    _func(**args)


def add_fehmtk_subparsers(parser):
    subparsers = parser.add_subparsers(help='FEHM toolkit commands')

    # --------------------
    # run_from_mesh
    # --------------------

    run_from_mesh = subparsers.add_parser(
        'run_from_mesh',
        help='Create a new run directory from a LaGriT mesh',
        description=(
            'Create a run directory by copying files from a LaGriT mesh directory. Also generates template '
            'configuration and FEHM input files, to be edited manually by the user.'
        ),
    )
    run_from_mesh.add_argument(
        'mesh_directory',
        type=Path,
        help='Mesh directory containing source files generated with LaGriT in `dump / fehm` style',
    )
    run_from_mesh.add_argument('target_directory', type=Path, help='Destination run directory to be created')
    run_from_mesh.add_argument(
        'water_properties_file',
        type=Path,
        help='NIST lookup table (.out/.wpi) containing water properties; will be static-linked rather than copied',
    )
    run_from_mesh.add_argument(
        '--append_zones',
        type=int_or_string,
        nargs='*',
        help=(
            'Space-separated list of zone names or numbers for outside zones to append to the material zone file; '
            'used to enable specifying outside zones as boundary conditions in FEHM'
        ),
    )
    run_from_mesh.add_argument(
        '--run_root',
        type=str,
        help=(
            'Common root used to name run files (e.g. `my_run.dat`) with alternative file extensions assigned '
            'to disambiguate files'
        ),
    )
    run_from_mesh.add_argument(
        '--grid_file',
        type=Path,
        help='Main grid (.fehm[n]) file; will be inferred from file names if not provided',
    )
    run_from_mesh.add_argument(
        '--storage_file',
        type=Path,
        help='FEHM storage coefficients (.stor) file; will be inferred from file names if not provided',
    )
    run_from_mesh.add_argument(
        '--material_zone_file',
        type=Path,
        help='Material (_material.zone) file; will be inferred from file names if not provided',
    )
    run_from_mesh.add_argument(
        '--outside_zone_file',
        type=Path,
        help='Boundary (_outside.zone) file; will be inferred from file names if not provided',
    )
    run_from_mesh.add_argument(
        '--area_file',
        type=Path,
        help='Boundary area (.area) file; will be inferred from file names if not provided',
    )
    run_from_mesh.set_defaults(_func=create_run_from_mesh, _name='run_from_mesh')

    # --------------------
    # run_from_run
    # --------------------

    run_from_run = subparsers.add_parser(
        'run_from_run',
        help='Create a run directory from a previous run',
        description=(
            'Create a run directory by copying files from an existing run. The final conditions file is copied as '
            'initial conditions, with model time reset to 0.'
        ),
    )
    run_from_run.add_argument('config_file', type=Path, help='Run configuration (config.yaml) file')
    run_from_run.add_argument('target_directory', type=Path, help='Destination run directory to be created')
    run_from_run.add_argument(
        '--run_root',
        type=str,
        help=(
            'Common root used to name run files (e.g. `my_run.dat`) with alternative file extensions assigned '
            'to disambiguate files; names updated in copied FEHM input file'
        ),
    )
    run_from_run_exclusive = run_from_run.add_mutually_exclusive_group()
    run_from_run_exclusive.add_argument('--reset_zones', type=int_or_string, nargs='+', help=(
        'Space-separated list of zone names or numbers referring to OUTSIDE zones; pressures set to '
        ' initial_conditions for nodes in specified zones (MUTUALLY EXCLUSIVE with `--pressure_file`)'
    ))
    run_from_run_exclusive.add_argument('--pressure_file', type=Path, help=(
        'Pressure (.iap/.icp) file; pressure set to those in file for all nodes '
        '(MUTUALLY EXCLUSIVE with `--reset_zones`)'
    ))
    run_from_run.set_defaults(_func=create_run_from_run, _name='run_from_run')

    # --------------------
    # rock_properties
    # --------------------

    rock_properties = subparsers.add_parser(
        'rock_properties',
        help='Generate rock properties from configuration',
        description=(
            'Generate rock properties files (rock_properties, conductivity, pore_pressure, permeability), based on '
            'configuration under `rock_properties_config` in specified file. These files must be referenced in FEHM '
            'input file to be used. See config documentation for available property models.'
        ),
    )
    rock_properties.add_argument('config_file', type=Path, help='Run configuration (config.yaml) file')
    rock_properties.set_defaults(_func=generate_rock_properties, _name='rock_properties')

    # --------------------
    # heat_flux
    # --------------------

    heat_flux = subparsers.add_parser(
        'heat_flux',
        help='Generate heat flux boundaries based on run configuration',
        description=(
            'Generate heat flux boundary condition file, based on configuration under `heat_flux_config` in specified '
            'file. This file must be referenced in FEHM input file to be used. See config documentation for available '
            'boundary models.'
        ),
    )
    heat_flux.add_argument('config_file', type=Path, help='Run configuration (config.yaml) file')
    heat_flux.add_argument(
        '--plot',
        action='store_true',
        help='Flag to plot 2D heat flux maps for outside zones; only supported when a single outside zone is used'
    )
    heat_flux.set_defaults(_func=generate_heat_flux_boundaries, _name='heat_flux')

    # --------------------
    # flow
    # --------------------

    flow = subparsers.add_parser(
        'flow',
        help='Generate flow boundary conditions based on run configuration',
        description=(
            'Generate fluid flow boundary condition file, based on configuration under `flow_config` in specified '
            'file. This file must be referenced in FEHM input file to be used. See config documentation for available '
            'boundary models.'
        ),
    )
    flow.add_argument('config_file', type=Path, help='Run configuration (config.yaml) file')
    flow.set_defaults(_func=generate_flow_boundaries, _name='flow')

    # --------------------
    # history
    # --------------------

    history = subparsers.add_parser(
        'history',
        help='Summary plots of run history file',
        description="Plot a time history of the run's properties at nodes, as recorded in the history file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    history.add_argument('config_file', type=Path, help='Run configuration (config.yaml) file')
    history.add_argument(
        '--last_fraction',
        type=float,
        help='Truncates plots, showing only last fraction of data (e.g., .5 displays the last half, .2 the last fifth)',
        default=0.9,
    )
    history.add_argument(
        '--nodes',
        type=int,
        nargs='+',
        help='Space-separated list of node numbers, only plot these; defaults to all nodes found in the history file',
    )
    history.add_argument(
        '--fields',
        type=str,
        nargs='+',
        help='Space-separated list of fields, only plot these; wrap fields with spaces in double-quotes',
        default=['temperature(deg C)', 'total pressure(Mpa)'],
    )
    history.add_argument(
        '--interact',
        action='store_true',
        help='Flag to open an interactive session with data in memory'
    )
    history.set_defaults(_func=check_history, _name='history')

    # --------------------
    # summary
    # --------------------

    summary = subparsers.add_parser(
        'summary',
        help="Summarize run's final output as CSV",
        description="Produce a summary of a run's final output, formatted as CSV with details for specified nodes.",
    )
    summary.add_argument('config_file', type=Path, help='Run configuration (config.yaml) file')
    summary.add_argument('output_file', type=Path, help='CSV output of properties at nodes to be written')
    summary.add_argument(
        '--nodes',
        type=int,
        nargs='+',
        help='Space-separated list of node numbers to inspect (default: nodes in "node" macros in FEHM input file)',
    )
    summary.add_argument(
        '--interact',
        action='store_true',
        help='Flag to open an interactive session with data in memory'
    )
    summary.set_defaults(_func=summarize_run, _name='summary')

    # --------------------
    # compare
    # --------------------

    compare = subparsers.add_parser(
        'compare',
        help="Compare two run's final outputs as CSV",
        description=(
            "Produce a comparison of two run's final outputs, formatted as CSV with details for specified nodes."
        ),
    )
    compare.add_argument('config_file', type=Path, help='Run configuration (config.yaml) file')
    compare.add_argument('compare_config_file', type=Path, help='Run configuration file for run to compare')
    compare.add_argument('output_file', type=Path, help='CSV output of node and state details to be written')
    compare.add_argument(
        '--nodes',
        type=int,
        nargs='+',
        help='Space-separated list of node numbers to inspect (default: nodes in "node" macros in FEHM input file)',
    )
    compare.add_argument(
        '--interact',
        action='store_true',
        help='Flag to open an interactive session with data in memory'
    )
    compare.set_defaults(_func=compare_runs, _name='compare')

    # --------------------
    # append_zones
    # --------------------

    zones = subparsers.add_parser(
        'append_zones',
        help='Append zones from one zone file to another, overwriting the target',
        description=(
            'Append zones from one zone file to another, overwriting the target file with the combined data. '
            'This is commonly used to add outside zones to a material zone file, to allow them to be referenced '
            'by FEHM.'
        ),
    )
    zones.add_argument('source_file', type=Path, help='Source file for new zones to add')
    zones.add_argument('target_file', type=Path, help='Target file that new zones will be added to')
    zones.add_argument(
        'zones',
        type=int_or_string,
        nargs='+',
        help='Space-separated list of zone names or numbers to append'
    )
    zones.set_defaults(_func=append_zones, _name='append_zones')

    # --------------------
    # hydrostat
    # --------------------

    hydrostat = subparsers.add_parser(
        'hydrostat',
        help='Calculate hydrostatic pressures from thermal state',
        description=(
            'Generate hydrostatic pressures by interpolating and bootstrapping down the water column. This calculation'
            'is based on the temperature state found in the final conditions. Note: this does not match the '
            'hydrostatic calculation done by FEHM, which limits its utility in model configuration and analysis.'
        ),
    )
    hydrostat.add_argument('config_file', type=Path, help='Run configuration (config.yaml) file')
    hydrostat.add_argument('output_file', type=Path, help='Pressure output (.iap/.icp) to be written')
    hydrostat.set_defaults(_func=generate_hydrostatic_pressure, _name='hydrostat')

    # --------------------
    # legacy_config
    # --------------------

    create_config = subparsers.add_parser(
        'legacy_config',
        help='Create config.yaml from legacy configuration files (e.g. .hfi/.rpi/.ipi)',
        description=(
            'Generate a config.yaml file for a legacy directory configured by an outdated version of the FEHM '
            'toolkit. This reads legacy configuration files (i.e. .hfi/.rpi/.ipi) and attempts to infer configuration '
            'from them, raising warnings when assumptions are required and errors if unknown config blocks are '
            'encountered.'
        )
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
    create_config.add_argument('--storage_file', type=Path, help='FEHM storage coefficients (.stor) file')
    create_config.add_argument('--history_file', type=Path, help='History file')
    create_config.add_argument('--water_properties_file', type=Path, help='Water_properties file')
    create_config.add_argument('--check_file', type=Path, help='Check file')
    create_config.add_argument('--error_file', type=Path, help='Error file')
    create_config.add_argument('--final_conditions_file', type=Path, help='Final_conditions file')
    create_config.add_argument('--flow_file', type=Path, help='Flow file')
    create_config.add_argument('--heat_flux_file', type=Path, help='Heat flux file')
    create_config.add_argument('--initial_conditions_file', type=Path, help='Initial_conditions file')
    create_config.set_defaults(_func=create_config_for_legacy_run, _name='legacy_config')

    return subparsers


def int_or_string(arg):
    try:
        return int(arg)  # try convert to int
    except ValueError:
        return arg
