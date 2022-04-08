from typing import Callable, Union

from ..fehm_objects import Vector


def get_generic_model(model_kind) -> Callable:
    return get_generic_models_by_kind()[model_kind]


def get_generic_models_by_kind() -> dict:
    return {
        'constant': _constant,
    }


def _constant(depth: float, rock_properties_config: dict, property_kind: str) -> Union[float, Vector]:
    params = rock_properties_config[property_kind]['model_params']
    constant = params['constant']

    if property_kind in ('conductivity', 'permeability'):
        return Vector(x=constant, y=constant, z=constant)

    return constant
