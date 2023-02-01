from decimal import Decimal
from typing import Callable, Union

from ..config import ModelConfig
from ..fehm_objects import Vector


def get_generic_model(model_kind) -> Callable:
    return get_generic_models_by_kind()[model_kind]


def get_generic_models_by_kind() -> dict:
    return {
        'constant': constant,
    }


def constant(
    depth: Decimal,
    model_config_by_property_kind: dict[str, ModelConfig],
    property_kind: str,
) -> Union[Decimal, Vector]:
    """Property set as a constant value. If the property is Vector valued, it is also isotropic.

    Required params:
    constant  (numeric)
    """
    params = model_config_by_property_kind[property_kind].params
    constant = params['constant']

    if property_kind in ('conductivity', 'permeability'):
        return Vector(x=constant, y=constant, z=constant)

    return constant
