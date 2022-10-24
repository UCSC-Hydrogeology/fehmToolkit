from decimal import Decimal

import pandas as pd
import pytest

from fehmtk.file_interface.history import read_history, read_history_times


def test_read_history_all(fixture_dir):
    history = read_history(fixture_dir / 'simple_run.hist', last_fraction=1, read_nodes=None, read_fields=None)
    assert len(history) == 1210
    assert history.time_days.nunique() == 605
    assert (history.time_days >= 0).all()
    assert history.loc[history.node == 221, 'time_days'].nunique() == 605
    assert history.loc[history.node == 662, 'time_days'].nunique() == 605
    assert not history.isnull().any().any()
    assert history.head(2).equals(
        pd.DataFrame({
            'time_days': [Decimal('0.0000000000000000'), Decimal('0.0000000000000000')],
            'node': [Decimal('221'), Decimal('662')],
            'flow enthalpy(Mj/kg)': [Decimal('563787.863'), Decimal('0.100000000E-19')],
            'flow(kg/s)': [Decimal('7343991.36'), Decimal('0.00000000')],
            'temperature(deg C)': [Decimal('2.00000005'), Decimal('29.0456162')],
            'total pressure(Mpa)': [Decimal('29.4709090'), Decimal('31.4565923')],
            'capillary pressure(Mpa)': [Decimal('0.00000000'), Decimal('0.00000000')],
            'saturation(kg/kg)': [Decimal('1.00000000'), Decimal('1.00000000')],
        })
    )


def test_read_history_partial(fixture_dir):
    history = read_history(
        fixture_dir / 'simple_run.hist',
        last_fraction=0.2,
        read_nodes=[662],
        read_fields=['temperature(deg C)', 'total pressure(Mpa)'],
    )
    assert len(history) == 121
    assert history.time_days.nunique() == 121
    assert (history.time_days >= 0).all()
    assert (history.node == 662).all()
    assert not history.isnull().any().any()
    assert history.head(2).equals(
        pd.DataFrame({
            'time_days': [Decimal('15614386.324303947'), Decimal('15667626.324303947')],
            'node': [Decimal('662'), Decimal('662')],
            'temperature(deg C)': [Decimal('36.0320759'), Decimal('36.0222481')],
            'total pressure(Mpa)': [Decimal('31.4195226'), Decimal('31.4197168')],
        })
    )


def test_read_history_no_nodes(fixture_dir):
    history = read_history(fixture_dir / 'simple_run_no_nodes.hist', last_fraction=1, read_nodes=None, read_fields=None)
    assert history.columns == 'time_days'
    assert len(history) == 605
    assert history.time_days.nunique() == 605
    assert (history.time_days >= 0).all()


@pytest.mark.parametrize('fixture_name', ('simple_run.hist', 'simple_run_no_nodes.hist'))
def test_read_history_times(fixture_dir, fixture_name):
    times = read_history_times(fixture_dir / fixture_name)
    assert len(times) == 605
    assert times[:5] == (
        Decimal('0.0000000000000000'),
        Decimal('1.00000000000000005E-004'),
        Decimal('2.10000000000000009E-004'),
        Decimal('3.31000000000000023E-004'),
        Decimal('4.64100000000000059E-004'),
    )
    assert times[-5:] == (
        Decimal('35725562.552298293'),
        Decimal('35925562.552298293'),
        Decimal('36125562.552298293'),
        Decimal('36325562.552298293'),
        Decimal('36500000.000000000'),
    )
    for time in times:
        isinstance(time, Decimal)


def test_read_history_times_incomplete(fixture_dir):
    times = read_history_times(fixture_dir / 'simple_run_incomplete.hist')
    assert times == (
        Decimal('0.0000000000000000'),
        Decimal('1.00000000000000005E-004'),
        Decimal('2.10000000000000009E-004'),
        Decimal('3.31000000000000023E-004'),
        Decimal('4.64100000000000059E-004'),
        Decimal('6.10510000000000089E-004'),
        Decimal('7.71561000000000143E-004'),
    )
