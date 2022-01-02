from enum import Enum, auto
from PySide6 import QtCore, QtQml
from PyQuotient import Quotient
from __feature__ import snake_case, true_property


class EventRoles(Enum):
    EventTypeRole = QtCore.Qt.UserRole + 1
    EventIdRole = auto()
    TimeRole = auto()
    SectionRole = auto()
    AboveSectionRole = auto()
    AuthorRole = auto()
    AboveAuthorRole = auto()
    ContentRole = auto()
    ContentTypeRole = auto()
    HighlightRole = auto()
    SpecialMarksRole = auto()
    LongOperationRole = auto()
    AnnotationRole = auto()
    UserHueRole = auto()
    RefRole = auto()
    ReactionsRole = auto()
    EventResolvedTypeRole = auto()


class MessageEventModel(QtCore.QAbstractListModel):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def row_count(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()):
        # TODO: implement
        return 2

    def data(self, index: QtCore.QModelIndex, role: int):
        row = index.row()

        if not index.is_valid() or row >= self.row_count():
            return {}

        if role == QtCore.Qt.DisplayRole:
            return 'it\'s a test message!'

        if role == QtCore.Qt.ToolTipRole:
            # return evt.originalJson()
            return {}

        if role == EventRoles.AuthorRole.value:
            return {
                'avatarMediaId': 1 # TODO: user
            }
        
        if role == EventRoles.AnnotationRole.value:
            return 'annotation'

        if role == EventRoles.ReactionsRole.value:
            return []

        if role == EventRoles.SectionRole.value:
            return 'date' # TODO: render_date()
        return {}

    @QtCore.Slot(result='QVariant')
    def role_names(self):
        roles = super().role_names()

        roles[EventRoles.EventTypeRole.value] = b'eventType'
        roles[EventRoles.EventIdRole.value] = b'eventId'
        roles[EventRoles.TimeRole.value] = b'time'
        roles[EventRoles.SectionRole.value] = b'section'
        roles[EventRoles.AboveSectionRole.value] = b'aboveSection'
        roles[EventRoles.AuthorRole.value] = b'author'
        roles[EventRoles.AboveAuthorRole.value] = b'aboveAuthor'
        roles[EventRoles.ContentRole.value] = b'content'
        roles[EventRoles.ContentTypeRole.value] = b'contentType'
        roles[EventRoles.HighlightRole.value] = b'highlight'
        roles[EventRoles.SpecialMarksRole.value] = b'marks'
        roles[EventRoles.LongOperationRole.value] = b'progressInfo'
        roles[EventRoles.AnnotationRole.value] = b'annotation'
        roles[EventRoles.UserHueRole.value] = b'userHue'
        roles[EventRoles.EventResolvedTypeRole.value] = b'eventResolvedType'
        roles[EventRoles.RefRole.value] = b'refId'
        roles[EventRoles.ReactionsRole.value] = b'reactions'

        return roles
