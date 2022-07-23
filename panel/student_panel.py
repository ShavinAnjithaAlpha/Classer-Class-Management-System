import typing

from PyQt5.QtWidgets import (QWidget, QPushButton, QTableView, QCheckBox, QRadioButton, QLineEdit, QLabel, QHBoxLayout,
                             QGridLayout, QHeaderView, QVBoxLayout, QMenu, QGroupBox, QButtonGroup,QActionGroup, QAction)
from PyQt5.QtCore import Qt, QSize, QSortFilterProxyModel, QRegularExpression, QModelIndex
from PyQt5.QtGui import QPixmap

from model.student_model import StudentModel
from panel.section_panel import SectionPanel
from panel.add_student_panel import StudentAddPanel

from widget.info_card import InfoCard

class StudentPanel(SectionPanel):

    sections = ["Add Student", "Student Table", "Student Search", "Update Student"]
    title = "Student Manager"
    section_id = 0

    def __init__(self, connection , logger, access_manager, current_sub_section_id : int = 0, parent = None):
        # create student data model instance for this
        self.studentModel = StudentModel(connection, logger)
        super(StudentPanel, self).__init__(self.section_id, self.sections, self.title, current_sub_section_id, parent,
                                           connection_ = connection, logger_=logger, access_manager_=access_manager)

    def createSubPanel(self, panel_id : int):
        """
        reimplement the createSubPanel method for customize the panels for student panel
        :param panel_id: int
        :return: None
        """

        if panel_id == 0:
            return StudentAddPanel(self.studentModel)
        elif panel_id == 1:
            return self.createTablePanel()
        else:
            return QLabel()

    def createTablePanel(self) -> QWidget:

        titleLabel = QLabel("Student Data")
        titleLabel.setObjectName("title")

        # create proxy model for wrap the main student model
        self.proxyStudentModel = QSortFilterProxyModel()
        self.proxyStudentModel.setSourceModel(self.studentModel)

        # create table view
        self.tableView = QTableView()
        self.tableView.setModel(self.proxyStudentModel)
        # self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableView.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableView.setMinimumHeight(500)
        self.tableView.setSortingEnabled(True)

        self.tableView.clicked.connect(self.displayStudent)

        # hide the password column
        self.tableView.hideColumn(self.studentModel.fields.index("Password"))


        # create search bar and other widgets
        self.searchBar = QLineEdit()
        self.searchBar.resize(700, 35)
        self.searchBar.setPlaceholderText("Search Students")
        self.searchBar.textChanged.connect(self.search)


        searchLabel = QLabel()
        searchLabel.setPixmap(QPixmap("resources/icons/search.png").scaled(QSize(35, 35), Qt.KeepAspectRatio, Qt.FastTransformation))
        # create search field
        self.filterOptionBtton = QPushButton("")
        self.filterOptionGroup = QActionGroup(self)
        self.filterOptionGroup.setExclusive(True)
        self.filterOptionGroup.triggered.connect(self.setFilterOption)

        filterMenu = QMenu()

        for filed in self.studentModel.fields:
            radioButton = QAction(filed)
            radioButton.setCheckable(True)
            self.filterOptionGroup.addAction(radioButton)
            filterMenu.addAction(radioButton)
        self.filterOptionBtton.setMenu(filterMenu)

        self.filterOptionGroup.actions()[0].setChecked(True)
        self.setFilterOption()

        # create column hide panel
        self.columnHideButton = QPushButton("Select Field")
        self.columnHideGroup = QActionGroup(self)
        self.columnHideGroup.setExclusive(False)

        self.columnRadioList = []

        columnHideMenu = QMenu()
        for field in self.studentModel.fields:
            if field == "Password":
                continue
            radioAction = QAction(field)
            radioAction.setCheckable(True)
            radioAction.setChecked(True)
            self.columnRadioList.append(radioAction)
            self.columnHideGroup.addAction(radioAction)
            columnHideMenu.addAction(radioAction)

        self.columnHideButton.setMenu(columnHideMenu)
        self.columnHideGroup.triggered.connect(self.setHideOption)

        # create additional feature widgets
        self.caseSensitiveSearchBox = QCheckBox("Case Sensitive Search")
        self.caseSensitiveSearchBox.setChecked(False)
        self.caseSensitiveSearchBox.stateChanged.connect(self.search)

        self.anyRadioButton = QRadioButton("Anywhere")
        self.startsWithRadioButton = QRadioButton("Start With")
        self.endWithRadioButton = QRadioButton("Ends With")
        self.fixedradioButton = QRadioButton("Fixed")

        self.searchPlaceRadioGroup = QButtonGroup(self)
        self.searchPlaceRadioGroup.addButton(self.anyRadioButton, 0)
        self.searchPlaceRadioGroup.addButton(self.startsWithRadioButton, 1)
        self.searchPlaceRadioGroup.addButton(self.endWithRadioButton, 2)
        self.searchPlaceRadioGroup.addButton(self.fixedradioButton, 3)
        self.searchPlaceRadioGroup.setExclusive(True)
        self.anyRadioButton.setChecked(True)
        # set the slots
        self.searchPlaceRadioGroup.buttonClicked.connect(lambda e : self.search())

        hbox = QHBoxLayout()
        for radio in self.searchPlaceRadioGroup.buttons() : hbox.addWidget(radio)
        hbox.addStretch()
        groupBox = QGroupBox("Search Placings")
        groupBox.setLayout(hbox)


        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(self.searchBar, 0, 0, 1, 2)
        grid.addWidget(self.filterOptionBtton, 0, 2)
        grid.addWidget(QLabel("show/hide"), 0, 3, alignment=Qt.AlignRight)
        grid.addWidget(self.columnHideButton, 0, 4, alignment=Qt.AlignLeft)
        grid.addWidget(self.caseSensitiveSearchBox, 1, 0)
        grid.addWidget(groupBox, 1, 1, alignment=Qt.AlignLeft)

        searchOptionGroup = QGroupBox("Searching and Filtering Option")
        searchOptionGroup.setLayout(grid)

        # create student details card
        self.selectedStudentCard = InfoCard(4)

        vbox = QVBoxLayout()
        vbox.addWidget(titleLabel)
        vbox.addWidget(searchOptionGroup)
        vbox.addWidget(self.tableView)
        vbox.addWidget(self.selectedStudentCard)

        widget = QWidget()
        widget.setLayout(vbox)
        widget.setObjectName("student-panel")
        return widget

    def setFilterOption(self):

        self.filterOptionBtton.setText(self.filterOptionGroup.checkedAction().text())
        self.search()

    def setHideOption(self):

        for radio in self.columnRadioList:
            if radio.isChecked():
                self.tableView.showColumn(self.studentModel.fields.index(radio.text()))
            else:
                self.tableView.hideColumn(self.studentModel.fields.index(radio.text()))

    def search(self):

        text = self.searchBar.text()
        if text == "":
            self.proxyStudentModel.invalidate()
            self.proxyStudentModel.invalidateFilter()
            self.proxyStudentModel.setFilterRegularExpression(None)
            self.proxyStudentModel.beginResetModel()
            return

        sensitivity = Qt.CaseSensitive if self.caseSensitiveSearchBox.isChecked() else Qt.CaseInsensitive
        self.proxyStudentModel.setFilterRegularExpression(self.getRegExp(text))
        self.proxyStudentModel.setFilterCaseSensitivity(sensitivity)
        self.proxyStudentModel.setFilterKeyColumn(self.studentModel.fields.index(
            self.filterOptionGroup.checkedAction().text()
        ))

    def getRegExp(self, text : str) -> typing.Any:

        placeID = self.searchPlaceRadioGroup.checkedId()
        if placeID == 0:
            return f"{text}"
        elif placeID == 1:
            return QRegularExpression(f"^{text}")
        elif placeID == 2:
            return QRegularExpression(f"{text}$")
        else:
            return QRegularExpression(f"^{text}$")


    def displayStudent(self, index : QModelIndex):

        self.selectedStudentCard.setDetail(self.studentModel._dataSet[index.row()])