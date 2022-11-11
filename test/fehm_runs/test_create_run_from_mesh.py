from pathlib import Path

from fehmtk.config import ModelConfig, RockPropertiesConfig, RunConfig
from fehmtk.fehm_runs.create_run_from_mesh import build_template_from_type, get_template_files_config


def test_build_template_from_model_config():
    (template, optional) = build_template_from_type(ModelConfig)
    assert optional is False
    assert template == {'REQUIRED__kind': 'TYPE__str', 'REQUIRED__params': {}}


def test_get_template_files_config():
    template = get_template_files_config(
        file_pairs_by_file_type={
            'material_zone': (Path('mesh/mesh_material.zone'), Path('cond/cond_material.zone')),
            'area': (Path('mesh/mesh.area'), Path('cond/cond.area')),
        },
        run_root=None,
    )
    assert template == dict(
        REQUIRED__run_root='run',
        REQUIRED__material_zone='cond_material.zone',
        REQUIRED__outside_zone='outside_zone.txt',
        REQUIRED__area='cond.area',
        REQUIRED__rock_properties='rock_properties.txt',
        REQUIRED__conductivity='conductivity.txt',
        REQUIRED__pore_pressure='pore_pressure.txt',
        REQUIRED__permeability='permeability.txt',
        REQUIRED__files='fehmn.files',
        REQUIRED__grid='grid.txt',
        REQUIRED__input='input.txt',
        REQUIRED__output='output.txt',
        REQUIRED__storage='storage.txt',
        REQUIRED__history='history.txt',
        REQUIRED__water_properties='water_properties.txt',
        REQUIRED__check='check.txt',
        REQUIRED__error='error.txt',
        REQUIRED__final_conditions='final_conditions.txt',
        OPTIONAL__initial_conditions='TYPE__Path',
        OPTIONAL__flow='TYPE__Path',
        OPTIONAL__heat_flux='TYPE__Path',
    )


def test_get_template_files_config_run_root():
    template = get_template_files_config(
        file_pairs_by_file_type={
            'outside_zone': (Path('mesh/mesh_outside.zone'), Path('cond/cond_outside.zone')),
            'grid': (Path('mesh/mesh.fehmn'), Path('cond/cond.fehm')),
        },
        run_root='my_run',
    )
    assert template == dict(
        REQUIRED__run_root='my_run',
        REQUIRED__material_zone='my_run_material.zone',
        REQUIRED__outside_zone='cond_outside.zone',
        REQUIRED__area='my_run.area',
        REQUIRED__rock_properties='my_run.rock',
        REQUIRED__conductivity='my_run.cond',
        REQUIRED__pore_pressure='my_run.ppor',
        REQUIRED__permeability='my_run.perm',
        REQUIRED__files='fehmn.files',
        REQUIRED__grid='cond.fehm',
        REQUIRED__input='my_run.dat',
        REQUIRED__output='my_run.out',
        REQUIRED__storage='my_run.stor',
        REQUIRED__history='my_run.hist',
        REQUIRED__water_properties='my_run.wpi',
        REQUIRED__check='my_run.chk',
        REQUIRED__error='my_run.err',
        REQUIRED__final_conditions='my_run.fin',
        OPTIONAL__initial_conditions='TYPE__Path',
        OPTIONAL__flow='TYPE__Path',
        OPTIONAL__heat_flux='TYPE__Path',
    )


def test_build_template_from_rock_properties_config():
    template, optional = build_template_from_type(RockPropertiesConfig)
    assert optional is False
    assert template == {
        'REQUIRED__zone_assignment_order': ['TYPE__str|int'],
        'REQUIRED__compressibility_configs': [
            {
                'REQUIRED__property_model': {'REQUIRED__kind': 'TYPE__str', 'REQUIRED__params': {}},
                'REQUIRED__zones': ['TYPE__str|int']
            },
        ],
        'REQUIRED__conductivity_configs': [
            {
                'REQUIRED__property_model': {'REQUIRED__kind': 'TYPE__str', 'REQUIRED__params': {}},
                'REQUIRED__zones': ['TYPE__str|int']
            },
        ],
        'REQUIRED__permeability_configs': [
            {
                'REQUIRED__property_model': {'REQUIRED__kind': 'TYPE__str', 'REQUIRED__params': {}},
                'REQUIRED__zones': ['TYPE__str|int']
            },
        ],
        'REQUIRED__grain_density_configs': [
            {
                'REQUIRED__property_model': {'REQUIRED__kind': 'TYPE__str', 'REQUIRED__params': {}},
                'REQUIRED__zones': ['TYPE__str|int']
            },
        ],
        'REQUIRED__specific_heat_configs': [
            {
                'REQUIRED__property_model': {'REQUIRED__kind': 'TYPE__str', 'REQUIRED__params': {}},
                'REQUIRED__zones': ['TYPE__str|int']
            },
        ],
        'REQUIRED__porosity_configs': [
            {
                'REQUIRED__property_model': {'REQUIRED__kind': 'TYPE__str', 'REQUIRED__params': {}},
                'REQUIRED__zones': ['TYPE__str|int']
            },
        ],
    }


def test_build_template_from_run_config():
    (template, optional) = build_template_from_type(RunConfig)
    assert optional is False
    assert template.keys() == {
        'OPTIONAL__command_defaults',
        'REQUIRED__files_config',
        'OPTIONAL__heat_flux_config',
        'REQUIRED__rock_properties_config',
        'OPTIONAL__flow_config',
        'OPTIONAL__hydrostat_config',
    }
    assert template['OPTIONAL__heat_flux_config'] == {
        'REQUIRED__boundary_configs': [
            {
                'REQUIRED__boundary_model': {'REQUIRED__kind': 'TYPE__str', 'REQUIRED__params': {}},
                'OPTIONAL__material_zones': ['TYPE__str|int'],
                'OPTIONAL__outside_zones': ['TYPE__str|int'],
            },
        ],
    }
    for key, value in template['REQUIRED__files_config'].items():
        if key == 'REQUIRED__run_root':
            assert value == 'TYPE__str'
        else:
            assert value == 'TYPE__Path'
