from decimal import Decimal

import pytest

from fehmtk.config import ModelConfig
from fehmtk.property_models.compressibility import Overburden


@pytest.mark.parametrize(
    'depth, params, expected',
    (
        (
            0,
            {
                'a': Decimal('0.09'),
                'grav': Decimal('9.81'),
                'rhow': Decimal('1000.0'),
                'min_overburden': Decimal('25.0'),
            },
            Decimal('0.000002347544522396114409066378845'),
        ),
        (
            20,
            {
                'a': Decimal('0.09'),
                'grav': Decimal('9.81'),
                'rhow': Decimal('1000.0'),
                'min_overburden': Decimal('25.0'),
            },
            Decimal('1.117878343998149718603037545E-7'),
        ),
        (
            20,
            {
                'a': Decimal('0.09'),
                'grav': Decimal('2.5'),
                'rhow': Decimal('800.0'),
                'min_overburden': Decimal('25.0'),
            },
            Decimal('3.924812030075187969924812030E-7'),
        ),
    ),
)
def test_overburden(depth, params, expected):
    overburden = Overburden()
    value = overburden(
        depth,
        model_config_by_property_kind={
            'compressibility': ModelConfig('overburden', params),
            'porosity': ModelConfig('constant', {'constant': Decimal('0.1')}),
            'grain_density': ModelConfig('constant', {'constant': Decimal('2700.0')}),
        },
        property_kind='compressibility',
    )
    assert value == expected
