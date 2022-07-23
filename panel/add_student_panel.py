import datetime

from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QFormLayout, QGroupBox, QVBoxLayout, QPushButton,
                             QLabel, QDateEdit, QRadioButton, QLineEdit, QComboBox, QButtonGroup, QMessageBox,
                             QApplication , QGridLayout)
from PyQt5.QtCore import Qt, QSize, QDateTime, QDate
from PyQt5.QtGui import QKeyEvent, QPainter, QPen, QColor
from PyQt5.QtChart import QChartView, QChart, QValueAxis, QLineSeries, QBarSeries, QBarSet, QDateTimeAxis, QCategoryAxis

from util.manager.student_manager import StudentManager
from style_sheet.main_style_sheet import main_style_sheet

from datetime import datetime
from model.student_model import StudentModel

class StudentAddPanel(QWidget):
    def __init__(self, student_model : StudentModel):
        super(StudentAddPanel, self).__init__()
        self.studentModel = student_model
        self.initializeUI() # render the widget

        self.setObjectName("add-student-panel")

    def initializeUI(self):

        # create title label
        titleLabel = QLabel("Register New Student")
        titleLabel.setObjectName("title")

        # create left and right sides
        hbox = QHBoxLayout()
        hbox.addWidget(self.createLeft())
        hbox.addWidget(self.createRight())

        vbox = QVBoxLayout()
        vbox.addWidget(titleLabel)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

    def createLeft(self) -> QGroupBox:

        # set up the dialog
        basic_info_group = QGroupBox("Basic Info")
        self.setUpBasicGroup(basic_info_group)

        contact_group = QGroupBox("Contact")
        self.setUpContactGroup(contact_group)

        account_group = QGroupBox("Student Account Info")
        self.setUpAccountGroup(account_group)

        # create the id label
        self.id_label = QLabel()
        self.id_label.setObjectName("id-label")
        # create the buttons for dialog
        clear_button = QPushButton("Clear")
        clear_button.pressed.connect(self.clearFields)
        submit_button = QPushButton("Register Student")
        submit_button.pressed.connect(self.registered)

        hbox = QHBoxLayout()
        hbox.addWidget(submit_button)
        hbox.addWidget(clear_button)

        vbox = QVBoxLayout()
        vbox.addSpacing(30)
        vbox.addWidget(basic_info_group)
        vbox.addWidget(contact_group)
        vbox.addWidget(account_group)
        vbox.addWidget(self.id_label)
        vbox.addLayout(hbox)

        # for item in [basic_info_group, account_group, contact_group]:
        #     item.setMaximumWidth(700)

        groupBox = QGroupBox("Student Register Form", self)
        groupBox.setMaximumWidth(700)
        groupBox.setLayout(vbox)
        return groupBox

    def setUpBasicGroup(self, group : QGroupBox):

        # create the fields
        self.first_name_entry = QLineEdit()
        self.first_name_entry.returnPressed.connect(lambda : self.last_name_entry.setFocus())

        self.last_name_entry = QLineEdit()
        self.last_name_entry.returnPressed.connect(lambda : self.address_entry.setFocus())

        self.address_entry = QLineEdit()
        self.address_entry.returnPressed.connect(lambda : self.school_entry.setFocus())

        self.school_entry = QComboBox()
        try:
            schools = set(self.studentModel.studentManager.getValuesFromKey("school"))
            self.school_entry.addItems(schools)
        except:
            self.school_entry.addItems(["", ])

        self.school_entry.setEditable(True)
        # self.school_entry.keyPressEvent = lambda e : self.birthday_edit.setFocus() if e.key() == QKeyEvent.Enter else self.school_entry.text

        # birthday edit
        self.birthday_edit = QDateEdit()
        self.birthday_edit.setCalendarPopup(True)

        # create the radio buttons for choose sex
        male_radio = QRadioButton("Male")
        male_radio.setChecked(True)

        female_radio = QRadioButton("FeMale")
        other_radio = QRadioButton("Other")

        # create the button group for set exclsuive to radios
        self.radio_group = QButtonGroup()
        self.radio_group.addButton(male_radio, 0)
        self.radio_group.addButton(female_radio, 1)
        self.radio_group.addButton(other_radio, 2)

        hbox  = QHBoxLayout()
        hbox.addWidget(male_radio)
        hbox.addWidget(female_radio)
        hbox.addWidget(other_radio)

        # create the form for packed them
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignCenter)

        form.addRow("First Name", self.first_name_entry)
        form.addRow("Last Name", self.last_name_entry)
        form.addRow("Address", self.address_entry)
        form.addRow("School", self.school_entry)
        form.addRow("Birth Day", self.birthday_edit)
        form.addRow("Sex", hbox)

        group.setLayout(form)


    def setUpContactGroup(self, group : QGroupBox):

        # create the telephone numbers edits
        self.tel_number_edit = QLineEdit()
        self.tel_number_edit.setInputMask("xxx-xx xx xxx")
        self.tel_number_edit.returnPressed.connect(lambda  : self.parent_tel_edit.setFocus())

        self.parent_tel_edit = QLineEdit()
        self.parent_tel_edit.setInputMask("xxx-xx xx xxx")

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)

        form.addRow("Student Contact Number", self.tel_number_edit)
        form.addRow("Parent Contact Number", self.parent_tel_edit)

        group.setLayout(form)

    def setUpAccountGroup(self, group = QGroupBox):

        # create username fields
        self.username_edit = QLineEdit()
        self.username_edit.returnPressed.connect(lambda : self.password_edit.setFocus())

        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.returnPressed.connect(lambda : self.password_confirmation_edit.setFocus())

        self.password_confirmation_edit = QLineEdit()
        self.password_confirmation_edit.setEchoMode(QLineEdit.Password)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)

        form.addRow("Username", self.username_edit)
        form.addRow("Password", self.password_edit)
        form.addRow("Confirm Password", self.password_confirmation_edit)

        group.setLayout(form)

    def registered(self) -> None:

        # check the all required data is filled
        if self.first_name_entry.text() == "":
            self.first_name_entry.setFocus()
            return
        if self.last_name_entry.text() == "":
            self.last_name_entry.setFocus()
            return
        if self.address_entry.text() == "":
            self.address_entry.setFocus()
            return
        if self.school_entry.currentText() == "":
            self.school_entry.setFocus()
            return
        if self.parent_tel_edit.text() == "":
            self.parent_tel_edit.setFocus()
            return

        if self.password_edit.text() == "" or not self.password_edit.text() == self.password_confirmation_edit.text():
            self.password_edit.setFocus()
            return

        sex = "male" if self.radio_group.checkedId() == 0 else "female"
        # build the data
        self.data = {"firstName" : self.first_name_entry.text().strip(),
                "lastName" : self.last_name_entry.text().strip(),
                "address" : self.address_entry.text().strip(),
                "school" : self.school_entry.currentText().strip(),
                "parent_contact" : self.parent_tel_edit.text(),
                "student_contact" : self.tel_number_edit.text(),
                "birthDay" : self.birthday_edit.date().toString("yyyy-MM-dd"),
                "sex" : sex,
                "username" : self.username_edit.text().strip(),
                "password" : self.password_edit.text()

            }

        try:
            student_id = self.studentModel.studentManager.addStudent(self.data)
            self.id_label.setText(f"{self.data['firstName']} {self.data['lastName']} Index No.: {student_id}")
            self.id_label.setVisible(True)

            QMessageBox.information(self, "New Student Added", "Student Added Successful",
                                    QMessageBox.StandardButton.Ok)
            # fill the count labels
            self.countIncrement()
            # update the charts
            self.updateChart()

        except Exception as ex:
            QMessageBox.warning(self, "Regsiter New Student", str(ex))

    def clearFields(self):

        # clear all fileds
        for widget in (self.first_name_entry, self.last_name_entry, self.address_entry, self.tel_number_edit,
                       self.parent_tel_edit, self.username_edit, self.password_edit, self.password_confirmation_edit):
            widget.clear()

        self.school_entry.clearEditText()
        # focus to first name entry
        self.first_name_entry.setFocus()




    # right side render and processing methods
    def createRight(self) -> QGroupBox:

        # create registered student count labels
        self.totalStudentLabel = QLabel()
        self.lastMonthStudentLabel = QLabel()
        self.lastDayStudentLabel = QLabel()
        self.fillCount() # fill  these labels using store data

        countGroupBox = QGroupBox("Student Statics")
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        countGroupBox.setLayout(form)
        # add labels to group box
        for field, label in {"Total Students" : self.totalStudentLabel,
                             "Total Students (Registered Last Month)" : self.lastMonthStudentLabel,
                             "Total Students (Registered Last Day)" : self.lastDayStudentLabel}.items():
            fieldLabel = QLabel(field)
            fieldLabel.setObjectName("field-label")
            form.addRow(fieldLabel, label)
            label.setObjectName("static-label")
            label.setAlignment(Qt.AlignRight)


        # create main right side layout
        vbox = QVBoxLayout()
        vbox.addWidget(countGroupBox)
        vbox.addWidget(self.createChartView())
        vbox.addStretch()

        groupBox = QGroupBox("Registered Students Statics", self)
        groupBox.setLayout(vbox)
        return groupBox

    def fillCount(self):

        # fill  the count labels
        self.totalStudentLabel.setText(f"{self.studentModel.studentManager.studentCount()}")
        self.lastMonthStudentLabel.setText(f"{self.studentModel.studentManager.lastMonthStudentCount()}")
        self.lastDayStudentLabel.setText(f"{self.studentModel.studentManager.lastDayStudentCount()}")

    def countIncrement(self):

        self.totalStudentLabel.setText(f"{int(self.totalStudentLabel.text()) + 1}")
        self.lastMonthStudentLabel.setText(f"{int(self.lastMonthStudentLabel.text()) + 1}")
        self.lastDayStudentLabel.setText(f"{int(self.lastDayStudentLabel.text()) + 1}")

    def createChartView(self) -> QGroupBox:

        # create chart view and chart instance
        chartView = QChartView()
        self.countChart = QChart()
        self.countChart.setTitle("Registered Students Statics")
        self.countChart.setAnimationOptions(QChart.AllAnimations)
        self.countChart.setTheme(QChart.ChartThemeLight)
        chartView.setChart(self.countChart)
        chartView.setRenderHints(QPainter.Antialiasing)

        # create tool box widgets
        self.durationComboBox = QComboBox()
        self.durationComboBox.setToolTip("Duration which used to determine charts date range")
        self.durationComboBox.addItems(["All Time", "Last Year", "Last Month"])
        self.durationComboBox.setCurrentText("Last Month")
        self.durationComboBox.currentTextChanged.connect(self.updateChart)

        self.intervalComboBox = QComboBox()
        self.intervalComboBox.addItems(["Days", "Months"])
        self.intervalComboBox.currentTextChanged.connect(self.updateChart)

        self.chartTypeComboBox = QComboBox()
        self.chartTypeComboBox.addItems(["Line Chart", "Bar Chart"])
        self.chartTypeComboBox.setCurrentText("Line Chart")
        self.chartTypeComboBox.currentTextChanged.connect(self.updateChart)

        # create chart
        self.updateChart()

        grid = QGridLayout()
        grid.addWidget(QLabel("Duration"), 0, 0, alignment=Qt.AlignRight)
        grid.addWidget(self.durationComboBox, 0, 1)
        grid.addWidget(QLabel("Chart Type"), 0, 2, alignment=Qt.AlignRight)
        grid.addWidget(self.chartTypeComboBox, 0, 3)
        grid.addWidget(chartView, 1, 0, 1, 4)

        groupBox = QGroupBox("Graphical Statics")
        groupBox.setLayout(grid)
        return groupBox

    def updateChart(self):

        if self.chartTypeComboBox.currentText() == "Line Chart":
            self.renderLineChart()
        else:
            self.renderBarChart()

    def renderBarChart(self):

        # first clear the chart area
        self.countChart.removeAllSeries()
        for axes in self.countChart.axes(Qt.Horizontal): self.countChart.removeAxis(axes)
        for axes in self.countChart.axes(Qt.Vertical): self.countChart.removeAxis(axes)

        # load the data
        data = self.loadData()

        # create bar series
        barSet = QBarSet("Student Count")
        barSet.append([item[0] for item in data])
        barSet.setColor(QColor.fromRgb(0, 250, 100))
        barSeries = QBarSeries()
        barSeries.append(barSet)

        # create default axis
        axisX = QDateTimeAxis()
        axisX.setTitleText("Date")
        axisX.setLabelsAngle(45)
        axisX.setRange(QDateTime.fromString(data[0][1].strftime("%Y-%m-%d"), "yyyy-MM-dd"),
                       QDateTime.fromString(data[-1][1].strftime("%Y-%m-%d"), "yyyy-MM-dd"))
        axisX.setFormat("dd MMM")
        self.countChart.addAxis(axisX, Qt.AlignBottom)
        self.countChart.setAxisX(axisX, barSeries)

        axisY = QValueAxis()
        axisY.setRange(0, max(map(lambda e : e[0] , data)))
        axisY.setTickInterval(1)
        axisY.setLabelFormat("%d")
        self.countChart.addAxis(axisY, Qt.AlignLeft)
        self.countChart.setAxisY(axisY, barSeries)

        # add to the chart
        self.countChart.addSeries(barSeries)

    def renderLineChart(self):

        # first clear the chart area
        self.countChart.removeAllSeries()
        for axes in self.countChart.axes(Qt.Horizontal) : self.countChart.removeAxis(axes)
        for axes in self.countChart.axes(Qt.Vertical) : self.countChart.removeAxis(axes)

        # create new line series
        lineSeries = QLineSeries()
        lineSeries.setName("Student registered count line chart")
        lineSeries.setPen(QPen(QColor.fromRgb(0, 0, 255), 3))
        lineSeries.setPointLabelsColor(QColor.fromRgb(0, 255, 255))
        lineSeries.setPointLabelsFormat("%d")

        # load the data
        data = self.loadData()

        # fill line series with these data
        max = -1
        for count, date in data:
            date = QDateTime.fromString(date.strftime("%Y-%m-%d"), "yyyy-MM-dd")
            lineSeries.append(date.toMSecsSinceEpoch(), count)
            if max < count:
                max = count

        # create default axis
        axisX = QDateTimeAxis()
        axisX.setTitleText("Date")
        axisX.setLabelsAngle(45)
        axisX.setRange(QDateTime.fromString(data[0][1].strftime("%Y-%m-%d"), "yyyy-MM-dd"),
                       QDateTime.fromString(data[-1][1].strftime("%Y-%m-%d"), "yyyy-MM-dd"))
        axisX.setFormat("dd MMM yyyy")
        self.countChart.addAxis(axisX, Qt.AlignBottom)
        self.countChart.setAxisX(axisX, lineSeries)

        axisY = QValueAxis()
        axisY.setRange(0, max)
        axisY.setTickInterval(1)
        axisY.setLabelFormat("%d")
        self.countChart.addAxis(axisY, Qt.AlignLeft)
        self.countChart.setAxisY(axisY, lineSeries)

        # add to the chart
        self.countChart.addSeries(lineSeries)

    def loadData(self):

        if self.durationComboBox.currentText() == "All Time":
            return self.studentModel.studentManager.countByGroup()
        elif self.durationComboBox.currentText() == "Last Year":
            return self.studentModel.studentManager.lastYear()
        else:
            return self.studentModel.studentManager.lastMonth()


if __name__ == "__main__":
    app = QApplication([])
    app.setStyleSheet(main_style_sheet)
    window = StudentAddPanel()
    app.exec_()