import pytest

from di3 import Provider


@pytest.fixture(scope="function")
def provider() -> Provider:
    return Provider()
