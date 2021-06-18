import inspect

from PySide6.QtNetwork import QSslError

from PyQuotient import Quotient


def test_networkaccessmanager_includes_networkaccessmanager():
    assert inspect.isclass(Quotient.NetworkAccessManager)


def test_networkaccessmanager_qnetworkaccessmanager_inherit():
    network_manager = Quotient.NetworkAccessManager()
    assert network_manager.isStrictTransportSecurityEnabled() == False
    network_manager.setStrictTransportSecurityEnabled(True)
    assert network_manager.isStrictTransportSecurityEnabled() == True


def test_networkaccessmanager_addignoredsslerrors():
    network_manager = Quotient.NetworkAccessManager()
    ssl_error = QSslError(QSslError.CertificateExpired)

    assert len(network_manager.ignoredSslErrors()) == 0
    network_manager.addIgnoredSslError(ssl_error)
    assert len(network_manager.ignoredSslErrors()) == 1
    assert network_manager.ignoredSslErrors()[0].error() == QSslError.CertificateExpired


def test_networkaccessmanager_clearignoredsslerrors():
    network_manager = Quotient.NetworkAccessManager()
    ssl_error = QSslError()

    network_manager.addIgnoredSslError(ssl_error)
    network_manager.clearIgnoredSslErrors()
    assert len(network_manager.ignoredSslErrors()) == 0


def test_networkaccessmanager_instance():
    instance = Quotient.NetworkAccessManager.instance()

    assert isinstance(instance, Quotient.NetworkAccessManager)
