from collections import defaultdict
from decimal import Decimal
from itertools import groupby
from pathlib import Path
from typing import Iterable, Union

from ..fehm_objects import Vector


def read_compact_node_data(compact_node_data_file: Path) -> dict[int, Decimal]:
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


def _parse_compact_node_data_line(line: str) -> dict[int, Decimal]:
    r""" Parse compact node data string into a lookup of values by node.
    >>> _parse_compact_node_data_line('80   81  1   -3.92330E-04    0.')
    {80: Decimal('-0.000392330'), 81: Decimal('-0.000392330')}
    >>> _parse_compact_node_data_line('1\t3\t2\t10.\t0.')
    {1: Decimal('10'), 3: Decimal('10')}
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
        data_by_node[node_number] = Decimal(value)

    return data_by_node


def write_compact_node_data(
    value_by_node: dict[int, Union[float, Decimal, Vector, tuple[Decimal]]],
    output_file: Path,
    header: str = None,
    footer: str = None,
):
    nodes_by_value = _group_nodes_by_formatted_output(value_by_node)
    ordered_entries = _get_grouped_entries(nodes_by_value)
    _write_compact_node_file(ordered_entries, output_file, header=header, footer=footer)


def _write_compact_node_file(
    entries: tuple[int, int, str],
    output_file: Path,
    header: str = None,
    footer: str = None,
):
    with open(output_file, 'w') as f:
        if header:
            f.write(header)
        for min_node, max_node, value in entries:
            f.write(_format_compact_entry(min_node, max_node, value))
        if footer:
            f.write(footer)


def _group_nodes_by_formatted_output(
    value_by_node: dict[int, Union[float, Decimal, Vector, tuple[Decimal]]],
) -> dict[str, list[int]]:
    nodes_by_formatted_value = defaultdict(list)
    for node, value in value_by_node.items():
        formatted_value = _format_for_output(value)
        nodes_by_formatted_value[formatted_value].append(node)
    return nodes_by_formatted_value


def _get_grouped_entries(nodes_by_value: dict[str, list[int]]) -> list[tuple[int, int, str]]:
    entries = []
    for value, nodes in nodes_by_value.items():
        for min_node, max_node in _consecutive_groups(sorted(nodes)):
            entries.append((min_node, max_node, value))
    return sorted(entries, key=lambda entry: entry[0])  # sort by min_node


def _format_compact_entry(min_node: int, max_node: int, value: str) -> str:
    r""" Format compact node data entry as a string.
    >>> _format_compact_entry(1, 10, '2.00000E02 0.')
    '      1      10 1 2.00000E02 0.\n'
    >>> _format_compact_entry(4, 5, '-3.56738E-04 0.')
    '      4       5 1 -3.56738E-04 0.\n'
    >>> _format_compact_entry(1, 10, '2.00000E02')
    '      1      10 1 2.00000E02\n'
    >>> _format_compact_entry(4, 5, '-3.56738E-04')
    '      4       5 1 -3.56738E-04\n'
    """
    return f'{min_node:7d} {max_node:7d} 1 {value}\n'


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


def _format_for_output(value: Union[float, Decimal, Vector, Iterable]) -> str:
    """ Format values for compact node data output.
    >>> _format_for_output('hello')
    'hello'
    >>> _format_for_output(15)
    '            15'
    >>> _format_for_output(Vector(10, 20, 5))
    '            10             20              5'
    >>> _format_for_output([Vector(10, 20, 5), '0.'])
    '            10             20              5 0.'
    >>> _format_for_output([(10, [20, 5]), '0.'])
    '            10             20              5 0.'
    """

    if isinstance(value, str):
        return value

    try:
        return f'{value:14.6G}'
    except TypeError:
        return ' '.join([_format_for_output(i) for i in value])
