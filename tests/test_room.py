from PyQuotient import Quotient
from __feature__ import snake_case, true_property


def test_init():
    connection = Quotient.Connection()
    room = Quotient.Room(connection, 'room1', Quotient.JoinState.Join)
    assert isinstance(room, Quotient.Room)


def test_subclass():
    class PyRoom(Quotient.Room):
        ...

    connection = Quotient.Connection()
    room = PyRoom(connection, 'room1', Quotient.JoinState.Join)
    assert isinstance(room, PyRoom)
