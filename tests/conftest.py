import pytest

from di3 import Provider


@pytest.fixture
def provider() -> Provider:
    return Provider()
