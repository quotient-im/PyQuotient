from PyQuotient.Quotient import HttpVerb


def test_base_job_includes_http_verb():
    assert type(Quotient.HttpVerb) == 'class'
