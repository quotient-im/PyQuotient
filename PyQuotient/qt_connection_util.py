from typing import Callable, List

from PySide6 import QtCore


def connect_single_shot(signal: QtCore.SignalInstance, slot: Callable, slot_arg_types: List[type] = []):
    @QtCore.Slot(*slot_arg_types)
    def help_slot(*args, **kwargs):
        slot(*args, **kwargs)
        signal.disconnect(help_slot)

    signal.connect(help_slot)
