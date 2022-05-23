from decimal import Decimal
from pathlib import Path


def read_pressure(pressure_file: Path) -> list[Decimal]:
    values = []
    with open(pressure_file) as f:
        for line in f:
            for value in line.strip().split():
                values.append(Decimal(value))

    if len(values) % 2:
        raise ValueError(f'Odd number of values in pressure file ({pressure_file}), should be even.')

    return values[int(len(values) / 2):]  # throw away first half (saturation values)
