from PySide6 import QtCore
from PyQuotient import Quotient
from __feature__ import snake_case, true_property


class PyquaternionRoom(Quotient.Room):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._html_safe_display_name_value = ''

    def _html_safe_display_name(self):
        return self._html_safe_display_name_value

    @QtCore.Signal
    def htmlSafeDisplayNameChanged(self):
        ...

    html_safe_display_name = QtCore.Property(str, _html_safe_display_name, notify=htmlSafeDisplayNameChanged)
