import inspect

from PyQuotient import Quotient


def test_request_data_includes_request_data():
    assert inspect.isclass(Quotient.RequestData)
