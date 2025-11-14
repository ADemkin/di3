import inspect
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Callable
from typing import Generic
from typing import Mapping
from typing import ParamSpec
from typing import TypeVar
from typing import get_type_hints

from di3.errors import DependencyInjectionError

T = TypeVar("T")
P = ParamSpec("P")


def is_builtin(obj: Any) -> bool:
    return isinstance(obj, type) and obj.__module__ == "builtins"


@dataclass(slots=True)
class Provider(Generic[T]):
    _instances: dict[Callable[..., T], T] = field(default_factory=dict)

    def register_instance(self, instance: T) -> None:
        self._instances[type(instance)] = instance

    def build(
        self,
        factory: Callable[P, T],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> T:
        if (instance := self._instances.get(factory)) is not None:
            return instance
        dependencies = self.gather_dependencies(factory, *args, **kwargs)
        instance = factory(**dependencies)  # type: ignore[call-arg]
        if inspect.isfunction(factory):
            return instance
        self.register_instance(instance)
        return instance

    def gather_dependencies(
        self,
        factory: Callable[P, T],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Mapping[str, Any]:
        try:
            type_hints = get_type_hints(factory, include_extras=True)
        except NameError as err:
            raise DependencyInjectionError(f"unable to resolve dependency {err.name!r}")
        if inspect.isfunction(factory):
            type_hints.pop("return")
        bound = inspect.signature(factory).bind_partial(*args, **kwargs)
        bound.apply_defaults()
        dependencies = {}
        for arg, dep in type_hints.items():
            if arg in bound.arguments:
                dependencies[arg] = bound.arguments[arg]
                continue
            # all builtins must be injected with defaults
            if is_builtin(dep):
                raise DependencyInjectionError(
                    f"Can not build {factory.__name__!r}: no value for param {arg}: {dep.__name__}"
                )
            dependencies[arg] = self.build(dep)
        return dependencies
