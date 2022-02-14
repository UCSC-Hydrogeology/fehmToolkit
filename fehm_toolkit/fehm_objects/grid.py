from pathlib import Path
from typing import Optional, TextIO

from .element import Element
from .node import Node


class Grid:
    """Class representing a mesh or grid object."""

    def __init__(self, nodes_by_number: dict, elements_by_number: dict):
        self._nodes_by_number = nodes_by_number or {}
        self._elements_by_number = elements_by_number or {}

    def node(self, number: int) -> Node:
        try:
            return self._nodes_by_number[number]
        except KeyError:
            raise KeyError(f'Node ({number}) not found in grid.')

    def element(self, number: int) -> Element:
        try:
            return self._elements_by_number[number]
        except KeyError:
            raise KeyError(f'Element ({number}) not found in grid.')

    @property
    def n_nodes(self) -> int:
        return len(self._nodes_by_number)

    @property
    def n_elements(self) -> int:
        return len(self._elements_by_number)

    @classmethod
    def from_files(
        cls,
        fehm_file: Path,
        *,
        material_zone_file: Optional[Path] = None,
        outside_zone_file: Optional[Path] = None,
        area_file: Optional[Path] = None,
    ) -> 'Grid':
        coordinates_by_number, elements_by_number = read_fehm(fehm_file)
        nodes_by_number = _construct_nodes_lookup(coordinates_by_number)

        return cls(nodes_by_number=nodes_by_number, elements_by_number=elements_by_number)


def _construct_nodes_lookup(
    coordinates_by_number,
) -> dict[int, Node]: 
    return {number: Node(number, x, y, z) for number, (x, y, z) in coordinates_by_number.items()}


def read_fehm(fehm_file: Path) -> tuple[dict, dict]:
    coordinates_by_number = None
    elements_by_number = None

    with open(fehm_file) as f:
        while True:
            block_name = next(f).strip()

            if block_name == 'coor':
                coordinates_by_number = _read_coor(f)
            elif block_name == 'elem':
                elements_by_number = _read_elem(f)
            elif block_name == 'stop':
                break
            else:
                raise NotImplementedError(f'No parser for block type "{block_name}"')
            next(f)  # throw away extra line after block

    if not coordinates_by_number:
        raise ValueError(f'Invalid fehm_file ({fehm_file}, no coordinate data found')
    if not elements_by_number:
        raise ValueError(f'Invalid fehm_file ({fehm_file}, no element data found')

    return coordinates_by_number, elements_by_number


def _read_coor(open_file: TextIO) -> dict[int, tuple[float]]:
    n_nodes = int(next(open_file))

    coordinates_by_number = {}
    for i in range(n_nodes):
        number, x, y, z = next(open_file).strip().split()
        coordinates_by_number[int(number)] = (float(x), float(y), float(z))

    return coordinates_by_number


def _read_elem(open_file: TextIO) -> dict[int, Node]:
    n_elements = int(next(open_file).strip().split()[1])

    elements_by_number = {}
    for i in range(n_elements):
        element = Element.from_fehm_line(next(open_file))
        elements_by_number[element.number] = element
    return elements_by_number
