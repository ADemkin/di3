from typing import Any
from typing import Mapping
from typing import get_type_hints
from typing import Generic
from typing import TypeVar
from typing import Type

from dataclasses import dataclass
from dataclasses import field

from di3.tools import name
from di3.errors import DependencyInjectionError


T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class Provider(Generic[T]):
    _instances: dict[str, T] = field(default_factory=dict)

    def register_instance(self, instance: T) -> None:
        self._instances[name(instance)] = instance

    def build(self, cls: Type[T]) -> T:
        if (instance := self._instances.get(name(cls))) is not None:
            return instance
        dependencies = self.gather_dependencies(cls)
        return cls(**dependencies)

    def gather_dependencies(self, obj: Type[T]) -> Mapping[str, Any]:
        try:
            type_hints = get_type_hints(obj)
        except NameError as err:
            raise DependencyInjectionError(f"unable to resolve dependency {err.name!r}")
        kwargs = {}
        for arg, dep in type_hints.items():
            kwargs[arg] = self.build(dep)
        return kwargs
