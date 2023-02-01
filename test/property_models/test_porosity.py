from decimal import Decimal

import pytest

from fehmtk.config import ModelConfig
from fehmtk.property_models.porosity import depth_exponential, depth_power_law_with_maximum


@pytest.mark.parametrize(
    'depth, params, expected',
    (
        (
            0,
            {'porosity_a': Decimal('0.84'), 'porosity_b': Decimal('-1.25')},
            Decimal('0.84'),
        ),
        (
            20,
            {'porosity_a': Decimal('0.84'), 'porosity_b': Decimal('-1.25')},
            Decimal('1.166587284656977729951588155E-11'),
        ),
        (
            20,
            {'porosity_a': Decimal('1.0'), 'porosity_b': Decimal('-1.0')},
            Decimal('2.061153622438557827965940380E-9'),
        ),
    ),
)
def test_depth_exponential(depth, params, expected):
    value = depth_exponential(
        depth,
        model_config_by_property_kind={'porosity': ModelConfig('depth_exponential', params)},
        property_kind='porosity',
    )
    assert value == expected


@pytest.mark.parametrize(
    'depth, params, expected',
    (
        (
            0,
            {'porosity_a': Decimal('0.84'), 'porosity_b': Decimal('-1.25')},
            Decimal('0.006317813196385141194449343514'),
        ),
        (
            50,
            {'porosity_a': Decimal('0.84'), 'porosity_b': Decimal('-1.25')},
            Decimal('0.006317813196385141194449343514'),
        ),
        (
            50,
            {'porosity_a': Decimal('1.0'), 'porosity_b': Decimal('-1.0')},
            Decimal('0.020'),
        ),
        (
            500,
            {'porosity_a': Decimal('1.0'), 'porosity_b': Decimal('-1.0')},
            Decimal('0.0020'),
        ),
    ),
)
def test_depth_power_law_with_maximum(depth, params, expected):
    value = depth_power_law_with_maximum(
        depth,
        model_config_by_property_kind={'porosity': ModelConfig('depth_power_law_with_maximum', params)},
        property_kind='porosity',
    )
    assert value == expected
