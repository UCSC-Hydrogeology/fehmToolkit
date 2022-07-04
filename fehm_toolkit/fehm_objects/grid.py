import logging
from typing import Optional, Iterable, Union

from .element import Element
from .node import Node
from .zone import Zone


logger = logging.getLogger(__name__)


class Grid:
    """Class representing a mesh or grid object."""

    def __init__(
        self,
        nodes_by_number: dict[int, Node],
        elements_by_number: dict[int, Element],
        *,
        material_zones: Optional[tuple[Zone]] = None,
        outside_zones: Optional[tuple[Zone]] = None,
    ):
        self._nodes_by_number = nodes_by_number
        self._elements_by_number = elements_by_number
        self._material_zones = material_zones
        self._outside_zones = outside_zones

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

    def validate_contains_node_numbers(self, node_numbers: Iterable[int]) -> bool:
        missing_nodes = set(node_numbers) - self._nodes_by_number.keys()
        if missing_nodes:
            raise ValueError(f'Grid does not contain nodes: {missing_nodes}.')

    @property
    def n_elements(self) -> int:
        return len(self._elements_by_number)

    @property
    def elements(self) -> Iterable[Element]:
        return self._elements_by_number.values()

    @property
    def material_zones(self) -> set[int]:
        if self._material_zones is None:
            raise ValueError('Grid has not been loaded with zone data.')
        return self._material_zones

    @property
    def outside_zones(self) -> set[int]:
        if self._outside_zones is None:
            raise ValueError('Grid has not been loaded with zone data.')
        return self._outside_zones

    def get_material_zone(self, zone_key: Union[int, str]) -> Zone:
        if zone_key is None:
            raise ValueError('Invalid zone name or number: None')

        for zone in self.material_zones:
            if zone_key in {zone.number, zone.name}:
                return zone

        raise KeyError(f'Zone "{zone_key}" not found in grid material_zones.')

    def get_outside_zone(self, zone_key: Union[int, str]) -> Zone:
        if zone_key is None:
            raise ValueError('Invalid zone name or number: None')

        for zone in self.outside_zones:
            if zone_key in {zone.number, zone.name}:
                return zone

        raise KeyError(f'Zone "{zone_key}" not found in grid outside_zones.')

    def get_nodes_in_material_zone(self, zone_key: Union[int, str]) -> tuple[Node]:
        zone = self.get_material_zone(zone_key)
        return tuple(self._nodes_by_number[node_number] for node_number in zone.data)

    def get_nodes_in_outside_zone(self, zone_key: Union[int, str]) -> tuple[Node]:
        zone = self.get_outside_zone(zone_key)
        return tuple(self._nodes_by_number[node_number] for node_number in zone.data)
