from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Vector:
    """Class for tracking vector values (e.g. vornoi areas)."""
    x: Decimal
    y: Decimal
    z: Decimal

    @property
    def value(self) -> tuple[Decimal]:
        return (self.x, self.y, self.z)

    def __format__(self, fmt) -> str:
        return f'{self.x:{fmt}} {self.y:{fmt}} {self.z:{fmt}}'
