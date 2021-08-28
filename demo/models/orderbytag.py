from typing import Any, List, Union
from demo.models.abstractroomordering import AbstractRoomOrdering, RoomGroup
from PyQuotient import Quotient
from __feature__ import snake_case, true_property


Invite = RoomGroup.SystemPrefix + "invite"
DirectChat = RoomGroup.SystemPrefix + "direct"
Untagged = RoomGroup.SystemPrefix + "none"
Left = RoomGroup.SystemPrefix + "left"

InvitesLabel = "The caption for invitations"
FavouritesLabel = "Favourites"
LowPriorityLabel = "Low priority"
ServerNoticeLabel = "Server notices"
DirectChatsLabel = "The caption for direct chats"
UngroupedRoomsLabel = "Ungrouped rooms"
LeftLabel = "The caption for left rooms"


def tag_to_caption(tag: str) -> str:
    if tag == Quotient.FavouriteTag:
        return FavouritesLabel
    elif tag == Quotient.LowPriorityTag:
        return LowPriorityLabel
    elif Quotient.ServerNoticeTag:
        return ServerNoticeLabel
    elif tag.startswith('u.'):
        return tag[2:]
    return tag


def caption_to_tag(caption: str):
    if caption == FavouritesLabel:
        return Quotient.FavouriteTag
    elif caption == LowPriorityLabel:
        return Quotient.LowPriorityTag
    elif caption == ServerNoticeLabel:
        return Quotient.ServerNoticeTag
    elif caption.startswith('m.') or caption.startswith('u.'):
        return caption
    return f'u.{caption}'


def find_index(item_list: List[Any], value):
    try:
        return item_list[item_list.index(value)]
    except ValueError:
        return item_list[-1]


def find_index_with_wildcards(item_list: List[str], value: str):
    if len(item_list) == 0 or len(value) == 0:
        return len(item_list)
    
    index = item_list.index(value)
    # Try namespace groupings (".*" in the list), from right to left
    dot_pos = 0
    i = 0
    while not (i == len(item_list)):
        i = find_index(item_list, value[:dot_pos + 1] + '*')
        try:
            dot_pos = value.rindex('.', dot_pos - 1)
        except ValueError:
            break;
    return i


class OrderByTag(AbstractRoomOrdering):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.tags_order: List[str] = self.init_tags_order()

    def init_tags_order(self):
        return [
            Invite,
            Quotient.FavouriteTag,
            "u.*",
            DirectChat,
            Untagged,
            Quotient.LowPriorityTag,
            Left
        ]

    def connect_signals(self, obj: Union[Quotient.Connection, Quotient.Room]) -> None:
        if isinstance(obj, Quotient.Connection):
            obj.directChatsListChanged.connect(lambda additions, removals: self.on_conn_direct_chats_list_changed(obj, additions, removals))
        elif isinstance(obj, Quotient.Room):
            obj.displaynameChanged.connect(lambda: self.update_groups(obj))
            obj.tagsChanged.connect(lambda: self.update_groups(obj))
            obj.joinStateChanged.connect(lambda: self.update_groups(obj))

    def on_conn_direct_chats_list_changed(self, conn, additions, removals):
        # The same room may show up in removals and in additions if it
        # moves from one userid to another (pretty weird but encountered
        # in the wild). Therefore process removals first.
        for room_id in removals:
            room = conn.room(room_id)
            if room:
                self.update_groups(room)

        for room_id in additions:
            room = conn.room(room_id)
            if room:
                self.update_groups(room)

    def update_groups(self, room: Quotient.Room) -> None:
        super().update_groups(room)

        # As the room may shadow predecessors, need to update their groups too.
        pred_room = room.predecessor() # TODO: 'Quotient.JoinState.Join' error: predecessor takes no arguments
        if pred_room:
            self.update_groups(pred_room)

    def group_label(group: RoomGroup) -> str:
        caption = tag_to_caption(group.key)
        if group.key == Untagged:
            caption = UngroupedRoomsLabel
        elif group.key == Invite:
            caption = InvitesLabel
        elif group.key == DirectChat:
            caption = DirectChatsLabel
        elif group.key == Left:
            caption = LeftLabel

        return f"{caption} ({len(group.rooms)} room(s))"

    def group_less_than(self, group1: RoomGroup, group2_key: str) -> bool:
        lkey = group1.key
        rkey = group2_key
        li = find_index_with_wildcards(self.tags_order, lkey)
        ri = find_index_with_wildcards(self.tags_order, rkey)
        return li < ri or (li == ri and lkey < rkey)

    def room_groups(self, room: Quotient.Room):
        if room.join_state == Quotient.JoinState.Invite:
            return [Invite]
        if room.join_state == Quotient.JoinState.Leave:
            return [Left]
        
        tags = self.get_filtered_tags(room)
        if len(tags) == 0:
            tags.insert(0, Untagged)
        # Check successors, reusing room as the current frame, and for each group
        # shadow this room if there's already any of its successors in the group
        successor_room = room.successor() # TODO: Quotient.JoinState.Join
        while successor_room is not None:
            successor_tags = self.get_filtered_tags(successor_room)

            if len(successor_tags) == 0:
                tags.remove(Untagged)
            else:
                for tag in successor_tags:
                    if tag in tags:
                        tags.remove(tag)
            
            if len(tags) == 0:
                return [] # No remaining groups, hide the room

            successor_room = room.successor() # TODO: Quotient.JoinState.Join
        return tags
    
    def get_filtered_tags(self, room: Quotient.Room) -> List[str]:
        all_tags = room.tag_names
        if room.is_direct_chat():
            all_tags.append(DirectChat)
        
        result: List[str] = []
        for tag in all_tags:
            if find_index_with_wildcards(self.tags_order, '-' + tag) == len(self.tags_order):
                result.append(tag) # Only copy tags that are not disabled
        return result

    def room_less_than(self, group_key: str, room1: Quotient.Room, room2: Quotient.Room):
        if room1 == room2:
            return False # 0. Short-circuit for coinciding room objects

        # 1. Compare tag order values
        tag = group_key
        order1 = room1.tag(tag).order
        order2 = room2.tag(tag).order
        if type(order2) != type(order1):
            return not order2 == None
        
        if order1 and order2:
            # Compare floats; fallthrough if neither is smaller
            if order1 < order2:
                return True
            
            if order1 > order2:
                return False

        # 2. Neither tag order is less than the other; compare room display names
        if room1.display_name != room2.display_name:
            return room1.display_name < room2.display_name

        # 3. Within the same display name, order by room id
        # (typically the case when both display names are completely empty)
        if room1.id != room2.id:
            return room1.id < room2.id
        
        # 4. Room ids are equal; order by connections (=userids)
        connection1 = room1.connection
        connection2 = room2.connection
        if connection1 != connection2:
            if connection1.user_id != connection2.user_id:
                return connection1.user_id < connection2.user_id
            
            # 4a. Two logins under the same userid: pervert, but technically correct
            return connection1.access_token < connection2.access_token
        
        # 5. Assume two incarnations of the room with the different join state
        # (by design, join states are distinct within one connection+roomid)
        return room1.join_state < room2.join_state
