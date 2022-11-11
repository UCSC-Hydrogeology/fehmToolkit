import dataclasses
import logging
from pathlib import Path
from typing import _UnionGenericAlias, GenericAlias, Optional, Sequence, Type, Union

import yaml

from fehmtk.config import FilesConfig, RunConfig
from fehmtk.file_interface import get_unique_file, write_files_index
from fehmtk import file_manipulation


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
    'storage': '.stor',
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
    append_zones: Optional[Sequence[str]] = ('top', 'bottom'),
    run_root: Optional[str] = None,
    grid_file: Optional[Path] = None,
    storage_file: Optional[Path] = None,
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
        storage_file=storage_file or get_unique_file(mesh_directory, f"*{EXT_BY_FILE['storage']}"),
        material_zone_file=material_zone_file or get_unique_file(mesh_directory, f"*{EXT_BY_FILE['material_zone']}"),
        outside_zone_file=outside_zone_file or get_unique_file(mesh_directory, f"*{EXT_BY_FILE['outside_zone']}"),
        area_file=area_file or get_unique_file(mesh_directory, f"*{EXT_BY_FILE['area']}"),
        water_properties_file=water_properties_file,
    )
    file_manipulation.create_run_with_source_files(target_directory, file_pairs_by_file_type)
    if append_zones:
        file_manipulation.append_zones(
            source_file=file_pairs_by_file_type['outside_zone'][1],
            target_file=file_pairs_by_file_type['material_zone'][1],
            zones=append_zones,
        )

    template_files_config = get_template_files_config(file_pairs_by_file_type, run_root)
    create_template_run_config(template_files_config, output_file=target_directory / CONFIG_NAME)

    files_config = FilesConfig.from_dict(template_files_config)

    logger.info('Writing files index to %s', target_directory / files_config.files.name)
    write_files_index(files_config, output_file=target_directory / files_config.files.name)

    create_template_input_file(files_config, output_file=target_directory / files_config.input.name)
    logger.info(
        'Suggested next steps:\n'
        f'* Update {target_directory / CONFIG_NAME} with desired configuration\n'
        '* Run heat_flux to generate heat flux file\n'
        '* Run rock_properties to generate physical properties files\n'
        f'* Update {target_directory / files_config.input.name} with desired configuration\n'
        f'* Run FEHM'
    )


def create_template_run_config(template_files_config: dict[str, Union[str, Path]], output_file: Path):
    logger.info(
        (
            'Writing run config file to %s. This file is incomplete and must be modified! '
            'Remove REQUIRED/OPTIONAL from all keys, and replace "TYPE__" values with real data.'
        ),
        output_file,
    )
    template_run_config = _generate_template_run_config(template_files_config)
    with open(output_file, 'w') as f:
        yaml.dump(template_run_config, f, Dumper=yaml.Dumper)


def _generate_template_run_config(template_files_config: dict[str, Union[str, Path]]) -> dict:
    (run_config_template, _) = build_template_from_type(RunConfig)
    run_config_template['REQUIRED__files_config'] = template_files_config
    return run_config_template


def build_template_from_type(base_type: Type):
    optional = False
    if isinstance(base_type, _UnionGenericAlias):
        types = set(base_type.__args__)
        if type(None) in types:
            optional = True
            types.remove(type(None))

        if len(types) > 1:
            return f"TYPE__{'|'.join(_get_type_name(t) for t in types)}", optional
        else:
            (base_type,) = types

    if base_type == list:
        return [], optional
    if base_type == dict:
        return {}, optional
    if isinstance(base_type, GenericAlias):
        if base_type.__origin__ == list:
            template, _ = build_template_from_type(base_type.__args__[0])
            return [template], optional
        return f'TYPE__{base_type}', optional
    if dataclasses.is_dataclass(base_type):
        template = {}
        for field in dataclasses.fields(base_type):
            field_template, field_optional = build_template_from_type(field.type)
            template[f"{'OPTIONAL' if field_optional else 'REQUIRED'}__{field.name}"] = field_template
        return template, optional

    return f'TYPE__{_get_type_name(base_type)}', optional


def _get_type_name(base_type: Type):
    try:
        return base_type.__name__
    except AttributeError:
        return str(base_type)


def create_template_input_file(files_config: FilesConfig, output_file: Path):
    logger.info(f'Writing template input file to {output_file}')
    with open(output_file, 'w') as f:
        f.write('"Template conductive run - ALL COMMENTS MUST BE REPLACED with real config!"\n')
        f.write('init\n    # init config goes here (pres macro may be used instead)\n')
        f.write('sol\n    -1    -1\n')
        f.write('ctrl\n    # ctrl config goes here\n')
        f.write('time\n    # time config goes here\n')
        f.write('hflx\n    # hflx config for fixed temperature zones goes here\n')
        f.write(f'hflx\nfile\n{files_config.heat_flux.name}\n')
        f.write(f'rock\nfile\n{files_config.rock_properties.name}\n')
        f.write(f'cond\nfile\n{files_config.conductivity.name}\n')
        f.write(f'perm\nfile\n{files_config.permeability.name}\n')
        f.write(f'ppor\nfile\n{files_config.pore_pressure.name}\n')
        f.write('stop\n')


def _gather_file_pairs_to_copy(
    target_directory: Path,
    run_root: Optional[str],
    *,
    grid_file: Path,
    storage_file: Path,
    material_zone_file: Path,
    outside_zone_file: Path,
    area_file: Path,
    water_properties_file: Path,
) -> dict[str, tuple[Path, Path]]:
    if run_root:
        return {
            'grid': (grid_file, target_directory / f"{run_root}{EXT_BY_FILE['grid']}"),
            'storage': (storage_file, target_directory / f"{run_root}{EXT_BY_FILE['storage']}"),
            'material_zone': (material_zone_file, target_directory / f"{run_root}{EXT_BY_FILE['material_zone']}"),
            'outside_zone': (outside_zone_file, target_directory / f"{run_root}{EXT_BY_FILE['outside_zone']}"),
            'area': (area_file, target_directory / f"{run_root}{EXT_BY_FILE['area']}"),
            'water_properties': (
                water_properties_file, target_directory / f"{run_root}{EXT_BY_FILE['water_properties']}"
            ),
        }

    return {
        'grid': (grid_file, target_directory / grid_file.name),
        'storage': (storage_file, target_directory / storage_file.name),
        'material_zone': (material_zone_file, target_directory / material_zone_file.name),
        'outside_zone': (outside_zone_file, target_directory / outside_zone_file.name),
        'area': (area_file, target_directory / area_file.name),
        'water_properties': (water_properties_file, target_directory / water_properties_file.name),
    }


def get_template_files_config(
    file_pairs_by_file_type: dict[str, tuple[Path, Path]],
    run_root: Optional[str],
) -> dict[str, Path]:

    template, _ = build_template_from_type(FilesConfig)

    template['REQUIRED__run_root'] = run_root or 'run'
    template['REQUIRED__files'] = 'fehmn.files'  # FEHM expects a specific name for this file

    for key, value in template.items():
        (required_str, file_name) = key.split('__')

        if file_name in ('run_root', 'files'):
            continue

        if file_name in file_pairs_by_file_type:
            (source_file, run_file) = file_pairs_by_file_type[file_name]
            template[key] = run_file.name
            continue

        if required_str == 'REQUIRED':
            template[key] = f'{run_root}{EXT_BY_FILE[file_name]}' if run_root else f'{file_name}.txt'

    return template
