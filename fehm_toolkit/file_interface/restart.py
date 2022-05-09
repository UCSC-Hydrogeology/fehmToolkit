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
            temperatures=values_by_block['temperature'],
            saturations=values_by_block['saturation'],
            pressures=values_by_block['pressure'],
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


def _parse_scalar_block(open_file: TextIO, n_nodes: int) -> tuple[float]:
    scalar_values = []
    while len(scalar_values) < n_nodes:
        line = next(open_file)
        for value in line.strip().split():
            scalar_values.append(Decimal(value))
    return scalar_values
