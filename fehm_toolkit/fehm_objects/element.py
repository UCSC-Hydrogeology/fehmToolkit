from dataclasses import dataclass


@dataclass
class Element:
    """Class representing grid elements (connectivity)."""
    number: int
    connectivity: int
    nodes: set[int]

    @classmethod
    def from_fehm_line(cls, raw_line: str) -> 'Element':
        """ Construct Element from FEHM file line
        >>> Element.from_fehm_line('4 1 2 3')
        Element(number=4, connectivity=3, nodes={1, 2, 3})
        """
        split_line = raw_line.strip().split()
        n, nodes = split_line[0], split_line[1:]
        return cls(number=int(n), connectivity=len(nodes), nodes=set(int(node) for node in nodes))
