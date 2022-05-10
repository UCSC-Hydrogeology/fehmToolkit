from dataclasses import dataclass
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
