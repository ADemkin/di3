from dataclasses import dataclass

from di3 import Provider
from di3 import DependencyInjectionError

import pytest


def test_build_gives_registered_instance(provider: Provider) -> None:
    @dataclass
    class Logger:
        level: str = "INFO"

    logger = Logger()
    provider.register_instance(logger)
    assert provider.build(Logger) is logger


@pytest.mark.xfail
def test_build_raises_if_class_is_not_registered_and_not_injectable(
    provider: Provider,
) -> None:
    @dataclass
    class Logger:
        level: str = "INFO"

    with pytest.raises(DependencyInjectionError) as e:
        provider.build(Logger)
    assert "instance of 'Logger' is not registered" in str(e.value)
