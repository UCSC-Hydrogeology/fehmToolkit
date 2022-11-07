from pathlib import Path

from fehmtk.config import ModelConfig, RockPropertiesConfig, RunConfig
from fehmtk.fehm_runs.create_run_from_mesh import build_template_from_type, get_template_files_config


def test_build_template_from_model_config():
    template = build_template_from_type(ModelConfig)
    assert template == {'kind': 'replace__str', 'params': {}}


def test_get_template_files_config():
    template = get_template_files_config(
        file_pairs_by_file_type={
            'material_zone': (Path('mesh/mesh_material.zone'), Path('cond/cond_material.zone')),
            'area': (Path('mesh/mesh.area'), Path('cond/cond.area')),
        },
        run_root=None,
    )
    assert template == dict(
        run_root='run',
        material_zone='cond_material.zone',
        outside_zone='outside_zone.txt',
        area='cond.area',
        rock_properties='rock_properties.txt',
        conductivity='conductivity.txt',
        pore_pressure='pore_pressure.txt',
        permeability='permeability.txt',
        files='fehmn.files',
        grid='grid.txt',
        input='input.txt',
        output='output.txt',
        storage='storage.txt',
        history='history.txt',
        water_properties='water_properties.txt',
        check='check.txt',
        error='error.txt',
        final_conditions='final_conditions.txt',
        flow='flow.txt',
        heat_flux='heat_flux.txt',
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
        run_root='my_run',
        material_zone='my_run_material.zone',
        outside_zone='cond_outside.zone',
        area='my_run.area',
        rock_properties='my_run.rock',
        conductivity='my_run.cond',
        pore_pressure='my_run.ppor',
        permeability='my_run.perm',
        files='fehmn.files',
        grid='cond.fehm',
        input='my_run.dat',
        output='my_run.out',
        storage='my_run.stor',
        history='my_run.hist',
        water_properties='my_run.wpi',
        check='my_run.chk',
        error='my_run.err',
        final_conditions='my_run.fin',
        flow='my_run.flow',
        heat_flux='my_run.hflx',
    )


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
    assert template.keys() == {
        'files_config',
        'heat_flux_config',
        'rock_properties_config',
        'flow_config',
        'pressure_config',
    }
    assert template['heat_flux_config'] == {'heat_flux_model': {'kind': 'replace__str', 'params': {}}}
    for key, value in template['files_config'].items():
        if key == 'run_root':
            assert value == 'replace__str'
        else:
            assert value in ('replace__Path', 'replace__Path|NoneType')
