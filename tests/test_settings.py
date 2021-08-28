from PyQuotient import Quotient
from __feature__ import snake_case, true_property


class TestSettings:
    def test_init(self):
        settings = Quotient.Settings()
        assert isinstance(settings, Quotient.Settings)


class TestSettingsGroup:
    def test_init(self):
        settings_group = Quotient.SettingsGroup('group1')
        assert isinstance(settings_group, Quotient.SettingsGroup)


class TestAccountSettings:
    def test_init(self):
        account_settings = Quotient.AccountSettings('account1')
        assert isinstance(account_settings, Quotient.AccountSettings)
