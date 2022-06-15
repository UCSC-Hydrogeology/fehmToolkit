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
RANDOM_SAMPLE_SEED = 12


def generate_hydrostatic_pressure_file(
    *,
    config_file: Path,
    fehm_file: Path,
    material_zone_file: Path,
    outside_zone_file: Path,
    restart_file: Path,
    water_properties_file: Path,
    output_file: Path,
):
    logger.info(f'Reading configuration file: {config_file}')
    pressure_config = _read_pressure_config(config_file)

    logger.info('Reading water properties lookup')
    density_lookup_MPa_degC = _read_density_lookup(water_properties_file)

    logger.info('Reading node data into memory')
    grid = read_grid(
        fehm_file,
        material_zone_file=material_zone_file,
        outside_zone_file=outside_zone_file,
        read_elements=False,
    )
    state, restart_metadata = read_restart(restart_file)

    coordinates_by_number = _get_coordinates_by_number_without_flat_dimensions(grid)
    sampled_node_numbers = _sample_node_numbers(grid, sampling_configs=pressure_config.get('sampling_configs'))
    sampled_node_coordinates, sampled_node_temperatures = _get_sampled_coordinate_and_temperature_arrays(
        coordinates_by_number=coordinates_by_number,
        state=state,
        sampled_node_numbers=sampled_node_numbers,
    )


    _validate_pressure_config(pressure_config, node_coordinates)

    # TODO(dustin): Add config support for uniform temperature
    logger.info('Generating temperature lookups')
    temperature_lookup = interpolate.NearestNDInterpolator(sampled_node_coordinates, sampled_node_temperatures)

    logger.info(f'Calculating explicit pressures for {len(sampled_node_numbers)}/{len(coordinates_by_number)} nodes')
    pressure_by_node = {}
    for i, node_number in enumerate(sampled_node_numbers, start=1):
        if not i % 10000 or i in (0, len(sampled_node_numbers)):
            logger.info(f'Pressures calculated: {i} / {len(sampled_node_numbers)}')
        pressure_by_node[node_number] = _calculate_hydrostatic_pressure(
            target_coordinates=coordinates_by_number[node_number],
            params=pressure_config['model_params'],
            density_lookup_MPa_degC=density_lookup_MPa_degC,
            temperature_lookup=temperature_lookup,
            n_iterations=N_ITERATIONS,
        )
        if np.isnan(pressure_by_node[node_number]):
            raise ValueError(f'Pressure at node {node_number} is not a number. May be out of range for density lookup.')

    logger.info('Interpolating remaining node pressures')
    pressure_lookup = get_lookup_with_out_of_range_backup(
        points=np.array([coordinates_by_number[node_number] for node_number in pressure_by_node.keys()]),
        values=np.fromiter(pressure_by_node.values(), dtype=float),
    )
    unassigned_nodes = coordinates_by_number.keys() - pressure_by_node.keys()
    pressures = pressure_lookup(np.array([coordinates_by_number[node_number] for node_number in unassigned_nodes]))
    for node, pressure in zip(unassigned_nodes, pressures):
        pressure_by_node[node] = pressure

    logger.info(f'Writing pressures to file {output_file}')
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

    for iteration in range(n_iterations):  # TODO(Dustin): use convergence criteria rather than set number
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


def _get_coordinates_by_number_without_flat_dimensions(grid: Grid) -> dict[int, np.ndarray]:
    numbers = []
    coordinates = []
    for node in grid.nodes:
        numbers.append(node.number)
        coordinates.append(node.coordinates.value)

    coordinates = np.array(coordinates)
    flat_dimension = _get_flat_dimension_or_none(coordinates)
    if flat_dimension is not None:
        coordinates = np.delete(coordinates, obj=flat_dimension, axis=1)
    return {n: c for n, c in zip(numbers, coordinates)}


def _get_sampled_coordinate_and_temperature_arrays(
    coordinates_by_number: dict[int, np.ndarray],
    state: State,
    sampled_node_numbers: set[int],
) -> tuple[np.ndarray]:
    sampled_coordinates = []
    sampled_temperatures = []
    for number, coordinate in coordinates_by_number.items():
        if number in sampled_node_numbers:
            sampled_coordinates.append(coordinate)
            sampled_temperatures.append(state.temperature[number - 1])

    return np.array(sampled_coordinates), np.array(sampled_temperatures)


def _read_pressure_config(config_file: Path):
    with open(config_file) as f:
        config = yaml.load(f, Loader=yaml.Loader)
    if not isinstance(config, dict):
        logger.info(f'Format for {config_file} is not YAML, trying legacy reader.')
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


def _sample_node_numbers(grid: Grid, sampling_configs: Optional[list[dict]]):
    sampled_nodes = set()
    for config in sampling_configs:
        sample_for_config = _get_sampled_nodes(grid, config)
        sampled_nodes = sampled_nodes.union(sample_for_config)
    return sampled_nodes


def _get_sampled_nodes(grid: Grid, config: dict):
    if config['zone_kind'] == 'outside':
        zone_getter = grid.get_outside_zone
    elif config['zone_kind'] == 'material':
        zone_getter = grid.get_material_zone
    else:
        raise NotImplementedError(f"No support for zone_kind {config['zone_kind']}")

    rng = np.random.default_rng(RANDOM_SAMPLE_SEED)
    sampled_nodes = set()
    for zone_key in config['zones']:
        zone = zone_getter(zone_key)

        if config['sample_method'] == 'number':
            sample_size = config['sample_size']
        elif config['sample_method'] == 'fraction':
            sample_size = int(config['sample_size'] * len(zone.data)) or 1
        else:
            raise NotImplementedError(f"No support for sample_method {config['sample_method']}")

        zone_sample = rng.choice(zone.data, size=sample_size, replace=False)
        sampled_nodes = sampled_nodes.union(set(zone_sample))

    return sampled_nodes


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


def _validate_pressure_config(config: dict, node_coordinates: np.ndarray):
    if config['model_kind'] not in ('depth'):
        raise NotImplementedError(f'model_kind {config["model_kind"]} not supported.')

    if config['interpolation_kind'] not in ('grid_samples'):
        raise NotImplementedError(f'interpolation_kind {config["interpolation_kind"]} not supported.')

    interpolation_params = config['interpolation_params']
    x_samples = interpolation_params.get('x_samples', 0)
    y_samples = interpolation_params.get('y_samples', 0)
    sample_xy_dimensions = (x_samples > 1) + (y_samples > 1)
    node_xy_dimensions = node_coordinates.shape[1] - 1
    if sample_xy_dimensions != node_xy_dimensions:
        raise ValueError(
            f'Number of sample dimensions ({sample_xy_dimensions}) '
            f'inconsistent with grid dimensions ({node_xy_dimensions}).'
        )


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s (%(levelname)s) %(message)s')

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--config_file', type=Path, help='Path to configuration (.yaml/.ipi) file.')
    parser.add_argument('--fehm_file', type=Path, help='Path to main grid (.fehm) file.')
    parser.add_argument('--material_zone_file', type=Path, help='Path to material (_material.zone) file.')
    parser.add_argument('--outside_zone_file', type=Path, help='Path to boundary (_outside.zone) file.')
    parser.add_argument('--restart_file', type=Path, help='Path to restart (.fin/.ini) file.')
    parser.add_argument('--water_properties_file', type=Path, help='Path to NIST lookup table (.out/.wpi).')
    parser.add_argument('--output_file', type=Path, help='Path for heatflux output to be written.')
    args = parser.parse_args()

    generate_hydrostatic_pressure_file(
        config_file=args.config_file,
        fehm_file=args.fehm_file,
        material_zone_file=args.material_zone_file,
        outside_zone_file=args.outside_zone_file,
        restart_file=args.restart_file,
        water_properties_file=args.water_properties_file,
        output_file=args.output_file,
    )
