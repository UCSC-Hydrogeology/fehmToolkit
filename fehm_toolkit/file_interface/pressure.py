from decimal import Decimal
from pathlib import Path


def read_pressure(pressure_file: Path) -> tuple[Decimal]:
    values = []
    with open(pressure_file) as f:
        for line in f:
            for value in line.strip().split():
                values.append(Decimal(value))

    return tuple(values)
