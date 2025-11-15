from collections.abc import Callable
from collections.abc import Mapping
from dataclasses import dataclass
from dataclasses import field
from functools import wraps
import inspect
from typing import Any
from typing import Generic
from typing import ParamSpec
from typing import TypeVar
from typing import cast
from typing import get_type_hints

from di3.errors import DependencyInjectionError

T = TypeVar("T")
P = ParamSpec("P")


def is_builtin(obj: Any) -> bool:  # noqa: ANN401
    return isinstance(obj, type) and obj.__module__ == "builtins"


def get_bound_params(
    factory: Callable[P, T] | type[T],
    *args: P.args,
    **kwargs: P.kwargs,
) -> Mapping[str, Any]:
    bound = inspect.signature(factory).bind_partial(*args, **kwargs)
    bound.apply_defaults()
    return bound.arguments


@dataclass(slots=True)
class Provider(Generic[T]):
    _instances: dict[type[T], T] = field(default_factory=dict)

    def register_instance(self, instance: T) -> None:
        self._instances[type(instance)] = instance

    def _execute(
        self,
        factory: Callable[P, T] | type[T],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> T:
        dependencies = self.gather_dependencies(factory, *args, **kwargs)
        return factory(**dependencies)  # type: ignore[call-arg]

    def build(
        self,
        factory: Callable[P, T] | type[T],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> T:
        if inspect.isfunction(factory):
            return self._execute(factory, *args, **kwargs)
        factory = cast("type[T]", factory)
        if instance := self._instances.get(factory):
            return instance
        instance = self._execute(factory, *args, **kwargs)
        self.register_instance(instance)
        return instance

    def gather_dependencies(
        self,
        factory: Callable[P, T] | type[T],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Mapping[str, Any]:
        type_hints = get_type_hints(factory, include_extras=True)
        type_hints = {k: v for k, v in type_hints.items() if k != "return"}
        bound_params = get_bound_params(factory, *args, **kwargs)
        dependencies = {}
        for arg_name, dep_type in type_hints.items():
            if arg_name in bound_params:
                dependencies[arg_name] = bound_params[arg_name]
                continue
            # all builtins must be injected with defaults
            if is_builtin(dep_type):
                raise DependencyInjectionError(
                    f"Can not build {factory.__name__!r}: no value for "
                    f"param {arg_name}: {dep_type.__name__}",
                )
            dependencies[arg_name] = self.build(dep_type)
        return dependencies

    def inject(self, factory: Callable[P, T] | type[T]) -> Callable[P, T] | type[T]:
        @wraps(factory)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            return self._execute(factory, *args, **kwargs)

        return wrapper
