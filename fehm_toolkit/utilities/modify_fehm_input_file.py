from pathlib import Path
import re
from typing import Optional


def write_modified_fehm_input_file(
    base_control_file: Path,
    out_file: Path,
    initial_timestep_days: float = None,
    initial_simulation_time_days: float = None,
    file_mapping: Optional[dict[str, str]] = None,
) -> str:
    """Write a control file (.dat) from the (modified) contents of another control file."""
    control_content = base_control_file.read_text()
    if file_mapping:
        control_content = _replace_mapped_files(control_content, file_mapping)

    if initial_timestep_days is not None or initial_simulation_time_days is not None:
        control_content = _replace_timing(
            control_content,
            initial_timestep_days=initial_timestep_days,
            initial_simulation_time_days=initial_simulation_time_days,
        )

    out_file.write_text(control_content)


def _replace_mapped_files(content: str, file_mapping: dict[str, str]) -> str:
    for initial_file, replace_file in file_mapping.items():
        content = re.sub(
            pattern=rf'(\s){initial_file}(\s)',
            repl=lambda match: rf'{match.group(1)}{replace_file}{match.group(2)}',
            string=content,
        )
    return content


def _replace_timing(
    content: str,
    *,
    initial_timestep_days: Optional[float],
    initial_simulation_time_days: Optional[float],
):

    def _timing_string(match: re.Match):
        time_args = match.group(1).strip().split()
        if len(time_args) != 7:
            raise ValueError(f'Unexpected number of arguments for "time" control statement ({len(time_args)})')
        if initial_timestep_days is not None:
            time_args[0] = str(initial_timestep_days)
        if initial_simulation_time_days is not None:
            time_args[6] = str(initial_simulation_time_days)
        return 'time\n  ' + ' '.join(time_args) + '\n'

    return re.sub(
        pattern=r'time\n(.*)\n',
        repl=_timing_string,
        string=content,
    )
