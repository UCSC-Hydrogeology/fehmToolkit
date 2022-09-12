import math

import numpy as np

from ..config import ModelConfig
from .generic import get_generic_model
from .porosity import get_porosity_model


def get_compressibility_models_by_kind() -> dict:
    return {
        'overburden': _overburden,
    }


def _overburden(depth: float, model_config_by_property_kind: dict[str, ModelConfig], property_kind: str) -> float:
    """Compressibility as a function of depth based on an overburden calculation:
    0.435 * A * (1 - p) / b
    where A is a constant and overburden b is calculated as described below. Porosity p is calculated separately with
    its own property model.

    Overburden b is calculated by summing up a column at a 1 meter interval as:
    G * sum(g * (1 - p) + W * p - W) or B, whichever is higher
    where G, W, and B are constants; G is the acceleration of gravity, W is the density of water, and B is the minimum
    allowed overburden. Grain density g is calculated separately with its own property model.
    """
    params = model_config_by_property_kind[property_kind].params
    porosity_model = get_porosity_model(model_config_by_property_kind['porosity'].kind)
    grain_density_model = get_generic_model(  # no grain_density-specific models exist at time of writing, using generic
        model_kind=model_config_by_property_kind['grain_density'].kind
    )

    depth_column_1m_spacing = list(range(math.floor(depth) + 1)) if depth else [0]
    porosity_column = np.array([
        porosity_model(d, model_config_by_property_kind, 'porosity') for d in depth_column_1m_spacing
    ])
    grain_density_column = np.array([
        grain_density_model(depth, model_config_by_property_kind, 'grain_density') for d in depth_column_1m_spacing
    ])
    rho_wet_bulk_column = (1 - porosity_column) * grain_density_column + porosity_column * params['rhow']
    overburden = max(params['grav'] * sum(rho_wet_bulk_column - params['rhow']), params['min_overburden'])
    porosity = porosity_model(depth, model_config_by_property_kind, 'porosity')
    return 0.435 * params['a'] * (1 - porosity) / overburden
