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

OPTIONAL_KEYS_MAPPING = {
    'initial_conditions': 'rsti',
}


def write_files_index(files_config: FilesConfig, output_file: Path):
    files_config_relative_to_output = files_config.relative_to(output_file.parent)

    with open(output_file, 'w') as f:
        for config_key, files_index_key in FILES_INDEX_KEY_MAPPING.items():
            file_path = getattr(files_config_relative_to_output, config_key)
            f.write(f'{files_index_key}: {file_path}\n')
        for config_key, files_index_key in OPTIONAL_KEYS_MAPPING.items():
            file_path = getattr(files_config_relative_to_output, config_key)
            if file_path is not None:
                f.write(f'{files_index_key}: {file_path}\n')

        f.write('\nall')
