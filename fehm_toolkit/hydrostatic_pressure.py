import argparse
import logging
from pathlib import Path
from typing import Callable, Optional

import numpy as np
from scipy import interpolate
import yaml

from .config import read_legacy_ipi_config
from .fehm_objects import Grid, State
from .file_interface import read_grid, read_nist_lookup_table, read_restart, write_pressure

logger = logging.getLogger(__name__)

N_ITERATIONS = 3
GRAVITY_ACCELERATION_M_S2 = -9.80665


def generate_hydrostatic_pressure_file(
    *,
    config_file: Path,
    fehm_file: Path,
    outside_zone_file: Path,
    restart_file: Path,
    water_properties_file: Path,
    output_file: Path,
):
    logger.info(f'Reading configuration file: {config_file}')
    pressure_config = _read_pressure_config(config_file)

    if pressure_config['model_kind'] not in ('depth'):
        raise NotImplementedError(f'model_kind {pressure_config["model_kind"]} not supported.')

    logger.info('Parsing grid into memory')
    grid = read_grid(fehm_file, outside_zone_file=outside_zone_file, read_elements=False)
    state, restart_metadata = read_restart(restart_file)
    density_lookup_MPa_degC = _read_density_lookup(water_properties_file)

    node_numbers, node_coordinates, node_temperatures = _get_structured_node_data(grid, state)

    # TODO(dustin): Add config support for uniform temperature
    logger.info('Generating temperature lookups')
    temperature_lookup = get_lookup_with_out_of_range_backup(points=node_coordinates, values=node_temperatures)

    logger.info('Bootstrapping node pressures')
    pressure_by_node = {}
    for i, (node_number, coordinates) in enumerate(zip(node_numbers, node_coordinates)):
        if not i % 1000:
            logger.info(f'Pressures calculated: {i} / {grid.n_nodes}')
        pressure_by_node[node_number] = _calculate_hydrostatic_pressure(
            target_coordinates=coordinates,
            params=pressure_config['model_params'],
            density_lookup_MPa_degC=density_lookup_MPa_degC,
            temperature_lookup=temperature_lookup,
            n_iterations=N_ITERATIONS,
        )
        if np.isnan(pressure_by_node[node_number]):
            raise ValueError(f'Pressure for node {node_number} is not a number.')

    write_pressure(pressure_by_node, output_file=output_file)


def _calculate_hydrostatic_pressure(
    *,
    target_coordinates: np.ndarray,
    params: dict[str, float],
    density_lookup_MPa_degC: Callable,
    temperature_lookup: Optional[Callable],
    n_iterations: int,
) -> float:
    target_xy = target_coordinates[:-1]
    target_z = target_coordinates[-1]

    if target_z == params['reference_z']:
        return params['reference_pressure_MPa']

    signed_z_interval_m = np.sign(target_z - params['reference_z']) * params['z_interval_m']
    z_column = np.arange(
        start=params['reference_z'],
        stop=target_z + signed_z_interval_m,
        step=signed_z_interval_m,
    )
    if temperature_lookup is not None:
        coordinates_column = _prepend_scalar_to_array(target_xy, z_column)
        T_column = temperature_lookup(coordinates_column)
    else:
        T_column = len(z_column) * [params['reference_temperature_degC']]

    mean_T = ((T_column + np.roll(T_column, -1)) / 2)[:-1]
    PT_column = _prepend_scalar_to_array(params['reference_pressure_MPa'], mean_T)

    for iteration in range(n_iterations):
        density_kg_m3 = density_lookup_MPa_degC(PT_column)
        delta_P = 1e-6 * density_kg_m3 * GRAVITY_ACCELERATION_M_S2 * signed_z_interval_m
        PT_column[:, 0] = params['reference_pressure_MPa'] + np.cumsum(delta_P)

    z = z_column[-1]
    P_MPa = PT_column[-1, 0]

    if z == target_z:
        return P_MPa

    previous_z = z_column[-2]
    previous_P_MPa = PT_column[-2, 0] if len(PT_column) > 1 else params['reference_pressure_MPa']
    return np.interp(target_z, xp=[previous_z, z], fp=[previous_P_MPa, P_MPa])


def _prepend_scalar_to_array(scalar: float, z_column: np.array):
    tiled_xy = np.tile(np.array(scalar), reps=(len(z_column), 1))
    return np.column_stack((tiled_xy, z_column))


def _get_structured_node_data(grid: Grid, state: State) -> tuple[np.ndarray]:
    numbers = []
    coordinates = []
    temperatures = []
    for node in grid.nodes:
        numbers.append(node.number)
        coordinates.append(node.coordinates.value)
        temperatures.append(state.temperature[node.number - 1])

    numbers, coordinates, temperatures = np.array(numbers), np.array(coordinates), np.array(temperatures)
    flat_dimension = _get_flat_dimension_or_none(coordinates)
    if flat_dimension is not None:
        coordinates = np.delete(coordinates, obj=flat_dimension, axis=1)

    return numbers, coordinates, temperatures


def _read_pressure_config(config_file: Path):
    with open(config_file) as f:
        config = yaml.load(f, Loader=yaml.Loader)
        logger.info(f'Format for {config_file} is not YAML, trying legacy reader.')
    if not isinstance(config, dict):
        config = read_legacy_ipi_config(config_file)

    return config['hydrostatic_pressure']


def _read_density_lookup(water_properties_file: Path):
    raw_lookup = read_nist_lookup_table(water_properties_file)
    points, density_kg_m3 = [], []
    for pressure_temperature_key, properties in raw_lookup.items():
        points.append(pressure_temperature_key)
        density_kg_m3.append(properties['density_kg_m3'])

    return interpolate.LinearNDInterpolator(points=np.array(points), values=np.array(density_kg_m3))


def get_lookup_with_out_of_range_backup(points: np.ndarray, values: np.ndarray) -> Callable:
    lookup_linear = interpolate.LinearNDInterpolator(points, values)
    lookup_nearest = interpolate.NearestNDInterpolator(points, values)

    def lookup_with_backup(lookup_points: np.ndarray):
        interpolated = lookup_linear(lookup_points)
        index_out_of_range = np.isnan(interpolated)
        if any(index_out_of_range):
            nearest_interpolated = lookup_nearest(lookup_points[index_out_of_range, :])
            interpolated[index_out_of_range] = nearest_interpolated
        return interpolated

    return lookup_with_backup


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


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s (%(levelname)s) %(message)s')

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--config_file', type=Path, help='Path to configuration (.yaml/.ipi) file.')
    parser.add_argument('--fehm_file', type=Path, help='Path to main grid (.fehm) file.')
    parser.add_argument('--outside_zone_file', type=Path, help='Path to boundary (_outside.zone) file.')
    parser.add_argument('--restart_file', type=Path, help='Path to restart (.fin/.ini) file.')
    parser.add_argument('--water_properties_file', type=Path, help='Path to NIST lookup table (.out/.wpi).')
    parser.add_argument('--output_file', type=Path, help='Path for heatflux output to be written.')
    args = parser.parse_args()

    generate_hydrostatic_pressure_file(
        config_file=args.config_file,
        fehm_file=args.fehm_file,
        outside_zone_file=args.outside_zone_file,
        restart_file=args.restart_file,
        water_properties_file=args.water_properties_file,
        output_file=args.output_file,
    )
