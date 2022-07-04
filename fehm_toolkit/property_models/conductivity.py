from collections import defaultdict
import re
from statistics import mean
from typing import Callable

from ..config import ModelConfig
from ..fehm_objects import Vector
from .porosity import get_porosity_model

TCON_SPACING_M = 1


def get_conductivity_models_by_kind() -> dict:
    return {
        'porosity_weighted': _porosity_weighted,
        'ctr2tcon': _ctr2tcon,
    }


def _porosity_weighted(
    depth: float,
    model_config_by_property_kind: dict[str, ModelConfig],
    property_kind: str,
) -> Vector:
    params = model_config_by_property_kind[property_kind].params
    kw, kg = params['water_conductivity'], params['rock_conductivity']

    porosity_model = get_porosity_model(model_config_by_property_kind['porosity'].kind)
    porosity = porosity_model(depth, model_config_by_property_kind, 'porosity')

    conductivity = (kw ** porosity) * (kg ** (1 - porosity))
    return Vector(x=conductivity, y=conductivity, z=conductivity)


def _ctr2tcon(depth: float, model_config_by_property_kind: dict[str, ModelConfig], property_kind: str) -> Vector:
    params = model_config_by_property_kind[property_kind].params

    tcon_func = _get_tcon_func(params['ctr_model'])
    node_ranges_by_depth = _get_node_ranges_by_depth(params['node_depth_columns'])

    nearest_depth = min(node_ranges_by_depth, key=lambda x: abs(x - depth))
    weight_total = 0
    weighted_tcon_total = 0
    for (lower, upper) in node_ranges_by_depth[nearest_depth]:
        lower, upper = round(lower), round(upper)
        weight_total += upper - lower
        weighted_tcon_total += sum([tcon_func(d) for d in range(lower, upper + 1, TCON_SPACING_M) if d != 0])

    tcon = weighted_tcon_total / weight_total
    return Vector(x=tcon, y=tcon, z=tcon)


def _get_node_ranges_by_depth(node_depth_columns: list[list[float]]) -> dict[float, tuple[float]]:
    node_ranges_by_depth = defaultdict(list)
    for column in node_depth_columns:
        if len(column) < 2:
            raise ValueError(f'Node column is invalid (not enough values): {column}')

        if len(column) == 2:
            node_ranges_by_depth[column[0]].append(tuple(column))
            continue

        first_node_range = (column[0], mean(column[0:2]))
        node_ranges_by_depth[column[0]].append(first_node_range)

        last_node_range = (mean(column[-3:-1]), column[-1])
        node_ranges_by_depth[column[-2]].append(last_node_range)

        for previous_depth, node_depth, next_depth in zip(column[0:-3], column[1:-2], column[2:-1]):
            node_range = (mean([previous_depth, node_depth]), mean([node_depth, next_depth]))
            node_ranges_by_depth[node_depth].append(node_range)

    return node_ranges_by_depth


def _get_tcon_func(ctr_model_config: dict) -> Callable:
    if ctr_model_config['model_kind'] not in ('polynomial'):
        raise NotImplementedError(f"CTR model kind not supported: {ctr_model_config['model_kind']}")

    resistance_terms = []
    for key, coefficient in ctr_model_config['model_params'].items():
        match = re.search(r'x\^(-{0,1}\d+)', key)
        if not match:
            raise KeyError(f"Invalid key in polynomial config: {ctr_model_config['model_params']}")
        resistance_terms.append((coefficient, float(match.group(1))))

    def tcon(depth: float):
        resistance_derivitive_terms = [coeff * power * depth ** (power - 1) for coeff, power in resistance_terms]
        return 1 / sum(resistance_derivitive_terms)

    return tcon
