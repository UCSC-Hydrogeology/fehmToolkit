from pathlib import Path
from typing import TextIO

from fehm_toolkit.fehm_objects import State


def read_restart(restart_file: Path) -> tuple[State, dict]:
    """Loads restart files (.ini, .fin) into memory as a model State."""

    with open(restart_file) as f:
        runtime_header = next(f).strip()
        model_description = next(f).strip()
        simulation_time_days = float(next(f).strip())
        n_nodes = _parse_nodes_header(next(f))

        values_by_block = {}
        for line in f:
            block_name = line.strip()
            if block_name in ('temperature', 'saturation', 'pressure'):
                values_by_block[block_name] = _parse_scalar_block(f, n_nodes)

    try:
        state = State(
            temperatures=values_by_block['temperature'],
            saturations=values_by_block['saturation'],
            pressures=values_by_block['pressure'],
        )
    except KeyError:
        raise KeyError(f'Required block "{block_name}" not found in restart file {restart_file}.')

    metadata = {
        'runtime_header': runtime_header,
        'model_description': model_description,
        'simulation_time_days': simulation_time_days,
        'n_nodes': n_nodes,
    }
    return state, metadata


def _parse_nodes_header(nodes_header: str) -> int:
    header_items = nodes_header.strip().split()
    return int(header_items[0])


def _parse_scalar_block(open_file: TextIO, n_nodes: int) -> tuple[float]:
    scalar_values = []
    while len(scalar_values) < n_nodes:
        line = next(open_file)
        for value in line.strip().split():
            scalar_values.append(float(value))
    return scalar_values
