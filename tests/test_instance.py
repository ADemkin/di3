from di3 import Provider
from di3 import DependencyInjectionError

import pytest


def test_build_gives_registered_instance(provider: Provider) -> None:
    class A:
        pass

    a = A()
    provider.register_instance(a)
    assert provider.build(A) is a


def test_build_raises_if_no_instance_registered(provider: Provider) -> None:
    class A:
        pass

    with pytest.raises(DependencyInjectionError) as e:
        provider.build(A)
    assert "Instance of 'A' is not registered" in str(e.value)
