import inspect

import pytest
from PySide6.QtCore import QByteArray, QUrl

from PyQuotient import Quotient
from __feature__ import snake_case, true_property


@pytest.fixture
def connection_data():
    base_url = QUrl('https://matrix.org')
    return Quotient.ConnectionData(base_url)


def test_connectiondata_includes_connectiondata():
    assert inspect.isclass(Quotient.ConnectionData)


def test_connectiondata_create():
    base_url = QUrl('https://matrix.org')
    connection_data = Quotient.ConnectionData(base_url)
    assert connection_data.base_url == base_url


# TODO: submit and limitRate. These methods will be tested after BaseJob tests


def test_connectiondata_baseurl(connection_data):
    new_base_url = QUrl('https://quotient.org')

    connection_data.base_url = new_base_url
    assert connection_data.base_url == new_base_url


def test_connectiondata_accesstoken(connection_data):
    access_token = QByteArray('randomaccesstoken')

    connection_data.access_token = access_token
    assert connection_data.access_token == access_token


def test_connectiondata_deviceid(connection_data):
    device_id = 'laptop_device_random_id'

    connection_data.device_id = device_id
    assert connection_data.device_id == device_id


def test_connectiondata_userid(connection_data):
    user_id = 'user_random_identifier'

    connection_data.user_id = user_id
    assert connection_data.user_id == user_id


def test_connectiondata_setneedstoken(connection_data):
    request_name = 'random_request_name'

    connection_data.set_needs_token(request_name)
    assert connection_data.needs_token(request_name) == True
    assert connection_data.needs_token('false_request_name') == False


def test_connectiondata_lastevent(connection_data):
    last_event = 'event_in_connection_data'

    connection_data.last_event = last_event
    assert connection_data.last_event == last_event


def test_connectiondata_generatetxnid(connection_data):
    txn_id = connection_data.generate_txn_id()

    assert isinstance(txn_id, QByteArray)


def test_connectiondata_nam(connection_data):
    nam = connection_data.nam()

    assert isinstance(nam, Quotient.NetworkAccessManager)

