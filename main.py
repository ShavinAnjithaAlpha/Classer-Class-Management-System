import os , sys

import json5
import mysql.connector as mysql

from util.security.access import AccessManager
from util.logger import Logger

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QStackedLayout, QErrorMessage, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent

from panel.system_bootup_panel import BootPanel
from panel.admin_data_panel import AdminDataPanel
from panel.login_panel import LoginPanel
from panel.user_account_panel import UserAccountPanel

from system_entry import SystemPanel
########################### enf of import statements ############################

# globally defined main connection and access manager instance
global connection, logger, accessManager

connection : mysql.MySQLConnection = mysql.connect()
logger : Logger = Logger(connection)
accessManager = AccessManager(connection)
# attach the loger to access manager
accessManager.attachLogger(logger)

######################### end of global variables declaring #####################

class Classer(QMainWindow):
    def __init__(self):
        super(Classer, self).__init__()
        self.initializeUI()

        self.showFullScreen()
        self.show()

    def initializeUI(self):

        self.login_panel ,self.user_account_panel, self.system_panel = None, None, None

        # create stack layout
        self.stackLayout = QStackedLayout()
        self.stackLayout.setContentsMargins(0, 0, 0, 0)

        # check if settings dir is exists or not
        if os.path.exists("settings"):

            # setup connection first
            self.setConnectionParams()

            self.login_panel = LoginPanel(accessManager, connection)
            self.login_panel.finished_signal.connect(self.loggedToSystem)
            self.login_panel.user_account_signal.connect(self.createUserAccount)
            self.login_panel.quit_signal.connect(self.close)

            self.stackLayout.addWidget(self.login_panel)
            self.stackLayout.setCurrentWidget(self.login_panel)
        else:
            boot_panel = BootPanel()
            boot_panel.finished_signal.connect(self.initializeSystem)
            boot_panel.quit_signal.connect(self.close)
            self.stackLayout.addWidget(boot_panel)


        widget = QWidget()
        widget.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(self.stackLayout)
        self.setCentralWidget(widget)
        self.setContentsMargins(0, 0, 0, 0)

    def setConnectionParams(self):

        with open("settings/db_settings.json", "r") as file:
            data = json5.load(file)

        try:
            connection.connect(**data)
        except mysql.Error as ex:
            err = QErrorMessage(self)
            err.showMessage(str(ex))

    def initializeSystem(self, connection_data : dict[str, str]) -> None:

        while True:
            try:
                # update the connection
                connection.connect(**connection_data)
                # initialize the Database and logs directory
                accessManager.initializeSystem(server=connection_data["host"], user=connection_data["user"] ,
                                               password=connection_data["password"])
                break
            except Exception as ex:
                err_msg = QErrorMessage(self)
                err_msg.showMessage(str(ex))
                continue

        # create a admin profile panel for collect admin profile data
        admin_profile_form = AdminDataPanel(self, access_manager=accessManager)
        admin_profile_form.finished_signal.connect(self.loginSystem)
        self.stackLayout.addWidget(admin_profile_form)
        self.stackLayout.setCurrentWidget(admin_profile_form)

    def loginSystem(self):

        # create login panel
        self.login_panel = LoginPanel(accessManager, connection)
        self.stackLayout.addWidget(self.login_panel)
        self.stackLayout.setCurrentWidget(self.login_panel)

        self.login_panel.finished_signal.connect(self.loggedToSystem)
        self.login_panel.user_account_signal.connect(self.createUserAccount)
        self.login_panel.quit_signal.connect(self.close)

    def loggedToSystem(self):

        self.system_panel = SystemPanel(connection, logger, accessManager)
        self.system_panel.quitSignal.connect(self.close)
        self.system_panel.logoutSignal.connect(self.logout)

        self.stackLayout.addWidget(self.system_panel)
        self.stackLayout.setCurrentWidget(self.system_panel)

    def createUserAccount(self):

        if self.user_account_panel:
            self.user_account_panel.deleteLater()

        self.user_account_panel = UserAccountPanel(accessManager, connection)
        self.stackLayout.addWidget(self.user_account_panel)
        self.stackLayout.setCurrentWidget(self.user_account_panel)

        self.user_account_panel.finished_signal.connect(lambda : self.stackLayout.setCurrentWidget(self.login_panel))
        self.user_account_panel.quit_signal.connect(self.close)

    def logout(self):

        self.stackLayout.removeWidget(self.system_panel)
        self.stackLayout.setCurrentWidget(self.login_panel)

        self.system_panel.deleteLater()

    def close(self) -> bool:

        if QMessageBox.question(self, "Quit System", "Are you sure to shutdown the system?",
                                QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            # end session if session exists
            if accessManager.session:
                accessManager.endSession()
            QApplication.quit()

    def keyPressEvent(self, event : QKeyEvent) -> None:

        if event.key() == Qt.Key_Escape:
            self.close()

if __name__ == '__main__':
   app = QApplication(sys.argv)
   with open("style_sheet/main.css", "r") as file:
       style_sheet = file.read()

   app.setStyleSheet(style_sheet)
   window = Classer()

   app.exec_()
