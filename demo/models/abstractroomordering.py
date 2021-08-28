from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING


from PySide6 import QtCore
from PyQuotient import Quotient
if TYPE_CHECKING:
    from demo.models.roomlistmodel import RoomListModel
from __feature__ import snake_case, true_property


class RoomGroup:
    SystemPrefix = "im.quotient."
    LegacyPrefix = "org.qmatrixclient."

    def __init__(self, key: str, rooms: Optional[List[Quotient.Room]] = None):
        self.key = key
        self.rooms: List[Quotient.Room] = []
        if rooms is not None:
            self.rooms = rooms

    def __eq__(self, o: object) -> bool:
        if isinstance(o, RoomGroup):
            return self.key == o.key
        return self.key == o
    
    def __repr__(self) -> str:
        return f"RoomGroup(key='{self.key}', len(rooms)={len(self.rooms)})"


RoomGroups = List[RoomGroup]


class AbstractRoomOrdering(QtCore.QObject):
    def __init__(self, model: RoomListModel) -> None:
        super().__init__(model)
        self.model = model

    def room_groups(self, room: Quotient.Room) -> RoomGroups:
        return []

    def update_groups(self, room: Quotient.Room) -> None:
        self.model.update_groups(room)
