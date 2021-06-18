import inspect

from PyQuotient import Quotient


def test_networkaccessmanager_includes_networkaccessmanager():
    assert inspect.isclass(Quotient.NetworkAccessManager)

    # simple test whether network access manager works
    network_manager = Quotient.NetworkAccessManager()
    assert network_manager.isStrictTransportSecurityEnabled() == False
    network_manager.setStrictTransportSecurityEnabled(True)
    assert network_manager.isStrictTransportSecurityEnabled() == True

