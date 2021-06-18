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
