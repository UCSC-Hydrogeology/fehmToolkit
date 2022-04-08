import math

from ..fehm_objects import Vector
from .porosity import get_porosity_model


def get_permeability_models_by_kind() -> dict:
    return {
        'void_ratio_power_law': _void_ratio_power_law,
    }


def _void_ratio_power_law(depth: float, rock_properties_config: dict, property_kind: str) -> Vector:
    params = rock_properties_config[property_kind]['model_params']

    porosity_model = get_porosity_model(rock_properties_config['porosity']['model_kind'])
    porosity = porosity_model(depth, rock_properties_config, 'porosity')

    void_ratio = porosity / (1 - porosity)
    permeability = params['A'] * math.exp(params['B'] * void_ratio)
    return Vector(x=permeability, y=permeability, z=permeability)
