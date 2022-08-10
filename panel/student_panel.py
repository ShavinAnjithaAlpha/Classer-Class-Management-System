import datetime
import typing, re

from PyQt5.QtWidgets import (QWidget, QPushButton, QProgressBar, QTableView, QCheckBox, QRadioButton, QLineEdit, QLabel,
                             QHBoxLayout, QScrollArea,
                             QGridLayout, QHeaderView, QVBoxLayout, QMenu, QGroupBox, QButtonGroup, QActionGroup,
                             QAction, QComboBox, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt, QSize, QSortFilterProxyModel, QRegularExpression, QModelIndex, QThread, pyqtSignal, \
    QThreadPool
from PyQt5.QtGui import QPixmap

from model.student_model import StudentModel
from panel.section_panel import SectionPanel
from panel.add_student_panel import StudentAddPanel

from util.time_engine import DateTimeUtil

from widget.StudentCard import StudentCard


class StudentSearcher(QThread):
    resultChanged = pyqtSignal(StudentCard)
    progressChanged = pyqtSignal(float)
    finished = pyqtSignal()

    def __init__(self, keyWord: str, model: StudentModel, searchField: str, filterOptions: dict, groupField):
        super(StudentSearcher, self).__init__()
        self.searchKeyWord = keyWord
        self.model = model
        self.searchField = searchField
        self.filterOptions = filterOptions
        self.groupFiled = groupField

    def run(self) -> None:

        # first apply the filter to student model data set
        dataSet = self.model._dataSet
        if self.filterOptions:
            # apply sex filter
            if not self.filterOptions["Sex"] == "All":
                dataSet = list(filter(lambda e: e["Sex"] == self.filterOptions["Sex"].lower(), dataSet))
            self.progressChanged.emit(0.1)

            # apply school filter
            if not self.filterOptions["School"] == "All School":
                dataSet = list(filter(lambda e: e["School"] == self.filterOptions["School"], dataSet))
            self.progressChanged.emit(0.2)

            # apply grade filter
            if not self.filterOptions["Grade"] == -1:
                dataSet = list(filter(self.checkGrade, dataSet))
            self.progressChanged.emit(0.3)

            # apply time filter
            if not self.filterOptions["Registered At"] == "All Time":
                dataSet = list(filter(self.checkTime, dataSet))


        # now process the search operations
        length = len(dataSet)
        for i, student in enumerate(dataSet):
            if self.searchKeyWord.lower() in str(student[self.searchField]).lower():
                # create student card and return it
                self.resultChanged.emit(StudentCard(4, student, scroll=False))
            self.progressChanged.emit(0.3 + i / length * 0.7)

        self.finished.emit()

    def checkGrade(self, student: dict) -> bool:

        if self.filterOptions["Grade"] == -2:
            return DateTimeUtil.gradeFromDate(student["Birthday"]) > 13
        else:
            return DateTimeUtil.gradeFromDate(student["Birthday"]) == int(self.filterOptions["Grade"])

    def checkTime(self, student : dict) -> bool:

        if self.filterOptions["Registered At"] == "Last Year":
            return student['Registered At'].year == datetime.datetime.now().year
        elif self.filterOptions["Registered At"] == "Last Month":
            return student["Registered At"].month == datetime.datetime.now().month and student["Registered At"].year == datetime.datetime.now().year
        else:
            return True


class StudentPanel(SectionPanel):
    sections = ["Add Student", "Student Table", "Student Search", "Update Student"]
    title = "Student Manager"
    section_id = 0

    def __init__(self, connection, logger, access_manager, current_sub_section_id: int = 0, parent=None):
        # create student data model instance for this
        self.studentModel = StudentModel(connection, logger)
        super(StudentPanel, self).__init__(self.section_id, self.sections, self.title, current_sub_section_id, parent,
                                           connection_=connection, logger_=logger, access_manager_=access_manager)

    def createSubPanel(self, panel_id: int):
        """
        reimplement the createSubPanel method for customize the panels for student panel
        :param panel_id: int
        :return: None
        """

        if panel_id == 0:
            return StudentAddPanel(self.studentModel)
        elif panel_id == 1:
            return self.createTablePanel()
        elif panel_id == 2:
            return self.createStudentSearchPanel()
        else:
            return QLabel()



    # design and develop student table panel UI and its processing side methods
    def createTablePanel(self) -> QWidget:

        titleLabel = QLabel("Student Data")
        titleLabel.setObjectName("title")

        # create proxy model for wrap the main student model
        self.proxyStudentModel = QSortFilterProxyModel()
        self.proxyStudentModel.setSourceModel(self.studentModel)
        self.proxyStudentModel.setSortCaseSensitivity(Qt.CaseSensitive)

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

        # create student details card
        self.selectedStudentCard = StudentCard(3, title="Selected Student", placeHolderText="No Student")

        vbox = QVBoxLayout()
        vbox.addWidget(titleLabel)
        vbox.addWidget(self.createSearchOptionBox())
        vbox.addWidget(self.tableView)
        vbox.addWidget(self.selectedStudentCard)

        widget = QWidget()
        widget.setLayout(vbox)
        widget.setObjectName("student-panel")
        return widget

    def createSearchOptionBox(self) -> QGroupBox:

        # create search bar and other widgets
        self.searchBar = QLineEdit()
        self.searchBar.resize(700, 35)
        self.searchBar.setPlaceholderText("Search Students")
        self.searchBar.textChanged.connect(self.search)

        searchLabel = QLabel()
        searchLabel.setPixmap(
            QPixmap("resources/icons/search.png").scaled(QSize(35, 35), Qt.KeepAspectRatio, Qt.FastTransformation))
        searchLabel.setBuddy(self.searchBar)

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
        self.searchPlaceRadioGroup.buttonClicked.connect(lambda e: self.search())

        hbox = QHBoxLayout()
        for radio in self.searchPlaceRadioGroup.buttons(): hbox.addWidget(radio)
        hbox.addStretch()
        groupBox = QGroupBox("Search Placings")
        groupBox.setLayout(hbox)

        # create sort option fields
        sortButton = QPushButton("Sort")
        sortFieldMenu = QMenu()
        sortButton.setMenu(sortFieldMenu)
        sortButton.pressed.connect(self.sort)

        # create action group
        self.sortOptionGroup = QActionGroup(self)
        self.sortOptionGroup.setExclusive(True)
        self.sortOptionGroup.triggered.connect(self.sort)

        for field in self.studentModel.fields:
            action = QAction(field)
            action.setCheckable(True)
            self.sortOptionGroup.addAction(action)
            sortFieldMenu.addAction(action)

        self.sortOptionGroup.actions()[0].setChecked(True)

        # ascending or descending option
        self.sortOrderComboBox = QComboBox()
        self.sortOrderComboBox.addItems(["Asc", "Desc"])
        self.sortOrderComboBox.currentTextChanged.connect(lambda e: self.sort())

        self.sortSaceSensitiveCheckBox = QCheckBox("Case Sensitive")
        self.sortSaceSensitiveCheckBox.setChecked(True)
        self.sortSaceSensitiveCheckBox.stateChanged.connect(lambda e: self.sort())

        hbox2 = QHBoxLayout()
        hbox2.addWidget(sortButton)
        hbox2.addWidget(self.sortOrderComboBox)
        hbox2.addWidget(self.sortSaceSensitiveCheckBox)
        sortGroupBox = QGroupBox("Sort Options")
        sortGroupBox.setLayout(hbox2)

        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(self.searchBar, 0, 0, 1, 2)
        grid.addWidget(self.filterOptionBtton, 0, 2)
        grid.addWidget(QLabel("show/hide"), 0, 3, alignment=Qt.AlignRight)
        grid.addWidget(self.columnHideButton, 0, 4, alignment=Qt.AlignLeft)
        grid.addWidget(self.caseSensitiveSearchBox, 1, 0)
        grid.addWidget(groupBox, 1, 1, alignment=Qt.AlignLeft)
        grid.addWidget(sortGroupBox, 1, 2, 1, 3)

        searchOptionGroup = QGroupBox("Searching and Sorting Options")
        searchOptionGroup.setLayout(grid)

        return searchOptionGroup

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

        """
        search through student source data model using student filter sort proxy model
        on search option widgets current values

        :return: None
        """

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

    def getRegExp(self, text: str) -> typing.Any:

        placeID = self.searchPlaceRadioGroup.checkedId()
        if placeID == 0:
            return f"{text}"
        elif placeID == 1:
            return QRegularExpression(f"^{text}")
        elif placeID == 2:
            return QRegularExpression(f"{text}$")
        else:
            return QRegularExpression(f"^{text}$")

    def displayStudent(self, index: QModelIndex):

        # first map the index to source model index
        index = self.proxyStudentModel.mapToSource(index)
        self.selectedStudentCard.setDetail(self.studentModel._dataSet[index.row()])

    def sort(self):

        """
        sort the proxy model using sort order and sort fields

        :return: None
        """

        # first get sort fields
        sortField = self.sortOptionGroup.checkedAction().text()
        sortOrder = self.sortOrderComboBox.currentText()
        self.proxyStudentModel.setSortCaseSensitivity(
            Qt.CaseSensitive if self.sortSaceSensitiveCheckBox.isChecked() else Qt.CaseInsensitive)

        self.proxyStudentModel.sort(self.studentModel.fields.index(sortField),
                                    Qt.AscendingOrder if sortOrder == "Asc" else Qt.DescendingOrder)



    # design and develop the student search panel UI and its processing events
    def createStudentSearchPanel(self) -> QWidget:

        titleLabel = QLabel("Search Students")
        titleLabel.setObjectName("title")

        # create search result add layout
        self.searchResultLayout = QVBoxLayout()
        self.searchResultLayout.setSpacing(0)
        # create search result widget list
        self.searchResultWidgets = []

        searchResultWidget = QWidget()
        searchResultWidget.setLayout(self.searchResultLayout)

        # create scroll area for add search results
        resultScrollArea = QScrollArea()
        resultScrollArea.setWidgetResizable(True)
        resultScrollArea.setWidget(searchResultWidget)
        resultScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # create progress bar area
        self.searchProgressBar = QProgressBar()
        self.searchProgressBar.setMinimum(0)
        self.searchProgressBar.setMaximum(100)

        self.statusLabel = QLabel()
        hbox = QHBoxLayout()
        hbox.addWidget(self.searchProgressBar)
        hbox.addWidget(self.statusLabel)
        hbox.addStretch()

        self.studentDisplayMethodCheckBox = QCheckBox("Shortest Mode for Display Students")

        # create vbox layout for packing all widgets
        vbox = QVBoxLayout()
        vbox.addWidget(titleLabel)
        vbox.addWidget(self.studentDisplayMethodCheckBox, alignment=Qt.AlignRight)
        vbox.addWidget(self.createSearchOptionPanel())
        vbox.addWidget(self.createFilterOptionBox())
        vbox.addWidget(self.createCategaryBox())
        vbox.addWidget(resultScrollArea, stretch=5)
        vbox.addLayout(hbox)

        widget = QWidget()
        widget.setObjectName("student-search-panel")
        widget.setLayout(vbox)
        return widget

    def createSearchOptionPanel(self) -> QGroupBox:

        self.studentSearchBar = QLineEdit()
        self.studentSearchBar.resize(600, 30)
        self.studentSearchBar.setPlaceholderText("Search Students")
        self.studentSearchBar.setClearButtonEnabled(True)
        self.studentSearchBar.returnPressed.connect(self.populateStudents)

        self.searchFieldMenu = QComboBox()
        self.searchFieldMenu.addItems(self.studentModel.fields)

        searchButton = QPushButton("Search")
        searchButton.pressed.connect(self.populateStudents)

        grid = QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.addWidget(QLabel("Search"), 0, 0, alignment=Qt.AlignLeft)
        grid.addWidget(self.studentSearchBar, 1, 0, 1, 2)
        grid.addWidget(QLabel("Search Field"), 0, 2, alignment=Qt.AlignLeft)
        grid.addWidget(self.searchFieldMenu, 1, 2)
        grid.addWidget(searchButton, 1, 3)

        searchGroupBox = QGroupBox("Search Options")
        searchGroupBox.setLayout(grid)
        return searchGroupBox

    def createFilterOptionBox(self) -> QGroupBox:

        self.sexComboBox = QComboBox()
        self.sexComboBox.addItems(["All", "Male", "Female", "Other"])

        self.schoolComboBox = QComboBox()
        self.schoolComboBox.addItems(set(self.studentModel.studentManager.getValuesFromKey("school")))
        self.schoolComboBox.addItem("All School", -1)
        self.schoolComboBox.setCurrentIndex(0)

        self.gradeComboBox = QComboBox()
        self.gradeComboBox.addItem("All Grades", -1)
        for i in range(1, 14):
            self.gradeComboBox.addItem(f"Grade {i}", i)
        self.gradeComboBox.addItem("Above 13", -2)

        self.timeComboBox = QComboBox()
        self.timeComboBox.addItem("All Time", -1)
        self.timeComboBox.addItems(["Last Week", "Last Month", "Last Year"])

        grid = QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.addWidget(QLabel("Sex"), 0, 0)
        grid.addWidget(self.sexComboBox, 1, 0)
        grid.addWidget(QLabel("School"), 0, 1)
        grid.addWidget(self.schoolComboBox, 1, 1)
        grid.addWidget(QLabel("Grade"), 0, 2)
        grid.addWidget(self.gradeComboBox, 1, 2)
        grid.addWidget(QLabel("Registered At"), 0, 3)
        grid.addWidget(self.timeComboBox, 1, 3)

        filterGroupBox = QGroupBox("Filter Options")
        filterGroupBox.setLayout(grid)
        return filterGroupBox

    def createCategaryBox(self) -> QGroupBox:


        grid = QGridLayout()
        grid.setHorizontalSpacing(20)

        self.groupCheckBoxes = QButtonGroup(self)
        for i, value in enumerate(["Sex", "School", "Grade"]):
            button = QRadioButton(value)
            grid.addWidget(button, 0, i)
            self.groupCheckBoxes.addButton(button, i)
        self.groupCheckBoxes.setExclusive(True)


        categoaryBox = QGroupBox("Group By")
        categoaryBox.setLayout(grid)
        return categoaryBox


    def populateStudents(self):

        [w.deleteLater() for w in self.searchResultWidgets]
        self.searchResultWidgets.clear()

        # get the search keyword
        searchKeyWord = self.studentSearchBar.text()
        searchFiled = self.searchFieldMenu.currentText()
        filterOptions = {
            "Sex": self.sexComboBox.currentText(),
            "School": self.schoolComboBox.currentText(),
            "Grade": self.gradeComboBox.currentData(),
            "Registered At": self.timeComboBox.currentText()
        }
        groupFiled = None
        if self.groupCheckBoxes.checkedButton() is not None:
            groupField = self.groupCheckBoxes.checkedButton().text()
        # create student search thread and run it
        worker = StudentSearcher(searchKeyWord, self.studentModel, searchFiled, filterOptions, groupField)
        worker.resultChanged.connect(self.addSearchResult)
        worker.progressChanged.connect(lambda e: self.searchProgressBar.setValue(e * 100))
        worker.finished.connect(self.searchingFinished)
        worker.run()

    def addSearchResult(self, studentCard: StudentCard):

        studentCard.mouseMoveEvent = lambda e, detail=studentCard.detail: self.showStatus(detail)

        self.searchResultLayout.addWidget(studentCard)
        self.searchResultWidgets.append(studentCard)

    def searchingFinished(self):

        self.searchProgressBar.setValue(0)
        self.searchResultLayout.addStretch()

    def showStatus(self, detail):

        self.statusLabel.setText(f"{detail['First Name']} {detail['Last Name']} - {detail['Student ID']}")
