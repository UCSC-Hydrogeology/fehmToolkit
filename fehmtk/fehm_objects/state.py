from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Sequence


@dataclass
class State:
    """Class representing a snapshotted model state."""
    temperature: Sequence[Decimal]
    pressure: Sequence[Decimal]
    saturation: Optional[Sequence[Decimal]] = None
    source: Optional[Sequence[Decimal]] = None
    mass_flux: Optional[Sequence[Decimal]] = None

    def __post_init__(self):
        self.validate()

    def validate(self):
        n_temps = len(self.temperature)
        for field, data in self.__dict__.items():
            if data is not None and len(data) != n_temps:
                raise ValueError(
                    f'Number of {field} ({len(data)}) does not match the number of temperatures ({n_temps})'
                )


@dataclass
class RestartMetadata:
    """Class for holding structured metadata from the header in restart (.ini, .fin) files."""
    simulation_time_days: Decimal
    n_nodes: int
    runtime_header: str
    model_description: str
    dual_porosity_permeability_keyword: str
    unsupported_blocks: bool = False
