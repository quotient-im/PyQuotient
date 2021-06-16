from PyQuotient import Quotient


def test_base_job_includes_http_verb():
    # how to test better if location of EnumMeta is unknown
    assert str(type(Quotient.HttpVerb)) == "<class 'Shiboken.EnumMeta'>"
