from pathlib import Path
from typing import Optional, TextIO

from fehm_toolkit.fehm_objects import Vector


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
    [Vector(x=1.0, y=2.0, z=3.0), Vector(x=4.0, y=5.0, z=6.0)]
    >>> _parse_zone_values_line(['1', '2', '3', '4', '5', '6', '7'], True)
    [Vector(x=1.0, y=2.0, z=3.0), Vector(x=4.0, y=5.0, z=6.0)]
    >>> _parse_zone_values_line(['1.0', '1.0', '4.5'], True)
    [Vector(x=1.0, y=1.0, z=4.5)]
    """
    if is_vector_format:
        first = Vector(*(float(v) for v in raw_line_values[:3]))
        second = Vector(*(float(v) for v in raw_line_values[3:6])) if raw_line_values[3:6] else None
        if not second:
            return [first]
        return [first, second]

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
