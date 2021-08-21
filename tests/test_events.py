from PyQuotient import Quotient
from __feature__ import snake_case, true_property


def test_event_init():
    event = Quotient.Event(1, {'a': 'b'})
    assert isinstance(event, Quotient.Event)


def test_roomevent_init():
    room_event = Quotient.RoomEvent(1, {'a': 'b'})
    assert isinstance(room_event, Quotient.RoomEvent)


def test_stateeventbase_init():
    state_event_base = Quotient.StateEventBase(1, {'a': 'b'})
    assert isinstance(state_event_base, Quotient.StateEventBase)
