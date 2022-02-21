from pathlib import Path
from typing import Optional, TextIO

from .element import Element
from .node import Node, Vector


class Grid:
    """Class representing a mesh or grid object."""

    def __init__(
        self,
        nodes_by_number: dict[int, Node],
        elements_by_number: dict[int, Element],
    ):
        self._nodes_by_number = nodes_by_number
        self._elements_by_number = elements_by_number

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
    return {number: Node(number, coordinates) for number, coordinates in coordinates_by_number.items()}


def read_fehm(fehm_file: Path) -> tuple[dict, dict]:
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
                elements_by_number = _read_elem(f)
            elif block_name == 'stop':
                break
            else:
                raise NotImplementedError(f'No parser for block type "{block_name}"')
            next(f)  # throw away extra line after block

    if not coordinates_by_number:
        raise ValueError(f'Invalid fehm_file ({fehm_file}), no coordinate data found')
    if not elements_by_number:
        raise ValueError(f'Invalid fehm_file ({fehm_file}), no element data found')

    return coordinates_by_number, elements_by_number


def _read_coor(open_file: TextIO) -> dict[int, Vector]:
    n_nodes = int(next(open_file))

    coordinates_by_number = {}
    for i in range(n_nodes):
        number, x, y, z = next(open_file).strip().split()
        coordinates_by_number[int(number)] = Vector(float(x), float(y), float(z))

    return coordinates_by_number


def _read_elem(open_file: TextIO) -> dict[int, Node]:
    n_elements = int(next(open_file).strip().split()[1])

    elements_by_number = {}
    for i in range(n_elements):
        element = Element.from_fehm_line(next(open_file))
        elements_by_number[element.number] = element
    return elements_by_number


def read_zones(zone_file: Path) -> tuple[dict, dict]:
    """Read zone-formatted files (_outside.zone, _material.zone, .area)

    Read zone-based values (node numbers, areas), and return these as a dictionary keyed by zone number. Also construct
    a mapping dictionary between the zone name and zone number.
    """

    zone_number_by_name = {}
    node_values_by_zone_number = {}

    with open(zone_file) as f:
        file_header = next(f).strip()
        if file_header != 'zone':
            raise ValueError('Invalid zone file, must start with "zone" header')

        while True:
            zone_header = next(f).strip()
            if _is_end_of_zone_file(zone_header, f):
                break

            zone_number, zone_name = _parse_zone_header(zone_header)
            node_values = _read_zone(f)

            node_values_by_zone_number[zone_number] = node_values
            if zone_name:
                zone_number_by_name[zone_name] = zone_number

    return node_values_by_zone_number, zone_number_by_name


def _read_zone(open_file: TextIO) -> tuple[int]:
    nnum_header = next(open_file).strip()
    if nnum_header != 'nnum':
        raise ValueError(f'Invalid zone file, expected "nnum" instead of "{nnum_header}"')

    n_nodes = int(next(open_file).strip())
    node_values = []
    while len(node_values) < n_nodes:
        raw_values_for_line = next(open_file).strip().split()
        if not node_values:
            is_vector_format = _is_vector_formatted(raw_values_for_line, n_nodes)

        values_for_line = _parse_zone_values_line(raw_values_for_line, is_vector_format=is_vector_format)
        node_values.extend(values_for_line)

    return tuple(node_values)


def _parse_zone_header(header: str) -> tuple[int, Optional[str]]:
    """ Split up a zone header string into the number and name (if present)
    >>> _parse_zone_header('00001 top')
    (1, 'top')
    >>> _parse_zone_header('00003')
    (3, None)
    >>> _parse_zone_header('4 front_s')
    (4, 'front_s')
    """
    parsed = header.strip().split()
    if len(parsed) == 1:
        return int(parsed[0]), None

    return int(parsed[0]), parsed[1]


def _is_end_of_zone_file(header: str, open_file: TextIO) -> bool:
    if not header:
        if next(open_file).strip() != 'stop':
            raise ValueError('Invalid zone file, unexpected blank line encountered')
        return True
    return False


def _parse_zone_values_line(raw_line_values: list[str], is_vector_format: bool) -> list:
    """ Convert zone values into a list of scalar or vector values
    >>> _parse_zone_values_line(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'], False)
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    >>> _parse_zone_values_line(['1', '2', '3', '4', '5', '6'], False)
    [1, 2, 3, 4, 5, 6]
    >>> _parse_zone_values_line(['1', '2', '3', '4', '5', '6'], True)
    [(1.0, 2.0, 3.0), (4.0, 5.0, 6.0)]
    >>> _parse_zone_values_line(['1', '2', '3', '4', '5', '6', '7'], True)
    [(1.0, 2.0, 3.0), (4.0, 5.0, 6.0)]
    >>> _parse_zone_values_line(['1.0', '1.0', '4.5'], True)
    [(1.0, 1.0, 4.5)]
    """
    if is_vector_format:
        first_vector = tuple(float(v) for v in raw_line_values[:3])
        second_vector = tuple(float(v) for v in raw_line_values[3:6])
        if not second_vector:
            return [first_vector]
        return [first_vector, second_vector]

    return [int(v) for v in raw_line_values]


def _is_vector_formatted(zone_line_values: list[str], n_nodes: int) -> bool:
    """ Check if line is vector formatted (contains 6 values)
    >>> _is_vector_formatted(['10.0', '10.0', '0.0', '0.0', '20.0', '20.0'], 10)
    True
    >>> _is_vector_formatted([1, 2, 3], 1)
    True
    >>> _is_vector_formatted(['1.0', '2.0', '3.0'], 2)
    False
    >>> _is_vector_formatted([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 10)
    False
    """
    if n_nodes == 1:
        return len(zone_line_values) == 3
    return len(zone_line_values) == 6  # Lagrit writes two 3-vectors per line instead of the usual 10 scalars
