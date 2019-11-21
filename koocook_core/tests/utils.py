from typing import Iterable, List
import random
from decimal import Decimal

import numpy as np
import names

cached_first_names = []
cached_last_names = []


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


def gen_username(first_name: str, last_name: str = '') -> str:
    """Returns a hopefully unique username for Django."""
    return first_name + last_name + str(random.random())[2:]


def _init_first():
    global cached_first_names
    with open(names.FILES[f'first:male']) as file:
        for line in file:
            name = line.split()[0].capitalize()
            cached_first_names.append(name)
    with open(names.FILES[f'first:female']) as file:
        for line in file:
            name = line.split()[0].capitalize()
            cached_first_names.append(name)
    random.shuffle(cached_first_names)


def _init_last():
    global cached_last_names
    with open(names.FILES['last']) as file:
        for line in file:
            name = line.split()[0].capitalize()
            cached_last_names.append(name)
    random.shuffle(cached_last_names)


def get_first_name():
    try:
        return cached_first_names.pop(-1)
    except IndexError:
        _init_first()
        return cached_first_names.pop(-1)


def get_last_name():
    try:
        return cached_last_names.pop(-1)
    except IndexError:
        _init_last()
        return cached_last_names.pop(-1)


def get_full_name():
    return ' '.join((get_first_name(), get_last_name()))
