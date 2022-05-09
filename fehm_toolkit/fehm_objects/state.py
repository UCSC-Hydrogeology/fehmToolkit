from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Sequence


@dataclass
class State:
    """Class representing a snapshotted model state."""
    temperatures: Sequence[float]
    pressures: Sequence[float]
    saturations: Optional[Sequence[float]] = None
    sources: Optional[Sequence[float]] = None
    mass_fluxes: Optional[Sequence[float]] = None

    def __post_init__(self):
        self.validate()

    def validate(self):
        n_temperatures = len(self.temperatures)
        for field, data in self.__dict__.items():
            if data is not None and len(data) != n_temperatures:
                raise ValueError(
                    f'Number of {field} ({len(data)}) does not match the number of temperatures ({n_temperatures})'
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
