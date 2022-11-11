import dataclasses
from pathlib import Path
from typing import Optional

import yaml

from .boundary_config import FlowConfig, HeatFluxConfig
from .files_config import FilesConfig
from .hydrostat_config import HydrostatConfig
from .rock_properties_config import RockPropertiesConfig


@dataclasses.dataclass
class RunConfig:
    """Configuration defining a run and its components."""
    files_config: FilesConfig
    rock_properties_config: RockPropertiesConfig
    command_defaults: Optional[dict] = None
    heat_flux_config: Optional[HeatFluxConfig] = None
    flow_config: Optional[FlowConfig] = None
    hydrostat_config: Optional[HydrostatConfig] = None

    @classmethod
    def from_dict(cls, dct: dict, files_relative_to: Optional[Path] = None):
        return cls(
            files_config=FilesConfig.from_dict(dct['files_config'], files_relative_to),
            rock_properties_config=RockPropertiesConfig.from_dict(dct['rock_properties_config']),
            command_defaults=dct.get('command_defaults'),
            heat_flux_config=(
                HeatFluxConfig.from_dict(dct['heat_flux_config']) if dct.get('heat_flux_config') else None
            ),
            flow_config=FlowConfig.from_dict(dct['flow_config']) if dct.get('flow_config') else None,
            hydrostat_config=(
                HydrostatConfig.from_dict(dct['hydrostat_config']) if dct.get('hydrostat_config') else None
            ),
        )

    @classmethod
    def from_yaml(cls, config_file: Path):
        with open(config_file) as f:
            raw_config = yaml.load(f, Loader=yaml.Loader)
        return cls.from_dict(raw_config, files_relative_to=config_file)

    def to_yaml(self, config_file: Path):
        files_config_relative_to_output = self.files_config.relative_to(config_file.parent)

        run_config_dict = dataclasses.asdict(self, dict_factory=lambda x: {k: v for (k, v) in x if v is not None})
        run_config_dict['files_config'] = {
            k: str(v) for k, v in dataclasses.asdict(files_config_relative_to_output).items() if v is not None
        }
        with open(config_file, 'w') as f:
            yaml.dump(run_config_dict, f, Dumper=yaml.Dumper)
