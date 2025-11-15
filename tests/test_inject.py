from dataclasses import dataclass

from di3 import Provider


def test_inject_class(provider: Provider) -> None:
    @dataclass
    class Logger:
        level: str = "INFO"

    @provider.inject
    @dataclass
    class Client:
        logger: Logger
        host: str = "localhost"
        port: int = 8080

    client = Client()
    assert isinstance(client.logger, Logger)


def test_inject_provides_dependencies(provider: Provider) -> None:
    @dataclass
    class Logger:
        level: str = "INFO"

    @provider.inject
    def function(logger: Logger) -> int:
        assert isinstance(logger, Logger)
        return 42

    assert function() == 42


def test_inject_allows_kwarg_params(provider: Provider) -> None:
    @dataclass
    class Logger:
        level: str = "INFO"

    @provider.inject
    def function(number: int, logger: Logger) -> int:
        assert isinstance(logger, Logger)
        return number

    assert function(number=42) == 42


def test_inject_allows_arg_params(provider: Provider) -> None:
    @dataclass
    class Logger:
        level: str = "INFO"

    @provider.inject
    def function(number: int, logger: Logger) -> int:
        assert isinstance(logger, Logger)
        return number

    assert function(42) == 42


async def test_inject_provides_dependencies_for_async_func(provider: Provider) -> None:
    @dataclass
    class Logger:
        level: str = "INFO"

    @provider.inject
    async def function(logger: Logger) -> int:
        assert isinstance(logger, Logger)

    await function()
