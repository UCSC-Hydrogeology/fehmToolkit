import math

import numpy as np

from .generic import get_generic_model
from .porosity import get_porosity_model


def get_compressibility_models_by_kind() -> dict:
    return {
        'overburden': _overburden,
    }


def _overburden(depth: float, rock_properties_config: dict, property_kind: str) -> float:
    params = rock_properties_config[property_kind]['model_params']
    porosity_model = get_porosity_model(rock_properties_config['porosity']['model_kind'])
    grain_density_model = get_generic_model(  # no grain_density-specific models exist at time of writing, using generic
        model_kind=rock_properties_config['grain_density']['model_kind']
    )

    depth_column_1m_spacing = list(range(math.floor(depth) + 1)) if depth else [0]
    porosity_column = np.array([
        porosity_model(d, rock_properties_config, 'porosity') for d in depth_column_1m_spacing
    ])
    grain_density_column = np.array([
        grain_density_model(depth, rock_properties_config, 'grain_density') for d in depth_column_1m_spacing
    ])
    rho_wet_bulk_column = (1 - porosity_column) * grain_density_column + porosity_column * params['rhow']
    overburden = max(params['grav'] * sum(rho_wet_bulk_column - params['rhow']), params['min_overburden'])
    porosity = porosity_model(depth, rock_properties_config, 'porosity')
    return 0.435 * params['a'] * (1 - porosity) / overburden
