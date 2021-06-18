import inspect

import pytest
from PySide6.QtCore import QByteArray, QUrl

from PyQuotient import Quotient


@pytest.fixture
def connection_data():
    base_url = QUrl('https://matrix.org')
    return Quotient.ConnectionData(base_url)


def test_connectiondata_includes_connectiondata():
    assert inspect.isclass(Quotient.ConnectionData)


def test_connectiondata_create():
    base_url = QUrl('https://matrix.org')
    connection_data = Quotient.ConnectionData(base_url)
    assert connection_data.baseUrl() == base_url


# TODO: submit and limitRate. These methods will be tested after BaseJob tests


def test_connectiondata_setbaseurl(connection_data):
    new_base_url = QUrl('https://quotient.org')

    connection_data.setBaseUrl(new_base_url)
    assert connection_data.baseUrl() == new_base_url


def test_connectiondata_settoken(connection_data):
    access_token = QByteArray('randomaccesstoken')

    connection_data.setToken(access_token)
    assert connection_data.accessToken() == access_token


def test_connectiondata_setdeviceid(connection_data):
    device_id = 'laptop_device_random_id'

    connection_data.setDeviceId(device_id)
    assert connection_data.deviceId() == device_id


def test_connectiondata_setuserid(connection_data):
    user_id = 'user_random_identifier'

    connection_data.setUserId(user_id)
    assert connection_data.userId() == user_id


def test_connectiondata_setneedstoken(connection_data):
    request_name = 'random_request_name'

    connection_data.setNeedsToken(request_name)
    assert connection_data.needsToken(request_name) == True
    assert connection_data.needsToken('false_request_name') == False


def test_connectiondata_setlastevent(connection_data):
    request_name = 'random_request_name'

    connection_data.setNeedsToken(request_name)
    assert connection_data.needsToken(request_name) == True
    assert connection_data.needsToken('false_request_name') == False


def test_connectiondata_generatetxnid(connection_data):
    txn_id = connection_data.generateTxnId()

    assert isinstance(txn_id, QByteArray)


def test_connectiondata_nam(connection_data):
    nam = connection_data.nam()

    assert isinstance(nam, Quotient.NetworkAccessManager)

