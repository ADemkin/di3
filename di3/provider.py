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
        raise DependencyInjectionError(f"Instance of {name(cls)!r} is not registered")
