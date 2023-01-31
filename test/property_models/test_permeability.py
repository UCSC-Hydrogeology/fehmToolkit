from decimal import Decimal

import pytest

from fehmtk.fehm_objects import Vector
from fehmtk.config import ModelConfig
from fehmtk.property_models.permeability import (
    constant_anisotropic,
    void_ratio_exponential,
    void_ratio_exponential_anisotropic,
)


@pytest.mark.parametrize(
    'depth, params, expected',
    (
        (0, {'constant': 5, 'x_scale': 2, 'y_scale': 1, 'z_scale': 0.5}, Vector(10, 5, 2.5)),
        (20, {'constant': 5, 'x_scale': 2, 'y_scale': 1, 'z_scale': 0.5}, Vector(10, 5, 2.5)),
        (20, {'constant': 8, 'x_scale': 2, 'y_scale': 1, 'z_scale': 0.5}, Vector(16, 8, 4)),
    ),
)
def test_constant_anisotropic(depth, params, expected):
    value = constant_anisotropic(
        depth,
        model_config_by_property_kind={'permeability': ModelConfig('constant_anisotropic', params)},
        property_kind='permeability',
    )
    assert value == expected


@pytest.mark.parametrize(
    'depth, params, expected',
    (
        (
            0,
            {'A': Decimal('3.66e-18'), 'B': Decimal('1.68')},
            Vector(
                x=Decimal('4.411125243111942297877447268E-18'),
                y=Decimal('4.411125243111942297877447268E-18'),
                z=Decimal('4.411125243111942297877447268E-18'),
            ),
        ),
        (
            20,
            {'A': Decimal('3.66e-18'), 'B': Decimal('1.68')},
            Vector(
                x=Decimal('4.411125243111942297877447268E-18'),
                y=Decimal('4.411125243111942297877447268E-18'),
                z=Decimal('4.411125243111942297877447268E-18'),
            ),
        ),
        (
            20,
            {'A': Decimal('2e-18'), 'B': Decimal('2')},
            Vector(
                x=Decimal('2.497697738003364341865537980E-18'),
                y=Decimal('2.497697738003364341865537980E-18'),
                z=Decimal('2.497697738003364341865537980E-18'),
            ),
        ),
    ),
)
def test_void_ratio_exponential(depth, params, expected):
    value = void_ratio_exponential(
        depth,
        model_config_by_property_kind={
            'permeability': ModelConfig('void_ratio_exponential', params),
            'porosity': ModelConfig('constant', {'constant': Decimal('0.1')})
        },
        property_kind='permeability',
    )
    assert value == expected


@pytest.mark.parametrize(
    'depth, params, expected',
    (
        (
            0,
            {
                'A': Decimal('3.66e-18'), 'B': Decimal('1.68'),
                'x_scale': Decimal(2), 'y_scale': Decimal(1), 'z_scale': Decimal('0.5'),
            },
            Vector(
                x=Decimal('8.822250486223884595754894536E-18'),
                y=Decimal('4.411125243111942297877447268E-18'),
                z=Decimal('2.205562621555971148938723634E-18'),
            ),
        ),
        (
            20,
            {
                'A': Decimal('3.66e-18'), 'B': Decimal('1.68'),
                'x_scale': Decimal(2), 'y_scale': Decimal(1), 'z_scale': Decimal('0.5'),
            },
            Vector(
                x=Decimal('8.822250486223884595754894536E-18'),
                y=Decimal('4.411125243111942297877447268E-18'),
                z=Decimal('2.205562621555971148938723634E-18'),
            ),
        ),
        (
            20,
            {
                'A': Decimal('2e-18'), 'B': Decimal('2'),
                'x_scale': Decimal(2), 'y_scale': Decimal(1), 'z_scale': Decimal('0.5'),
            },
            Vector(
                x=Decimal('4.995395476006728683731075960E-18'),
                y=Decimal('2.497697738003364341865537980E-18'),
                z=Decimal('1.248848869001682170932768990E-18'),
            ),
        ),
    ),
)
def test_void_ratio_exponential_anisotropic(depth, params, expected):
    value = void_ratio_exponential_anisotropic(
        depth,
        model_config_by_property_kind={
            'permeability': ModelConfig('void_ratio_exponential_anisotropic', params),
            'porosity': ModelConfig('constant', {'constant': Decimal('0.1')})
        },
        property_kind='permeability',
    )
    assert value == expected
