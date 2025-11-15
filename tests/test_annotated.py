from dataclasses import dataclass
from functools import partial
from typing import Annotated

from di3 import Provider


def test_build_with_annotated_factory(provider: Provider) -> None:
    @dataclass
    class Logger:
        level: str

    def get_logger() -> Logger:
        return Logger(level="DEBUG")

    @dataclass
    class Client:
        logger: Annotated[Logger, get_logger]

    client = provider.build(Client)
    assert client.logger.level == "DEBUG"


def test_build_with_annotated_partial(provider: Provider) -> None:
    @dataclass
    class Logger:
        level: str

    @dataclass
    class Client:
        logger: Annotated[Logger, partial(Logger, level="DEBUG")]

    client = provider.build(Client)
    assert client.logger.level == "DEBUG"


def test_build_with_annotated_lambda(provider: Provider) -> None:
    @dataclass
    class Logger:
        level: str

    @dataclass
    class Client:
        logger: Annotated[Logger, lambda: Logger(level="DEBUG")]

    client = provider.build(Client)
    assert client.logger.level == "DEBUG"
