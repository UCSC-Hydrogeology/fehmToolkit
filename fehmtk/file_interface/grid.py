from decimal import Decimal
import logging
from pathlib import Path
from typing import Iterable, Optional

import numpy as np
from scipy import interpolate

from ..common import round_significant_figures
from ..fehm_objects import Grid, Node, Vector, Zone
from .fehm import read_fehm
from .storage import read_volume_from_storage
from .zone import read_zones

COORDINATE_SIGNIFICANT_FIGURES = 13  # Coordinates in FEHM files stored as e.g. 1.000000000000E+01


logger = logging.getLogger(__name__)


def read_grid(
    fehm_file: Path,
    *,
    material_zone_file: Optional[Path] = None,
    outside_zone_file: Optional[Path] = None,
    area_file: Optional[Path] = None,
    storage_file: Optional[Path] = None,
    read_elements: Optional[bool] = True,
) -> Grid:
    if area_file and not outside_zone_file:
        raise NotImplementedError('Must specify an outside_zone_file to load area data.')

    logger.debug(f'Reading nodes and elements from {fehm_file}')
    coordinates_by_node_number, elements_by_number = read_fehm(fehm_file, read_elements=read_elements)

    material_zones = None
    if material_zone_file:
        logger.debug(f'Reading material zones from {material_zone_file}')
        material_zones = read_zones(material_zone_file)

    volume_by_node_number = None
    if storage_file:
        logger.debug(f'Reading volumes from {storage_file}')
        volumes = read_volume_from_storage(storage_file)
        volume_by_node_number = {n: v for n, v in zip(sorted(coordinates_by_node_number.keys()), volumes)}

    outside_zones, area_by_node_number, depth_by_node_number = (None, None, None)
    if outside_zone_file:
        logger.debug(f'Reading outside zones from {outside_zone_file}')
        outside_zones = read_zones(outside_zone_file)

        if area_file:
            logger.debug(f'Reading outside area from {area_file}')
            area_zones = read_zones(area_file)
            _validate_outside_zones_match_area_zones(area_zones, outside_zones)
            area_by_node_number = _get_area_by_node_number(area_zones=area_zones, outside_zones=outside_zones)

        logger.debug('Calculating node depths')
        top_zone = {zone.name: zone for zone in outside_zones}.get('top')
        depth_by_node_number = calculate_node_depths(coordinates_by_node_number, top_zone)

    logger.debug('Constructing nodes lookup')
    nodes_by_number = _construct_nodes_lookup(
        coordinates_by_number=coordinates_by_node_number,
        area_by_number=area_by_node_number,
        depth_by_number=depth_by_node_number,
        volume_by_number=volume_by_node_number,
    )

    return Grid(
        nodes_by_number=nodes_by_number,
        elements_by_number=elements_by_number,
        material_zones=material_zones,
        outside_zones=outside_zones,
    )


def _validate_outside_zones_match_area_zones(area_zones: Iterable[Zone], outside_zones: Iterable[Zone]):
    area_zone_name_lookup = {zone.number: zone.name for zone in area_zones}
    outside_zone_name_lookup = {zone.number: zone.name for zone in outside_zones}
    if area_zone_name_lookup != outside_zone_name_lookup:
        raise ValueError(
            'Name lookups mismatch between .area and _outside_zone files: '
            f'{area_zone_name_lookup} vs {outside_zone_name_lookup}'
        )


def _get_area_by_node_number(*, area_zones: Iterable[Zone], outside_zones: Iterable[Zone]) -> dict[int, tuple[Decimal]]:
    area_data_by_zone_number = {area.number: area.data for area in area_zones}
    outside_zone_nodes_by_zone_number = {zone.number: zone.data for zone in outside_zones}

    mismatched_keys = area_data_by_zone_number.keys() ^ outside_zone_nodes_by_zone_number.keys()  # symmetric difference
    if mismatched_keys:
        raise ValueError(f'Area and node number lookups do not have the same zones: {mismatched_keys}')

    area_by_node_number = {}
    for zone_number, areas in area_data_by_zone_number.items():
        node_numbers = outside_zone_nodes_by_zone_number[zone_number]
        if len(areas) != len(node_numbers):
            raise ValueError(
                f'Different number of nodes ({len(node_numbers)}) and areas ({len(areas)}) in zone "{zone_number}"'
            )

        for node_number, area in zip(node_numbers, areas):
            assigned_area = area_by_node_number.get(node_number)
            if assigned_area:
                if assigned_area != area:
                    raise ValueError(
                        f'Node "{node_number}"" area ({area}) for zone "{zone_number}" '
                        f'does not match area assigned from previous zone ({assigned_area})'
                    )
                continue
            area_by_node_number[node_number] = area

    return area_by_node_number


def _construct_nodes_lookup(
    coordinates_by_number: dict[int, Vector],
    *,
    area_by_number: Optional[dict[int, Vector]],
    depth_by_number: Optional[dict[int, Decimal]],
    volume_by_number: Optional[dict[int, Decimal]],
) -> dict[int, Node]:
    return {
        number: Node(
            number,
            coordinates,
            outside_area=area_by_number.get(number) if area_by_number else None,
            depth=depth_by_number.get(number) if depth_by_number else None,
            volume=volume_by_number.get(number) if volume_by_number else None,
        )
        for number, coordinates in coordinates_by_number.items()
    }


def calculate_node_depths(
    coordinates_by_number: dict[int, Vector],
    top_zone: Optional[Zone],
) -> Optional[dict[int, Decimal]]:
    if top_zone is None:
        return None

    top_coordinates = np.array([coordinates_by_number[node_number].value for node_number in top_zone.data])
    flat_dimension = _get_flat_dimension_or_none(top_coordinates)
    top_coordinates = top_coordinates.astype(float)  # interpolation routines require floats
    if flat_dimension is not None:
        return _calculate_2d_node_depths(coordinates_by_number, top_coordinates, flat_dimension)

    return _calculate_3d_node_depths(coordinates_by_number, top_coordinates, flat_dimension)


def _get_flat_dimension_or_none(coordinates: np.array) -> Optional[int]:
    """Identify which (if any) of the first two dimensions has no variance.
    >>> import numpy as np
    >>> _get_flat_dimension_or_none(np.array([[1, 1, 1], [2, 1, 2], [3, 1, 3]]))
    1
    >>> _get_flat_dimension_or_none(np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]]))
    0
    >>> _get_flat_dimension_or_none(np.array([[1, 1, 1], [2, 2, 1], [3, 3, 1]]))
    """
    for dim in (0, 1):
        if not coordinates[:, dim].var():
            return dim
    return None


def _calculate_3d_node_depths(
    coordinates_by_number: dict[int, Vector],
    top_coordinates: np.ndarray,
    flat_dimension: int,
) -> dict[int, Decimal]:
    seafloor_2d_linear = interpolate.LinearNDInterpolator(top_coordinates[:, 0:2], top_coordinates[:, 2])
    seafloor_2d_nearest = interpolate.NearestNDInterpolator(top_coordinates[:, 0:2], top_coordinates[:, 2])

    ordered_entries = sorted(coordinates_by_number.items())
    ordered_xy = np.array([coordinates.value[:2] for number, coordinates in ordered_entries])
    linear_interpolated = seafloor_2d_linear(ordered_xy)

    depth_by_number = {}
    for linear, (number, coordinates) in zip(linear_interpolated, ordered_entries):
        interpolated_seafloor = linear if not np.isnan(linear) else seafloor_2d_nearest(coordinates.x, coordinates.y)
        seafloor_z = round_significant_figures(
            Decimal(interpolated_seafloor),  # convert float back to Decimal to work with Decimal coordinates
            n=COORDINATE_SIGNIFICANT_FIGURES,
        )
        depth_by_number[number] = seafloor_z - coordinates.z
    return depth_by_number


def _calculate_2d_node_depths(
    coordinates_by_number: dict[int, Vector],
    top_coordinates: np.ndarray,
    flat_dimension: int,
) -> dict[int, Decimal]:
    model_dimension = 1 if flat_dimension == 0 else 0
    seafloor_1d = interpolate.interp1d(
        x=top_coordinates[:, model_dimension],
        y=top_coordinates[:, 2],
        bounds_error=False,
        fill_value='extrapolate',
    )
    depth_by_number = {}
    for number, coordinates in coordinates_by_number.items():
        horizontal_coordinate = coordinates.value[model_dimension]
        seafloor_z = round_significant_figures(
            Decimal(seafloor_1d(float(horizontal_coordinate)).item()),  # interpolant requires floats
            n=COORDINATE_SIGNIFICANT_FIGURES,
        )
        depth_by_number[number] = seafloor_z - coordinates.z
    return depth_by_number
    return {
        number: seafloor_1d(coordinates.value[model_dimension]) - coordinates.z
        for number, coordinates in coordinates_by_number.items()
    }
