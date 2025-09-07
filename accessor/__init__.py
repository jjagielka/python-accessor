"""Access nested dictionaries.

Create functions to manipulate dictionaries similar to itemgetter.
"""

from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Union

import operator

ops = [
    "__abs__", "__add__", "__all__", "__and__", "__concat__", "__contains__", "__delitem__",
    "__eq__", "__floordiv__", "__ge__", "__gt__", "__iadd__", "__iand__", "__iconcat__",
    "__ifloordiv__", "__ilshift__", "__imatmul__", "__imod__", "__imul__", "__index__",
    "__inv__", "__invert__", "__ior__", "__ipow__", "__irshift__", "__isub__", "__itruediv__",
    "__ixor__", "__le__", "__lshift__", "__lt__", "__matmul__", "__mod__", "__mul__","__ne__",
    "__neg__", "__not__", "__or__", "__pos__", "__pow__", "__rshift__", "__sub__", "__truediv__",
    "__xor__",
]  # fmt: skip


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
    return ":".join(["" if x is None else str(x) for x in t])


class Accessor(metaclass=Meta):
    """Return a callable object that fetches the given item(s) from its operand.

    It is like itemgetter with recursion and object dot notation.
    After f = Accessor.foo.bar, the call f(r) returns r["foo"]["bar"].
    """

    __slots__ = ("_accessor", "_name", "_path")

    def __init__(self, accessor: Callable = None, name: str = "", path: str = "") -> None:
        self._accessor = accessor
        self._name = name
        self._path = path

    def __call__(self, x: Any) -> Any:
        return x if self._accessor is None else self._accessor(x)

    def __getattr__(self, name: str) -> "Accessor":
        return self.__getitem__(name)

    def __getitem__(self, name: Union[str, int, slice]) -> "Accessor":
        def accessor(x: Any) -> Any:
            value = x if self._accessor is None else self._accessor(x)  # self(x)
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


def values(*getters: "Accessor") -> Callable[[Any], tuple]:
    """Return func extracting values of multiple getters as tuple."""
    return lambda x: tuple(n(x) for n in getters)


def keys(*getters: "Accessor") -> Callable[[Any], tuple]:
    """Return paths."""
    return lambda x: tuple(n._path for n in getters)


def items(*getters: "Accessor", prefix: str = "") -> Callable[[Any], Dict[str, Any]]:
    """Return func extracting names and values of multiple getters as tuple."""
    if prefix:
        return lambda x: {prefix + n._name: n(x) for n in getters}
    return lambda x: {n._name: n(x) for n in getters}


def select(*getters: "Accessor", **name_getters: "Accessor") -> Callable[[Any], Dict[str, Any]]:
    """Return func extracting values of multiple getters as dict.

    getters: list of getters for dict entries with _name key
    name_getters: list of getters with names
    """
    return lambda x: dict({n._name: n(x) for n in getters}, **{k: f(x) for k, f in name_getters.items()})


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
