from dataclasses import dataclass
from typing import Optional, Union

from .model_config import ModelConfig


@dataclass
class FlowConfig:
    boundary_model: ModelConfig
    outside_zones: Optional[list[Union[int, str]]]
    material_zones: Optional[list[Union[int, str]]]

    @classmethod
    def from_dict(cls, dct):
        return cls(
            boundary_model=ModelConfig.from_dict(dct['boundary_model']),
            outside_zones=dct.get('outside_zones', []),
            material_zones=dct.get('material_zones', []),
        )


@dataclass
class BoundariesConfig:
    flow_configs: list[FlowConfig]

    @classmethod
    def from_dict(cls, dct):
        return cls(
            flow_configs=[FlowConfig.from_dict(c) for c in dct['flow_configs']],
        )
