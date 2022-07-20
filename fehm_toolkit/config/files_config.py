from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class FilesConfig:
    """Files configuration defining paths for model run."""
    run_root: Path
    material_zone: Path
    outside_zone: Path
    area: Path
    rock_properties: Path
    conductivity: Path
    pore_pressure: Path
    permeability: Path
    files: Path
    grid: Path
    input: Path
    output: Path
    store: Path
    history: Path
    water_properties: Path
    check: Path
    error: Path
    final_conditions: Path
    flow: Optional[Path] = None
    heat_flux: Optional[Path] = None
    initial_conditions: Optional[Path] = None

    @classmethod
    def from_dict(cls, dct):
        return cls(**{
            k: Path(v) if k != 'run_root' and v is not None else v
            for k, v in dct.items()
        })
