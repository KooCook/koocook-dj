from typing import Iterable, List
import random
from decimal import Decimal

import numpy as np


def gen_ints(a: int, b: int, n: int) -> List[int]:
    """Returns an iterable (currently list) of non-repeating, randomized ints."""
    assert a < b, "a must be smaller than b"
    return random.sample(range(a, b), n)


def gen_floats(a: float, b: float, n: int) -> List[float]:
    """Returns an iterable (currently list) of non-repeating, randomized floats.

    References:
        > Given 2**53 distinct possible values from random(), duplicates are infrequent.
        > On average, you can expect a duplicate float at about 120,000,000 samples.
        https://stackoverflow.com/questions/45394981/how-to-generate-list-of-unique-random-floats-in-python
    """
    assert a < b, "a must be smaller than b"
    out = np.empty(n)
    needed = n
    while needed != 0:
        arr = np.random.uniform(a, b, needed)
        uniqs = np.setdiff1d(np.unique(arr), out[:n-needed])
        out[n-needed: n-needed+uniqs.size] = uniqs
        needed -= uniqs.size
    np.random.shuffle(out)
    return out.tolist()


def gen_decimals(a: float, b: float, n: int) -> Iterable[Decimal]:
    """Returns an iterable (currently list) of non-repeating, randomized Decimals.

    References:
        > Given 2**53 distinct possible values from random(), duplicates are infrequent.
        > On average, you can expect a duplicate float at about 120,000,000 samples.
        https://stackoverflow.com/questions/45394981/how-to-generate-list-of-unique-random-floats-in-python
    """
    assert a < b, "a must be smaller than b"
    out = np.empty(n)
    needed = n
    while needed != 0:
        arr = np.random.uniform(a, b, needed)
        uniqs = np.setdiff1d(np.unique(arr), out[:n-needed])
        out[n-needed: n-needed+uniqs.size] = uniqs
        needed -= uniqs.size
    np.random.shuffle(out)
    return map(Decimal, out)