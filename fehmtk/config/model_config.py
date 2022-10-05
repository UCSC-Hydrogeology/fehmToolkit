from dataclasses import dataclass
from decimal import Decimal

from fehmtk.common import round_significant_figures

MODEL_PARAMS_SIGNIFICANT_FIGURES = 10


@dataclass
class ModelConfig:
    kind: str
    params: dict

    @classmethod
    def from_dict(cls, dct):
        dct = dct.copy()
        for k, p in dct['params'].items():
            if isinstance(p, float):
                dct['params'][k] = round_significant_figures(Decimal(p), n=MODEL_PARAMS_SIGNIFICANT_FIGURES)
        return cls(**dct)
