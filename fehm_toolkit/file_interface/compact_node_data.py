from collections import defaultdict
from itertools import groupby
from pathlib import Path
from typing import Iterable, Union

from fehm_toolkit.fehm_objects import Vector


def read_compact_node_data(compact_node_data_file: Path) -> dict[int, float]:
    data_by_node = {}
    with open(compact_node_data_file) as f:
        file_header = next(f).strip().split()
        if len(file_header) > 1:
            raise ValueError(f'Unrecognised file header {file_header}')

        for line in f:
            data_for_line = _parse_compact_node_data_line(line)
            if not data_for_line:
                break

            data_by_node.update(data_for_line)

    return data_by_node


def _parse_compact_node_data_line(line: str) -> dict[int, float]:
    r""" Parse compact node data string into a lookup of values by node.
    >>> _parse_compact_node_data_line('80   81  1   -3.92330E-04    0.')
    {80: -0.00039233, 81: -0.00039233}
    >>> _parse_compact_node_data_line('1\t3\t2\t10.\t0.')
    {1: 10.0, 3: 10.0}
    >>> _parse_compact_node_data_line('0')
    >>> _parse_compact_node_data_line('\n')
    """

    line = line.strip()
    if not line or line == '0':
        return

    data_by_node = {}
    try:
        [min_node, max_node, spacing, value, zero] = line.split()
    except ValueError:
        raise ValueError(f'Could not parse compact node data line: {line}')

    for node_number in range(int(min_node), int(max_node) + 1, int(spacing)):
        data_by_node[node_number] = float(value)

    return data_by_node


def write_compact_node_data(
    value_by_node: dict[int, Union[float, Vector, tuple[float]]],
    output_file: Path,
    header: str = None,
    footer: str = None,
    style: str = 'rock_properties',
):
    nodes_by_value = _group_nodes_by_formatted_output(value_by_node, style)
    ordered_entries = _get_grouped_entries(nodes_by_value)
    _write_compact_node_file(ordered_entries, output_file, style, header=header, footer=footer)


def _write_compact_node_file(
    entries: tuple[int, int, str],
    output_file: Path,
    style: str,
    header: str = None,
    footer: str = None,
):
    with open(output_file, 'w') as f:
        if header:
            f.write(header)
        for min_node, max_node, value in entries:
            f.write(_format_compact_entry(min_node, max_node, value, style))
        if footer:
            f.write(footer)


def _group_nodes_by_formatted_output(
    value_by_node: dict[int, Union[float, Vector, tuple[float]]],
    style: str,
) -> dict[str, list[int]]:
    nodes_by_formatted_value = defaultdict(list)
    for node, value in value_by_node.items():
        formatted_value = _format_for_output(value, style)
        nodes_by_formatted_value[formatted_value].append(node)
    return nodes_by_formatted_value


def _get_grouped_entries(nodes_by_value: dict[str, list[int]]) -> list[tuple[int, int, str]]:
    entries = []
    for value, nodes in nodes_by_value.items():
        for min_node, max_node in _consecutive_groups(sorted(nodes)):
            entries.append((min_node, max_node, value))
    return sorted(entries, key=lambda entry: entry[0])  # sort by min_node


def _format_compact_entry(min_node: int, max_node: int, value: str, style: str) -> str:
    r""" Format compact node data entry as a string.
    >>> _format_compact_entry(1, 10, '2.00000E02', 'heatflux')
    '1\t10\t1\t2.00000E02\t0.\n'
    >>> _format_compact_entry(4, 5, '-3.56738E-04', 'heatflux')
    '4\t5\t1\t-3.56738E-04\t0.\n'
    >>> _format_compact_entry(1, 10, '2.00000E02', 'rock_properties')
    '      1      10 1\t2.00000E02\n'
    >>> _format_compact_entry(4, 5, '-3.56738E-04', 'rock_properties')
    '      4       5 1\t-3.56738E-04\n'
    """
    if style == 'heatflux':
        return f'{min_node}\t{max_node}\t1\t{value}\t0.\n'

    return f'{min_node:7d}{max_node:8d} 1\t{value}\n'


def _consecutive_groups(x: list[int]) -> list[tuple[int]]:
    """ Iterate over consecutive groups found in list of integers.
    >>> list(_consecutive_groups([1, 2, 4]))
    [(1, 2), (4, 4)]
    >>> list(_consecutive_groups([4, 5, 6, 9, 10, 15, 16]))
    [(4, 6), (9, 10), (15, 16)]
    """
    def _value_minus_index(enum: tuple[int, int]) -> int:
        index = enum[0]
        value = enum[1]
        return index - value

    for k, g in groupby(enumerate(x), key=_value_minus_index):
        g = list(g)
        group_start = g[0][1]
        group_end = g[-1][1]
        yield group_start, group_end


def _format_for_output(value: Union[float, Vector, tuple[float]], style: str) -> str:
    try:
        return _format_numeric_for_output(value, style)
    except TypeError:
        return _format_iterable_triple_for_output(value, style)


def _format_iterable_triple_for_output(values: Iterable, style: str) -> str:
    r""" Format iterable values with three items for output to compact node output file.
    >>> _format_iterable_triple_for_output((1, 2.5, 3), 'rock_properties')
    '  1.00000E+00\t  2.50000E+00\t  3.00000E+00'
    >>> _format_iterable_triple_for_output([100, 0.2, 3], 'rock_properties')
    '  1.00000E+02\t  2.00000E-01\t  3.00000E+00'
    """
    try:
        x, y, z = values
        return '\t'.join([_format_numeric_for_output(i, style) for i in (x, y, z)])
    except ValueError:
        raise ValueError(f'Cannot format value for compact node output: {values}')


def _format_numeric_for_output(value: float, style: str) -> str:
    """ Format float value for output to compact node output file.
    >>> _format_for_output(-0.0397631, 'heatflux')
    '-3.97631E-02'
    >>> _format_for_output(200, 'heatflux')
    '2.00000E+02'
    >>> _format_for_output(-0.0397631, 'rock_properties')
    ' -3.97631E-02'
    >>> _format_for_output(200, 'rock_properties')
    '  2.00000E+02'
    """
    if style == 'heatflux':
        return f'{value:.5E}'

    return f'{value:13.5E}'
