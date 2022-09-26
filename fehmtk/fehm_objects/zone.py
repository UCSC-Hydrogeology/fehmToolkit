from dataclasses import dataclass
from typing import Optional


@dataclass
class Zone:
    """Class for tracking data held by zone, such as node numbers or vornoi areas."""
    number: int
    data: tuple
    name: Optional[str] = None
