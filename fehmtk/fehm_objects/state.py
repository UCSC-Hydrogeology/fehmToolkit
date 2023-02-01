from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Sequence


@dataclass(frozen=True)
class State:
    """Class representing a snapshotted model state."""
    temperature: Sequence[Decimal]
    pressure: Sequence[Decimal]
    saturation: Optional[Sequence[Decimal]] = None
    porosity: Optional[Sequence[Decimal]] = None
    source: Optional[Sequence[Decimal]] = None
    mass_flux: Optional[Sequence[Decimal]] = None

    def __post_init__(self):
        self.validate()

    def __sub__(self, other):
        return State(
            pressure=_subtract_items(self.pressure, other.pressure),
            temperature=_subtract_items(self.temperature, other.temperature),
            saturation=_subtract_items(self.saturation, other.saturation),
            porosity=_subtract_items(self.porosity, other.porosity),
            mass_flux=_subtract_items(self.mass_flux, other.mass_flux),
            source=_subtract_items(self.source, other.source),
        )

    def validate(self):
        n_temps = len(self.temperature)
        for field, data in self.__dict__.items():
            if data is not None and len(data) != n_temps:
                raise ValueError(
                    f'Number of {field} ({len(data)}) does not match the number of temperatures ({n_temps})'
                )


@dataclass(frozen=True)
class RestartMetadata:
    """Class for holding structured metadata from the header in restart (.ini, .fin) files."""
    simulation_time_days: Decimal
    n_nodes: int
    runtime_header: str
    model_description: str
    dual_porosity_permeability_keyword: str
    unsupported_blocks: bool = False


def _subtract_items(seq, other):
    if seq is None or other is None:
        return None

    if len(seq) != len(other):
        raise ValueError(f'Incompatible states, number of nodes not equal ({len(seq)} != {len(other)})')

    return tuple(a - b for a, b, in zip(seq, other))
