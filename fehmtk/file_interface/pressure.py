from decimal import Decimal
from pathlib import Path
from typing import Optional, TextIO

from .helpers import grouper


def read_pressure(pressure_file: Path) -> list[Decimal]:
    values = []
    with open(pressure_file) as f:
        for line in f:
            for value in line.strip().split():
                values.append(Decimal(value))

    if len(values) % 2:
        raise ValueError(f'Odd number of values in pressure file ({pressure_file}), should be even.')

    return values[int(len(values) / 2):]  # throw away first half (saturation values)


def write_pressure(
    pressure_by_node: dict[int, Decimal],
    output_file: Path,
    saturation_by_node: Optional[dict[int, Decimal]] = None,
):
    with open(output_file, 'w') as f:
        if saturation_by_node:
            _write_node_data(f, saturation_by_node)
        else:
            _write_default_saturation(f, n_nodes=len(pressure_by_node))

        _write_node_data(f, pressure_by_node, final_newline=False)


def _write_default_saturation(open_file: TextIO, n_nodes: int):
    for chunk in grouper(range(n_nodes), chunksize=4):
        saturations = len(chunk) * ['        1.0000000']
        open_file.write('    '.join(saturations) + '\n')


def _write_node_data(open_file: TextIO, values_by_node: dict[int, Decimal], final_newline=True):
    chunksize = 4
    sorted_values = [v for node, v in sorted(values_by_node.items())]
    for i, chunk in enumerate(grouper(sorted_values, chunksize=chunksize), start=1):
        open_file.write('    '.join([f'{v:17.7f}' for v in chunk]))

        # TODO(dustin): remove this when not trying to match legacy file formats
        if final_newline or i * chunksize < len(values_by_node):
            open_file.write('\n')
