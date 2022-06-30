from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QGridLayout, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtCore import Qt, QSize

from style_sheet.boot_panel_style_sheet import style_sheet

class BootPanel(QWidget):
    def __init__(self):
        super(BootPanel, self).__init__()
        self.initializePanel()
        self.setStyleSheet(style_sheet)

    def initializePanel(self):
        widget = QWidget()
        widget.setObjectName("main")
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(widget)

if __name__ == "__main__":
    app = QApplication([])
    window = BootPanel()
    window.show()

    app.exec_()
