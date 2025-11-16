from collections.abc import Iterable
from dataclasses import dataclass
from functools import partial
from typing import Annotated
from typing import Any

import pytest

from di3 import Params
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


def test_build_with_annotated_params(provider: Provider) -> None:
    @dataclass
    class Logger:
        level: str

    @dataclass
    class Client:
        logger: Annotated[Logger, Params(level="DEBUG")]

    client = provider.build(Client)
    assert client.logger.level == "DEBUG"


def test_build_with_annotated_arg_params(provider: Provider) -> None:
    @dataclass
    class Logger:
        level: str

    @dataclass
    class Client:
        logger: Annotated[Logger, Params("DEBUG")]

    client = provider.build(Client)
    assert client.logger.level == "DEBUG"


@pytest.mark.parametrize(
    "annotation",
    [
        [],
        [[]],
        [lambda x: x],
        [tuple, tuple],
    ],
)
def test_build_raises_if_incorrectly_annotated(
    provider: Provider, annotation: Iterable[Any]
) -> None:
    @dataclass
    class Logger:
        level: str

    @dataclass
    class Client:
        logger: Annotated[Logger, *annotation]

    with pytest.raises(TypeError):
        provider.build(Client)


def test_build_with_annotated_dict(provider: Provider) -> None:
    @dataclass
    class Logger:
        level: str

    @dataclass
    class Client:
        logger: Annotated[Logger, {"level": "DEBUG"}]

    client = provider.build(Client)
    assert client.logger.level == "DEBUG"
