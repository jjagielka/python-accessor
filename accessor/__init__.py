"""Access nested dictionaries.

Create functions to manipulate dictionaries smililar to itemgetter.
"""

from functools import wraps

import operator

ops = ['__lt__', '__le__', '__eq__', '__ne__', '__ge__', '__gt__', '__not__',
       '__abs__', '__add__', '__and__', '__floordiv__', '__index__', '__inv__',
       '__invert__', '__lshift__', '__mod__', '__mul__', '__matmul__',
       '__neg__', '__or__', '__pos__', '__pow__', '__rshift__', '__sub__',
       '__truediv__', '__xor__', '__concat__', '__contains__']


class Meta(type):
    """Bind methods from operator module to Accessor class."""

    def __init__(cls, name, bases, attrs):
        super(Meta, cls).__init__(name, bases, attrs)

        def wrapper(func):
            @wraps(func)
            def inner(self, *args, **kwargs):
                return lambda x: func(self(x), *args, **kwargs)
            return inner

        for name in ops:
            setattr(cls, name, wrapper(getattr(operator, name)))


def _str_slice(s):
    t = (s.start, s.stop, s.step) if s.step else (s.start, s.stop)
    return ':'.join(['' if x is None else str(x) for x in t])


class Accessor(metaclass=Meta):
    """Return a callable object that fetches the given item(s) from its operand.

    It is like itemgetter with recusion and object dot notation.
    After f = Accessor.foo.bar, the call f(r) returns r["foo"]["bar"].
    """

    __slots__ = ('_accessor', '_path')

    def __init__(self, accessor=None):
        self._accessor = accessor
        self._path = accessor._path if accessor else ''

    def __call__(self, x):
        return x if self._accessor is None else self._accessor(x)

    def __getattr__(self, name):
        return self.__getitem__(name)

    def __getitem__(self, name):
        def accessor(x, resolve=True):
            value = self(x) if resolve else x  # for the below recurence
            if not isinstance(name, (int, slice)) and isinstance(value, list):
                return [accessor(n, False) for n in value]
            try:
                return getattr(value, '__getitem__', lambda a: None)(name)
            except (KeyError, TypeError):
                return None
        accessor._path = _str_slice(name) if isinstance(name, slice) else name
        return self.__class__(accessor)

    def __repr__(self):
        return f"<{self.__class__.__name__} '{self._path}'>"


accessor = Accessor()


def values(*getters):
    """Return func extracting values of mulitple getters as tuple.

    After g = itemgetter(2, 5, 3), the call g(r) returns (r[2], r[5], r[3])
    """
    return lambda x: tuple(n(x) for n in getters)


def keys(*getters):
    """Return paths."""
    return lambda x: tuple(n._path for n in getters)


def items(*getters, prefix=''):
    return lambda x: {prefix + n._path: n(x) for n in getters}


def select(*getters, **name_getters):
    """Return func extracting values of mulitple getters as dict.

    getters: list of getters for dict entries with _path key
    name_getters: list of getters with names
    """
    return lambda x: dict(
        {n._path: n(x) for n in getters},
        **{k: f(x) for k, f in name_getters.items()})


def normalize(data, c_getter, select, c_select):
    """Normalize semi-structured JSON data into a flat table.

    Parameters
    ----------
    data : dict or list of dicts
        Unserialized JSON objects
    c_getter : getter or select of strings
        Path in each object to list of records. If not passed, data will be
        assumed to be an array of records
    """
    for x in [data] if isinstance(data, dict) else data:
        yield from (dict(select(x), **c_select(c)) for c in c_getter(x) or [{}])


data = [{
        'state': 'Florida',
        'shortname': 'FL',
        'info': {'governor': 'Rick Scott'},
        'counties': [
            {'name': 'Dade', 'population': 12345},
            {'name': 'Broward', 'population': 40000},
            {'name': 'Palm Beach', 'population': 60000}
        ]},
        {'state': 'Ohio',
         'shortname': 'OH',
         'info': {'governor': 'John Kasich'},
         'counties': [
             {'name': 'Summit', 'population': 1234},
             {'name': 'Cuyahoga', 'population': 1337}
         ]}
        ]
