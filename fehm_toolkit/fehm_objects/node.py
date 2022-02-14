from dataclasses import dataclass


@dataclass
class Node:
    """Class for tracking individual node properties."""
    number: int
    x: float
    y: float
    z: float

    @property
    def coordinates(self) -> tuple[float]:
        return (self.x, self.y, self.z)
