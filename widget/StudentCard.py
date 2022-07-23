from PyQt5.QtWidgets import QWidget, QLineEdit, QGridLayout,QLabel, QSizePolicy,QVBoxLayout, QFormLayout, QHBoxLayout, QScrollArea
from PyQt5.QtCore import Qt, QDate

from widget.info_card import InfoCard

import datetime

class StudentCard(InfoCard):

    def setDetail(self, detail : dict):

        if not detail:
            label = QLabel(self.placeHolderText)
            self.gridLayout.addWidget(label, 0, 0 ,alignment=Qt.AlignCenter)
            self.widgets.append(label)
            return

        self.detail = detail
        [w.deleteLater() for w in self.widgets]
        self.widgets.clear()

        iconLabel = QLabel(f"{self.detail['First Name'][0]}{self.detail['Last Name']}".upper())
        iconLabel.setObjectName("profile-label")

        nameLabel = QLabel(f"{self.detail['First Name']} {self.detail['Last Name']}")
        nameLabel.setObjectName("name-label")

        idLabel = QLabel(f"ID {self.detail['Student ID']}")
        userNameLabel = QLabel(f"@{self.detail['Username']}")
        userNameLabel.setObjectName("user-label")

        self.widgets.extend([iconLabel, nameLabel, idLabel, userNameLabel])

        for key in ["First Name", "Last Name", "Username", "Password", "Student ID"]:
            self.detail.pop(key)

        self.gridLayout.setVerticalSpacing(5)
        self.gridLayout.addWidget(iconLabel, 0, 0)
        self.gridLayout.addWidget(nameLabel, 0 ,1)
        self.gridLayout.addWidget(userNameLabel, 1, 1, alignment=Qt.AlignTop)
        self.gridLayout.addWidget(idLabel, 0, 3)

        subGrid = QGridLayout()
        self.gridLayout.addLayout(subGrid, 2, 0, 1, 4)

        i = 0
        for key, value in self.detail.items():
            valueField = QLineEdit(str(value))
            if isinstance(value, datetime.datetime):
                valueField.setText(QDate.fromString(value.strftime("%Y-%m-%d"), "yyyy-MM-dd").toString("dd MMM yyyy"))
            valueField.setReadOnly(True)
            valueField.setObjectName("value-field")

            keyLabel = QLabel(key)
            keyLabel.setObjectName("key-label")

            self.widgets.extend([keyLabel, valueField])
            subGrid.addWidget(keyLabel, i % self.rows, i // self.rows * 2)
            subGrid.addWidget(valueField, i % self.rows, i // self.rows * 2 + 1)

            i += 1