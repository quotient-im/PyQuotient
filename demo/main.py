import sys

from PySide6 import QtWidgets
from __feature__ import snake_case, true_property

from demo.mainwindow import MainWindow



def start():
    app = QtWidgets.QApplication([])

    widget = MainWindow()
    widget.resize(400, 300)
    widget.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    start()
