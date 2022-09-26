import dataclasses
import os
from pathlib import Path
from typing import Optional


@dataclasses.dataclass
class FilesConfig:
    """Files configuration defining paths for model run."""
    run_root: str
    material_zone: Path
    outside_zone: Path
    area: Path
    rock_properties: Path
    conductivity: Path
    pore_pressure: Path
    permeability: Path
    files: Path
    grid: Path
    input: Path
    output: Path
    store: Path
    history: Path
    water_properties: Path
    check: Path
    error: Path
    final_conditions: Path
    flow: Optional[Path] = None
    heat_flux: Optional[Path] = None
    initial_conditions: Optional[Path] = None

    def __post_init__(self):
        self.validate()

    @classmethod
    def from_dict(cls, dct: dict, files_relative_to: Optional[Path] = None):
        if files_relative_to is None:
            files_relative_to = Path.cwd()
        if not files_relative_to.is_dir():
            files_relative_to = files_relative_to.parent

        return cls(**{
            key: files_relative_to / file_name if key != 'run_root' and file_name is not None else file_name
            for key, file_name in dct.items()
        })

    def relative_to(self, base: Path):
        return FilesConfig(**{
            k: Path(os.path.relpath(v, start=base)) if k != 'run_root' and v is not None else v
            for k, v in dataclasses.asdict(self).items()
        })

    def validate(self):
        seen = set()
        for path in dataclasses.asdict(self).values():
            if path is None:
                continue
            if path in seen:
                raise ValueError(f'Invalid FilesConfig, file duplicated: {path}')
            seen.add(path)

    def assert_specified_paths_exist(self):
        does_not_exist = set()
        for key, path in dataclasses.asdict(self).items():
            if key == 'run_root':
                continue
            if path is not None and not path.exists():
                does_not_exist.add(path)
        if does_not_exist:
            raise AssertionError(
                f'FileConfig contains specified paths that do not exist: {[p.absolute() for p in does_not_exist]}'
            )
