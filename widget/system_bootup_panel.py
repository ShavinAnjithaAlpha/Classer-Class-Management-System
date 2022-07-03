import os, json5
import mysql.connector as ms

from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox ,QGroupBox, QFormLayout ,QGridLayout, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtCore import pyqtSignal

from style_sheet.boot_panel_style_sheet import style_sheet
from style_sheet.main_style_sheet import main_style_sheet

class BootPanel(QWidget):

    finished_signal = pyqtSignal()

    def __init__(self):
        super(BootPanel, self).__init__()
        self.initializePanel()

        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet(style_sheet)

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

        # exit button
        exit_button = QPushButton("X", widget)
        exit_button.move(0, 0)
        exit_button.setObjectName("red-btn")
        exit_button.pressed.connect(lambda : QApplication.exit(0))


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
        except Exception as ex:
            ex_msg = str(ex)

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("server connection status")
        if _connection.is_connected():
            msg_box.setText("""Server successfully connected\n
                             MySQL version {}\n
                             status : {}""".format(_connection.get_server_version(),
                                                  _connection.get_server_info()))

        else:
            msg_box.setText("Server connection unsuccessful.")
        # show message box
        msg_box.exec_()
        msg_box.show()

    def setUpConnection(self, data : dict[str , str]) -> None:

        if not os.path.exists("settings"):
            # save server settings to json file in setting directory
            os.mkdir("settings")

            data["database"] = "classer"
            with open(os.path.join("settings", "db_settings.json"), mode="w") as file:
                json5.dump(data, file, indent=4)

        # emit the finished signal
        self.finished_signal.emit()

if __name__ == "__main__":
    app = QApplication([])
    app.setStyleSheet(main_style_sheet)
    window = BootPanel()
    window.showFullScreen()
    window.show()

    app.exec_()
