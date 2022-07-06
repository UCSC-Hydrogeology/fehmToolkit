import math
from typing import Callable

from ..config import ModelConfig
from .generic import get_generic_models_by_kind


def get_porosity_model(model_kind: str) -> Callable:
    porosity_models_by_kind = get_porosity_models_by_kind()
    generic_models_by_kind = get_generic_models_by_kind()
    try:
        return porosity_models_by_kind[model_kind]
    except KeyError:
        return generic_models_by_kind[model_kind]


def get_porosity_models_by_kind() -> dict:
    return {
        'depth_power_law': _depth_power_law,
        'depth_exponential_with_maximum': _depth_exponential_with_maximum,
    }


def _depth_power_law(depth: float, model_config_by_property_kind: dict[str, ModelConfig], property_kind: str) -> float:
    params = model_config_by_property_kind[property_kind].params
    porosity_a, porosity_b = params['porosity_a'], params['porosity_b']
    return porosity_a * math.exp(porosity_b * depth)


def _depth_exponential_with_maximum(
    depth: float,
    model_config_by_property_kind: dict[str, ModelConfig],
    property_kind: str,
) -> float:
    params = model_config_by_property_kind[property_kind].params
    porosity_a, porosity_b = params['porosity_a'], params['porosity_b']

    max_porosity = porosity_a * 50 ** porosity_b
    if depth == 0:
        return max_porosity

    return min(porosity_a * depth ** porosity_b, max_porosity)
