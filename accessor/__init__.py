"""Access nested dictionaries.

Create functions to manipulate dictionaries similar to itemgetter.
"""

from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Union

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

    It is like itemgetter with recursion and object dot notation.
    After f = Accessor.foo.bar, the call f(r) returns r["foo"]["bar"].
    """

    __slots__ = ('_accessor', '_name', '_path')

    def __init__(self, accessor: Callable = None, name: str="", path: str="") -> None:
        self._accessor = accessor
        self._name = name
        self._path = path

    def __call__(self, x: Any) -> Any:
        return x if self._accessor is None else self._accessor(x)

    def __getattr__(self, name: str) -> 'Accessor':
        return self.__getitem__(name)

    def __getitem__(self, name: Union[str, int, slice]) -> 'Accessor':
        def accessor(x: Any) -> Any:
            value = x if self._accessor is None else self._accessor(x) # self(x)
            try:
                if not isinstance(name, (int, slice)) and isinstance(value, list):
                    return [v[name] for v in value]
                else:
                    return value[name]
            except (KeyError, TypeError, IndexError, AttributeError):
                return None

        # Pre-compute name and path strings
        if isinstance(name, slice):
            _name = _str_slice(name)
            _path = f"{self._path}[{_name}]" if self._path else f"[{_name}]"
        else:
            _name = str(name)
            _path = f"{self._path}.{_name}" if self._path else _name
            
        return self.__class__(accessor, _name, _path)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} '{self._path}'>"


accessor = Accessor()


def values(*getters: 'Accessor') -> Callable[[Any], tuple]:
    """Return func extracting values of multiple getters as tuple."""
    return lambda x: tuple(n(x) for n in getters)


def keys(*getters: 'Accessor') -> Callable[[Any], tuple]:
    """Return paths."""
    return lambda x: tuple(n._path for n in getters)


def items(*getters: 'Accessor', prefix: str = '') -> Callable[[Any], Dict[str, Any]]:
    """Return func extracting names and values of multiple getters as tuple."""
    if prefix:
        return lambda x: {prefix + n._name: n(x) for n in getters}
    return lambda x: {n._name: n(x) for n in getters}


def select(*getters: 'Accessor', **name_getters: 'Accessor') -> Callable[[Any], Dict[str, Any]]:
    """Return func extracting values of multiple getters as dict.

    getters: list of getters for dict entries with _name key
    name_getters: list of getters with names
    """
    return lambda x: dict(
        {n._name: n(x) for n in getters},
        **{k: f(x) for k, f in name_getters.items()})


def flatten(list_getter: 'Accessor', *getters: 'Accessor', **kwargs: Any) -> Callable[[Any], List[Dict[str, Any]]]:
    """Flatten nested data structures with optional field mapping.
    
    Parameters
    ----------
    list_getter : Accessor
        Accessor that returns a list to flatten
    *getters : Accessor
        Additional accessors to include in flattened result
    **kwargs : dict
        Additional fields to include, where keys are field names and values are accessors
        Special keyword 'suffix' can be used to add suffix to list_getter field names
        
    Returns
    -------
    function
        A function that takes data and returns flattened list of dictionaries
    """
    suffix = kwargs.pop('suffix', '')
    
    def flattener(data: Any) -> List[Dict[str, Any]]:
        result = []
        items = list_getter(data) or []
        
        for item in items:
            flat_item = {}
            
            # Add fields from getters
            for getter in getters:
                if hasattr(getter, '_name'):
                    flat_item[getter._name] = getter(data)
            
            # Add fields from kwargs (excluding suffix)
            for key, getter in kwargs.items():
                if hasattr(getter, '_name'):
                    flat_item[key] = getter(data)
            
            # Add fields from the list item with optional suffix
            if isinstance(item, dict):
                for key, value in item.items():
                    flat_item[key + suffix] = value
            
            result.append(flat_item)
        
        return result
    
    return flattener


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

