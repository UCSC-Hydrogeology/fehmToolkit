from collections import defaultdict
from itertools import groupby
from pathlib import Path


def write_compact_node_data(
    value_by_node: dict[int, float],
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


def _group_nodes_by_formatted_output(value_by_node: dict[int, float]) -> dict[str, list[int]]:
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
    >>> _format_compact_entry(1, 10, '2.00000E02')
    '1\t10\t1\t2.00000E02\t0.\n'
    >>> _format_compact_entry(4, 5, '-3.56738E-04')
    '4\t5\t1\t-3.56738E-04\t0.\n'
    """
    return f'{min_node}\t{max_node}\t1\t{value}\t0.\n'


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


def _format_for_output(value: float) -> str:
    """ Format float value for output to boundary condition file.
    >>> _format_for_output(-0.0397631)
    '-3.97631E-02'
    >>> _format_for_output(200)
    '2.00000E+02'
    """
    return f"{value:.5E}"
