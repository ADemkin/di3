from collections.abc import Callable
from collections.abc import Mapping
import inspect
from types import NoneType
from types import UnionType
from typing import Annotated
from typing import Any
from typing import ParamSpec
from typing import TypeVar
from typing import get_args
from typing import get_origin

T = TypeVar("T")
P = ParamSpec("P")


def get_bound_params(
    factory: Callable[P, T] | type[T],
    *args: P.args,
    **kwargs: P.kwargs,
) -> Mapping[str, Any]:
    bound = inspect.signature(factory).bind_partial(*args, **kwargs)
    bound.apply_defaults()
    return bound.arguments


def is_function(obj: Any) -> bool:
    return inspect.isfunction(obj)


def is_annotated(obj: Any) -> bool:
    return get_origin(obj) is Annotated


def unwrap_annotated(obj: Any) -> tuple[Any, Any]:
    obj, meta, *rest = get_args(obj)
    if rest:
        raise TypeError(f"{obj.__name__} must have exactly 1 Annotated arg.")
    return obj, meta


def is_union(obj: Any) -> bool:
    return get_origin(obj) is UnionType


def unwrap_union(obj: Any) -> Any:
    return next(item for item in get_args(obj) if item is not NoneType)


def is_builtin(obj: Any) -> bool:
    return isinstance(obj, type) and obj.__module__ == "builtins"
