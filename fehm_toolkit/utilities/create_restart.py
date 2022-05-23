import dataclasses
from pathlib import Path

from ..fehm_objects import RestartMetadata, State
from ..file_interface import read_avs, read_restart


def create_restart_from_restart(
    base_restart_file: Path,
    reset_model_time: bool = True,
) -> tuple[State, RestartMetadata]:
    state, metadata = read_restart(base_restart_file)

    if reset_model_time:
        metadata = dataclasses.replace(metadata, simulation_time_days=0)

    return state, metadata


def create_restart_from_avs(
    avs_file: Path,
    base_restart_file: Path,
    reset_model_time: bool = True,
) -> tuple[State, RestartMetadata]:
    """Creates a new restart (State, RestartMetadata) from AVS data.

    Pressure and Temperature data come from `avs_file`, while other properties and RestartMetadata are pulled
    from an existing restart file (.ini, .fin).
    """
    base_restart_state, metadata = read_restart(base_restart_file)
    avs_state = read_avs(avs_file)
    combined = _combine_state(avs_state, other=base_restart_state, property_kind_from_other='saturations')

    if reset_model_time:
        metadata = dataclasses.replace(metadata, simulation_time_days=0)

    return combined, metadata


def _combine_state(
    state: State,
    other: State,
    property_kind_from_other: str,
) -> State:
    if property_kind_from_other not in {f.name for f in dataclasses.fields(State)}:
        raise ValueError(f'property_kind {property_kind_from_other} is not supported by State')

    new_values = dataclasses.asdict(other)[property_kind_from_other]
    new_state = dataclasses.replace(state, **{property_kind_from_other: new_values})
    new_state.validate()
    return new_state
