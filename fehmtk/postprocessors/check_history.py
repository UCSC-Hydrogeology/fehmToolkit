import logging
from pathlib import Path
from typing import Optional

from IPython import embed
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
    interact: bool = False,
):
    logger.info(f'Reading configuration file: {config_file}')
    config = RunConfig.from_yaml(config_file)

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

    plot_history(history, fields, run_root=config.files_config.run_root)
    if interact:
        embed()


def plot_history(history: pd.DataFrame, fields: list[str], run_root=None):
    n_nodes = history.node.nunique()
    marker = 'o' if history.time_days.nunique() < 75 else None
    markersize = 4

    history = history.astype(float)  # Plotting doesn't play nice with Decimal types
    history['node'] = history.node.astype(int).astype(str)  # Remove trailing zeroes, treat as categorical
    history['time_years'] = history.time_days / 365

    sns.set_palette('muted')
    fig, axs = plt.subplots(len(fields), 1, figsize=(6, 2 + len(fields)), constrained_layout=True, sharex=True)
    fig.suptitle(run_root or 'Run history')
    for i, (field, ax) in enumerate(zip(fields, axs)):
        sns.lineplot(
            data=history,
            x='time_years',
            y=field,
            hue='node',
            style='node',
            ax=ax,
            legend=i == 0,
            marker=marker,
            markersize=markersize,
        )
        ax.set_xlabel(r'$t\:(years)$')
        ax.set_ylabel(PLOT_AXES_MAPPING.get(field, field))

    delta_history = history[['node', 'time_years']][n_nodes:]
    delta_history['delta_time_years'] = history.groupby('node').time_years.diff()
    for field in fields:
        delta_history[field] = 1000 * history.groupby('node')[field].diff() / delta_history.delta_time_years

    fig, axs = plt.subplots(len(fields) + 1, 1, figsize=(6, 4 + len(fields)), constrained_layout=True, sharex=True)
    fig.suptitle(run_root or 'Run history')
    for i, (field, ax) in enumerate(zip(fields, axs)):
        sns.lineplot(
            data=delta_history,
            x='time_years',
            y=field,
            hue='node',
            style='node',
            ax=ax,
            legend=i == 0,
            marker=marker,
            markersize=markersize,
        )
        ax.set_ylabel(r'$\Delta\:$' + PLOT_AXES_MAPPING.get(field, field) + r'$/\:kya$')

    sns.lineplot(
        data=delta_history.drop_duplicates(subset=['time_years', 'delta_time_years']),
        x='time_years',
        y='delta_time_years',
        ax=axs[-1],
        legend=False,
        color='grey',
        marker=marker,
        markersize=markersize,
    )
    axs[-1].set_xlabel(r'$t\:(years)$')
    axs[-1].set_ylabel(r'$\Delta\:t\:(years)$')

    plt.show()
