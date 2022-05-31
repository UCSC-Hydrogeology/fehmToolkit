from pathlib import Path


def read_legacy_ipi_config(ipi_file: Path) -> dict:
    with open(ipi_file) as f:
        next(f)
        header = next(f).strip()
        if header != 'lagrit':
            raise ValueError(f'Unexpected header in {ipi_file}: "{header}"')
        z_interval = float(next(f).strip())
        reference_z, reference_pressure, reference_temperature = [float(v) for v in next(f).strip().split(',')]
    return {
        'hydrostatic_pressure': {
            'model_kind': 'depth',
            'model_params': {
                'z_interval_m': z_interval,
                'reference_z': reference_z,
                'reference_pressure_MPa': reference_pressure,
                'reference_temperature_degC': reference_temperature,
            }
        }
    }
