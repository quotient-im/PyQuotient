import sys

from PySide6 import QtCore, QtWidgets
from __feature__ import snake_case, true_property
# from PySide6.support.__feature__ import snake_case, true_property


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.hello = ["Hallo Welt", "Hei maailma", "Hola Mundo", "Привет мир"]

        self.button = QtWidgets.QPushButton("Click me!")
        print(QtCore.Qt.AlignCenter)
        self.text_label = QtWidgets.QLabel("Hello World")
                                     #alignment=QtCore.Qt.AlignCenter)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.add_widget(self.text_label)
        self.layout.add_widget(self.button)

        self.button.clicked.connect(self.magic)

    @QtCore.Slot()
    def magic(self):
        self.text_label.text = "abra cadabra"
        print(1)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec_())
