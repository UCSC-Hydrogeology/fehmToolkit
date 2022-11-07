from dataclasses import dataclass
from typing import Optional, Union

from .model_config import ModelConfig


@dataclass
class BoundaryConfig:
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
class FlowConfig:
    boundary_configs: list[BoundaryConfig]

    @classmethod
    def from_dict(cls, dct):
        return cls(
            boundary_configs=[BoundaryConfig.from_dict(c) for c in dct['boundary_configs']],
        )


@dataclass
class HeatFluxConfig:
    boundary_configs: list[BoundaryConfig]

    @classmethod
    def from_dict(cls, dct):
        return cls(
            boundary_configs=[BoundaryConfig.from_dict(c) for c in dct['boundary_configs']],
        )
