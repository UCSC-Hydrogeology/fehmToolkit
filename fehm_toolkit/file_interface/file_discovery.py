import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def get_unique_file(directory: Path, pattern: str, optional: bool = False) -> Optional[Path]:
    matches = list(directory.glob(pattern))
    if not matches and optional:
        logger.info('No file found for optional file "%s", skipping...', pattern)
        return
    if len(matches) != 1:
        raise ValueError(f'Found {len(matches)} matches for "{pattern}" in {directory}, please specify explicitly.')
    return matches[0]
