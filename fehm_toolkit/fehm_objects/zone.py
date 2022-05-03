from dataclasses import dataclass


@dataclass
class Zone:
    """Class for tracking data held by zone, such as node numbers or vornoi areas."""
    number: int
    data: tuple
    name: str = None
