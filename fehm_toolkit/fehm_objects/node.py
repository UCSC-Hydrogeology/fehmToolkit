from dataclasses import dataclass

from .vector import Vector


@dataclass
class Node:
    """Class for tracking individual node properties."""
    number: int
    coordinates: Vector
    outside_area: Vector = None
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
