from dataclasses import dataclass


@dataclass
class Node:
    """Class for tracking individual node properties."""
    number: int
    coordinates: 'Vector'
    outside_area: 'Vector' = None
    depth: float = None

    @property
    def x(self) -> float:
        return self.coordinates.x

    @property
    def y(self):
        return self.coordinates.y

    @property
    def z(self):
        return self.coordinates.z


@dataclass
class Vector:
    """Class for tracking vector values (e.g. vornoi areas)."""
    x: float
    y: float
    z: float

    @property
    def value(self) -> tuple[float]:
        return (self.x, self.y, self.z)
