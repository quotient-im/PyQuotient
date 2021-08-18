from typing import List
from PySide6 import QtCore
from PyQuotient import Quotient
from __feature__ import snake_case, true_property


class Account(Quotient.Connection):
    ...


class AccountRegistry(QtCore.QObject):
    addedAccount = QtCore.Signal(Account)
    aboutToDropAccount = QtCore.Signal(Account)

    def __init__(self) -> None:
        super().__init__()
        self.accounts: List[Account] = []

    def __len__(self):
        return len(self.accounts)

    def __getitem__(self, position):
        return self.accounts[position]

    def add(self, account: Account) -> None:
        if (account in self.accounts):
            return

        self.accounts.append(account)
        self.addedAccount.emit(account)

    def drop(self, account: Account) -> None:
        self.aboutToDropAccount.emit(account)
        self.accounts.remove(account)

    def is_logged_in(self, user_id: str) -> bool:
        return next((user for user in self.accounts if user.user_id == user_id), None) is not None
