from collections import defaultdict
from decimal import Decimal
from pathlib import Path

from fehmtk.fehm_objects import State

SUPPORTED_FIELDS = {
    'Liquid Pressure (MPa), (MPa)': 'pressure',
    'Temperature (deg C), (deg C)': 'temperature',
    'Source (kg/s), (kg/s)': 'source',
    'Liquid Flux (kg/s), (kg/s)': 'mass_flux',
}


def read_avs(avs_file: Path) -> State:
    """Loads AVS contour files (.avs) into memory as a model State."""

    with open(avs_file) as f:
        metadata = [int(value) for value in next(f).strip().split()]
        n_columns, column_dimensions = metadata[0], metadata[1:]
        if any(dim > 1 for dim in column_dimensions):
            raise NotImplementedError('Vector AVS data not supported.')

        avs_data = defaultdict(list)
        field_names = ['node_number'] + [next(f).strip() for _ in range(n_columns)]
        fields_to_save = [field for field in field_names if field in SUPPORTED_FIELDS]

        for line in f:
            row = {
                field_name: round(Decimal(value), 10)
                for field_name, value in zip(field_names, line.strip().split())
            }
            for field_name in fields_to_save:
                avs_data[field_name].append(row[field_name])

    return State(**{state_name: avs_data[field_name] for field_name, state_name in SUPPORTED_FIELDS.items()})
