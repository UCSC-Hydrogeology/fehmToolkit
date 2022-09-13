from typing import Callable

from fehm_toolkit.fehm_objects import Node


def get_heatflux_models_by_kind() -> dict[str, Callable]:
    return {
        'crustal_age': _crustal_age_heatflux,
        'constant_MW_per_m2': _constant_MW_per_m2,
    }


def _crustal_age_heatflux(node: Node, params: dict) -> float:
    """Heat input per square meter as a function of distance to ridge in x:
    C / a^0.5
    Where C is a parameter and a is the crustal age, calculated as:
    (D ± d) / (1000 * R)
    Where R is the spread rate in mm/year, D is the distance between x=0 and the ridge, and d is the distance to a
    given node. The sign in (D ± d) is determined by the crustal age sign, which denotes whether age increases or
    decreases with x.

    Required params:
    coefficient_MW                [C]  (numeric)
    boundary_distance_to_ridge_m  [D]  (numeric)
    spread_rate_mm_per_year       [R]  (numeric)
    crustal_age_sign              [±]  (+, -, 1, or -1)
    """
    if params['crustal_age_sign'] not in (1, -1, '+', '-'):
        raise ValueError(f'Invalid crustal_age_sign {params["crustal_age_sign"]}, must be 1, -1, +, or -')

    crustal_age_sign = 1 if params['crustal_age_sign'] in (1, '+') else -1
    distance_from_boundary_m = crustal_age_sign * node.x
    distance_from_ridge_m = params['boundary_distance_to_ridge_m'] + distance_from_boundary_m
    age_ma = 1 / (params['spread_rate_mm_per_year'] * 1E3) * distance_from_ridge_m
    heatflux_per_m2 = params['coefficient_MW'] / age_ma ** 0.5
    return -abs(node.outside_area.z * heatflux_per_m2)


def _constant_MW_per_m2(node: Node, params: dict) -> float:
    """Heat input per square meter as a constant value throughout the grid.

    Required params:
    constant  (numeric)
    """
    return -abs(node.outside_area.z * params['constant'])
