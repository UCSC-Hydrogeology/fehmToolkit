import logging
from pathlib import Path
from typing import Optional

from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns

from fehmtk.config import RunConfig
from fehmtk.file_interface import read_history

logger = logging.getLogger(__name__)

PLOT_AXES_MAPPING = {
    'flow enthalpy(Mj/kg)': r'$H\:(\frac{Mj}{kg})$',
    'flow(kg/s)': r'$Q\:(\frac{kg}{s})$',
    'temperature(deg C)': r'$T\:( \degree{C})$',
    'total pressure(Mpa)': r'$P\:(MPa)$',
    'capillary pressure(Mpa)': r'$P_{cap}\:(MPa)$',
    'saturation(kg/kg)': r'$S$',
}


def check_history(
    config_file: Path,
    last_fraction: Optional[float] = None,
    nodes: Optional[list[int]] = None,
    fields: Optional[list[str]] = None,
):
    logger.info(f'Reading configuration file: {config_file}')
    config = RunConfig.from_yaml(config_file)
    if not config.files_config.history:
        raise ValueError(f'No history file defined in {config_file}.')

    history = read_history(
        config.files_config.history,
        last_fraction=last_fraction,
        read_nodes=nodes,
        read_fields=fields,
    )
    if len(history.columns) == 1:
        raise ValueError(f'No node data found in history file {config.files_config.history}')
    if fields is None:
        fields = [field for field in history.columns if field not in ('time_days', 'node')]

    plot_history(history, fields)


def plot_history(history: pd.DataFrame, fields: list[str]):
    n_nodes = history.node.nunique()

    history = history.astype(float)  # Plotting doesn't play nice with Decimal types
    history['node'] = history.node.astype(int).astype(str)  # Remove trailing zeroes, treat as categorical
    history['time_years'] = history.time_days / 365

    sns.set_palette('muted')
    fig, axs = plt.subplots(len(fields), 1, figsize=(6, 2 + len(fields)), constrained_layout=True, sharex=True)
    for i, (field, ax) in enumerate(zip(fields, axs)):
        sns.lineplot(data=history, x='time_years', y=field, hue='node', ax=ax, legend=i == 0)
        ax.set_xlabel(r'$t\:(years)$')
        ax.set_ylabel(PLOT_AXES_MAPPING.get(field, field))

    delta_history = history[['node', 'time_years']][n_nodes:]
    delta_history['delta_time_years'] = history.groupby('node').time_years.diff()
    for field in fields:
        delta_history[field] = history.groupby('node')[field].diff()

    fig, axs = plt.subplots(len(fields) + 1, 1, figsize=(6, 4 + len(fields)), constrained_layout=True, sharex=True)
    for i, (field, ax) in enumerate(zip(fields, axs)):
        sns.lineplot(data=delta_history, x='time_years', y=field, hue='node', ax=ax, legend=i == 0)
        ax.set_ylabel(r'$\Delta\:$' + PLOT_AXES_MAPPING.get(field, field))

    sns.lineplot(data=delta_history, x='time_years', y='delta_time_years', hue='node', ax=axs[-1], legend=False)
    axs[-1].set_xlabel(r'$t\:(years)$')
    axs[-1].set_ylabel(r'$\Delta\:t\:(years)$')

    plt.show()
