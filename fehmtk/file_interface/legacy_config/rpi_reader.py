from collections import defaultdict
from pathlib import Path
import re
from typing import Callable, Optional

from fehmtk.config import RockPropertiesConfig

PROPERTY_KINDS = {'porosity', 'conductivity', 'permeability', 'compressibility'}
NUMERIC_PATTERN = r'-{0,1}(?:(?:\d+\.\d+)|(?:\.{0,1}\d+))(?:(?:e|E)-{0,1}\d+){0,1}'


def read_legacy_rpi_config(rpi_file: Path) -> RockPropertiesConfig:
    """Read legacy rock properties file (.rpi)

    This assumes a fairly specific format for these files, supporting only a few specific files and structure for
    limited backwards compatibility.
    """
    blocks_by_property = _read_and_process_rpi(rpi_file)

    config = defaultdict(list)
    for property_kind, property_block in blocks_by_property.items():
        for zone_block in property_block.split('stop\n'):
            property_config = _parse_zone_block(zone_block)
            config[f'{property_kind}_configs'].append(property_config)

            grain_density = _match_grain_density(zone_block)
            if grain_density is not None:
                property_config = {
                    'property_model': {'kind': 'constant', 'params': {'constant': grain_density}},
                    'zones': _match_zones(zone_block),
                }
                config['grain_density_configs'].append(property_config)

            specific_heat = _match_specific_heat(zone_block)
            if specific_heat is not None:
                property_config = {
                    'property_model': {'kind': 'constant', 'params': {'constant': specific_heat}},
                    'zones': _match_zones(zone_block),
                }
                config['specific_heat_configs'].append(property_config)

            for zone in property_config['zones']:
                if zone not in config['zone_assignment_order']:
                    config['zone_assignment_order'].append(zone)

    return RockPropertiesConfig.from_dict(config)


def get_zone_order_by_appearance(config: dict):
    zone_order = []
    for property_kind, block_configs in config.items():
        for block_config in block_configs:
            for zone in block_config['zones']:
                if zone not in zone_order:
                    zone_order.append(zone)
    return zone_order


def _read_and_process_rpi(rpi_file: Path) -> dict[str, str]:
    with open(rpi_file) as f:
        processed_blocks_by_property = {}
        processing_property = None
        block = ''
        for line in f:
            line = line.strip()
            if not processing_property:
                if line in PROPERTY_KINDS:
                    processing_property = line
                continue

            if line == f'{processing_property}stop':
                processed_blocks_by_property[processing_property] = block
                processing_property, block = None, ''
                continue

            comments_removed = line.split('%')[0]
            compressed = comments_removed.replace(' ', '')
            block += compressed + '\n'

    missing_keys = processed_blocks_by_property.keys() - PROPERTY_KINDS
    if missing_keys:
        raise NotImplementedError(f'File ({rpi_file}) missing properties ({missing_keys}), file format not supported.')

    return processed_blocks_by_property


def _parse_zone_block(block: str) -> dict:
    zones = _match_zones(block)
    for model in _get_models():
        if re.search(model['signature'], block):
            parser = model['parser']
            params = parser(block)
            return {
                'property_model': {'kind': model['model_kind'], 'params': params},
                'zones': zones,
            }

    raise NotImplementedError(f'No model kind matched for block:\n{block}.')


def _match_zones(block: str) -> list[int]:
    match = re.search(r'ZONES=(\d)(?::(\d))?', block)
    if match is None:
        raise NotImplementedError(f'Block in legacy .rpi file does not contain ZONES definition:\n{block}')

    zone_min, zone_max = match.group(1), match.group(2)
    return list(range(int(zone_min), int(zone_max or zone_min) + 1))


def _match_grain_density(block: str) -> Optional[float]:
    match = re.search(rf'RHOG=({NUMERIC_PATTERN})(?:;|\n)', block)
    if match is None:
        return

    return float(match.group(1))


def _match_specific_heat(block: str) -> Optional[float]:
    match = re.search(rf'SPECHEAT=({NUMERIC_PATTERN})(?:;|\n)', block)
    if match is None:
        return

    return float(match.group(1))


def _get_models() -> tuple[tuple[str, str, Callable]]:
    return (
        {
            'model_kind': 'constant',
            'signature': rf'FUN=@\((?:\w|,)+\){NUMERIC_PATTERN}(?:;|\n)',
            'parser': _parse_params__constant,
        },
        {
            'model_kind': 'constant',
            'signature': r'FUN=@\((?:\w|,)+\)\w+(?:;|\n)',
            'parser': _parse_params__assigned_constant,
        },
        {
            'model_kind': 'depth_power_law_with_maximum',
            'signature': r'FUN=@\(depth\)min\(PORA\.\*depth\.\^\(PORB\),PORA\.\*50\.\^\(PORB\)\)(?:;|\n)',
            'parser': _parse_params__sediment_porosity,
        },
        {
            'model_kind': 'depth_exponential',
            'signature': r'FUN=@\(depth\)PORA\.\*exp\(PORB\.\*depth\);',
            'parser': _parse_params__sediment_porosity,
        },
        {
            'model_kind': 'ctr2tcon',
            'signature': r'FUN=@\(depth,porosity\)TCON\(round\(depth\)\+1\)(?:;|\n)',
            'parser': _parse_params__jdf_ctr2tcon,
        },
        {
            'model_kind': 'porosity_weighted',
            'signature': r'FUN=@\(depth,porosity\)\(KW\.\^porosity\)\.\*\(\w+\.\^\(1-porosity\)\)(?:;|\n)',
            'parser': _parse_params__porosity_weighted,
        },
        {
            'model_kind': 'void_ratio_exponential',
            'signature': r'FUN=@\(depth,porosity\)A\.\*exp\(B\.\*VOID\(porosity\)\)(?:;|\n)',
            'parser': _parse_params__void_ratio_exponential,
        },
        {
            'model_kind': 'overburden',
            'signature': r'FUN=@\(depth,porosity\)0\.435\.\*A\.\*\(1-porosity\)\./OB\(depth\)(?:;|\n)',
            'parser': _parse_params__overburden,
        },
    )


def _parse_params__constant(block: str) -> dict:
    match = re.search(rf'FUN=@\((?:\w|,)+\)({NUMERIC_PATTERN})(?:;|\n)', block)
    if not match:
        raise NotImplementedError(f'No match found for constant function in block:\n{block}')
    return {'constant': float(match.group(1))}


def _parse_params__assigned_constant(block: str) -> dict:
    assigned_variable = re.search(r'FUN=@\((?:\w|,)+\)(\w+)(?:;|\n)', block).group(1)
    match = re.search(rf'{assigned_variable}=({NUMERIC_PATTERN})(?:;|\n)', block)
    if not match:
        raise NotImplementedError(f'No assignment found for variable {assigned_variable} in block:\n{block}')
    return {'constant': float(match.group(1))}


def _parse_params__sediment_porosity(block: str) -> dict:
    match_pora = re.search(rf'PORA=({NUMERIC_PATTERN})(?:;|\n)', block)
    match_porb = re.search(rf'PORB=({NUMERIC_PATTERN})(?:;|\n)', block)
    if not match_pora or not match_porb:
        raise NotImplementedError(f'No match found for porosity constants (PORA, PORB) in block:\n{block}')
    return {'porosity_a': float(match_pora.group(1)), 'porosity_b': float(match_porb.group(1))}


def _parse_params__jdf_ctr2tcon(block: str) -> dict:
    match = re.search(r'TCON=ctr2tcon\(\[((?:\d|,|\[|\])+)\]\)(?:;|\n)', block)
    if not match:
        raise NotImplementedError(f'No match found for ctr2tcon depths in block:\n{block}')

    tcon_args = match.group(1).replace(' ', '').split('],[')
    node_depth_columns = [
        [int(depth) for depth in arg.split(',')]
        for arg in tcon_args
    ]
    return {
        'node_depth_columns': node_depth_columns,
        'ctr_model': {
            'model_kind': 'polynomial',
            'model_params': {
                'x^0': 0,
                'x^1': 0.603,
                'x^2': 0.000531,
                'x^3': -0.000000684,
            },
        },
    }


def _parse_params__porosity_weighted(block: str) -> dict:
    match_var = re.search(r'FUN=@\(depth,porosity\)\(KW\.\^porosity\)\.\*\((\w+)\.\^\(1-porosity\)\)(?:;|\n)', block)
    grain_conductivity_variable = match_var.group(1)

    match_kw = re.search(rf'KW=({NUMERIC_PATTERN})(?:;|\n)', block)
    match_k_grain = re.search(rf'{grain_conductivity_variable}=({NUMERIC_PATTERN})(?:;|\n)', block)
    if not match_kw or not match_k_grain:
        raise NotImplementedError(f'No match found for conductivity constants (KW, KR) in block:\n{block}')
    return {'water_conductivity': float(match_kw.group(1)), 'rock_conductivity': float(match_k_grain.group(1))}


def _parse_params__void_ratio_exponential(block: str) -> dict:
    match_a = re.search(rf'A=({NUMERIC_PATTERN})(?:;|\n)', block)
    match_b = re.search(rf'B=({NUMERIC_PATTERN})(?:;|\n)', block)
    if not match_a or not match_b:
        raise NotImplementedError(f'No match found for power law constants (A, B) in block:\n{block}')
    return {'A': float(match_a.group(1)), 'B': float(match_b.group(1))}


def _parse_params__overburden(block: str) -> dict:
    match_a = re.search(rf'A=({NUMERIC_PATTERN})(?:;|\n)', block)
    match_grav = re.search(rf'GRAV=({NUMERIC_PATTERN})(?:;|\n)', block)
    match_rhow = re.search(rf'RHOW=({NUMERIC_PATTERN})(?:;|\n)', block)
    match_min_ob = re.search(rf'OB=@\(depth\)max\(overburden\(depth\),({NUMERIC_PATTERN})\)(?:;|\n)', block)
    if not (match_a and match_grav and match_rhow and match_min_ob):
        raise NotImplementedError(f'Failed to match all overburden constants in block:\n{block}')

    return {
        'a': float(match_a.group(1)),
        'grav': float(match_grav.group(1)),
        'rhow': float(match_rhow.group(1)),
        'min_overburden': float(match_min_ob.group(1)),
    }
