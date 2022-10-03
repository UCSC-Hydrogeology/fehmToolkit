from decimal import Decimal
from pathlib import Path


def read_volume_from_storage(storage_file: Path) -> tuple[Decimal]:
    """Read FEHM storage coefficient files (.stor), extracting node volume data"""

    volume = []
    with open(storage_file) as f:
        next(f)  # skip title header
        next(f)  # skip model header
        _, n_nodes, _, _, _ = [int(v) for v in next(f).strip().split()]

        while len(volume) < n_nodes:
            line_values = [Decimal(v) for v in next(f).strip().split()]
            volume.extend(line_values)

    if len(volume) != n_nodes:
        raise ValueError(f'Got more volumes ({len(volume)}) than n_nodes ({n_nodes})')

    return tuple(volume)
