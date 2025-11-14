from dataclasses import dataclass


from di3 import Provider


def test_build_gives_instance(provider: Provider) -> None:
    @dataclass
    class Logger:
        level: str = "INFO"

    logger = provider.build(Logger)
    assert isinstance(logger, Logger)


def test_build_gives_registered_instance(provider: Provider) -> None:
    @dataclass
    class Logger:
        level: str = "INFO"

    logger = Logger()
    provider.register_instance(logger)
    assert provider.build(Logger) is logger
