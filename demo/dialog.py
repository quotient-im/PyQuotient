from enum import Enum, auto

from PySide6 import QtCore, QtWidgets
from __feature__ import snake_case, true_property


class Dialog(QtWidgets.QDialog):
    class UseStatusLine(Enum):
        NO_STATUS_LINE = auto()
        STATUS_LINE = auto()

    no_extra_buttons = QtWidgets.QDialogButtonBox.NoButton

    def __init__(self, title: str, parent: QtWidgets.QWidget, use_status_line: UseStatusLine = UseStatusLine.NO_STATUS_LINE, apply_title: str = '',
                add_buttons: QtWidgets.QDialogButtonBox.StandardButtons = None):
        super().__init__(parent)

        self.apply_latency = use_status_line
        self.pending_apply_message: str = 'Applying changes, please wait'

        self.status_label = None
        if use_status_line == Dialog.UseStatusLine.STATUS_LINE:
            self.status_label = QtWidgets.QLabel(self)
        
        buttons_flag = QtWidgets.QDialogButtonBox.Ok | add_buttons
        self.buttons = QtWidgets.QDialogButtonBox(buttons_flag, self)
        self.buttons.clicked.connect(self.button_clicked)
        
        self.outer_layout = QtWidgets.QVBoxLayout(self)
        self.outer_layout.add_widget(self.buttons)
        if self.status_label:
            self.outer_layout.add_widget(self.status_label)

        self.window_title = title

        if len(apply_title) > 0:
            self.buttons.button(QtWidgets.QDialogButtonBox.Ok).text = apply_title

    # properties
    @property
    def status_message(self):
        return self.status_label.text
    
    @status_message.setter
    def status_message(self, text):
        self.status_label.text = text
    
    @property
    def button_box(self):
        return self.buttons

    # methods & slots
    def add_layout(self, layout: QtWidgets.QLayout, stretch: int = 0):
        offset = 1
        if self.status_label:
            offset += 1
        
        layout.parent = self.outer_layout
        self.outer_layout.insert_layout(self.outer_layout.count() - offset, layout, stretch)
    
    def add_widget(self, widget: QtWidgets.QWidget, stretch: int, alignment: QtCore.Qt.Alignment):
        offset = 1
        if self.status_label:
            offset += 1
        widget.parent = self.outer_layout
        self.outer_layout.insertWidget(self.outer_layout.count() - offset, widget, stretch, alignment)
    
    @QtCore.Slot(QtWidgets.QAbstractButton)
    def button_clicked(self, button: QtWidgets.QAbstractButton):
        role = self.buttons.button_role(button)
        if role == QtWidgets.QDialogButtonBox.AcceptRole or role == QtWidgets.QDialogButtonBox.YesRole:
            if self.validate():
                if self.status_label:
                    self.status_label.text = self.pending_apply_message
                self.disabled = True
                self.apply()
        elif role == QtWidgets.QDialogButtonBox.ResetRole:
            self.load()
        elif role == QtWidgets.QDialogButtonBox.RejectRole or role == QtWidgets.QDialogButtonBox.NoRole:
            self.reject()

    def apply_failed(self, error_message: str):
        self.status_message = error_message
        self.disabled = False
    
    def button(self, button: QtWidgets.QDialogButtonBox.StandardButton) -> QtWidgets.QPushButton:
        return self.button_box.button(button)

    def reactivate(self):
        if not self.visible:
            self.load()
            self.show()
        self.raise_()
        self.activate_window()

    # (Re-)Load data in the dialog
    # \sa buttonClicked
    def load(self):
        ...

    # Check data in the dialog before accepting
    # \sa apply, buttonClicked
    def validate(self):
        return True

    """
    This method is invoked upon clicking the "apply" button (by default
    it's the one with `AcceptRole`), if validate() returned true.
    \sa buttonClicked, validate
    """
    def apply(self):
        self.accept()
