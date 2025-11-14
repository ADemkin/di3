from dataclasses import dataclass
from dataclasses import field

import pytest

from di3 import DependencyInjectionError
from di3 import Provider


def test_build_inject_single_dependency(provider: Provider) -> None:
    @dataclass
    class Logger:
        level: str = "INFO"

    @dataclass
    class Client:
        logger: Logger
        host: str = "localhost"
        port: int = 8080

    client = provider.build(Client)
    assert isinstance(client, Client)


def test_build_injects_multiple_dependencies(provider: Provider) -> None:
    @dataclass
    class Logger:
        level: str = "INFO"

    @dataclass
    class Client:
        logger: Logger
        host: str = "localhost"
        port: int = 8080

    @dataclass
    class Service:
        logger: Logger
        client: Client

    service = provider.build(Service)
    assert isinstance(service, Service)
    assert isinstance(service.client, Client)
    assert isinstance(service.logger, Logger)


def test_build_injects_same_instance_when_building_multiple_dependencies(
    provider: Provider,
) -> None:
    @dataclass
    class Logger:
        level: str = "INFO"

    @dataclass
    class Client:
        logger: Logger
        host: str = "localhost"
        port: int = 8080

    @dataclass
    class Service:
        logger: Logger
        client: Client

    logger = Logger()
    provider.register_instance(logger)
    service = provider.build(Service)
    assert service.logger is logger
    assert service.client.logger is logger


def test_build_raises_if_unknown_dependency(provider: Provider) -> None:
    @dataclass
    class WithMissingDependency:
        undefined: "Undefined"  # type: ignore # noqa: F821

    with pytest.raises(DependencyInjectionError) as err:
        provider.build(WithMissingDependency)

    assert "unable to resolve dependency 'Undefined'" in str(err.value)


def test_build_keeps_default_values_when_building(provider: Provider) -> None:
    @dataclass
    class Client:
        host: str = "localhost"
        port: int = 8080

    client = provider.build(Client)
    assert client.host == "localhost"
    assert client.port == 8080


def test_build_keeps_field_default_values_when_building(provider: Provider) -> None:
    @dataclass
    class Client:
        host: str = field(default="localhost")
        port: int = field(default=8080)

    client = provider.build(Client)
    assert client.host == "localhost"
    assert client.port == 8080


@pytest.mark.xfail
def test_build_injects_class_from_string_type(
    provider: Provider,
) -> None:
    @dataclass
    class Logger:
        level: str = "INFO"

    @dataclass
    class Service:
        logger: "Logger"

    service = provider.build(Service)
    assert isinstance(service.logger, Logger)


def test_build_uses_provided_params(
    provider: Provider,
) -> None:
    @dataclass
    class Logger:
        level: str = "INFO"

    @dataclass
    class Service:
        logger: Logger

    logger = Logger(level="DEBUG")
    service = provider.build(Service, logger=logger)
    assert service.logger is logger


def test_build_fails_if_not_enough_params(
    provider: Provider,
) -> None:
    @dataclass
    class Service:
        host: str
        port: int

    with pytest.raises(
        DependencyInjectionError,
        match="Not enought params to build <class 'str'>",
    ):
        provider.build(Service)


def test_build_fails_if_not_enough_params_for_dependency(
    provider: Provider,
) -> None:
    @dataclass
    class Logger:
        level: str

    @dataclass
    class Service:
        logger: Logger
        host: str = "localhost"
        port: int = 8080

    with pytest.raises(
        DependencyInjectionError,
        match="Not enought params to build <class 'str'>",
    ):
        provider.build(Service)


def test_build_allow_to_build_builtin_object(
    provider: Provider,
) -> None:
    assert provider.build(int, 42) == 42
