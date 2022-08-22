import argparse
import logging
from pathlib import Path
from typing import Optional

from fehm_toolkit.config import FilesConfig, RunConfig
from fehm_toolkit.file_interface.legacy_config import (
    read_legacy_hfi_config,
    read_legacy_ipi_config,
    read_legacy_rpi_config,
)

logger = logging.getLogger(__name__)


def create_run_config_for_legacy_directory(
    directory: Path,
    config_file: Path,
    hfi_file: Optional[Path] = None,
    rpi_file: Optional[Path] = None,
    ipi_file: Optional[Path] = None,
    material_zone_file: Optional[Path] = None,
    outside_zone_file: Optional[Path] = None,
    area_file: Optional[Path] = None,
    rock_properties_file: Optional[Path] = None,
    conductivity_file: Optional[Path] = None,
    pore_pressure_file: Optional[Path] = None,
    permeability_file: Optional[Path] = None,
    files_file: Optional[Path] = None,
    grid_file: Optional[Path] = None,
    input_file: Optional[Path] = None,
    output_file: Optional[Path] = None,
    store_file: Optional[Path] = None,
    history_file: Optional[Path] = None,
    water_properties_file: Optional[Path] = None,
    check_file: Optional[Path] = None,
    error_file: Optional[Path] = None,
    final_conditions_file: Optional[Path] = None,
    flow_file: Optional[Path] = None,
    heat_flux_file: Optional[Path] = None,
    initial_conditions_file: Optional[Path] = None,
):
    if not directory.is_dir():
        raise ValueError(f'{directory.absolute()} is not a directory.')

    hfi_file = hfi_file or _find_unique_match(directory, '*.hfi')
    ipi_file = ipi_file or _find_unique_match(directory, '*.ipi')
    rpi_file = rpi_file or _find_unique_match(directory, '*.rpi')
    run_root = hfi_file.stem if hfi_file.stem == ipi_file.stem == rpi_file.stem else 'run'

    files_config = FilesConfig(
        run_root=run_root,
        material_zone=material_zone_file or _find_material_zone_file(directory),
        outside_zone=outside_zone_file or _find_unique_match(directory, '*_outside.zone'),
        area=area_file or _find_unique_match(directory, '*.area'),
        rock_properties=rock_properties_file or _find_unique_match(directory, '*.rock'),
        conductivity=conductivity_file or _find_unique_match(directory, '*.cond'),
        pore_pressure=pore_pressure_file or _find_unique_match(directory, '*.ppor'),
        permeability=permeability_file or _find_unique_match(directory, '*.perm'),
        files=files_file or _find_unique_match(directory, '*.files'),
        grid=grid_file or _find_unique_match(directory, '*.fehm*'),
        input=input_file or _find_unique_match(directory, '*.dat'),
        output=output_file or _find_unique_match(directory, '*.out'),
        store=store_file or _find_unique_match(directory, '*.stor'),
        history=history_file or _find_unique_match(directory, '*.hist'),
        water_properties=water_properties_file or _find_unique_match(directory, '*.wpi'),
        check=check_file or _find_unique_match(directory, '*.chk'),
        error=error_file or _find_unique_match(directory, '*.err'),
        final_conditions=final_conditions_file or _find_unique_match(directory, '*.fin'),
        flow=flow_file or _find_unique_match(directory, '*.flow', allow_none=True),
        heat_flux=heat_flux_file or _find_unique_match(directory, '*.hflx', allow_none=True),
        initial_conditions=initial_conditions_file or _find_unique_match(directory, '*.ini', allow_none=True),
    )
    files_config.validate()
    files_config = files_config.relative_to(directory)

    run_config = RunConfig(
        heat_flux_config=read_legacy_hfi_config(hfi_file),
        pressure_config=read_legacy_ipi_config(ipi_file),
        rock_properties_config=read_legacy_rpi_config(rpi_file),
        files_config=files_config,
    )
    logger.info('Writing config file to %s', config_file)
    run_config.to_yaml(config_file)


def _find_unique_match(directory: Path, pattern: str, allow_none: bool = False) -> Path:
    matches = list(directory.glob(pattern))
    if not matches and allow_none:
        logger.info('No file found for optional file "%s", skipping...', pattern)
        return None
    if len(matches) != 1:
        raise ValueError(f'Found {len(matches)} matches for "{pattern}" in {directory}, please specify explicitly.')
    return matches[0]


def _find_material_zone_file(directory: Path) -> Path:
    material_zone_file = None
    for path in directory.glob('*.zone'):
        if path.stem.endswith('_outside'):
            continue

        if path.stem.endswith('_material'):
            material_zone_file = path
        else:
            return path  # prefer plain *.zone file

    if not material_zone_file:
        raise ValueError('Could not find unique material zone file.')

    return material_zone_file


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)s (%(levelname)s) %(message)s")

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('directory', type=Path, help='Path to directory with legacy configuration files.')
    parser.add_argument('--config_file', type=Path, help='Output configuration file location (default: config.yaml).')
    parser.add_argument('--hfi_file', type=Path, help='Optional location of legacy heat flux configuration file.')
    parser.add_argument('--rpi_file', type=Path, help='Optional location of legacy rock properties configuration file.')
    parser.add_argument('--ipi_file', type=Path, help='Optional location of legacy pressure configuration file.')
    parser.add_argument('--material_zone_file', type=Path, help='Optional location of material_zone file.')
    parser.add_argument('--outside_zone_file', type=Path, help='Optional location of outside_zone file.')
    parser.add_argument('--area_file', type=Path, help='Optional location of area file.')
    parser.add_argument('--rock_properties_file', type=Path, help='Optional location of rock_properties file.')
    parser.add_argument('--conductivity_file', type=Path, help='Optional location of conductivity file.')
    parser.add_argument('--pore_pressure_file', type=Path, help='Optional location of pore_pressure file.')
    parser.add_argument('--permeability_file', type=Path, help='Optional location of permeability file.')
    parser.add_argument('--files_file', type=Path, help='Optional location of files file.')
    parser.add_argument('--grid_file', type=Path, help='Optional location of grid file.')
    parser.add_argument('--input_file', type=Path, help='Optional location of input file.')
    parser.add_argument('--output_file', type=Path, help='Optional location of output file.')
    parser.add_argument('--store_file', type=Path, help='Optional location of store file.')
    parser.add_argument('--history_file', type=Path, help='Optional location of history file.')
    parser.add_argument('--water_properties_file', type=Path, help='Optional location of water_properties file.')
    parser.add_argument('--check_file', type=Path, help='Optional location of check file.')
    parser.add_argument('--error_file', type=Path, help='Optional location of error file.')
    parser.add_argument('--final_conditions_file', type=Path, help='Optional location of final_conditions file.')
    parser.add_argument('--flow_file', type=Path, help='Optional location of flow file.')
    parser.add_argument('--heat_flux_file', type=Path, help='Optional location of heat_flux file.')
    parser.add_argument('--initial_conditions_file', type=Path, help='Optional location of initial_conditions file.')
    args = parser.parse_args()

    create_run_config_for_legacy_directory(
        args.directory,
        config_file=args.config_file or args.directory / 'config.yaml',
        hfi_file=args.hfi_file,
        rpi_file=args.rpi_file,
        ipi_file=args.ipi_file,
        material_zone_file=args.material_zone_file,
        outside_zone_file=args.outside_zone_file,
        area_file=args.area_file,
        rock_properties_file=args.rock_properties_file,
        conductivity_file=args.conductivity_file,
        pore_pressure_file=args.pore_pressure_file,
        permeability_file=args.permeability_file,
        files_file=args.files_file,
        grid_file=args.grid_file,
        input_file=args.input_file,
        output_file=args.output_file,
        store_file=args.store_file,
        history_file=args.history_file,
        water_properties_file=args.water_properties_file,
        check_file=args.check_file,
        error_file=args.error_file,
        final_conditions_file=args.final_conditions_file,
        flow_file=args.flow_file,
        heat_flux_file=args.heat_flux_file,
        initial_conditions_file=args.initial_conditions_file,
    )
