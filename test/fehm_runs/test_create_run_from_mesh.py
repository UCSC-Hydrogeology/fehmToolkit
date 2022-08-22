from fehm_toolkit.config import ModelConfig, RockPropertiesConfig, RunConfig
from fehm_toolkit.fehm_runs.create_run_from_mesh import build_template_from_type


def test_build_template_from_model_config():
    template = build_template_from_type(ModelConfig)
    assert template == {'kind': 'replace__str', 'params': {}}


def test_build_template_from_rock_properties_config():
    template = build_template_from_type(RockPropertiesConfig)
    assert template == {
        'zone_assignment_order': ['replace__int|str'],
        'compressibility_configs': [
            {
                'property_model': {'kind': 'replace__str', 'params': {}},
                'zones': ['replace__int|str']
            },
        ],
        'conductivity_configs': [
            {
                'property_model': {'kind': 'replace__str', 'params': {}},
                'zones': ['replace__int|str']
            },
        ],
        'permeability_configs': [
            {
                'property_model': {'kind': 'replace__str', 'params': {}},
                'zones': ['replace__int|str']
            },
        ],
        'grain_density_configs': [
            {
                'property_model': {'kind': 'replace__str', 'params': {}},
                'zones': ['replace__int|str']
            },
        ],
        'specific_heat_configs': [
            {
                'property_model': {'kind': 'replace__str', 'params': {}},
                'zones': ['replace__int|str']
            },
        ],
        'porosity_configs': [
            {
                'property_model': {'kind': 'replace__str', 'params': {}},
                'zones': ['replace__int|str']
            },
        ],
    }


def test_build_template_from_run_config():
    template = build_template_from_type(RunConfig)
    assert template.keys() == {'files_config', 'heat_flux_config', 'rock_properties_config', 'pressure_config'}
    assert template['heat_flux_config'] == {'heat_flux_model': {'kind': 'replace__str', 'params': {}}}
    for key, value in template['files_config'].items():
        if key == 'run_root':
            assert value == 'replace__str'
        else:
            assert value in ('replace__Path', 'replace__Path|NoneType')
