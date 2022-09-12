import math

from ..config import ModelConfig
from ..fehm_objects import Vector
from .porosity import get_porosity_model


def get_permeability_models_by_kind() -> dict:
    return {
        'void_ratio_exponential': _void_ratio_exponential,
    }


def _void_ratio_exponential(
    depth: float,
    model_config_by_property_kind: dict[str, ModelConfig],
    property_kind: str,
) -> Vector:
    params = model_config_by_property_kind[property_kind].params

    porosity_model = get_porosity_model(model_config_by_property_kind['porosity'].kind)
    porosity = porosity_model(depth, model_config_by_property_kind, 'porosity')

    void_ratio = porosity / (1 - porosity)
    permeability = params['A'] * math.exp(params['B'] * void_ratio)
    return Vector(x=permeability, y=permeability, z=permeability)
