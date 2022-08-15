import dataclasses
from pathlib import Path
from typing import Optional

import yaml

from .files_config import FilesConfig
from .heat_flux_config import HeatFluxConfig
from .pressure_config import PressureConfig
from .rock_properties_config import RockPropertiesConfig


@dataclasses.dataclass
class RunConfig:
    """Configuration defining a run and its components."""
    files_config: FilesConfig
    heat_flux_config: HeatFluxConfig
    rock_properties_config: RockPropertiesConfig
    pressure_config: Optional[PressureConfig] = None

    @classmethod
    def from_dict(cls, dct: dict):
        return cls(
            files_config=FilesConfig.from_dict(dct['files_config']),
            heat_flux_config=HeatFluxConfig.from_dict(dct['heat_flux_config']),
            rock_properties_config=RockPropertiesConfig.from_dict(dct['rock_properties_config']),
            pressure_config=PressureConfig.from_dict(dct['pressure_config']) if dct.get('pressure_config') else None,
        )

    @classmethod
    def from_yaml(cls, config_file: Path):
        with open(config_file) as f:
            raw_config = yaml.load(f, Loader=yaml.Loader)
            return cls.from_dict(raw_config)

    def to_yaml(self, config_file: Path):
        run_config_dict = dataclasses.asdict(self)
        run_config_dict['files_config'] = {k: str(v) for k, v in run_config_dict['files_config'].items()}
        with open(config_file, 'w') as f:
            yaml.dump(run_config_dict, f, Dumper=yaml.Dumper)
