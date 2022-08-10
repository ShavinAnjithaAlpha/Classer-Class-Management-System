from PyQt5.QtWidgets import QWidget, QLineEdit, QGridLayout, QLabel, QSizePolicy, QVBoxLayout, QFormLayout, QHBoxLayout, \
    QScrollArea
from PyQt5.QtCore import Qt, QDate

import datetime


class InfoCard(QWidget):
    def __init__(self, rows: int, details: dict = None, title: str = None, placeHolderText: str = None,
                 scroll=True):
        super(InfoCard, self).__init__()
        self.detail = details
        self.rows = rows
        self.title = title
        self.placeHolderText = placeHolderText
        self.scroll = scroll
        self.initializeUI()

        self.setObjectName("info-card")
        self.setMinimumWidth(800)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding))

    def initializeUI(self):

        self.widgets = list()

        self.gridLayout = QGridLayout()
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(5)

        self.setDetail(self.detail)

        vbox = QVBoxLayout()
        vbox.setSpacing(5)
        vbox.setContentsMargins(20, 10, 10, 10)

        if self.title:
            titleLabel = QLabel(self.title)
            titleLabel.setObjectName("title")
            vbox.addWidget(titleLabel)

        vbox.addLayout(self.gridLayout)
        if self.scroll:
            baseWidget = QScrollArea()
            baseWidget.setContentsMargins(0, 0, 0, 0)
            baseWidget.setWidgetResizable(True)
            baseWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            baseWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

            widget = QWidget()
            widget.setContentsMargins(0, 0, 0, 0)
            widget.setObjectName("base")
            widget.setLayout(vbox)
            baseWidget.setWidget(widget)

            vbox = QVBoxLayout()
            vbox.setContentsMargins(0, 0, 0, 0)
            self.setLayout(vbox)
            self.layout().addWidget(baseWidget)
        else:
            widget = QWidget()
            widget.setContentsMargins(0, 0, 0, 0)
            widget.setObjectName("base")
            widget.setLayout(vbox)

            vbox = QVBoxLayout()
            vbox.setContentsMargins(0, 0, 0, 0)
            self.setLayout(vbox)
            self.layout().addWidget(widget)
        self.setContentsMargins(0, 0, 0, 0)

    def setRows(self, row: int):

        self.rows = row
        self.setDetail(self.detail)

    def setDetail(self, detail: dict):

        if not detail:
            label = QLabel(self.placeHolderText)
            self.widgets.append(label)
            self.gridLayout.addWidget(label, 0, 0, alignment=Qt.AlignCenter)
            return

        self.detail = detail
        # clear the widgets
        [w.deleteLater() for w in self.widgets]
        self.widgets.clear()

        i = 0
        for key, value in self.detail.items():
            valueField = QLineEdit()
            if isinstance(value, datetime.datetime):
                valueField.setText(QDate.fromString(value.strftime("%Y-%m-%d"), "yyyy-MM-dd").toString("dd MMM yyyy"))
            valueField.setText(str(value))
            valueField.setReadOnly(True)
            valueField.setObjectName("value-field")

            keyLabel = QLabel(key)
            keyLabel.setObjectName("key-label")
            self.widgets.extend((valueField, keyLabel))

            self.gridLayout.addWidget(keyLabel, i % self.rows, i // self.rows * 2)
            self.gridLayout.addWidget(valueField, i % self.rows, i // self.rows * 2 + 1)
            i += 1
