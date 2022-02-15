from dataclasses import dataclass


@dataclass
class Element:
    """Class representing grid elements (connectivity)."""
    number: int
    connectivity: int
    nodes: tuple[int]

    @classmethod
    def from_fehm_line(cls, raw_line: str) -> 'Element':
        split_line = raw_line.strip().split()
        n, nodes = split_line[0], split_line[1:]
        return cls(number=int(n), connectivity=len(nodes), nodes=tuple(int(node) for node in nodes))
