from decimal import Decimal
import math
from typing import Union


def round_significant_figures(x: Union[float, Decimal], n: int):
    """Round a number to a given number of significant figures
    >>> round_significant_figures(1234, 2)
    1200
    >>> round_significant_figures(33.990001, 4)
    33.99
    >>> round_significant_figures(Decimal('1.0000000000000000000002384'), 10)
    Decimal('1.000000000')
    >>> round_significant_figures(Decimal('-1.0000000000000000000002384'), 10)
    Decimal('-1.000000000')
    >>> round_significant_figures(0, 10)
    0
    """
    if not n or n <= 0:
        raise ValueError(f'Invalid number of significant figures ({n}).')

    if x == 0:
        return 0

    return round(x, -int(math.floor(math.log10(abs(x)))) + (n - 1))
