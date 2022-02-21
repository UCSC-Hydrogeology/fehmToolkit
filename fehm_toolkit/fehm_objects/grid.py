from typing import TextIO

from .element import Element
from .node import Node


class Grid:
    """Class representing a mesh or grid object."""

    def __init__(self, nodes_by_number: dict, elements_by_number: dict):
        self._nodes_by_number = nodes_by_number or {}
        self._elements_by_number = elements_by_number or {}

    def node(self, number: int) -> Node:
        try:
            return self._nodes_by_number[number]
        except KeyError:
            raise KeyError(f'Node ({number}) not found in grid.')

    def element(self, number: int) -> Element:
        try:
            return self._elements_by_number[number]
        except KeyError:
            raise KeyError(f'Element ({number}) not found in grid.')

    @property
    def n_nodes(self) -> int:
        return len(self._nodes_by_number)

    @property
    def n_elements(self) -> int:
        return len(self._elements_by_number)

    @classmethod
    def from_fehm(cls, fehm_file) -> 'Grid':
        nodes_by_number = None
        elements_by_number = None

        with open(fehm_file) as f:
            while True:
                block_name = next(f).strip()

                if block_name == 'coor':
                    nodes_by_number = cls._read_coor(f)
                elif block_name == 'elem':
                    elements_by_number = cls._read_elem(f)
                elif block_name == 'stop':
                    break
                else:
                    raise NotImplementedError(f'No parser for block type "{block_name}"')

                next(f)  # throw away extra line after block

        return cls(nodes_by_number=nodes_by_number, elements_by_number=elements_by_number)

    @classmethod
    def _read_coor(cls, open_file: TextIO) -> dict[int, Node]:
        n_nodes = int(next(open_file))

        nodes_by_number = {}
        for i in range(n_nodes):
            node = Node.from_fehm_line(next(open_file))
            nodes_by_number[node.number] = node

        return nodes_by_number

    @classmethod
    def _read_elem(cls, open_file: TextIO) -> dict[int, Node]:
        n_elements = int(next(open_file).strip().split()[1])

        elements_by_number = {}
        for i in range(n_elements):
            element = Element.from_fehm_line(next(open_file))
            elements_by_number[element.number] = element
        return elements_by_number
