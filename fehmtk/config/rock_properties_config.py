from collections import defaultdict
from dataclasses import dataclass
from typing import Union

from .model_config import ModelConfig


@dataclass
class PropertyConfig:
    property_model: ModelConfig
    zones: list[Union[int, str]]

    @classmethod
    def from_dict(cls, dct):
        return cls(
            property_model=ModelConfig.from_dict(dct['property_model']),
            zones=dct['zones'],
        )


@dataclass
class RockPropertiesConfig:
    zone_assignment_order: list[Union[int, str]]
    compressibility_configs: list[PropertyConfig]
    conductivity_configs: list[PropertyConfig]
    permeability_configs: list[PropertyConfig]
    grain_density_configs: list[PropertyConfig]
    specific_heat_configs: list[PropertyConfig]
    porosity_configs: list[PropertyConfig]

    def create_model_lookup_by_zone_and_property(self):
        lookup = defaultdict(dict)
        for property_kind, property_configs in (
            ('compressibility', self.compressibility_configs),
            ('conductivity', self.conductivity_configs),
            ('permeability', self.permeability_configs),
            ('grain_density', self.grain_density_configs),
            ('specific_heat', self.specific_heat_configs),
            ('porosity', self.porosity_configs),
        ):
            for config in property_configs:
                for zone in config.zones:
                    lookup[zone][property_kind] = config.property_model
        return lookup

    @classmethod
    def from_dict(cls, dct):
        return cls(
            zone_assignment_order=dct['zone_assignment_order'],
            compressibility_configs=[PropertyConfig.from_dict(c) for c in dct['compressibility_configs']],
            conductivity_configs=[PropertyConfig.from_dict(c) for c in dct['conductivity_configs']],
            permeability_configs=[PropertyConfig.from_dict(c) for c in dct['permeability_configs']],
            grain_density_configs=[PropertyConfig.from_dict(c) for c in dct['grain_density_configs']],
            specific_heat_configs=[PropertyConfig.from_dict(c) for c in dct['specific_heat_configs']],
            porosity_configs=[PropertyConfig.from_dict(c) for c in dct['porosity_configs']],
        )
