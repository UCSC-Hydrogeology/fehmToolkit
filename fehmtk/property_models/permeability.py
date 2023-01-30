from decimal import Decimal

from ..config import ModelConfig
from ..fehm_objects import Vector
from .generic import _constant
from .porosity import get_porosity_model

#TODO: write tests for these functions
def get_permeability_models_by_kind() -> dict:
    return {
        'void_ratio_exponential': _void_ratio_exponential,
        'void_ratio_exponential_anisotropic': _void_ratio_exponential_anisotropic,
        'constant_anisotropic': _constant_anisotropic,
    }


def _void_ratio_exponential(
    depth: Decimal,
    model_config_by_property_kind: dict[str, ModelConfig],
    property_kind: str,
) -> Vector:
    """Permeability following an exponential function of void ratio:
    A * e^(B * v)
    where A and B are constants, and v is the void ratio (p / (1 - p)). Porosity p is calculated separately with its
    own property model.

    Required params:
    A  (numeric)
    B  (numeric)
    """
    params = model_config_by_property_kind[property_kind].params

    porosity_model = get_porosity_model(model_config_by_property_kind['porosity'].kind)
    porosity = porosity_model(depth, model_config_by_property_kind, 'porosity')

    void_ratio = porosity / (1 - porosity)
    permeability = params['A'] * (params['B'] * void_ratio).exp()  # A * e^(B * v)
    return Vector(x=permeability, y=permeability, z=permeability)


def _void_ratio_exponential_anisotropic(
    depth: Decimal,
    model_config_by_property_kind: dict[str, ModelConfig],
    property_kind: str,
) -> Vector:
    """Permeability set by _void_ratio_exponential function, with anisotropic scaling applied after.
    [x_scale * value, y_scale * value, z_scale * value]

    Required params:
    A         (numeric)
    B         (numeric)
    x_scale   (numeric)
    y_scale   (numeric)
    z_scale   (numeric)
    """
    value = _void_ratio_exponential(depth, model_config_by_property_kind, property_kind)
    params = model_config_by_property_kind[property_kind].params
    x_scale, y_scale, z_scale = params['x_scale'], params['y_scale'], params['z_scale']
    return Vector(x=value.x * x_scale, y=value.y * y_scale, z=value.z * z_scale)


def _constant_anisotropic(
    depth: Decimal,
    model_config_by_property_kind: dict[str, ModelConfig],
    property_kind: str,
) -> Vector:
    """Property set as a constant value, with anisotropic scaling applied after.
    [x_scale * constant, y_scale * constant, z_scale * constant]

    Required params:
    constant  (numeric)
    x_scale   (numeric)
    y_scale   (numeric)
    z_scale   (numeric)
    """
    constant = _constant(depth, model_config_by_property_kind, property_kind)
    params = model_config_by_property_kind[property_kind].params
    x_scale, y_scale, z_scale = params['x_scale'], params['y_scale'], params['z_scale']
    return Vector(x=constant.x * x_scale, y=constant.y * y_scale, z=constant.z * z_scale)
