import json

from PyQt5.QtWidgets import (QApplication, QDialog, QGroupBox, QFormLayout, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel,
                             QMessageBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont

from util.security.access import AccessManager

from style_sheet.main_style_sheet import main_style_sheet

class AdminDialog(QDialog):
    def __init__(self, parent = None, access_manager : AccessManager = None):
        super(AdminDialog, self).__init__(parent)
        self.access_manager = access_manager
        self.setModal(True)
        self.resize(500, 400)
        self.setWindowTitle("User Profile Dialog")

        self.initializeUI()
        self.show()

    def initializeUI(self):

        self.required_fileds = []

        # create the three group for this
        basic_group = QGroupBox("Basic Info")
        self.setUpBasicBox(basic_group)

        # create the institute group
        institute_group = QGroupBox("Institute Info")
        self.setUpInstituteBox(institute_group)

        # create the personal contact group
        personal_contact_group = QGroupBox("Personal Contacts")
        self.setUpContactBox(personal_contact_group)

        # create the security box
        security_box  = QGroupBox("Security")
        self.setUpSecurityBox(security_box)

        # create the buttons
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")

        save_button.pressed.connect(self.accept)
        cancel_button.pressed.connect(self.reject)

        hbox = QHBoxLayout()
        hbox.addWidget(save_button)
        hbox.addWidget(cancel_button)

        vbox = QVBoxLayout()
        vbox.addWidget(basic_group)
        vbox.addWidget(institute_group)
        vbox.addWidget(personal_contact_group)
        vbox.addWidget(security_box)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

    def setUpBasicBox(self, group : QGroupBox):

        # create the fields
        self.first_name_entry = QLineEdit()

        self.last_name_entry = QLineEdit()

        self.qualify_entry = QLineEdit()

        self.user_name_entry = QLineEdit()

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)

        form.addRow("First Name", self.first_name_entry)
        form.addRow("Last Name", self.last_name_entry)
        form.addRow("Qualifiers", self.qualify_entry)
        form.addRow("User Name", self.user_name_entry)
        form.addWidget(QLabel("*user name must be a one word without white spaces"))

        group.setLayout(form)

        [self.required_fileds.append(i) for i in (self.first_name_entry, self.last_name_entry,
                                                  self.qualify_entry, self.user_name_entry)]

    def setUpInstituteBox(self, group : QGroupBox):

        self.ins_name_entry  = QLineEdit()
        self.ins_address_entry = QLineEdit()
        self.ins_address_entry.returnPressed.connect(lambda :self.ins_number_entry.setFocus())
        self.ins_number_entry  = QLineEdit()

        self.ins_number_entry.setInputMask("xxx-xx xx xxx")

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.addRow("Institute Name", self.ins_name_entry)
        form.addRow("Address", self.ins_address_entry)
        form.addRow("Institute Contact Number(LAN)", self.ins_number_entry)

        group.setLayout(form)

        [self.required_fileds.append(i) for i in (self.ins_name_entry, self.ins_address_entry, self.ins_number_entry)]

    def setUpContactBox(self, group : QGroupBox):


        self.per_number = QLineEdit()
        self.per_number.setInputMask("xxx-xx xx xxx")

        self.email_entry = QLineEdit()
        self.whatsapp_entry = QLineEdit()
        self.whatsapp_entry.setInputMask("xxx-xx xx xxx")

        self.ins_number_entry.returnPressed.connect(lambda: self.per_number.setFocus())
        self.per_number.returnPressed.connect(lambda : self.whatsapp_entry.setFocus())
        self.whatsapp_entry.returnPressed.connect(lambda : self.email_entry.setFocus())

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.addRow("Personal Contact Number", self.per_number)
        form.addRow("Whatsapp Number" ,self.whatsapp_entry)
        form.addRow("Class Email Address", self.email_entry)

        group.setLayout(form)

        [self.required_fileds.append(i) for i in (self.per_number, self.email_entry, self.whatsapp_entry)]

    def setUpSecurityBox(self, group : QGroupBox):

        def enableConfirm(text):
            if not self.enter_pw_confirm.isEnabled():
                self.enter_pw_confirm.setEnabled(True)

        def enablePin(text):
            if not self.exit_pin_cofirm.isEnabled():
                self.exit_pin_cofirm.setEnabled(True)

        self.enter_pw = QLineEdit()
        self.enter_pw.setEchoMode(QLineEdit.EchoMode.Password)
        self.enter_pw.textChanged.connect(enableConfirm)

        self.enter_pw_confirm = QLineEdit()
        self.enter_pw_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.enter_pw_confirm.setEnabled(False)

        self.exit_pin = QLineEdit()
        self.exit_pin.setEchoMode(QLineEdit.EchoMode.Password)
        self.exit_pin.setInputMask("xxxxx")
        self.exit_pin.textChanged.connect(enablePin)

        self.exit_pin_cofirm = QLineEdit()
        self.exit_pin_cofirm.setEnabled(False)
        self.exit_pin_cofirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.exit_pin_cofirm.setInputMask("xxxxx")

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.addWidget(QLabel("*Password must be least 8 character with numbers and alphabetic"))
        form.addRow("Logging Password", self.enter_pw)
        form.addRow("Confirm Password", self.enter_pw_confirm)
        form.addWidget(QLabel(""))
        form.addWidget(QLabel("pin must be a 5 numbers"))
        form.addRow("pin", self.exit_pin)
        form.addRow("confirm pin", self.exit_pin_cofirm)

        group.setLayout(form)

        [self.required_fileds.append(i) for i in (self.enter_pw, self.exit_pin)]

    def accept(self) -> None:

        for edit in self.required_fileds:
            if edit.text() == "" or edit.text() == "   -         ":
                edit.setFocus()
                return

        if self.user_name_entry.text().isspace():
            self.user_name_entry.setFocus()
            return

        if self.enter_pw.text() != self.enter_pw_confirm.text():
            self.enter_pw_confirm.setText("")
            self.enter_pw.setEchoMode(QLineEdit.EchoMode.Password)
            self.enter_pw_confirm.setFocus()
            return

        if self.exit_pin.text() != self.exit_pin_cofirm.text():
            self.exit_pin_cofirm.setText("")
            self.exit_pin.setEchoMode(QLineEdit.Password)
            self.exit_pin_cofirm.setFocus()

        # collect the data to dictionary
        data = {
            "First Name" : self.first_name_entry.text(),
            "Last Name" : self.last_name_entry.text(),
            "Quality" : self.qualify_entry.text(),
            "username" : self.user_name_entry.text(),

            "Institute Name" : self.ins_name_entry.text(),
            "Institute Address" : self.ins_address_entry.text(),
            "Institute Number(LAN)" : self.ins_number_entry.text(),

            "Personal Telephone Number" : self.per_number.text(),
            "WhatsApp Contact" : self.whatsapp_entry.text(),
            "Email" : self.email_entry.text(),

            "password" : self.enter_pw.text(),
            "pin" : int(self.exit_pin.text())
        }

        self.access_manager.saveAdminData(data)

        QMessageBox.information(self, "Admin Profile", "Admin Profile Update Successful", QMessageBox.StandardButton.Ok)

        super().accept()
        return data


if __name__ == "__main__":
    app = QApplication([])
    app.setStyleSheet(main_style_sheet)
    window = AdminDialog()
    app.exec_()
