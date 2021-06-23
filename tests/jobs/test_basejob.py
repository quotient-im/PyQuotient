import inspect

from PyQuotient import Quotient


def test_base_job_includes_http_verb():
    assert inspect.isclass(Quotient.HttpVerb)
    # how to test better if location of EnumMeta is unknown
    assert str(type(Quotient.HttpVerb)) == "<class 'Shiboken.EnumMeta'>"

def test_base_job_includes_base_job():
    assert inspect.isclass(Quotient.BaseJob)


def test_base_job_includes_status_code():
    assert inspect.isclass(Quotient.BaseJob.StatusCode)


def test_base_job_includes_query():
    assert inspect.isclass(Quotient.BaseJob.Query)


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
