from pathlib import Path
from typing import Optional, TextIO

from fehm_toolkit.fehm_objects import Element, Node, Vector


def read_fehm(fehm_file: Path, read_elements: Optional[bool] = True) -> tuple[dict, dict]:
    """Read FEHM-formatted files (.fehm)

    Read coordinates and elements and return as dictionaries keyed by number.
    """

    coordinates_by_number = None
    elements_by_number = None

    with open(fehm_file) as f:
        while True:
            block_name = next(f).strip()

            if block_name == 'coor':
                coordinates_by_number = _read_coor(f)
            elif block_name == 'elem':
                elements_by_number = _read_elem(f, should_read=read_elements)
            elif block_name == 'stop':
                break
            else:
                raise NotImplementedError(f'No parser for block type "{block_name}"')
            next(f)  # throw away extra line after block

    if not coordinates_by_number:
        raise ValueError(f'Invalid fehm_file ({fehm_file}), no coordinate data found')
    if read_elements and not elements_by_number:
        raise ValueError(f'Invalid fehm_file ({fehm_file}), no element data found')

    return coordinates_by_number, elements_by_number


def _read_coor(open_file: TextIO) -> dict[int, Vector]:
    n_nodes = int(next(open_file))

    coordinates_by_number = {}
    for i in range(n_nodes):
        number, x, y, z = next(open_file).strip().split()
        coordinates_by_number[int(number)] = Vector(float(x), float(y), float(z))

    return coordinates_by_number


def _read_elem(open_file: TextIO, should_read: Optional[bool] = True) -> dict[int, Node]:
    n_elements = int(next(open_file).strip().split()[1])

    elements_by_number = {}
    for i in range(n_elements):
        line = next(open_file)
        if not should_read:
            continue

        element = Element.from_fehm_line(line)
        elements_by_number[element.number] = element
    return elements_by_number
