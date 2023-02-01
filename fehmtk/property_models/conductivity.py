from collections import defaultdict
from decimal import Decimal
import re
from statistics import mean
from typing import Callable

from ..common import round_significant_figures
from ..config.model_config import MODEL_PARAMS_SIGNIFICANT_FIGURES, ModelConfig
from ..fehm_objects import Vector
from .generic import constant
from .porosity import get_porosity_model

TCON_SPACING_M = 1


def get_conductivity_models_by_kind() -> dict:
    return {
        'porosity_weighted': porosity_weighted,
        'porosity_weighted_anisotropic': porosity_weighted_anisotropic,
        'constant_anisotropic': constant_anisotropic,
        'ctr2tcon': ctr2tcon,
    }


def porosity_weighted(
    depth: Decimal,
    model_config_by_property_kind: dict[str, ModelConfig],
    property_kind: str,
) -> Vector:
    """Combined conductivity of water and rock, weighted by porosity:
    W^p * R^(1 - p)
    where W and R are constants: water conductivity and rock conductivity, respectively. Porosity p is calculated
    separately with its own property model.

    Required params:
    water_conductivity  [W]  (numeric)
    rock_conductivity   [R]  (numeric)
    """
    params = model_config_by_property_kind[property_kind].params
    kw, kg = params['water_conductivity'], params['rock_conductivity']

    porosity_model = get_porosity_model(model_config_by_property_kind['porosity'].kind)
    porosity = porosity_model(depth, model_config_by_property_kind, 'porosity')

    conductivity = (kw ** porosity) * (kg ** (1 - porosity))
    return Vector(x=conductivity, y=conductivity, z=conductivity)


def porosity_weighted_anisotropic(
    depth: Decimal,
    model_config_by_property_kind: dict[str, ModelConfig],
    property_kind: str,
) -> Vector:
    """Conductivity set by _porosity_weighted function, with anisotropic scaling applied after.
    [x_scale * value, y_scale * value, z_scale * value]

    Required params:
    water_conductivity   (numeric)
    rock_conductivity    (numeric)
    x_scale   (numeric)
    y_scale   (numeric)
    z_scale   (numeric)
    """
    value = porosity_weighted(depth, model_config_by_property_kind, property_kind)
    params = model_config_by_property_kind[property_kind].params
    x_scale, y_scale, z_scale = params['x_scale'], params['y_scale'], params['z_scale']
    return Vector(x=value.x * x_scale, y=value.y * y_scale, z=value.z * z_scale)


def constant_anisotropic(
    depth: Decimal,
    model_config_by_property_kind: dict[str, ModelConfig],
    property_kind: str,
) -> Vector:
    """Property set as a constant value, with anisotropic scaling applied after.
    [x_scale * constant, y_scale * constant, z_scale * constant]

    Required params:
    value     (numeric)
    x_scale   (numeric)
    y_scale   (numeric)
    z_scale   (numeric)
    """
    value = constant(depth, model_config_by_property_kind, property_kind)
    params = model_config_by_property_kind[property_kind].params
    x_scale, y_scale, z_scale = params['x_scale'], params['y_scale'], params['z_scale']
    return Vector(x=value.x * x_scale, y=value.y * y_scale, z=value.z * z_scale)


def ctr2tcon(depth: Decimal, model_config_by_property_kind: dict[str, ModelConfig], property_kind: str) -> Vector:
    """Conductivity calculated by inverting a cumulative thermal resistance profile.

    CTR must be defined with a ctr_model (e.g. polynomial function), and is optimised on the basis of the node depths
    provided. For example, depth arrays of [[0, 50, 100], [0, 80]] will optimize the conductivity for two separate
    columns (one with nodes at 0, 50, and 100, one with nodes at 0, 80).

    This function is DEPRECATED, and has been included for backwards compatibility. It is recommended to specify
    conductivity explicitly instead, performing any necessary calculations separately.

    Required params:
    ctr_model           (model)
    node_depth_columns  (list of list of numbers; [[0, 50, 100], [0, 80]])
    """
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


def _get_node_ranges_by_depth(node_depth_columns: list[list[Decimal]]) -> dict[Decimal, tuple[Decimal]]:
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
        resistance_terms.append((
            round_significant_figures(Decimal(coefficient), MODEL_PARAMS_SIGNIFICANT_FIGURES),
            Decimal(match.group(1))),
        )

    def tcon(depth: Decimal):
        resistance_derivitive_terms = [coeff * power * depth ** (power - 1) for coeff, power in resistance_terms]
        return 1 / sum(resistance_derivitive_terms)

    return tcon
