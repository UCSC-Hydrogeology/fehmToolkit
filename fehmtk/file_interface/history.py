from decimal import Decimal, InvalidOperation
from pathlib import Path
import math
from typing import Optional, Sequence, TextIO

import pandas as pd


TIME_HEADING = 'time_days'


def read_history(
    history_file: Path,
    last_fraction: float = None,
    read_nodes: Optional[Sequence[int]] = None,
    read_fields: Optional[Sequence[str]] = None,
) -> pd.DataFrame:
    times = None
    if last_fraction is None or last_fraction == 1:
        skip_times = 0
    else:
        times = read_history_times(history_file)
        skip_times = math.floor((1 - last_fraction) * len(times))

    with open(history_file) as f:
        _skip_lines(f, 5)  # throw away headers
        n_nodes = int(next(f).strip())
        nodes = _read_node_numbers(f, n_nodes=n_nodes)
        node_read_pattern = [n in read_nodes for n in nodes] if read_nodes else n_nodes * [True]

        headings, first_time = _read_headings_and_first_time(f, read_fields)
        field_read_pattern = [h in ['node'] + read_fields for h in headings] if read_fields else len(headings) * [True]
        headings = [h for h, read_field in zip(headings, field_read_pattern) if read_field]

        if skip_times:
            data = []
            _skip_lines(f, n_nodes)
        else:
            data = _read_node_data(f, time=first_time, node_pattern=node_read_pattern, field_pattern=field_read_pattern)

        _skip_lines(f, (skip_times - 1) * (n_nodes + 1))  # first already handled

        for line in f:
            time = Decimal(line.strip())
            if time < 0:  # FEHM writes the final time twice, once negative to signal end of run
                break
            data.extend(_read_node_data(f, time=time, node_pattern=node_read_pattern, field_pattern=field_read_pattern))

    if not data:
        times = times or read_history_times(history_file)
        return pd.DataFrame({TIME_HEADING: times})

    return pd.DataFrame.from_records(data, columns=[TIME_HEADING] + headings)


def read_history_times(history_file) -> tuple[Decimal]:
    with open(history_file) as f:
        _skip_lines(f, 5)  # throw away headers
        n_nodes = int(next(f).strip())
        _skip_lines(f, n_nodes + 2)  # +2 skips "headings" and first headings row

        for line in f:  # skip headings lines until you find a timestamp
            try:
                times = [Decimal(line.strip())]
                _skip_lines(f, n_nodes)
                break
            except InvalidOperation:
                pass

        for line in f:
            time = Decimal(line.strip())
            if time < 0:  # FEHM writes the final time twice, once negative to signal end of run
                return tuple(times)
            times.append(time)
            _skip_lines(f, n_nodes)

        return tuple(times)


def _skip_lines(open_file: TextIO, lines: int):
    for i in range(lines):
        next(open_file)


def _read_node_numbers(open_file: TextIO, n_nodes: int) -> list[bool]:
    nodes = []
    for i in range(n_nodes):
        line = next(open_file)
        nodes.append(int(line.strip().split()[0]))
    return nodes


def _read_headings_and_first_time(open_file: TextIO, read_fields: list[bool]) -> tuple[list[str], Decimal]:
    next(open_file)  # "headings"
    heading_lines = [next(open_file)]
    for line in open_file:
        try:
            time = Decimal(line.strip())
        except InvalidOperation:
            heading_lines.append(line)
            continue

        headings = _parse_heading_lines(heading_lines)
        missing_fields = set(read_fields or []) - set(headings)
        if missing_fields:
            raise ValueError(f'Specified field names {missing_fields} not found in history file: {headings}')
        return headings, time


def _parse_heading_lines(lines: Sequence[str]) -> list[str]:
    r"""Get headings from raw lines
    >>> _parse_heading_lines(['node flow enthalpy(Mj/kg) flow(kg/s) temperature(deg C) total pressure(Mpa)'])
    ['node', 'flow enthalpy(Mj/kg)', 'flow(kg/s)', 'temperature(deg C)', 'total pressure(Mpa)']
    >>> _parse_heading_lines(['node flow enthalpy(Mj/kg) flow(kg/s)\n', 'temperature(deg C) total pressure(Mpa)'])
    ['node', 'flow enthalpy(Mj/kg)', 'flow(kg/s)', 'temperature(deg C)', 'total pressure(Mpa)']
    >>> _parse_heading_lines(['flow(kg/s) temperature(deg C) total pressure(Mpa)'])
    ['flow(kg/s)', 'temperature(deg C)', 'total pressure(Mpa)']
    """
    raw_headings = ' '.join([line.strip() for line in lines])

    headings = []
    if raw_headings[:5] == 'node ':
        headings.append('node')
        raw_headings = raw_headings[5:]

    parsed = [_amend_heading(heading) for heading in raw_headings.split(') ')]
    headings.extend(parsed)
    return headings


def _amend_heading(heading: str) -> str:
    if heading.endswith(')'):
        return heading
    return f'{heading})'


def _read_node_data(
    open_file: TextIO,
    time: Decimal,
    node_pattern: list[bool],
    field_pattern: list[bool],
) -> list[list[Decimal]]:
    data = []
    for read_node in node_pattern:
        line = next(open_file)
        if read_node:
            node_data = [Decimal(item) for item, read_field in zip(line.strip().split(), field_pattern) if read_field]
            data.append([time] + node_data)
    return data
