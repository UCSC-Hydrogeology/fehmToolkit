from decimal import Decimal
import math

import numpy as np

from ..config import ModelConfig
from .generic import get_generic_model
from .porosity import get_porosity_model


def get_compressibility_models_by_kind() -> dict:
    return {
        'overburden': Overburden(),
    }


class Overburden:
    def __init__(self):
        self.model_config_by_property_kind = None
        self.params = None
        self.porosity_model = None
        self.rho_wet_bulk_column = None

    def __call__(
        self,
        depth: Decimal,
        model_config_by_property_kind: dict[str, ModelConfig],
        property_kind: str,
    ) -> Decimal:
        if (
            self.model_config_by_property_kind is None
            or self.model_config_by_property_kind != model_config_by_property_kind
            or depth > len(self.rho_wet_bulk_column)
        ):
            self._precompute(model_config_by_property_kind, depth=depth if depth >= 1000 else 1000)

        return self._model(depth=depth)

    def _precompute(self, model_config_by_property_kind: dict[str, ModelConfig], depth: Decimal):
        self.model_config_by_property_kind = model_config_by_property_kind
        self.params = self.model_config_by_property_kind['compressibility'].params
        self.porosity_model = get_porosity_model(self.model_config_by_property_kind['porosity'].kind)
        grain_density_model = get_generic_model(  # no grain_density-specific models exist currently, using generic
            model_kind=self.model_config_by_property_kind['grain_density'].kind
        )
        depth_column_1m_spacing = list(range(math.floor(depth) + 1)) if depth else [0]
        porosity_column = np.array([
            self.porosity_model(d, self.model_config_by_property_kind, 'porosity')
            for d in depth_column_1m_spacing
        ])
        grain_density_column = np.array([
            grain_density_model(depth, self.model_config_by_property_kind, 'grain_density')
            for d in depth_column_1m_spacing
        ])
        self.rho_wet_bulk_column = (1 - porosity_column) * grain_density_column + porosity_column * self.params['rhow']

    def _model(self, depth: Decimal) -> Decimal:
        """Compressibility as a function of depth based on an overburden calculation:
        0.435 * A * (1 - p) / b
        where A is a constant and overburden b is calculated as described below. Porosity p is calculated separately
        with its own property model.

        Overburden b is calculated by summing up a column at a 1 meter interval as:
        G * sum(g * (1 - p) + W * p - W) or B, whichever is higher
        where G, W, and B are constants; G is the acceleration of gravity, W is the density of water, and B is the
        minimum allowed overburden. Grain density g is calculated separately with its own property model.

        Required params:
        a               [A]  (numeric)
        grav            [G]  (numeric)
        rhow            [W]  (numeric)
        min_overburden  [B]  (numeric)
        """
        a, grav, rhow, min_overburden = (
            self.params['a'], self.params['grav'], self.params['rhow'], self.params['min_overburden']
        )
        porosity = self.porosity_model(depth, self.model_config_by_property_kind, 'porosity')
        rho_wet_bulk_column_to_depth = self.rho_wet_bulk_column[:math.ceil(depth) + 1]

        overburden = max(grav * sum(rho_wet_bulk_column_to_depth - rhow), min_overburden)
        return Decimal('0.435') * a * (1 - porosity) / overburden
