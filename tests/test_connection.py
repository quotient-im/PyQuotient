import pytest
from pytest_mock import MockerFixture
from PySide6.QtCore import QByteArray, QUrl

from PyQuotient import Quotient
from __feature__ import snake_case, true_property


@pytest.fixture
def connection():
    server = QUrl('https://matrix-client.matrix.org')
    return Quotient.Connection(server)


def test_homeserver(connection):
    connection.homeserver = 'https://pyquotient.org'
    assert connection.homeserver == 'https://pyquotient.org'
