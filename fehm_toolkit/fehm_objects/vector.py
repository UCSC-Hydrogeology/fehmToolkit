from dataclasses import dataclass


@dataclass
class Vector:
    """Class for tracking vector values (e.g. vornoi areas)."""
    x: float
    y: float
    z: float

    @property
    def value(self) -> tuple[float]:
        return (self.x, self.y, self.z)

    def __format__(self, fmt) -> str:
        return f'{self.x:{fmt}}\t{self.y:{fmt}}\t{self.z:{fmt}}'
