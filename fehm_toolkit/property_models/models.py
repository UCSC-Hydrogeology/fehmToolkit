from typing import Callable

from .compressibility import get_compressibility_models_by_kind
from .conductivity import get_conductivity_models_by_kind
from .generic import get_generic_models_by_kind
from .permeability import get_permeability_models_by_kind
from .porosity import get_porosity_models_by_kind


def get_rock_property_model(property_kind, model_kind) -> dict[str, Callable]:

    property_model_lookup = _get_model_lookup_by_property_kind()[property_kind]
    generic_model_lookup = get_generic_models_by_kind()

    try:
        return property_model_lookup[model_kind]
    except KeyError:
        return generic_model_lookup[model_kind]


def _get_model_lookup_by_property_kind() -> dict:
    return {
        'grain_density': {},
        'specific_heat': {},
        'porosity': get_porosity_models_by_kind(),
        'conductivity': get_conductivity_models_by_kind(),
        'permeability': get_permeability_models_by_kind(),
        'compressibility': get_compressibility_models_by_kind(),
    }
