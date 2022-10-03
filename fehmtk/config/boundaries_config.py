from dataclasses import dataclass
from typing import Union

from .model_config import ModelConfig


@dataclass
class FlowConfig:
    boundary_model: ModelConfig
    zones: list[Union[int, str]]

    @classmethod
    def from_dict(cls, dct):
        return cls(
            boundary_model=ModelConfig.from_dict(dct['boundary_model']),
            zones=dct['zones'],
        )


@dataclass
class BoundariesConfig:
    flow_configs: list[FlowConfig]

    @classmethod
    def from_dict(cls, dct):
        return cls(
            flow_configs=[FlowConfig.from_dict(c) for c in dct['flow_configs']],
        )
