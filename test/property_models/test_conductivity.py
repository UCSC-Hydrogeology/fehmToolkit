import pytest

from fehmtk.fehm_objects import Vector
from fehmtk.config import ModelConfig
from fehmtk.property_models.conductivity import constant_anisotropic, porosity_weighted, porosity_weighted_anisotropic


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
        model_config_by_property_kind={'conductivity': ModelConfig('constant_anisotropic', params)},
        property_kind='conductivity',
    )
    assert value == expected


@pytest.mark.parametrize(
    'depth, params, expected',
    (
        (
            0,
            {'water_conductivity': 2.05, 'rock_conductivity': 0.62},
            Vector(x=0.6987597916377928, y=0.6987597916377928, z=0.6987597916377928),
        ),
        (
            20,
            {'water_conductivity': 2.05, 'rock_conductivity': 0.62},
            Vector(x=0.6987597916377928, y=0.6987597916377928, z=0.6987597916377928),
        ),
        (
            20,
            {'water_conductivity': 2.05, 'rock_conductivity': 1},
            Vector(x=1.0744232213528402, y=1.0744232213528402, z=1.0744232213528402),
        ),
    ),
)
def test_porosity_weighted(depth, params, expected):
    value = porosity_weighted(
        depth,
        model_config_by_property_kind={
            'conductivity': ModelConfig('porosity_weighted', params),
            'porosity': ModelConfig('constant', {'constant': 0.1})
        },
        property_kind='conductivity',
    )
    assert value == expected


@pytest.mark.parametrize(
    'depth, params, expected',
    (
        (
            0,
            {'water_conductivity': 2.05, 'rock_conductivity': 0.62, 'x_scale': 2, 'y_scale': 1, 'z_scale': 0.5},
            Vector(x=1.3975195832755856, y=0.6987597916377928, z=0.3493798958188964),
        ),
        (
            20,
            {'water_conductivity': 2.05, 'rock_conductivity': 0.62, 'x_scale': 2, 'y_scale': 1, 'z_scale': 0.5},
            Vector(x=1.3975195832755856, y=0.6987597916377928, z=0.3493798958188964),
        ),
        (
            20,
            {'water_conductivity': 2.05, 'rock_conductivity': 1, 'x_scale': 2, 'y_scale': 1, 'z_scale': 0.5},
            Vector(x=2.1488464427056804, y=1.0744232213528402, z=0.5372116106764201),
        ),
    ),
)
def test_porosity_weighted_anisotropic(depth, params, expected):
    value = porosity_weighted_anisotropic(
        depth,
        model_config_by_property_kind={
            'conductivity': ModelConfig('porosity_weighted_anisotropic', params),
            'porosity': ModelConfig('constant', {'constant': 0.1})
        },
        property_kind='conductivity',
    )
    assert value == expected
