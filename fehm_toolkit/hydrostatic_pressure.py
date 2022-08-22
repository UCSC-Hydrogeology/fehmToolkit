import argparse
import logging
from pathlib import Path
from typing import Callable, Optional, Sequence

import numpy as np
from scipy.interpolate import LinearNDInterpolator, NearestNDInterpolator, RegularGridInterpolator

from .config import ModelConfig, PressureConfig, RunConfig
from .fehm_objects import Grid, State
from .file_interface import read_grid, read_nist_lookup_table, read_restart, write_pressure

logger = logging.getLogger(__name__)

N_ITERATIONS = 5
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
    config = RunConfig.from_yaml(config_file)

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

    pressure_by_node = compute_hydrostatic_pressure(
        grid=grid,
        state=state,
        pressure_config=config.pressure_config,
        density_lookup_MPa_degC=density_lookup_MPa_degC,
    )

    logger.info(f'Writing pressures to file {output_file}')
    write_pressure(pressure_by_node, output_file=output_file)


def compute_hydrostatic_pressure(
    *,
    grid: Grid,
    state: State,
    pressure_config: PressureConfig,
    density_lookup_MPa_degC: LinearNDInterpolator,
) -> dict[int, float]:
    coordinates_by_number = _get_coordinates_by_number_without_flat_dimensions(grid)
    node_coordinates, node_temperatures = _get_coordinate_and_temperature_arrays(coordinates_by_number, state)
    _validate_pressure_config(pressure_config, node_coordinates)

    # TODO(dustin): Add config support for uniform temperature
    logger.info('Generating temperature lookups')
    temperature_lookup = NearestNDInterpolator(node_coordinates, node_temperatures)

    if pressure_config.interpolation_model.kind == 'none':
        sampled_node_numbers = [node.number for node in grid.nodes]
    else:
        sampled_node_numbers = _sample_node_numbers(grid, sampling_model=pressure_config.sampling_model)

    logger.info(f'Calculating explicit pressures for {len(sampled_node_numbers)}/{len(coordinates_by_number)} nodes')
    pressure_by_node = {}
    for i, node_number in enumerate(sampled_node_numbers, start=1):
        if not i % 10000 or i in (0, len(sampled_node_numbers)):
            logger.info(f'Pressures calculated: {i} / {len(sampled_node_numbers)}')

        pressures = calculate_hydrostatic_pressure_for_column(
            target_xy=coordinates_by_number[node_number][:-1],
            z_targets=np.array([coordinates_by_number[node_number][-1]]),
            params=pressure_config.pressure_model.params,
            density_lookup_MPa_degC=density_lookup_MPa_degC,
            temperature_lookup=temperature_lookup,
            n_iterations=N_ITERATIONS,
        )
        pressure_by_node[node_number] = pressures[0]
        if np.isnan(pressure_by_node[node_number]):
            raise ValueError(f'Pressure at node {node_number} is not a number. May be out of range for density lookup.')

    if pressure_config.interpolation_model.kind != 'none':
        x_targets, y_targets, z_targets = _get_xyz_targets(
            node_coordinates,
            interpolation_params=pressure_config.interpolation_model.params,
        )
        n_columns = _get_n_columns(pressure_config.interpolation_model.params)
        logger.info(f'Calculating explicit pressures for {n_columns} sampled columns.')

        target_points, P_cube = _calculate_explicit_target_pressures(
            x=x_targets,
            y=y_targets,
            z=z_targets,
            params=pressure_config.pressure_model.params,
            density_lookup_MPa_degC=density_lookup_MPa_degC,
            temperature_lookup=temperature_lookup,
            n_iterations=N_ITERATIONS,
        )

        logger.info('Interpolating remaining node pressures')
        unassigned_nodes = coordinates_by_number.keys() - pressure_by_node.keys()
        unassigned_coordinates = np.array([coordinates_by_number[node_number] for node_number in unassigned_nodes])

        P_lookup = RegularGridInterpolator(points=target_points, values=P_cube)
        P_interpolated = P_lookup(unassigned_coordinates)
        for node, pressure in zip(unassigned_nodes, P_interpolated):
            pressure_by_node[node] = pressure
    return pressure_by_node


def calculate_hydrostatic_pressure_for_column(
    *,
    target_xy: np.ndarray,
    z_targets: np.ndarray,
    params: dict[str, float],
    density_lookup_MPa_degC: Callable,
    temperature_lookup: Callable,
    n_iterations: int,
) -> np.ndarray:

    if len(z_targets) == 1 and z_targets[0] == params['reference_z']:
        return np.array([params['reference_pressure_MPa']])

    z_column = build_z_column_around_reference(z_targets, params)

    reference_index = np.where(z_column == params['reference_z'])[0][0]
    coordinates_column = _prepend_entry_to_array(target_xy, z_column)

    T_column = temperature_lookup(coordinates_column)
    mean_T = ((T_column + np.roll(T_column, -1)) / 2)[:-1]
    PT_column = _prepend_entry_to_array(params['reference_pressure_MPa'], mean_T)

    for iteration in range(n_iterations):  # TODO(Dustin): use convergence criteria rather than set number
        density_kg_m3 = density_lookup_MPa_degC(PT_column)
        delta_P = -1e-6 * density_kg_m3 * GRAVITY_ACCELERATION_M_S2 * params['z_interval_m']

        P_column = np.concatenate((
            params['reference_pressure_MPa'] - np.flip(np.cumsum(np.flip(delta_P[:reference_index]))),
            np.array([params['reference_pressure_MPa']]),
            params['reference_pressure_MPa'] + np.cumsum(delta_P[reference_index:]),
        ))
        PT_column[:, 0] = ((P_column + np.roll(P_column, -1)) / 2)[:-1]  # TODO(dustin): skip this on last iteration

    return np.interp(z_targets, xp=np.flip(z_column), fp=np.flip(P_column))


def build_z_column_around_reference(z_targets: np.ndarray, params: dict[str, float]) -> np.ndarray:
    upper_column = np.arange(
        start=params['reference_z'],
        stop=z_targets.max() + params['z_interval_m'],
        step=params['z_interval_m'],
    )
    lower_column = np.arange(
        start=params['reference_z'],
        stop=z_targets.min() - params['z_interval_m'],
        step=-params['z_interval_m'],
    )
    z_column = np.concatenate((
        np.flip(upper_column[1:]),
        np.array([params['reference_z']]),
        lower_column[1:],
    ))
    return z_column


def _calculate_explicit_target_pressures(
    x: Sequence,
    y: Sequence,
    z: Sequence,
    params: dict[str, int],
    density_lookup_MPa_degC: Callable,
    temperature_lookup: Callable,
    n_iterations: int,
) -> tuple[tuple[Sequence], np.ndarray]:
    if x is None or y is None:
        horizontal_target = x if x is not None else y
        P_square = np.zeros(shape=(len(horizontal_target), len(z)))
        for i, target in enumerate(horizontal_target):
            if not i % 10 or i in (0, len(horizontal_target) - 1):
                logger.info(f'Pressures calculated: {100 * i / len(horizontal_target):3.0f}%')

            pressures = calculate_hydrostatic_pressure_for_column(
                target_xy=target,
                z_targets=z,
                params=params,
                density_lookup_MPa_degC=density_lookup_MPa_degC,
                temperature_lookup=temperature_lookup,
                n_iterations=N_ITERATIONS,
            )
            P_square[i, :] = pressures
        return (horizontal_target, z), P_square

    P_cube = np.zeros(shape=(len(x), len(y), len(z)))
    for i, target_x in enumerate(x):
        if not i % 10 or i in (0, len(x) - 1):
            logger.info(f'Pressures calculated: {100 * i / len(x):3.0f}%')

        for j, target_y in enumerate(y):
            pressures = calculate_hydrostatic_pressure_for_column(
                target_xy=np.array([target_x, target_y]),
                z_targets=z,
                params=params,
                density_lookup_MPa_degC=density_lookup_MPa_degC,
                temperature_lookup=temperature_lookup,
                n_iterations=N_ITERATIONS,
            )
            P_cube[i, j, :] = pressures
    return (x, y, z), P_cube


def _prepend_entry_to_array(scalar: float, z_column: np.array):
    tiled_xy = np.tile(np.array(scalar), reps=(len(z_column), 1))
    return np.column_stack((tiled_xy, z_column))


def _get_xyz_targets(node_coordinates: np.ndarray, interpolation_params: dict[str, int]) -> np.ndarray:
    x_samples = interpolation_params.get('x_samples', 0)
    y_samples = interpolation_params.get('y_samples', 0)
    z_samples = interpolation_params['z_samples']

    z_targets = np.linspace(node_coordinates[:, -1].min(axis=0), node_coordinates[:, -1].max(axis=0), z_samples)

    if x_samples < 2:
        y_targets = np.linspace(node_coordinates[:, 0].min(axis=0), node_coordinates[:, 0].max(axis=0), y_samples)
        logger.info(
            'Sampling with spacing:\n    y: %10.2f\n    z: %10.2f',
            y_targets[1] - y_targets[0],
            z_targets[1] - z_targets[0],
        )

        return (None, y_targets, z_targets)

    if y_samples < 2:
        x_targets = np.linspace(node_coordinates[:, 0].min(axis=0), node_coordinates[:, 0].max(axis=0), x_samples)
        logger.info(
            'Sampling with spacing:\n    x: %10.2f\n    z: %10.2f',
            x_targets[1] - x_targets[0],
            z_targets[1] - z_targets[0],
        )
        return (x_targets, None, z_targets)

    x_targets = np.linspace(node_coordinates[:, 0].min(axis=0), node_coordinates[:, 0].max(axis=0), x_samples)
    y_targets = np.linspace(node_coordinates[:, 1].min(axis=0), node_coordinates[:, 1].max(axis=0), y_samples)
    logger.info(
        'Sampling with spacing:\n    x: %10.2f\n    y: %10.2f\n    z: %10.2f',
        x_targets[1] - x_targets[0],
        y_targets[1] - y_targets[0],
        z_targets[1] - z_targets[0],
    )
    return x_targets, y_targets, z_targets


def _get_n_columns(interpolation_params: dict[str, int]):
    return interpolation_params.get('x_samples', 1) * interpolation_params.get('y_samples', 1)


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


def _get_coordinate_and_temperature_arrays(
    coordinates_by_number: dict[int, np.ndarray],
    state: State,
) -> tuple[np.ndarray]:
    coordinates = []
    temperatures = []
    for number, coordinate in coordinates_by_number.items():
        coordinates.append(coordinate)
        temperatures.append(state.temperature[number - 1])

    return np.array(coordinates), np.array(temperatures)


def _read_density_lookup(water_properties_file: Path) -> LinearNDInterpolator:
    raw_lookup = read_nist_lookup_table(water_properties_file)
    points, density_kg_m3 = [], []
    for pressure_temperature_key, properties in raw_lookup.items():
        points.append(pressure_temperature_key)
        density_kg_m3.append(properties['density_kg_m3'])

    return LinearNDInterpolator(points=np.array(points), values=np.array(density_kg_m3))


def get_lookup_with_out_of_range_backup(points: np.ndarray, values: np.ndarray) -> Callable:
    lookup_linear = LinearNDInterpolator(points, values)
    lookup_nearest = NearestNDInterpolator(points, values)

    def lookup_with_backup(lookup_points: np.ndarray):
        interpolated = lookup_linear(lookup_points)
        index_out_of_range = np.isnan(interpolated)
        if any(index_out_of_range):
            nearest_interpolated = lookup_nearest(lookup_points[index_out_of_range, :])
            interpolated[index_out_of_range] = nearest_interpolated
        return interpolated

    return lookup_with_backup


def _sample_node_numbers(grid: Grid, sampling_model: Optional[ModelConfig]) -> set[int]:
    if sampling_model is None:
        return set()

    explicit_nodes = sampling_model.params.get('explicit_nodes', [])
    explicit_material_zones = sampling_model.params.get('explicit_material_zones', [])
    explicit_outside_zones = sampling_model.params.get('explicit_outside_zones', [])
    grid.validate_contains_node_numbers(explicit_nodes)

    sampled_nodes = set(explicit_nodes)
    for zone_key in explicit_material_zones:
        zone = grid.get_material_zone(zone_key)
        sampled_nodes = sampled_nodes.union(zone.data)
    for zone_key in explicit_outside_zones:
        zone = grid.get_outside_zone(zone_key)
        sampled_nodes = sampled_nodes.union(zone.data)

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


def _validate_pressure_config(config: PressureConfig, node_coordinates: np.ndarray):
    if config.pressure_model.kind not in ('depth'):
        raise NotImplementedError(f'Pressure model kind {config.pressure_model.kind} not supported.')

    if config.interpolation_model.kind not in ('regular_grid', 'none'):
        raise NotImplementedError(f'Interpolation model kind {config.interpolation_model.kind} not supported.')

    if config.sampling_model is not None and config.sampling_model.kind not in ('explicit_lists'):
        raise NotImplementedError(f'Sampling model kind {config.sampling_model.kind} not supported.')

    interpolation_params = config.interpolation_model.params

    if config.interpolation_model.kind == 'regular_grid':
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
