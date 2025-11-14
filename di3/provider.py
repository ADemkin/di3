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

_NOT_SET = object()


def is_builtin(obj: Any) -> bool:
    return obj.__module__ == "builtins"  # type: ignore[no-any-return]


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
        if is_builtin(factory):
            if not any((args, kwargs)):
                raise DependencyInjectionError(f"Not enought params to build {factory!r}")
            return factory(*args, **kwargs)
        if (instance := self._instances.get(factory)) is not None:
            return instance
        dependencies = self.gather_dependencies(factory, *args, **kwargs)
        return factory(**dependencies)  # type: ignore[call-arg]

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
        signature = inspect.signature(factory)
        bound = signature.bind_partial(*args, **kwargs)
        bound.apply_defaults()
        dependencies = {}
        for arg, dep in type_hints.items():
            # default value can be any
            if (value := bound.arguments.get(arg, _NOT_SET)) is _NOT_SET:
                value = self.build(dep)
            dependencies[arg] = value
        return dependencies
