from decimal import Decimal
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
        'depth_exponential': _depth_exponential,
        'depth_power_law_with_maximum': _depth_power_law_with_maximum,
    }


def _depth_exponential(
        depth: Decimal,
        model_config_by_property_kind: dict[str, ModelConfig],
        property_kind: str,
) -> Decimal:
    """Porosity following an exponential function of depth:
    A * e^(B * d)
    where A and B are constants, and d is depth below the seafloor.

    Required params:
    porosity_a  [A]  (numeric)
    porosity_b  [B]  (numeric)
    """
    params = model_config_by_property_kind[property_kind].params
    porosity_a, porosity_b = params['porosity_a'], params['porosity_b']
    return porosity_a * (porosity_b * depth).exp()  # A * e^(B * d)


def _depth_power_law_with_maximum(
    depth: Decimal,
    model_config_by_property_kind: dict[str, ModelConfig],
    property_kind: str,
) -> Decimal:
    """Porosity following a power-law relationship of depth, with a maximum porosity applied:
    A * d^B or A * 50^B, whichever is lower
    where A and B are constants, and d is depth below the seafloor.

    Required params:
    porosity_a  [A]  (numeric)
    porosity_b  [B]  (numeric)
    """
    params = model_config_by_property_kind[property_kind].params
    porosity_a, porosity_b = params['porosity_a'], params['porosity_b']

    max_porosity = porosity_a * 50 ** porosity_b
    if depth == 0:
        return max_porosity

    return min(porosity_a * depth ** porosity_b, max_porosity)
