import functools
from enum import Enum, auto
from typing import Callable, Dict, List, Optional
from PySide6 import QtCore
from PyQuotient import Quotient
from demo.models.abstractroomordering import AbstractRoomOrdering, RoomGroup, RoomGroups
from __feature__ import snake_case, true_property


Visitor = Callable[[QtCore.QModelIndex], None]


class Roles(Enum):
    HasUnreadRole = QtCore.Qt.UserRole + 1
    HighlightCountRole = auto()
    JoinStateRole = auto()
    ObjectRole = auto()


class RoomListModel(QtCore.QAbstractItemModel):
    saveCurrentSelection = QtCore.Signal()
    restoreCurrentSelection = QtCore.Signal()
    groupAdded = QtCore.Signal(int)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.room_groups: RoomGroups = []
        self.connections: List[Quotient.Connection] = []
        self.room_order: Optional[AbstractRoomOrdering] = None
        self.room_indices: Dict[Quotient.Room, QtCore.QPersistentModelIndex] = {}

        self.modelAboutToBeReset.connect(self.saveCurrentSelection)
        self.modelReset.connect(self.restoreCurrentSelection)

    def column_count(self, index: QtCore.QModelIndex) -> int:
        return 1
    
    def row_count(self, parent: QtCore.QModelIndex) -> int:
        if not parent.is_valid():
            return len(self.room_groups)

        if self.is_valid_group_index(parent):
            return len(self.room_groups[parent.row].rooms)

        return 0

    def is_valid_group_index(self, index: QtCore.QModelIndex) -> bool:
        return index.is_valid() and not index.parent().is_valid() and index.row < len(self.room_groups)

    def is_valid_room_index(self, index: QtCore.QModelIndex) -> bool:
        return index.is_valid() and self.is_valid_group_index(index.parent()) and index.row < len(self.room_groups[index.parent.row].rooms)

    def add_connection(self, connection: Quotient.Connection) -> None:
        self.connections.append(connection)
        connection.loggedOut.connect(lambda: self.delete_connection(connection))
        connection.newRoom.connect(self.add_room)
        self.room_order.connect_signals(connection)

        for room in connection.all_rooms():
            self.add_room(room)

    def delete_connection(self, connection: Quotient.Connection):
        conn = next((conn for conn in self.connections if conn == connection), None)
        if conn == None:
            print('Connection is missing in the rooms model')
            return

        for room in connection.all_rooms():
            self.delete_room(room)
        self.connections.remove(connection)

    @QtCore.Slot(Quotient.Room)
    def add_room(self, room: Quotient.Room) -> None:
        self.add_room_to_groups(room)
        self.connect_room_signals(room)

    def add_room_to_groups(self, room: Quotient.Room, groups_keys: List[str] = None) -> None:
        if groups_keys is None:
            groups_keys = []

        if len(groups_keys) == 0:
           groups_keys = self.room_order.room_groups(room)

        for group_key in groups_keys:
            inserted_group = self.try_insert_group(group_key)
            lower_bound_room = self.lower_bound_room(inserted_group, room)
            if lower_bound_room == room:
                print("RoomListModel: room is already listed under group")
                continue
            
            group_index = self.index(len(self.room_groups), 0)
            try:
                room_index = inserted_group.rooms.index(room)
            except ValueError:
                room_index = 0
            
            self.begin_insert_rows(group_index, room_index, room_index)
            inserted_group.rooms.insert(room_index, room)
            self.end_insert_rows()
            self.room_indices[room] = self.index(room_index, 0, group_index)
            print(f"RoomListModel: Added {room.object_name} to group {group_key}")
    
    def try_insert_group(self, group_key: str) -> RoomGroup:
        lower_bound_group = self.lower_bound_group(group_key)
        if lower_bound_group is None:
            group_index = len(self.room_groups)
            # TODO:         const auto affectedIdxs = preparePersistentIndexChange(gPos, 1);
            self.begin_insert_rows(QtCore.QModelIndex(), group_index, group_index)
            room_group = RoomGroup(group_key)
            self.room_groups.append(room_group) # TODO: insert on correct position
            lower_bound_group = room_group
            self.end_insert_rows()
            # TODO:         changePersistentIndexList(affectedIdxs.first, affectedIdxs.second);
            self.groupAdded.emit(self.room_groups.index(room_group))
        # TODO
        return lower_bound_group


    def connect_room_signals(self, room: Quotient.Room) -> None:
        room.beforeDestruction.connect(self.delete_room)
        self.room_order.connect_signals(room)
        room.displaynameChanged.connect(lambda: self.refresh(room))
        room.unreadMessagesChanged.connect(lambda: self.refresh(room))
        room.notificationCountChanged.connect(lambda: self.refresh(room))
        room.avatarChanged.connect(lambda: self.refresh(room, [QtCore.Qt.DecorationRole]))

    @QtCore.Slot(Quotient.Room)
    def delete_room(self, room: Quotient.Room) -> None:
        self.visit_room(room, lambda index: self.do_remove_room(index))
    
    def do_remove_room(self, index: QtCore.QModelIndex) -> None:
        if not self.is_valid_room_index(index):
            print(f'Attempt to remove a room at invalid index {index}')
        
        group_position = index.parent.row
        group = self.room_groups[group_position]
        room = group.rooms[index.row]
        print(f'RoomListModel: Removing room {room.object_name} from group {group.key}')
        try:
            del self.room_indices[room]
        except KeyError:
            print(f'Index {index} for room {room.object_name} not found in the index registry')
        
        self.begin_remove_rows(index.parent, index.row, index.row)
        group.rooms.remove(room)
        self.end_remove_rows()

        if len(group.rooms) == 0:
            # Update persistent indices with parents after the deleted one
            affected_indexes = self.prepare_persistent_index_change(group_position + 1, -1)

            self.begin_remove_rows([], group_position, group_position)
            del self.room_groups[group_position]
            self.end_remove_rows()

            self.change_persistent_index_list(affected_indexes[0], affected_indexes[1])

    def refresh(self, room: Quotient.Room, roles: List[int] = None) -> None:
        if roles is None:
            roles = []
        
        # The problem here is that the change might cause the room to change
        # its groups. Assume for now that such changes are processed elsewhere
        # where details about the change are available (e.g. in tagsChanged).
        def refresh_visitor(index: QtCore.QModelIndex) -> None:
            self.dataChanged.emit(index, index, roles)
            self.dataChanged.emit(index.parent, index.parent, roles)

        self.visit_room(room, refresh_visitor)

    def visit_room(self, room: Quotient.Room, visitor: Visitor) -> None:
        # Copy persistent indices because visitors may alter m_roomIndices
        indices = self.room_indices.values()
        for index in indices:
            room_at_index = self.room_at(index)
            if room_at_index == room:
                visitor(index)
            elif room_at_index is not None:
                print(f'Room at {index} is {self.room_at(index).object_name} instead of {room.object_name}')
            else:
                print(f'Room at index {index} not found')

    def room_at(self, index: QtCore.QModelIndex) -> Optional[Quotient.Room]:
        if self.is_valid_room_index(index):
            return self.room_groups[index.parent.row].rooms[index.row]
        return None

    def total_rooms(self) -> int:
        return functools.reduce(lambda c1, c2: len(c1.all_rooms()) + len(c2.all_rooms()), self.connections)

    def set_order(self, order: AbstractRoomOrdering) -> None:
        self.begin_reset_model()
        self.room_groups.clear()
        self.room_indices.clear()
        self.room_order = order
        self.end_reset_model()

        for connection in self.connections:
            self.room_order.connect_signals(connection)
            for room in connection.all_rooms():
                self.add_room_to_groups(room)
                self.room_order.connect_signals(room)

    def update_groups(self, room: Quotient.Room) -> None:
        groups = self.room_order.room_groups(room)
        old_room_index = self.room_indices[room] # TODO: should be multiple?

        group_index = old_room_index.parent()
        group = self.room_groups[group_index.row()]
        try:
            groups.remove(group.key)
            # The room still in this group but may need to move around
            # TODO: move rows if needed

            assert self.room_at(old_room_index) == room
        except ValueError:
            self.do_remove_room(old_room_index)

        if len(groups) > 0:
            self.add_room_to_groups(room, groups) # Groups the room wasn't before
        print(f"RoomListModel: groups for {room.object_name()} updated")

    def lower_bound_group(self, group_key: str, room = '') -> Optional[RoomGroup]:
        found_group = None
        for room_group in self.room_groups:
            if not self.room_order.group_less_than(room_group, group_key):
                found_group = room_group
                break
        if found_group is not None:
            return found_group
        else:
            if len(self.room_groups) == 0:
                return None
            return self.room_groups[len(self.room_groups) - 1]


    def lower_bound_room(self, group: RoomGroup, room: Quotient.Room):
        found_room = None
        for group_room in group.rooms:
            if not self.room_order.room_less_than(group_room, group.key):
                found_room = group_room
                break
        if found_room:
            return found_room
        else:
            if len(group.rooms) == 0:
                return None
            return group.rooms[len(group.rooms) - 1]

    def index(self, row: int, column: int, parent: QtCore.QModelIndex = QtCore.QModelIndex()):
        if not self.has_index(row, column, parent):
            return QtCore.QModelIndex()
        
        # Groups get internalId() == -1, rooms get the group ordinal number
        parent_row = -1
        if parent:
            parent_row = parent.row
        return self.create_index(row, column, parent_row)

    def parent(self, child: QtCore.QModelIndex):
        parent_pos = int(child.internal_id())
        # TODO: fix OverflowError (point to unexisting data?)
        # if child.is_valid() and parent_pos > -1:
        #     return self.index(parent_pos, 0)
        return QtCore.QModelIndex()

    def room_group_at(self, index: QtCore.QModelIndex):
        assert index.is_valid() # Root item shouldn't come here
        # If we're on a room, find its group; otherwise just take the index
        group_index = index
        if index.parent().is_valid():
            group_index = index.parent()
        try:
            return self.room_groups[group_index.row()].key
        except ValueError:
            return ''

    def index_of(self, group_key, room = None):
        if room is not None:
            index = self.room_indices.get(room, None)
            if group_key == '' and index != None:
                return index;
            
            for room_index in self.room_indices.keys():
                if self.room_groups[room_index.parent().row()].key == group_key:
                    return room_index
            return QtCore.QModelIndex()
        else:
            group = self.lower_bound_group(group_key)
            if group not in self.room_groups:
                # Group not found
                return QtCore.QModelIndex()
            return self.index(self.room_groups.index(group), 0)
