import logging
from pathlib import Path
import shutil


logger = logging.getLogger(__name__)


def create_run_with_source_files(target_directory: Path, file_pairs_by_file_type: dict[str, tuple[Path, Path]]):
    logger.info('Creating directory %s', target_directory)
    target_directory.mkdir()

    file_pairs_by_file_type = file_pairs_by_file_type.copy()
    (source_water_properties_file, run_water_properties_file) = file_pairs_by_file_type.pop('water_properties')
    if source_water_properties_file.is_symlink():
        source_water_properties_file = source_water_properties_file.readlink()

    logger.info('Linking %s -> %s', run_water_properties_file, source_water_properties_file)
    run_water_properties_file.symlink_to(source_water_properties_file)

    for k, (source_file, run_file) in file_pairs_by_file_type.items():
        logger.info('Copying %s to %s', source_file, run_file)
        shutil.copy(source_file, run_file)
