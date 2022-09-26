from dataclasses import dataclass

from .model_config import ModelConfig


@dataclass
class HeatFluxConfig:
    heat_flux_model: ModelConfig

    @classmethod
    def from_dict(cls, dct):
        return cls(heat_flux_model=ModelConfig.from_dict(dct['heat_flux_model']))
