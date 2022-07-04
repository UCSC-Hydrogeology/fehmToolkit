from dataclasses import dataclass
from typing import Optional

from .model_config import ModelConfig


@dataclass
class PressureConfig:
    pressure_model: ModelConfig
    interpolation_model: ModelConfig
    sampling_model: Optional[ModelConfig] = None

    @classmethod
    def from_dict(cls, dct):
        return cls(
            pressure_model=ModelConfig.from_dict(dct['pressure_model']),
            interpolation_model=ModelConfig.from_dict(dct['interpolation_model']),
            sampling_model=ModelConfig.from_dict(dct['sampling_model']) if dct.get('sampling_model') else None,
        )
