from typing import Callable, Union

from ..config import ModelConfig
from ..fehm_objects import Vector


def get_generic_model(model_kind) -> Callable:
    return get_generic_models_by_kind()[model_kind]


def get_generic_models_by_kind() -> dict:
    return {
        'constant': _constant,
    }


def _constant(
    depth: float,
    model_config_by_property_kind: dict[str, ModelConfig],
    property_kind: str,
) -> Union[float, Vector]:
    params = model_config_by_property_kind[property_kind].params
    constant = params['constant']

    if property_kind in ('conductivity', 'permeability'):
        return Vector(x=constant, y=constant, z=constant)

    return constant
