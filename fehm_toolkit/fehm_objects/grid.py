import logging
from typing import Optional, Iterable, Union

from .element import Element
from .node import Node


logger = logging.getLogger(__name__)


class Grid:
    """Class representing a mesh or grid object."""

    def __init__(
        self,
        nodes_by_number: dict[int, Node],
        elements_by_number: dict[int, Element],
        *,
        node_numbers_by_material_zone_number: Optional[dict[int, tuple[int]]] = None,
        node_numbers_by_outside_zone_number: Optional[dict[int, tuple[int]]] = None,
        outside_zone_number_by_name: Optional[dict[str, int]] = None,
    ):
        self._nodes_by_number = nodes_by_number
        self._elements_by_number = elements_by_number
        self._node_numbers_by_material_zone_number = node_numbers_by_material_zone_number
        self._node_numbers_by_outside_zone_number = node_numbers_by_outside_zone_number
        self._outside_zone_number_by_name = outside_zone_number_by_name

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
    def nodes(self) -> Iterable[Node]:
        return self._nodes_by_number.values()

    @property
    def n_elements(self) -> int:
        return len(self._elements_by_number)

    @property
    def elements(self) -> Iterable[Element]:
        return self._elements_by_number.values()

    @property
    def material_zones(self) -> set[int]:
        if self._node_numbers_by_material_zone_number is None:
            raise ValueError('Grid has not been loaded with zone data.')
        return set(self._node_numbers_by_material_zone_number.keys())

    @property
    def outside_zones(self) -> set[int]:
        if self._node_numbers_by_outside_zone_number is None:
            raise ValueError('Grid has not been loaded with zone data.')
        return set(self._node_numbers_by_outside_zone_number.keys())

    def get_nodes_in_material_zone(self, zone_number: Union[int, Iterable[int]]) -> tuple[Node]:
        try:
            nodes = []
            for number in zone_number:
                for node in self._get_nodes_in_material_zone(number):
                    nodes.append(node)
            return tuple(nodes)
        except TypeError:
            return tuple(node for node in self._get_nodes_in_material_zone(zone_number))

    def _get_nodes_in_material_zone(self, zone_number: int) -> Iterable[Node]:
        if self._node_numbers_by_material_zone_number is None:
            raise ValueError('Grid has not been loaded with zone data.')

        try:
            node_numbers = self._node_numbers_by_material_zone_number[zone_number]
        except KeyError:
            raise KeyError(f'Zone "{zone_number}" not found in grid.')

        for node_number in node_numbers:
            yield self._nodes_by_number[node_number]

    def get_nodes_in_outside_zone(self, zone_number_or_name: Union[int, str]):
        if self._node_numbers_by_outside_zone_number is None:
            raise ValueError('Grid has not been loaded with zone data.')

        try:
            node_numbers = self._node_numbers_by_outside_zone_number[zone_number_or_name]
        except KeyError as e:
            if self._outside_zone_number_by_name is None:
                raise e

            try:
                zone_number = self._outside_zone_number_by_name[zone_number_or_name]
                node_numbers = self._node_numbers_by_outside_zone_number[zone_number]
            except KeyError:
                raise KeyError(f'Zone "{zone_number_or_name}" not found in grid.')

        for node_number in node_numbers:
            yield self._nodes_by_number[node_number]
