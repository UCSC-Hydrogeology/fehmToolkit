import dataclasses
import logging
from pathlib import Path
from typing import _UnionGenericAlias, GenericAlias, Optional, Sequence, Type, Union

import yaml

from fehm_toolkit.config import FilesConfig, RunConfig
from fehm_toolkit.file_interface import get_unique_file, write_files_index
from fehm_toolkit.file_manipulation import append_zones, create_run_with_source_files


logger = logging.getLogger(__name__)

CONFIG_NAME = 'config.yaml'
EXT_BY_FILE = {
    'material_zone': '_material.zone',
    'outside_zone': '_outside.zone',
    'area': '.area',
    'rock_properties': '.rock',
    'conductivity': '.cond',
    'permeability': '.perm',
    'pore_pressure': '.ppor',
    'heat_flux': '.hflx',
    'flow': '.flow',
    'files': '.files',
    'grid': '.fehm',
    'input': '.dat',
    'output': '.out',
    'store': '.stor',
    'history': '.hist',
    'water_properties': '.wpi',
    'check': '.chk',
    'error': '.err',
    'final_conditions': '.fin',
    'initial_conditions': '.ini',
}


def create_run_from_mesh(
    mesh_directory: Path,
    target_directory: Path,
    water_properties_file: Path,
    append_outside_zones: Optional[Sequence[str]] = ('top', 'bottom'),
    run_root: Optional[str] = None,
    grid_file: Optional[Path] = None,
    store_file: Optional[Path] = None,
    material_zone_file: Optional[Path] = None,
    outside_zone_file: Optional[Path] = None,
    area_file: Optional[Path] = None,
):
    if not mesh_directory.is_dir():
        raise ValueError(f'mesh_directory: {mesh_directory} is not a directory.')

    if target_directory.exists():
        raise ValueError(f'target_directory: {target_directory} already exists.')

    if not water_properties_file.exists() or water_properties_file.is_dir():
        raise ValueError(f'water_properties_file: {water_properties_file} does not exist or is a directory.')

    file_pairs_by_file_type = _gather_file_pairs_to_copy(
        target_directory,
        run_root,
        grid_file=grid_file or get_unique_file(mesh_directory, f"*{EXT_BY_FILE['grid']}*"),
        store_file=store_file or get_unique_file(mesh_directory, f"*{EXT_BY_FILE['store']}"),
        material_zone_file=material_zone_file or get_unique_file(mesh_directory, f"*{EXT_BY_FILE['material_zone']}"),
        outside_zone_file=outside_zone_file or get_unique_file(mesh_directory, f"*{EXT_BY_FILE['outside_zone']}"),
        area_file=area_file or get_unique_file(mesh_directory, f"*{EXT_BY_FILE['area']}"),
        water_properties_file=water_properties_file,
    )
    create_run_with_source_files(target_directory, file_pairs_by_file_type)
    if append_outside_zones:
        append_zones(
            add_zones_from_file=file_pairs_by_file_type['outside_zone'][1],
            add_zones_to_file=file_pairs_by_file_type['material_zone'][1],
            zone_keys_to_add=append_outside_zones,
        )

    template_files_config = _get_template_files_config(file_pairs_by_file_type, run_root)
    create_template_run_config(template_files_config, output_file=target_directory / CONFIG_NAME)

    files_config = FilesConfig.from_dict(template_files_config)
    write_files_index(files_config, output_file=target_directory / files_config.files.name)
    create_template_input_file(files_config, output_file=target_directory / files_config.input.name)
    logger.info(
        'Suggested next steps:\n'
        f'* Update {target_directory / CONFIG_NAME} with desired configuration\n'
        '* Run heat_in to generate heat flux file\n'
        '* Run rock_properties to generate physical properties files\n'
        f'* Update {files_config.input} with desired configuration\n'
        f'* Run FEHM\n'
    )


def create_template_run_config(template_files_config: dict[str, Union[str, Path]], output_file: Path):
    logger.info(f'Writing run config file to {output_file}. This file is incomplete and must be modified!')

    template_run_config = _generate_template_run_config(template_files_config)
    with open(output_file, 'w') as f:
        yaml.dump(template_run_config, f, Dumper=yaml.Dumper)


def _generate_template_run_config(template_files_config: dict[str, Union[str, Path]]) -> dict:
    run_config_template = build_template_from_type(RunConfig)
    run_config_template['files_config'] = template_files_config
    return run_config_template


def build_template_from_type(base_type: Type):
    if base_type == list:
        return []
    if base_type == dict:
        return {}
    if isinstance(base_type, GenericAlias):
        if base_type.__origin__ == list:
            return [build_template_from_type(base_type.__args__[0])]
        return f'replace__{base_type}'
    if isinstance(base_type, _UnionGenericAlias):
        type_names = [_get_type_name(t) for t in base_type.__args__]
        return f"replace__{'|'.join(type_names)}"
    if dataclasses.is_dataclass(base_type):
        return {field.name: build_template_from_type(field.type) for field in dataclasses.fields(base_type)}

    return f'replace__{_get_type_name(base_type)}'


def _get_type_name(base_type: Type):
    try:
        return base_type.__name__
    except AttributeError:
        return str(base_type)


def create_template_input_file(files_config: FilesConfig, output_file: Path):
    logger.info(f'Writing template input file to {output_file}. This file is incomplete and must be modified!')
    with open(output_file, 'w') as f:
        f.write('"Template conductive run - ALL COMMENTS MUST BE REPLACED with real config!"\n')
        f.write('init\n    # init config goes here (pres macro may be used instead)\n')
        f.write('sol\n    -1    -1\n')
        f.write('ctrl\n    # ctrl config goes here\n')
        f.write('time\n    # time config goes here\n')
        f.write('hflx\n    # hflx config for fixed temperature zones goes here\n')
        f.write(f'hflx\nfile\n{files_config.heat_flux}\n')
        f.write(f'rock\nfile\n{files_config.rock_properties}\n')
        f.write(f'cond\nfile\n{files_config.conductivity}\n')
        f.write(f'perm\nfile\n{files_config.permeability}\n')
        f.write(f'ppor\nfile\n{files_config.pore_pressure}\n')
        f.write('stop\n')


def _gather_file_pairs_to_copy(
    target_directory: Path,
    run_root: Optional[str],
    *,
    grid_file: Path,
    store_file: Path,
    material_zone_file: Path,
    outside_zone_file: Path,
    area_file: Path,
    water_properties_file: Path,
) -> dict[str, tuple[Path, Path]]:
    if run_root:
        return {
            'grid': (grid_file, target_directory / f"{run_root}{EXT_BY_FILE['grid']}"),
            'store': (store_file, target_directory / f"{run_root}{EXT_BY_FILE['store']}"),
            'material_zone': (material_zone_file, target_directory / f"{run_root}{EXT_BY_FILE['material_zone']}"),
            'outside_zone': (outside_zone_file, target_directory / f"{run_root}{EXT_BY_FILE['outside_zone']}"),
            'area': (area_file, target_directory / f"{run_root}{EXT_BY_FILE['area']}"),
            'water_properties': (
                water_properties_file, target_directory / f"{run_root}{EXT_BY_FILE['water_properties']}"
            ),
        }

    return {
        'grid': (grid_file, target_directory / grid_file.name),
        'store': (store_file, target_directory / store_file.name),
        'material_zone': (material_zone_file, target_directory / material_zone_file.name),
        'outside_zone': (outside_zone_file, target_directory / outside_zone_file.name),
        'area': (area_file, target_directory / area_file.name),
        'water_properties': (water_properties_file, target_directory / water_properties_file.name),
    }


def _get_template_files_config(
    file_pairs_by_file_type: dict[str, tuple[Path, Path]],
    run_root: Optional[str],
) -> dict[str, Path]:
    template_files_config = {'run_root': run_root or 'run'}
    for field in dataclasses.fields(FilesConfig):
        if field.name == 'initial_conditions':
            continue

        if field.name == 'files':  # FEHM expects a specific name for this file
            template_files_config[field.name] = 'fehmn.files'
            continue

        if field.name in file_pairs_by_file_type:
            (source_file, run_file) = file_pairs_by_file_type[field.name]
        elif field.name == 'run_root':
            field_value = run_root
        elif run_root:
            field_value = f"{run_root}{EXT_BY_FILE[field.name]}"
        else:
            field_value = f'{field.name}.txt'

        template_files_config[field.name] = field_value

    return template_files_config
