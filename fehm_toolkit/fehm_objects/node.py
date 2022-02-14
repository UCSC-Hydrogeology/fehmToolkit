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

    @classmethod
    def from_fehm_line(cls, raw_line: str) -> 'Node':
        n, x, y, z = raw_line.strip().split()
        return cls(number=int(n), x=float(x), y=float(y), z=float(z))
