import os, json5
import mysql.connector as ms

from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox,QErrorMessage ,QGroupBox, QFormLayout ,QGridLayout, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import pyqtSignal ,QSize

from style_sheet.boot_panel_style_sheet import style_sheet
from style_sheet.main_style_sheet import main_style_sheet

class BootPanel(QWidget):

    finished_signal = pyqtSignal(dict)
    quit_signal = pyqtSignal()

    def __init__(self):
        super(BootPanel, self).__init__()
        self.initializePanel()

        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet(style_sheet)
        self.adjustSize()


    def initializePanel(self):

        widget = QWidget()
        widget.setObjectName("main")
        widget.setContentsMargins(0, 0, 0, 0)

        # create title label
        title_label = QLabel("Classer System", widget)
        title_label.setObjectName("title-label")

        title_label.move(50, 50)

        # initialize the system connection form
        self.setUpConnectionForm(widget)

        # create close button for panel
        close_button = QPushButton("X", self.widget)
        close_button.setObjectName("red-btn")
        close_button.setFixedWidth(60)
        close_button.move(self.width() - close_button.width(), 0)
        close_button.pressed.connect(lambda: self.quit_signal.emit())


        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vbox)
        self.layout().addWidget(widget)

    def setUpConnectionForm(self, widget : QWidget):

        # create form layout
        form = QFormLayout()
        form.setSpacing(20)
        # form.setFormAlignment(Qt.AlignmentFlag.AlignHCenter)

        host_edit = QLineEdit()
        host_edit.setPlaceholderText("Host")

        user_edit = QLineEdit()
        user_edit.setPlaceholderText("User")
        pw_edit = QLineEdit()
        pw_edit.setPlaceholderText("Password")
        pw_edit.setEchoMode(QLineEdit.Password)

        test_connection_button = QPushButton("Test Connection")
        test_connection_button.setObjectName("link")
        test_connection_button.pressed.connect(lambda : self.testConnection(
            [host_edit.text(), user_edit.text(), pw_edit.text()]
        ))

        setUpFunction = lambda : self.setUpConnection(
            {
                "host" : host_edit.text(),
                "user" : user_edit.text(),
                "password" : pw_edit.text()
            }
        )

        connect_button = QPushButton("Connect")
        connect_button.setObjectName("connect-btn")
        connect_button.pressed.connect(setUpFunction)

        host_edit.returnPressed.connect(lambda: user_edit.setFocus())
        user_edit.returnPressed.connect(lambda : pw_edit.setFocus())
        pw_edit.returnPressed.connect(setUpFunction)

        form.addRow("Host", host_edit)
        form.addRow("User", user_edit)
        form.addRow("Password" , pw_edit)
        form.addWidget(test_connection_button)
        form.addWidget(connect_button)

        gr_box = QGroupBox(widget)
        gr_box.setTitle("Set Up Connection")
        gr_box.setLayout(form)

        gr_box.move(1000, 500)

    def testConnection(self, data : list[str]) -> None:

        # create temporal connection
        try:
            _connection = ms.connect(host=data[0], user=data[1], password=data[2])

            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("server connection status")
            if _connection.is_connected():
                msg_box.setText("""Server successfully connected\n
                                    \tMySQL version {}\n\t
                                         status : {}""".format(_connection.get_server_version(),
                                                               _connection.get_server_info()))

            else:
                msg_box.setText("Server connection unsuccessful.")
            # show message box
            msg_box.show()
            _connection.close()

        except Exception as ex:
            msg = QErrorMessage(self)
            msg.showMessage(str(ex))
            msg.show()



    def setUpConnection(self, data : dict[str , str]) -> None:

        try:
            _con = ms.connect(**data)
            if not _con.is_connected():
                err_msg = QErrorMessage(self)
                err_msg.showMessage("Database Server nor connected! please try again")
                return
        except ms.Error as ex:
            err_msg = QErrorMessage(self)
            err_msg.showMessage(str(ex))
            return


        if not os.path.exists("settings"):
            # save server settings to json file in setting directory
            os.mkdir("settings")

            data["database"] = "classer"
            with open(os.path.join("settings", "db_settings.json"), mode="w") as file:
                json5.dump(data, file, indent=4)

        # emit the finished signal
        self.finished_signal.emit(data)

if __name__ == "__main__":
    app = QApplication([])
    app.setStyleSheet(main_style_sheet)
    window = BootPanel()
    # window.showFullScreen()
    window.show()

    app.exec_()
