from decimal import Decimal
from typing import Callable

from fehmtk.fehm_objects import Node


def get_boundary_model(boundary_kind: str, model_kind: str) -> Callable:
    if boundary_kind == 'heat_flux':
        models_by_kind = _get_heat_flux_models_by_kind()
    elif boundary_kind == 'flow':
        models_by_kind = _get_flow_models_by_kind()
    else:
        raise NotImplementedError(f'No models defined for boundary_kind {boundary_kind}')

    try:
        return models_by_kind[model_kind]
    except KeyError:
        raise NotImplementedError(f'No model defined for kind {model_kind}')


def _get_flow_models_by_kind() -> dict[str, Callable]:
    return {
        'open_flow': _open_flow,
    }


def _open_flow(node: Node, params: dict) -> tuple[Decimal]:
    """Fluid flow set to constant pressure, allowing flow in or out to maintain it.

    Fluid input comes in at the specified temperature, output is at the in-place temperature. AIPED value sets the
    impedence to flow, and therefore determines the model's ability to maintain the desired pressure.
    """
    skd = '0'
    eflow = -params['input_fluid_temp_degC']
    aiped = abs(node.volume * params['aiped_to_volume_ratio'])
    return (skd, eflow, aiped)


def _get_heat_flux_models_by_kind() -> dict[str, Callable]:
    return {
        'crustal_age': _crustal_age_heatflux,
        'constant_MW_per_m2': _constant_MW_per_m2,
    }


def _crustal_age_heatflux(node: Node, params: dict) -> Decimal:
    """Heat input per square meter as a function of distance to ridge in x:

    C / a^0.5
    Where C is a parameter and a is the crustal age, calculated as:
    (D ± x) / (1000 * R)
    Where R is the spread rate in mm/year, D is the distance between x=0 and the ridge. The sign in (D ± x) is
    determined by the crustal age sign, which denotes whether age increases or decreases with x.

    Required params:
    coefficient_MW                [C]  (numeric)
    boundary_distance_to_ridge_m  [D]  (numeric)
    spread_rate_mm_per_year       [R]  (numeric)
    crustal_age_sign              [±]  (+, -, 1, or -1)
    crustal_age_dimension         [x]  (x, y, or z) [default x]
    """
    if params['crustal_age_sign'] not in (1, -1, '+', '-'):
        raise ValueError(f'Invalid crustal_age_sign {params["crustal_age_sign"]}, must be 1, -1, +, or -')

    crustal_age_sign = 1 if params['crustal_age_sign'] in (1, '+') else -1

    crustal_age_dimension = params.get('crustal_age_dimension', 'x')
    if crustal_age_dimension not in ('x', 'y', 'z'):
        raise ValueError(f'Invalid crustal_age_dimension: {crustal_age_dimension}')
    distance_from_boundary_m = crustal_age_sign * getattr(node, crustal_age_dimension)

    distance_from_ridge_m = params['boundary_distance_to_ridge_m'] + distance_from_boundary_m
    age_ma = 1 / (params['spread_rate_mm_per_year'] * Decimal('1E3')) * distance_from_ridge_m
    heatflux_per_m2 = params['coefficient_MW'] / age_ma ** Decimal('0.5')
    return -abs(node.outside_area.z * heatflux_per_m2)


def _constant_MW_per_m2(node: Node, params: dict) -> Decimal:
    """Heat input per square meter as a constant value throughout the grid.

    Required params:
    constant  (numeric)
    """
    return -abs(node.outside_area.z * params['constant'])
