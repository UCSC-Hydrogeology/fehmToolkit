from decimal import Decimal
from pathlib import Path
from typing import Sequence, TextIO

from fehm_toolkit.fehm_objects import RestartMetadata, State
from .helpers import grouper

SUPPORTED_BLOCK_KINDS = ('temperature', 'saturation', 'pressure')
EXPECTED_BLOCK_KINDS = ('no fluxes',)


def read_restart(restart_file: Path) -> tuple[State, RestartMetadata]:
    """Loads restart files (.ini, .fin) into memory as a model State."""

    with open(restart_file) as f:
        runtime_header = next(f).strip()
        model_description = next(f).strip()
        simulation_time_days = Decimal(next(f).strip())
        n_nodes, dual_porosity_permeability_keyword = _parse_nodes_header(next(f))

        values_by_block = {}
        unsupported_blocks = False
        for line in f:
            block_name = line.strip()
            if block_name in SUPPORTED_BLOCK_KINDS:
                values_by_block[block_name] = _parse_scalar_block(f, n_nodes)
            elif block_name not in EXPECTED_BLOCK_KINDS:
                unsupported_blocks = True

    try:
        state = State(
            temperature=values_by_block['temperature'],
            saturation=values_by_block['saturation'],
            pressure=values_by_block['pressure'],
        )
    except KeyError:
        raise KeyError(f'Required block "{block_name}" not found in restart file {restart_file}.')

    metadata = RestartMetadata(
        runtime_header=runtime_header,
        model_description=model_description,
        simulation_time_days=simulation_time_days,
        n_nodes=n_nodes,
        dual_porosity_permeability_keyword=dual_porosity_permeability_keyword,
        unsupported_blocks=unsupported_blocks,
    )
    return state, metadata


def _parse_nodes_header(nodes_header: str) -> int:
    header_items = nodes_header.strip().split()
    keyword = header_items[1] if len(header_items) > 1 else ''
    return int(header_items[0]), keyword


def _parse_scalar_block(open_file: TextIO, n_nodes: int) -> list[Decimal]:
    scalar_values = []
    while len(scalar_values) < n_nodes:
        line = next(open_file)
        for value in line.strip().split():
            scalar_values.append(Decimal(value))
    return scalar_values


def write_restart(state: State, metadata: RestartMetadata, output_file: Path, fmt: str = 'legacy'):
    state.validate()
    if metadata.unsupported_blocks:
        raise NotImplementedError('Some blocks in restart not supported, cannot guarantee accurate write.')

    with open(output_file, 'w') as f:

        if fmt == 'fehm':
            _write_headers_fehm_format(f, metadata)
            for block_name in SUPPORTED_BLOCK_KINDS:
                block_data = _get_data_for_block(block_name, state)
                _write_block_fehm_format(f, block_name, block_data)
        elif fmt == 'legacy':
            _write_headers_legacy_format(f, metadata)
            for block_name in SUPPORTED_BLOCK_KINDS:
                block_data = _get_data_for_block(block_name, state)
                _write_block_legacy_format(f, block_name, block_data)
        else:
            raise NotImplementedError(f'Invalid format for restart writer ({fmt})')

        f.write('no fluxes')


def _write_headers_fehm_format(open_file: TextIO, metadata: RestartMetadata):
    open_file.write(f'{metadata.runtime_header}\n')
    open_file.write(f'{metadata.model_description:80}\n')
    open_file.write(f'   {metadata.simulation_time_days or "0.0000000000000000"}     \n')

    if metadata.dual_porosity_permeability_keyword:
        open_file.write(f'{metadata.n_nodes:9d} {metadata.dual_porosity_permeability_keyword}\n')
    else:
        open_file.write(f'{metadata.n_nodes:9d}\n')


def _write_headers_legacy_format(open_file: TextIO, metadata: RestartMetadata):
    open_file.write(f'{metadata.runtime_header}\n')
    open_file.write(f'{metadata.model_description:80}\n')
    open_file.write(f'   {metadata.simulation_time_days or "0000000000.000000"}\n')

    if metadata.dual_porosity_permeability_keyword:
        open_file.write(f'{metadata.n_nodes:9d} {metadata.dual_porosity_permeability_keyword}\n')
    else:
        open_file.write(f'{metadata.n_nodes:9d}\n')


def _write_block_fehm_format(open_file: TextIO, block_name: str, block_data: Sequence):
    open_file.write(f'{block_name:11}\n')
    for chunk in grouper(block_data, chunksize=4):
        open_file.write(''.join(f'    {v:17}    ' for v in chunk) + '\n')


def _write_block_legacy_format(open_file: TextIO, block_name: str, block_data: Sequence):
    open_file.write(f'{block_name}\n')
    for chunk in grouper(block_data, chunksize=4):
        open_file.write('    '.join(f'{float(v):21.10f}' for v in chunk) + '\n')


def _get_data_for_block(block_name: str, state: State) -> Sequence:
    if block_name == 'temperature':
        return state.temperature
    elif block_name == 'pressure':
        return state.pressure
    elif block_name == 'saturation':
        return state.saturation
    else:
        raise NotImplementedError(f'Block kind "{block_name}" not supported.')
