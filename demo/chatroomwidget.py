from PySide6 import QtCore, QtWidgets, QtQuickWidgets, QtQml
from PyQuotient import Quotient

from demo.models.messageeventmodel import MessageEventModel

from __feature__ import snake_case, true_property


class ChatRoomWidget(QtWidgets.QWidget):
    resourceRequested = QtCore.Signal()
    roomSettingsRequested = QtCore.Signal()
    showStatusMessage = QtCore.Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.message_model = MessageEventModel(self)

        QtQml.qmlRegisterUncreatableType(Quotient.Room, 'Quotient', 1, 0, 'Room', 'Room objects can only be created by libQuotient')
        QtQml.qmlRegisterUncreatableType(Quotient.User, 'Quotient', 1, 0, 'User', 'User objects can only be created by libQuotient')
        QtQml.qmlRegisterType(Quotient.GetRoomEventsJob, 'Quotient', 1, 0, 'GetRoomEventsJob')
        QtQml.qmlRegisterType(MessageEventModel, 'Quotient', 1, 0, 'MessageEventModel')

        QtQml.qmlRegisterType(Quotient.Settings, 'Quotient', 1, 0, 'Settings')

        self.timeline_widget = QtQuickWidgets.QQuickWidget(self)
        self.timeline_widget.size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.timeline_widget.resize_mode = QtQuickWidgets.QQuickWidget.SizeRootObjectToView

        self.timeline_widget.root_context().set_context_property("messageModel", self.message_model)
        self.timeline_widget.root_context().set_context_property("controller", self)
        self.timeline_widget.root_context().set_context_property("room", None)

        self.timeline_widget.source = "qrc:///qml/Timeline.qml"

        self.message_text_edit = QtWidgets.QTextEdit(self)
        self.message_text_edit.maximum_height = self.maximum_chat_edit_height()
        self.send_button = QtWidgets.QPushButton('Send', self)
        self.send_button.clicked.connect(self.send_message)

        self.h_layout = QtWidgets.QHBoxLayout()
        self.h_layout.add_widget(self.message_text_edit)
        self.h_layout.add_widget(self.send_button)

        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.v_layout.add_widget(self.timeline_widget)
        self.v_layout.add_layout(self.h_layout)
        self.set_layout(self.v_layout)


    @QtCore.Slot(str, bool)
    def onMessageShownChanged(self, eventId: str, shown: bool): # name should be in camelCase, because it is used so in QML
        ...
    
    def maximum_chat_edit_height(self):
        return self.maximum_height / 3
    
    @QtCore.Slot()
    def send_message(self):
        ...
