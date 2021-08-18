from demo.models.abstractroomordering import RoomGroup
from PySide6 import QtCore, QtWidgets, QtGui
from PyQuotient import Quotient
from demo.pyquaternionroom import PyquaternionRoom
from demo.models.roomlistmodel import RoomListModel, Roles
from demo.models.orderbytag import OrderByTag
from __feature__ import snake_case, true_property


class RoomListItemDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex):
        new_option = QtWidgets.QStyleOptionViewItem(option)
        if not index.parent().is_valid():
            # Group captions
            new_option.display_alignment = QtCore.Qt.AlignHCenter
            new_option.font.bold = True

        if index.data(Roles.HasUnreadRole) is not None:
            new_option.font.bold = True

        if int(index.data(Roles.HighlightCountRole)) > 0:
            highlight_color = QtGui.QColor("orange")
            new_option.palette.set_color(QtGui.QPalette.Text, highlight_color)
            # Highlighting the text may not work out on monochrome colour schemes,
            # hence duplicating with italic font.
            new_option.font.italic = True

        join_state = index.data(Roles.JoinStateRole)
        if join_state == "invite":
            new_option.font.italic = True
        elif join_state == "leave" or join_state == "upgraded":
            new_option.font.strike_out = True

        super().paint(painter, new_option, index)

class RoomListDock(QtWidgets.QDockWidget):
    roomSelected = QtCore.Signal(PyquaternionRoom)

    def __init__(self, parent=None) -> None:
        super().__init__("Rooms", parent)
        self.selected_group_cache = None
        self.selected_room_cache = None

        self.object_name = "RoomsDock"
        self.view = QtWidgets.QTreeView(self)
        self.model = RoomListModel(self.view)
        self.update_sorting_mode()
        self.view.set_model(self.model)
        self.view.set_item_delegate(RoomListItemDelegate(self))
        self.view.animated = True
        self.view.uniform_row_heights = True
        self.view.selection_behavior = QtWidgets.QTreeView.SelectRows
        self.view.header_hidden = True
        self.view.indentation = 0
        self.view.root_is_decorated = False

        self.view.activated.connect(self.row_selected) # See Quaternion #608
        self.view.clicked.connect(self.row_selected)
        self.model.rowsInserted.connect(self.refresh_title)
        self.model.rowsRemoved.connect(self.refresh_title)
        self.model.saveCurrentSelection.connect(self.save_current_selection)

        self.set_widget(self.view)

    def add_connection(self, connection: Quotient.Connection):
        self.model.add_connection(connection)

    @QtCore.Slot()
    def set_selected_room(self, room: PyquaternionRoom):
        if self.get_selected_room() == room:
            return
        
        # First try the current group; if that fails, try the entire list
        index = None
        current_group = self.get_selected_group()
        if current_group is not None:
            index = self.model.index_of(current_group, room)
        if not index.is_valid():
            index = self.model.index_of(RoomGroup(''), room)
        if index.is_valid():
            self.view.current_index = index
            self.view.scroll_to(index)

    @QtCore.Slot()
    def update_sorting_mode(self):
        self.model.set_order(OrderByTag(self.model))

    @QtCore.Slot(QtCore.QModelIndex)
    def row_selected(self, index: QtCore.QModelIndex):
        if self.model.is_valid_room_index(index):
            self.roomSelected.emit(self.model.room_at(index))

    @QtCore.Slot()
    def refresh_title(self):
        self.window_title = f"Rooms ({self.model.total_rooms()})"

    @QtCore.Slot()
    def save_current_selection(self):
        self.selected_room_cache = self.get_selected_room()
        self.selected_group_cache = self.get_selected_group()

    def get_selected_room(self):
        index = self.view.current_index()
        if not index.is_valid() or not index.parent().is_valid():
            return None
        return self.model.room_at(index)
    
    def get_selected_group(self):
        index = self.view.current_index()
        if not index.is_valid():
            return None
        return self.model.room_group_at(index)
