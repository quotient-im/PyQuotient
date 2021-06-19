import inspect

from PySide6.QtNetwork import QSslError

from PyQuotient import Quotient
from __feature__ import snake_case, true_property


def test_networkaccessmanager_includes_networkaccessmanager():
    assert inspect.isclass(Quotient.NetworkAccessManager)


def test_networkaccessmanager_qnetworkaccessmanager_inherit():
    network_manager = Quotient.NetworkAccessManager()
    # not all properties/methods of Qt API support true_property in Qt 6.1
    assert network_manager.is_strict_transport_security_enabled() == False
    network_manager.set_strict_transport_security_enabled(True)
    assert network_manager.is_strict_transport_security_enabled() == True


def test_networkaccessmanager_addignoredsslerrors():
    network_manager = Quotient.NetworkAccessManager()
    ssl_error = QSslError(QSslError.CertificateExpired)

    assert len(network_manager.ignored_ssl_errors) == 0
    network_manager.add_ignored_ssl_error(ssl_error)
    assert len(network_manager.ignored_ssl_errors) == 1
    assert network_manager.ignored_ssl_errors[0].error() == QSslError.CertificateExpired


def test_networkaccessmanager_clear_ignored_ssl_errors():
    network_manager = Quotient.NetworkAccessManager()
    ssl_error = QSslError()

    network_manager.add_ignored_ssl_error(ssl_error)
    network_manager.clear_ignored_ssl_errors()
    assert len(network_manager.ignored_ssl_errors) == 0


def test_networkaccessmanager_instance():
    instance = Quotient.NetworkAccessManager.instance()

    assert isinstance(instance, Quotient.NetworkAccessManager)
