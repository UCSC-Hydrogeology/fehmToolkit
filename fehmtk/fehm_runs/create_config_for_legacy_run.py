import logging
from pathlib import Path
from typing import Optional

from fehmtk.config import BoundaryConfig, FilesConfig, FlowConfig, ModelConfig, RunConfig
from fehmtk.file_interface import get_unique_file
from fehmtk.file_interface.legacy_config import (
    read_legacy_hfi_config,
    read_legacy_ipi_config,
    read_legacy_rpi_config,
)

logger = logging.getLogger(__name__)


def create_config_for_legacy_run(
    directory: Path,
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
    storage_file: Optional[Path] = None,
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

    hfi_file = hfi_file or get_unique_file(directory, '*.hfi')
    ipi_file = ipi_file or get_unique_file(directory, '*.ipi')
    rpi_file = rpi_file or get_unique_file(directory, '*.rpi')
    run_root = hfi_file.stem if hfi_file.stem == ipi_file.stem == rpi_file.stem else 'run'

    files_config = FilesConfig(
        run_root=run_root,
        material_zone=material_zone_file or _find_material_zone_file(directory),
        outside_zone=outside_zone_file or get_unique_file(directory, '*_outside.zone'),
        area=area_file or get_unique_file(directory, '*.area'),
        rock_properties=rock_properties_file or get_unique_file(directory, '*.rock'),
        conductivity=conductivity_file or get_unique_file(directory, '*.cond'),
        pore_pressure=pore_pressure_file or get_unique_file(directory, '*.ppor'),
        permeability=permeability_file or get_unique_file(directory, '*.perm'),
        files=files_file or get_unique_file(directory, '*.files'),
        grid=grid_file or get_unique_file(directory, '*.fehm*'),
        input=input_file or get_unique_file(directory, '*.dat'),
        output=output_file or get_unique_file(directory, '*.out'),
        storage=storage_file or get_unique_file(directory, '*.stor'),
        history=history_file or get_unique_file(directory, '*.hist'),
        water_properties=water_properties_file or get_unique_file(directory, '*.wpi'),
        check=check_file or get_unique_file(directory, '*.chk'),
        error=error_file or get_unique_file(directory, '*.err'),
        final_conditions=final_conditions_file or get_unique_file(directory, '*.fin'),
        flow=flow_file or get_unique_file(directory, '*.flow', optional=True),
        heat_flux=heat_flux_file or get_unique_file(directory, '*.hflx', optional=True),
        initial_conditions=initial_conditions_file or get_unique_file(directory, '*.ini', optional=True),
    )
    files_config.assert_specified_paths_exist()

    flow_config = None
    if files_config.flow is not None:
        open_flow_params = {'input_fluid_temp_degC': 2, 'aiped_to_volume_ratio': 1e-8}
        logger.warning(
            'Creating flow_config with default parameters, THESE MAY NOT MATCH WHAT WAS INITIALLY USED! %s',
            open_flow_params,
        )
        flow_config = FlowConfig(
            boundary_configs=[
                BoundaryConfig(
                    outside_zones=['top'],
                    material_zones=[],
                    boundary_model=ModelConfig(
                        kind='open_flow',
                        params=open_flow_params,
                    ),
                ),
            ],
        )

    run_config = RunConfig(
        heat_flux_config=read_legacy_hfi_config(hfi_file),
        pressure_config=read_legacy_ipi_config(ipi_file),
        rock_properties_config=read_legacy_rpi_config(rpi_file),
        flow_config=flow_config,
        files_config=files_config,
    )
    logger.info('Writing config file to %s', directory / 'config.yaml')
    run_config.to_yaml(directory / 'config.yaml')


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
