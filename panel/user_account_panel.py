import mysql.connector as mysql

from PyQt5.QtWidgets import (QApplication, QWidget, QGridLayout, QGroupBox, QFormLayout, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel,
                             QMessageBox, QStackedWidget, QErrorMessage)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QDate, QTime

from style_sheet.boot_panel_style_sheet import style_sheet
from style_sheet.main_style_sheet import main_style_sheet

from util.security.access import AccessManager



global accessManager , connection

class UserAccountPanel(QWidget):

    finished_signal = pyqtSignal()
    quit_signal = pyqtSignal()

    def __init__(self, access_manager : AccessManager, _connection : mysql.MySQLConnection = None):
        super(UserAccountPanel, self).__init__()
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

        self.setUpAccountForm()

        # create date time labels
        self.time_label = QLabel(QTime.currentTime().toString("hh:mm"),self.widget)
        self.time_label.setObjectName("time-label")
        self.date_label = QLabel(QDate.currentDate().toString("dddd, MMM dd"), self.widget)
        self.date_label.setObjectName("date-label")
        self.time_label.move(30 ,20)
        self.date_label.move(20, self.time_label.height() + 170)

        # create close button for panel
        close_button = QPushButton("X", self.widget)
        close_button.setObjectName("red-btn")
        close_button.setFixedWidth(60)
        close_button.move(self.width() - close_button.width(), 0)
        close_button.pressed.connect(lambda: self.quit_signal.emit())

        # create timer for update time in every second
        timer = QTimer(self)
        timer.start(1000)
        timer.timeout.connect(self.updateDateTime)

        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vbox)
        vbox.addWidget(self.widget)

    def setUpAccountForm(self):

        self.stack_widget = QStackedWidget(self.widget)
        self.stack_widget.setMinimumWidth(500)

        # create login group box
        self.login_gr_box = QGroupBox("Create User Account")
        self.login_gr_box.setMinimumWidth(500)
        # create username and password fields
        self.email_edit = QLineEdit()
        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.confirm_password_edit = QLineEdit()

        self.error_msg = QLabel()
        self.error_msg.setStyleSheet("font-size : 18px; color : red;")

        self.username_edit.setPlaceholderText("Username")
        self.password_edit.setPlaceholderText("Password")
        self.confirm_password_edit.setPlaceholderText("Confirm Password")
        self.email_edit.setPlaceholderText("Email")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.confirm_password_edit.setEchoMode(QLineEdit.Password)

        self.email_edit.returnPressed.connect(lambda : self.username_edit.setFocus())
        self.username_edit.returnPressed.connect(lambda: self.password_edit.setFocus())
        self.password_edit.returnPressed.connect(lambda : self.confirm_password_edit.setFocus())
        self.confirm_password_edit.returnPressed.connect(self.checkData)

        next_button = QPushButton("Next")
        next_button.setContentsMargins(50, 0, 0, 15)
        # next_button.setObjectName("connect-btn")

        close_button = QPushButton("Close")
        close_button.pressed.connect(lambda : self.finished_signal.emit())

        log_grid = QGridLayout()
        log_grid.setSpacing(25)
        log_grid.addWidget(self.email_edit, 0, 0, 1, 2)
        log_grid.addWidget(self.username_edit, 1, 0, 1, 2)
        log_grid.addWidget(self.password_edit, 2, 0, 1, 2)
        log_grid.addWidget(self.confirm_password_edit, 3, 0, 1, 2)
        log_grid.addWidget(self.error_msg, 4, 0, 1, 2)
        log_grid.addWidget(next_button, 5, 0)
        log_grid.addWidget(close_button, 5, 1)

        log_grid.setColumnStretch(0, 6)

        next_button.pressed.connect(self.checkData)

        self.login_gr_box.setLayout(log_grid)
        self.stack_widget.addWidget(self.login_gr_box)
        self.stack_widget.move(int(self.width() * 0.5), int(self.height() * 0.4))

    def checkData(self):

        for w in [self.username_edit, self.email_edit, self.password_edit, self.confirm_password_edit]:
            if w.text() == "":
                self.error_msg.setText("please fill the fields")
                return

        if not self.password_edit.text() == self.confirm_password_edit.text():
            self.error_msg.setText("Password Confirmation failed!")
            return
        elif accessManager.isExistsByEmail(self.email_edit.text()):
            self.error_msg.setText("email already used!")
            return
        elif accessManager.isExistsByUsername(self.username_edit.text()):
            self.error_msg.setText("username already used!")
            return
        elif accessManager.isPasswordDuplicate(self.password_edit.text()):
            self.error_msg.setText("Choose another password!")
            return

        self.moveAdminPanel()


    def moveAdminPanel(self):

        # create password field
        admin_pw_edit = QLineEdit()
        admin_pw_edit.setPlaceholderText("Admin Password")
        admin_pw_edit.setEchoMode(QLineEdit.Password)

        text = QLabel("To create user account you need administrator authentication. admin needs to enter his password to successful admin authentication.")
        text.setStyleSheet("color : rgba(255, 255, 255, 0.7);")
        text.setWordWrap(True)

        create_acc_button = QPushButton("Create Account")
        create_acc_button.pressed.connect(lambda e = admin_pw_edit : self.userAccountAuthenticate(e))

        cancel_button = QPushButton("Cancel")
        cancel_button.pressed.connect(lambda : self.stack_widget.setCurrentWidget(self.login_gr_box))


        auth_gr_box = QGroupBox("Admin Authentication", parent=self.widget)
        grid = QGridLayout()
        grid.setSpacing(20)

        grid.addWidget(text, 0, 0, 1, 2)
        grid.addWidget(QLabel("Admin.\nPassword"), 1, 0)
        grid.addWidget(admin_pw_edit, 1, 1)
        grid.addWidget(create_acc_button, 2, 1)
        grid.addWidget(cancel_button, 2, 0)

        grid.setColumnStretch(0, 4)
        grid.setColumnStretch(1, 6)

        auth_gr_box.setLayout(grid)
        self.stack_widget.addWidget(auth_gr_box)
        self.stack_widget.setCurrentWidget(auth_gr_box)


    def userAccountAuthenticate(self, password_edit : QLineEdit):

        if not accessManager.adminAuthentication(password_edit.text()):
            QMessageBox.warning(self, "Admin Authentication", "Admin Authentication Failed!")
            return

        try:
            data = {
                "email" : self.email_edit.text(),
                "username" : self.username_edit.text(),
                "password" : self.password_edit.text()
            }
            user_id = accessManager.createUser(**data)
            QMessageBox.information(self, "New User Account", f"Create user account successfully.\nUser Id : {user_id}\nUsername : {data['username']}")
            # emit the finished signal
            self.finished_signal.emit()

        except Exception as ex:
            err = QErrorMessage(self)
            err.showMessage(str(ex))

    def updateDateTime(self):

        self.time_label.setText(QTime.currentTime().toString("hh:mm"))
        self.date_label.setText(QDate.currentDate().toString("dddd, MMM dd"))

if __name__ == "__main__":
    app = QApplication([])
    app.setStyleSheet(main_style_sheet)
    window = UserAccountPanel(None)
    window.show()

    app.exec_()


