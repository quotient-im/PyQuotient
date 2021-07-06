from PyQuotient import Quotient
from __feature__ import snake_case, true_property


def test_getloginflowsjob():
    # test whether class exists, can be instanciated
    # will be extended by more advanced tests soon
    get_login_flows_job = Quotient.GetLoginFlowsJob()
    assert get_login_flows_job.request_url.url() == ''