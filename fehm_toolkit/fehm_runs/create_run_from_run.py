import dataclasses
from pathlib import Path
from typing import Optional, Sequence

import numpy as np

from fehm_toolkit.fehm_objects import State
from fehm_toolkit.config import FilesConfig, RunConfig
from fehm_toolkit.file_manipulation import create_restart_from_restart, create_run_with_source_files
from fehm_toolkit.file_interface import read_grid, read_restart, write_files_index, write_restart


def create_run_from_run(
    config_file: Path,
    target_directory: Path,
    run_root: str = None,
    reset_zones: Optional[Sequence[str]] = None,
    pressure_file: Optional[Path] = None,
):
    config = RunConfig.from_yaml(config_file)
    files_config = config.files_config

    if target_directory.exists():
        raise ValueError(f'target_directory: {target_directory} already exists.')

    if reset_zones and pressure_file:
        raise ValueError('Cannot override pressures and also reset to initial pressures, must choose one.')

    if reset_zones and files_config.initial_conditions is None:
        raise ValueError('Cannot reset initial pressures, no initial_conditions file set in config.')

    state, metadata = create_restart_from_restart(
        files_config.final_conditions,
        reset_model_time=True,
        pressure_file=pressure_file,
    )
    if reset_zones:
        replacement_state, initial_metadata = read_restart(files_config.initial_conditions)
        grid = read_grid(files_config.grid, outside_zone_file=files_config.outside_zone, read_elements=False)
        state = replace_node_pressures(state, replacement_state, node_numbers={
            node.number for zone in reset_zones for node in grid.get_nodes_in_outside_zone(zone)
        })

    target_files = _generate_target_files_config(files_config, target_directory, run_root=run_root)
    file_pairs_by_kind = _gather_file_pairs_to_copy(files_config, target_files)
    create_run_with_source_files(target_directory, file_pairs_by_kind)
    write_files_index(target_files, output_file=target_files.files)

    write_restart(state, metadata, output_file=target_files.initial_conditions)

    target_config = dataclasses.replace(config, files_config=target_files)
    target_config.to_yaml(target_directory / config_file.name)


def _generate_target_files_config(
    source_files: FilesConfig,
    target_directory: Path,
    run_root: str = None,
) -> FilesConfig:
    old_root = source_files.run_root
    return FilesConfig(
        run_root=run_root or old_root,
        material_zone=target_directory / _get_file_name(source_files.material_zone, old_root, run_root),
        outside_zone=target_directory / _get_file_name(source_files.outside_zone, old_root, run_root),
        area=target_directory / _get_file_name(source_files.area, old_root, run_root),
        rock_properties=target_directory / _get_file_name(source_files.rock_properties, old_root, run_root),
        conductivity=target_directory / _get_file_name(source_files.conductivity, old_root, run_root),
        pore_pressure=target_directory / _get_file_name(source_files.pore_pressure, old_root, run_root),
        permeability=target_directory / _get_file_name(source_files.permeability, old_root, run_root),
        files=target_directory / _get_file_name(source_files.files, old_root, run_root),
        grid=target_directory / _get_file_name(source_files.grid, old_root, run_root),
        input=target_directory / _get_file_name(source_files.input, old_root, run_root),
        output=target_directory / _get_file_name(source_files.output, old_root, run_root),
        store=target_directory / _get_file_name(source_files.store, old_root, run_root),
        history=target_directory / _get_file_name(source_files.history, old_root, run_root),
        water_properties=target_directory / _get_file_name(source_files.water_properties, old_root, run_root),
        check=target_directory / _get_file_name(source_files.check, old_root, run_root),
        error=target_directory / _get_file_name(source_files.error, old_root, run_root),
        final_conditions=target_directory / _get_file_name(source_files.final_conditions, old_root, run_root),
        flow=(
            target_directory / _get_file_name(source_files.flow, old_root, run_root)
            if source_files.flow else None
        ),
        heat_flux=(
            target_directory / _get_file_name(source_files.heat_flux, old_root, run_root)
            if source_files.heat_flux else None
        ),
        initial_conditions=(
            target_directory / _get_file_name(source_files.initial_conditions, old_root, run_root)
            if source_files.initial_conditions else target_directory / f'{run_root or old_root}.ini'
        ),
    )


def _get_file_name(file, old_root, new_root):
    """Get new file name, replacing old root where necessary.
    >>> _get_file_name(Path('run.txt'), 'run', 'run2')
    'run2.txt'
    >>> _get_file_name(Path('p12_outside.zone'), 'p12', 'p13')
    'p13_outside.zone'
    >>> _get_file_name(Path('fehmn.files'), 'run', 'run2')
    'fehmn.files'
    >>> _get_file_name(Path('run.txt'), 'run', None)
    'run.txt'
    """
    if new_root is None:
        return file.name

    return file.name.replace(old_root, new_root)


def _gather_file_pairs_to_copy(
    source_files: FilesConfig,
    target_files: FilesConfig,
) -> dict[str, tuple[Path, Path]]:
    file_pairs_by_kind = {
        'material_zone': (source_files.material_zone, target_files.material_zone),
        'outside_zone': (source_files.outside_zone, target_files.outside_zone),
        'area': (source_files.area, target_files.area),
        'rock_properties': (source_files.rock_properties, target_files.rock_properties),
        'conductivity': (source_files.conductivity, target_files.conductivity),
        'permeability': (source_files.permeability, target_files.permeability),
        'pore_pressure': (source_files.pore_pressure, target_files.pore_pressure),
        'grid': (source_files.grid, target_files.grid),
        'input': (source_files.input, target_files.input),
        'store': (source_files.store, target_files.store),
        'water_properties': (source_files.water_properties, target_files.water_properties),
    }

    if source_files.flow:
        file_pairs_by_kind['flow'] = (source_files.flow, target_files.flow)

    if source_files.heat_flux:
        file_pairs_by_kind['heat_flux'] = (source_files.heat_flux, target_files.heat_flux)

    return file_pairs_by_kind


def replace_node_pressures(state: State, replacement_state: State, node_numbers: Sequence[str]) -> State:
    if len(state.pressure) != len(replacement_state.pressure):
        raise ValueError(
            f'Pressure array not same size as replacement ({len(state.pressure)} != {len(replacement_state.pressure)})'
        )
    if max(node_numbers) - 1 > len(state.pressure):
        raise ValueError(f'Node number out of range for pressure array (len: {len(state.pressure)})')

    indexes = [n - 1 for n in node_numbers]
    combined = np.array(state.pressure)
    combined[indexes] = np.array(replacement_state.pressure)[indexes]
    return dataclasses.replace(state, pressure=tuple(combined))
