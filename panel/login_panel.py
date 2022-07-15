import mysql.connector as mysql

from PyQt5.QtWidgets import (QApplication, QWidget, QGridLayout, QGroupBox, QFormLayout, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel,
                             QMessageBox, QErrorMessage)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QTimer, QDate, QTime

from style_sheet.boot_panel_style_sheet import style_sheet
from style_sheet.main_style_sheet import main_style_sheet

from util.security.access import AccessManager



global accessManager , connection

class LoginPanel(QWidget):

    finished_signal = pyqtSignal()
    user_account_signal = pyqtSignal()
    quit_signal = pyqtSignal()

    def __init__(self, access_manager : AccessManager, _connection : mysql.MySQLConnection = None):
        super(LoginPanel, self).__init__()
        global accessManager, connection
        accessManager = access_manager
        connection = _connection

        self.resize(self.screen().size())
        self.initializeUI()
        self.setStyleSheet(style_sheet)

    def initializeUI(self):

        self.widget = QWidget()
        self.widget.setObjectName("main")
        self.widget.setContentsMargins(0, 0, 0, 0)

        self.setUpLogGrid()

        # create date time labels
        self.time_label = QLabel(QTime.currentTime().toString("hh:mm"),self.widget)
        self.time_label.setObjectName("time-label")
        self.date_label = QLabel(QDate.currentDate().toString("dddd, MMM dd"), self.widget)
        self.date_label.setObjectName("date-label")
        self.time_label.move(20 ,20)
        self.date_label.move(20, self.time_label.height() + 170)

        # create close button for panel
        close_button = QPushButton("X", self.widget)
        close_button.setFixedWidth(60)
        close_button.move(self.width() - close_button.width(), 0)
        close_button.pressed.connect(lambda : self.quit_signal.emit())

        # create timer for update time in every second
        timer = QTimer(self)
        timer.start(1000)
        timer.timeout.connect(self.updateDateTime)

        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vbox)
        vbox.addWidget(self.widget)

    def setUpLogGrid(self):
        # create login group box
        login_gr_box = QGroupBox("Login To System", parent=self.widget)
        # create username and password fields
        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()

        self.username_edit.setPlaceholderText("Username")
        self.password_edit.setPlaceholderText("Password")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.username_edit.setFocus()
        self.username_edit.setContentsMargins(0, 0, 0, 25)

        self.username_edit.returnPressed.connect(lambda: self.password_edit.setFocus())
        self.password_edit.returnPressed.connect(self.loggedToSystem)

        # other buttons to login forms
        reset_password_button = QPushButton("Forger Password")
        reset_password_button.setObjectName("link")

        user_acc_button = QPushButton("Create User Account")
        user_acc_button.setObjectName("link")
        user_acc_button.pressed.connect(lambda : self.user_account_signal.emit())

        login_button = QPushButton("Login")
        login_button.setObjectName("connect-btn")
        login_button.pressed.connect(self.loggedToSystem)

        log_grid = QGridLayout()
        log_grid.setSpacing(10)
        log_grid.addWidget(self.username_edit, 0, 0, 1, 2)
        log_grid.addWidget(self.password_edit, 1, 0, 1, 2)
        log_grid.addWidget(reset_password_button, 2, 0)
        log_grid.addWidget(user_acc_button, 3, 1)
        log_grid.addWidget(login_button, 4, 0, 1, 2)

        login_gr_box.setLayout(log_grid)
        login_gr_box.move(int(self.width() * 0.7), int(self.height() * 0.5))

    def loggedToSystem(self):

        if self.username_edit.text() == "":
            QMessageBox.warning(self, "System logging", "Please enter the username")
            return

        username = self.username_edit.text()
        password = self.password_edit.text()

        try:
            if accessManager.logToSystem(username, password):
                self.finished_signal.emit()
            else:
                QMessageBox.warning(self, "System Logging", "Access Denied :(")
        except mysql.Error as ex:
            err = QErrorMessage(self)
            err.showMessage(str(ex))

    def updateDateTime(self):

        self.time_label.setText(QTime.currentTime().toString("hh:mm"))
        self.date_label.setText(QDate.currentDate().toString("dddd, MMM dd"))

if __name__ == "__main__":
    app = QApplication([])

    window = LoginPanel(None)
    app.setStyleSheet(main_style_sheet)
    window.show()

    app.exec_()


