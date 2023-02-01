from decimal import Decimal

import pytest

from fehmtk.fehm_objects import Element, RestartMetadata, State, Vector, Zone
from fehmtk.file_interface import (
    read_avs,
    read_fehm,
    read_nist_lookup_table,
    read_pressure,
    read_restart,
    read_volume_from_storage,
    read_zones,
)


def test_read_fehm_pyramid(fixture_dir):
    coordinates_by_number, elements_by_number = read_fehm(fixture_dir / 'simple_pyramid.fehm')
    assert coordinates_by_number and elements_by_number

    for node_number, coordinates in coordinates_by_number.items():
        assert isinstance(node_number, int)
        assert isinstance(coordinates, Vector)
        for coor in coordinates.value:
            assert isinstance(coor, Decimal)

    for element_number, element in elements_by_number.items():
        assert isinstance(element_number, int)
        assert isinstance(element, Element)
        for node_number in element.nodes:
            assert node_number in coordinates_by_number
            assert len(element.nodes) == element.connectivity


def test_read_outside_zone_pyramid(fixture_dir):
    outside_zones = read_zones(fixture_dir / 'simple_pyramid_outside.zone')
    assert outside_zones == (
        Zone(number=1, name='top', data=(1, 2, 3, 4, 5)),
        Zone(number=2, name='bottom', data=(1, 2, 3, 4)),
        Zone(number=3, name='left_w', data=(1, 4, 5)),
        Zone(number=5, name='right_e', data=(2, 3, 5)),
        Zone(number=6, name='back_n', data=(3, 4, 5)),
        Zone(number=4, name='front_s', data=(1, 2, 5)),
    )


def test_read_material_zone_pyramid(fixture_dir):
    material_zones = read_zones(fixture_dir / 'simple_pyramid_material.zone')
    assert material_zones == (
        Zone(number=1, name=None, data=(5,)),
        Zone(number=2, name=None, data=(1, 2, 3, 4)),
    )


def test_read_area_pyramid(fixture_dir):
    area_zones = read_zones(fixture_dir / 'simple_pyramid.area')
    assert area_zones == (
        Zone(
            number=1,
            name='top',
            data=(
                Vector(-30.0, -30.0, -15.0),
                Vector(30.0, -30.0, -15.0),
                Vector(30.0, 30.0, -15.0),
                Vector(-30.0, 30.0, -15.0),
                Vector(0.0, 0.0, 40.0),
            ),
        ),
        Zone(
            number=2,
            name='bottom',
            data=(
                Vector(-30.0, -30.0, -15.0),
                Vector(30.0, -30.0, -15.0),
                Vector(30.0, 30.0, -15.0),
                Vector(-30.0, 30.0, -15.0),
            ),
        ),
        Zone(
            number=3,
            name='left_w',
            data=(Vector(-30.0, -30.0, -15.0), Vector(-30.0, 30.0, -15.0), Vector(0.0, 0.0, 40.0)),
        ),
        Zone(
            number=5,
            name='right_e',
            data=(Vector(30.0, -30.0, -15.0), Vector(30.0, 30.0, -15.0), Vector(0.0, 0.0, 40.0)),
        ),
        Zone(
            number=6,
            name='back_n',
            data=(Vector(30.0, 30.0, -15.0), Vector(-30.0, 30.0, -15.0), Vector(0.0, 0.0, 40.0)),
        ),
        Zone(
            number=4,
            name='front_s',
            data=(Vector(-30.0, -30.0, -15.0), Vector(30.0, -30.0, -15.0), Vector(0.0, 0.0, 40.0)),
        ),
    )


def test_read_simple_restart_legacy_format(fixture_dir):
    state, metadata = read_restart(fixture_dir / 'simple_restart_legacy_format.ini')
    assert metadata == RestartMetadata(
        runtime_header='FEHM V3.1gf 12-02-29 QA:NA       09/23/2018    02:31:14',
        model_description='"Simple restart description"',
        simulation_time_days=0,
        n_nodes=6,
        dual_porosity_permeability_keyword='nddp',
    )
    assert state == State(
        temperature=[
            Decimal(v) for v in (
                '35.3103156449', '26.3715674828', '26.6993730893', '13.7232584411', '13.4748018922', '9.9921394765',
            )
        ],
        saturation=[
            Decimal(v) for v in (
                '1.0000000000', '1.0000000000', '1.0000000000', '1.0000000000', '1.0000000000', '1.0000000000',
            )
        ],
        pressure=[
            Decimal(v) for v in (
                '46.1720206040', '45.6706062299', '45.6811178622', '45.4069398347', '45.3847810418', '45.1548391299',
            )
        ],
    )


def test_read_simple_restart_fehm_format(fixture_dir):
    state, metadata = read_restart(fixture_dir / 'simple_restart_fehm_format.fin')
    assert metadata == RestartMetadata(
        runtime_header='FEHM V3.1gf 12-02-29 QA:NA       02/27/2015    13:16:15',
        model_description='"Simple restart, FEHM formatted"',
        simulation_time_days=Decimal('99953355.443100005'),
        n_nodes=8,
        dual_porosity_permeability_keyword='nddp',
    )
    assert state == State(
        temperature=[
            Decimal(v) for v in (
                '9.482060132451755', '14.20269570985147', '8.414855364338784', '69.80068704764734',
                '86.91250913933038', '85.88408430521636', '69.38671894047677', '68.56111995201577',
            )
        ],
        saturation=8 * [Decimal('1.000000000000000')],
        pressure=[
            Decimal(v) for v in (
                '33.69520926926931', '33.69378317097816', '31.45654762003292', '36.15766656073081',
                '37.61776959952319', '37.61945828718319', '36.15826817848320', '34.69600450690525',
            )
        ],
    )


def test_read_porosity_restart(fixture_dir):
    state, metadata = read_restart(fixture_dir / 'simple_restart_with_porosity.fin')
    assert metadata == RestartMetadata(
        runtime_header='FEHM V3.4.0macMojave 19-09-12    01/28/2023    10:46:20',
        model_description='"Conductive run - 10km box model of a section of crust"',
        simulation_time_days=36500000000,
        n_nodes=12,
        dual_porosity_permeability_keyword='nddp',
        unsupported_blocks=False,
    )
    assert state == State(
        temperature=[
            Decimal(v) for v in (
                '2.000000012398605', '2.000000024793144', '2.000000024781631', '2.000000024763683',
                '2.000000024740088', '2.000000024711498', '2.000000024678946', '2.000000024643460',
                '2.000000024605882', '2.000000024566908', '2.000000024527291', '2.000000024487809',
            )
        ],
        saturation=12 * [Decimal('1.000000000000000')],
        pressure=12 * [Decimal('25.00000000000000')],
        porosity=12 * [Decimal('0.5151200000000000')],
    )


def test_read_tracer_restart(fixture_dir):
    state, metadata = read_restart(fixture_dir / 'tracer_restart.fin')
    assert metadata == RestartMetadata(
        runtime_header='FEHM V3.1gf 12-02-09 QA:NA       02/09/2012    11:48:27',
        model_description='Unsaturated Diffusion tests',
        simulation_time_days=5000,
        n_nodes=12,
        dual_porosity_permeability_keyword='nddp',
        unsupported_blocks=True,
    )
    assert state == State(
        temperature=[
            Decimal(v) for v in (
                '34.99999999987494', '34.99999999987494', '29.99740954219060', '29.99740954219060',
                '24.99481908388880', '24.99481908388880', '19.99222863160355', '19.99222863160355',
                '14.99935303204482', '14.99935303204482', '10.00000000012507', '10.00000000012507',
            )
        ],
        saturation=[
            Decimal(v) for v in (
                '0.1000000000000000E-98', '0.1000000000000000E-98', '0.1000000000000000E-98', '0.1000000000000000E-98',
                '0.1000000000000000E-98', '0.1000000000000000E-98', '0.1727371363921276', '0.1727371363921281',
                '0.4344871249926068', '0.4344871249926068', '0.7817833455822488', '0.7817833455822516',
            )
        ],
        pressure=[
            Decimal(v) for v in (
                '0.1001154694602094', '0.1001154694602094', '0.1001154694628803', '0.1001154694628803',
                '0.1001154694707533', '0.1001154694707533', '0.1001154694901246', '0.1001154694901246',
                '0.1001154722096991', '0.1001154722096991', '0.1001154822144740', '0.1001154822144740',
            )
        ]
    )


def test_read_avs_simple_scalar(fixture_dir):
    state = read_avs(fixture_dir / 'simple_sca_node.avs')
    assert state == State(
        temperature=[Decimal(v) for v in ('9.48206013', '14.2026957', '8.41485536', '69.8006870')],
        pressure=[Decimal(v) for v in ('33.6952093', '33.6937832', '31.4565476', '36.1576666')],
        source=[Decimal(v) for v in (0, 0, 0, 0)],
        mass_flux=[Decimal(v) for v in (0, 0, 0, 0)],
    )


def test_read_avs_simple_vector_raises(fixture_dir):
    with pytest.raises(NotImplementedError):
        read_avs(fixture_dir / 'simple_vec_node.avs')


def test_read_pressure_square(fixture_dir):
    pressure = read_pressure(fixture_dir / 'square.iap')
    assert pressure == [
        Decimal(v) for v in ('36.0977050', '38.9579341', '38.9579867', '34.6465422', '35.1315995')
    ]


def test_read_nist_lookup(fixture_dir):
    lookup_table = read_nist_lookup_table(fixture_dir / 'nist_lookup_sample.in')
    assert lookup_table == {
        (20, 0): {'density_kg_m3': 0.100974E+04},
        (20, 2): {'density_kg_m3': 0.100970E+04},
        (20, 4): {'density_kg_m3': 0.100960E+04},
        (20, 6): {'density_kg_m3': 0.100946E+04},
        (22, 0): {'density_kg_m3': 0.101071E+04},
        (22, 2): {'density_kg_m3': 0.101065E+04},
        (22, 4): {'density_kg_m3': 0.101055E+04},
        (22, 6): {'density_kg_m3': 0.101039E+04},
    }


def test_read_storage_volume_square(fixture_dir):
    volume = read_volume_from_storage(fixture_dir / 'square.stor')
    assert volume == (
        Decimal('6.230119676777E+04'),
        Decimal('1.246023935355E+05'),
        Decimal('6.230119676777E+04'),
        Decimal('1.246023935355E+05'),
        Decimal('2.492047870711E+05'),
    )


def test_read_storage_volume_pyramid(fixture_dir):
    volume = read_volume_from_storage(fixture_dir / 'simple_pyramid.stor')
    assert volume == (
        Decimal('9.375000000000E+04'),
        Decimal('9.374999999999E+04'),
        Decimal('4.687500000000E+04'),
        Decimal('2.343750000000E+04'),
        Decimal('4.687500000001E+04'),
    )
