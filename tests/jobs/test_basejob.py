import inspect

import pytest
from PySide6 import QtCore

from PyQuotient import Quotient
from __feature__ import snake_case, true_property


def test_base_job_includes_http_verb():
    assert inspect.isclass(Quotient.HttpVerb)
    # how to test better if location of EnumMeta is unknown
    assert str(type(Quotient.HttpVerb)) == "<class 'Shiboken.EnumMeta'>"

def test_base_job_includes_base_job():
    assert inspect.isclass(Quotient.BaseJob)


def test_base_job_includes_status_code():
    assert inspect.isclass(Quotient.BaseJob.StatusCode)


def test_base_job_includes_status():
    assert inspect.isclass(Quotient.BaseJob.Status)

class TestStatus:
    def test_create_from_status_code(self):
        status_code = Quotient.BaseJob.StatusCode.NetworkError

        status = Quotient.BaseJob.Status(status_code)
        assert status.code == status_code

    def test_create_from_code_and_message(self):
        status_code = 5
        message = 'Status message ok'

        status = Quotient.BaseJob.Status(status_code, message)
        assert status.code == status_code
        assert status.message == message

    def test_fromhttpcode(self):
        http_status_code = 404

        status_code = Quotient.BaseJob.Status.from_http_code(http_status_code)
        assert isinstance(status_code, Quotient.BaseJob.StatusCode)
        assert status_code == Quotient.BaseJob.StatusCode.NotFoundError
    
    def test_fromhttpcode_with_message(self):
        http_status_code = 404
        message = 'Not found error message'

        status = Quotient.BaseJob.Status.from_http_code(http_status_code, message)
        assert status.code == Quotient.BaseJob.StatusCode.NotFoundError
        assert status.message == message

    def test_good(self):
        status_code = Quotient.BaseJob.StatusCode.NetworkError

        status = Quotient.BaseJob.Status(status_code)
        assert status.good() == False

    # dumb_to_log is skipped because PySide6 doesn't have bindings for QDebug class
    # it's possible to make in PyQuotient, but has low priority

    def test_equal_with_other_status(self):
        http_status_code = 404
        message = 'Not found error message'

        status_1 = Quotient.BaseJob.Status(http_status_code, message)
        status_2 = Quotient.BaseJob.Status(http_status_code, message)
        assert status_1 == status_2

    def test_not_equal_with_other_status(self):
        status_1 = Quotient.BaseJob.Status(404, 'Not found error message')
        status_2 = Quotient.BaseJob.Status(200, 'Success')
        assert status_1 != status_2
    
    def test_equal_with_code(self):
        http_status_code = 404
        message = 'Not found error message'

        status = Quotient.BaseJob.Status(http_status_code, message)
        assert status == http_status_code

    def test_not_equal_with_code(self):
        status = Quotient.BaseJob.Status(404, 'Not found error message')
        assert status != 200


@QtCore.Slot()
def void_slot():
    ...


@QtCore.Slot(Quotient.BaseJob.Status)
def status_slot(status):
    ...


class TestBaseJob:
    @pytest.fixture
    def base_job(self):
        return Quotient.BaseJob(
            Quotient.HttpVerb.Get,
            'custom_job',
            '/api/custom/',
            True
        )

    def test_create_basejob(self):
        base_job = Quotient.BaseJob(
            Quotient.HttpVerb.Get,
            'custom_job',
            '/api/custom/',
            True
        )

        assert isinstance(base_job, Quotient.BaseJob)

    # constructor with query doesn't have binding yet. shiboken returns no error related to
    # and doesn't generate a binding
    # def test_create_basejob_with_query(self):
    #     query = QtCore.QUrlQuery('server=quotient&room=dev')
    #     request_data = Quotient.RequestData(dict(user='Admin1', group='admins'))

    #     base_job = Quotient.BaseJob(
    #         Quotient.HttpVerb.Get,
    #         'custom_job',
    #         '/api/custom/',
    #         query,
    #         request_data,
    #         True
    #     )

    #     assert isinstance(base_job, Quotient.BaseJob)

    # properties and methods
    def test_request_url(self, base_job):
        assert isinstance(base_job.request_url, QtCore.QUrl)
        # local http server is needed to test url of reply?
        # assert base_job.request_url.url() == '/api/custom/'

    def test_max_retries(self, base_job):
        base_job.max_retries = 7
        assert base_job.max_retries == 7
    
    def test_status_code(self, base_job):
        assert base_job.status_code == Quotient.BaseJob.StatusCode.Unprepared

    def test_is_background(self, base_job):
        assert base_job.is_background == False
    
    def test_status(self, base_job):
        assert isinstance(base_job.status, Quotient.BaseJob.Status)

    def test_status_caption(self, base_job):
        assert base_job.status_caption == 'Request failed'

    def test_raw_data(self, base_job):
        assert base_job.raw_data() == ''

    def test_raw_data_with_limit(self, base_job):
        assert base_job.raw_data(100) == ''

    def test_raw_data_sample(self, base_job):
        assert base_job.raw_data_sample(100) == ''

    def test_json_data(self, base_job):
        assert isinstance(base_job.json_data, dict)

    def test_json_items(self, base_job):
        assert isinstance(base_job.json_items, QtCore.QJsonArray)
    
    # error doesn't have binding yet. shiboken returns no error related to this property
    # and doesn't generate a binding
    # def test_error(self, base_job):
    #     assert base_job.error == 404

    def test_error_string(self, base_job):
        assert base_job.error_string == ''

    def test_error_url(self, base_job):
        assert base_job.error_url == ''

    # TODO: getCurrentTimeout, getCurrentTimeoutMs, getNextRetryInterval, getNextRetryMs, timeToRetry millisToRetry

    # signals
    def test_about_to_send_request(self, mocker, base_job):
        slot_stub = mocker.stub(name='void_slot')
        base_job.aboutToSendRequest.connect(slot_stub)
        base_job.aboutToSendRequest.emit()
        slot_stub.assert_called_with()

    def test_sent_request(self, base_job):
        base_job.sentRequest.connect(void_slot)

    def test_status_changed(self, base_job):
        base_job.statusChanged.connect(status_slot)

    def test_retry_scheduled(self, base_job):
        base_job.retryScheduled.connect(void_slot)

    def test_rate_limited(self, base_job):
        base_job.rateLimited.connect(void_slot)

    def test_finished(self, base_job):
        base_job.finished.connect(void_slot)
    
    def test_result(self, base_job):
        base_job.result.connect(void_slot)
    
    def test_success(self, mocker, base_job):
        slot_stub = mocker.stub(name='base_job_slot')
        base_job.success.connect(slot_stub)
        base_job.success.emit(base_job)
        assert slot_stub.called == 1
        assert len(slot_stub.call_args[0]) == 1
        assert isinstance(slot_stub.call_args[0][0], Quotient.BaseJob)

    def test_(self, base_job):
        base_job.result.connect(void_slot)
