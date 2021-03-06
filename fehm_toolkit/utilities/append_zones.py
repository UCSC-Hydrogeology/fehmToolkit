from pathlib import Path
from typing import Sequence, Union

from ..fehm_objects import Zone
from ..file_interface import read_zones


def append_zones(
    zone_keys_to_add: Sequence[Union[int, str]],
    add_zones_from_file: Path,
    add_zones_to_file: Path,
):
    zones_to_add = _filter_zones_to_add(zone_keys_to_add, raw_zones_to_add=read_zones(add_zones_from_file))
    return _combine_zones(zones_to_add=zones_to_add, source_zones=read_zones(add_zones_to_file))


def _filter_zones_to_add(zone_keys_to_add: Sequence[Union[int, str]], raw_zones_to_add: tuple[Zone]) -> tuple[Zone]:
    return (zone for zone in raw_zones_to_add if zone.number in zone_keys_to_add or zone.name in zone_keys_to_add)


def _combine_zones(*, zones_to_add: tuple[Zone], source_zones: tuple[Zone]) -> list[Zone]:
    max_source_zone_number = max(zone.number for zone in source_zones)
    source_zone_names = {zone.name for zone in source_zones}

    combined_zones = list(source_zones)
    for i, zone in enumerate(zones_to_add, start=1):
        if zone.name in source_zone_names:
            raise ValueError(f'Zone {zone.name} already exists in zone file, cannot append.')
        combined_zones.append(Zone(number=i + max_source_zone_number, name=zone.name, data=zone.data))

    return combined_zones
