from enum import Flag
from PySide6 import QtCore
from .PyQuotient import Quotient
from __feature__ import snake_case, true_property


class EventStatus(QtCore.QObject):

    @QtCore.QFlag
    class Code(Flag):
        Normal = 0x00 #< No special designation
        Submitted = 0x01 #< The event has just been submitted for sending
        FileUploaded = 0x02 #< The file attached to the event has been
                             # uploaded to the server
        Departed = 0x03 #< The event has left the client
        ReachedServer = 0x04 #< The server has received the event
        SendingFailed = 0x05 #< The server could not receive the event
        Redacted = 0x08 #< The event has been redacted
        Replaced = 0x10 #< The event has been replaced
        Hidden = 0x100


Quotient.EventStatus = EventStatus
