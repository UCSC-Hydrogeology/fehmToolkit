from pathlib import Path

from fehmtk.config import FilesConfig

FILES_INDEX_KEY_MAPPING = {
    'run_root': 'root',
    'input': 'input',
    'output': 'outpu',
    'grid': 'grida',
    'storage': 'storo',
    'final_conditions': 'rsto',
    'error': 'error',
    'check': 'check',
    'material_zone': 'zone',
    'water_properties': 'look',
    'history': 'hist',
}


def write_files_index(files_config: FilesConfig, output_file: Path):
    with open(output_file, 'w') as f:
        for config_key, files_index_key in FILES_INDEX_KEY_MAPPING.items():
            f.write(f'{files_index_key}: {getattr(files_config, config_key)}\n')
        f.write('\nall')
