from decimal import Decimal
from pathlib import Path

from fehmtk.config import ModelConfig, HydrostatConfig


def read_legacy_ipi_config(ipi_file: Path) -> HydrostatConfig:
    with open(ipi_file) as f:
        next(f)
        header = next(f).strip()
        if header != 'lagrit':
            raise ValueError(f'Unexpected header in {ipi_file}: "{header}"')
        z_interval = Decimal(next(f).strip())
        reference_z, reference_pressure, reference_temperature = [Decimal(v) for v in next(f).strip().split(',')]
    return HydrostatConfig(
        pressure_model=ModelConfig(
            kind='depth',
            params={
                'z_interval_m': z_interval,
                'reference_z': reference_z,
                'reference_pressure_MPa': reference_pressure,
                'reference_temperature_degC': reference_temperature,
            },
        ),
    )
