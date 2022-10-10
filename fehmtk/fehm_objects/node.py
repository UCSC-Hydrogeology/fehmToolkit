from dataclasses import dataclass
from decimal import Decimal

from .vector import Vector


@dataclass(frozen=True)
class Node():
    """Class for tracking individual node properties."""
    number: int
    coordinates: Vector
    outside_area: Vector = None
    depth: Decimal = None
    volume: Decimal = None

    @property
    def x(self) -> Decimal:
        return self.coordinates.x

    @property
    def y(self) -> Decimal:
        return self.coordinates.y

    @property
    def z(self) -> Decimal:
        return self.coordinates.z
