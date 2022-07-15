import mysql.connector as mysql
import json5, os
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QGridLayout, QStackedWidget, QHBoxLayout,
                             QCheckBox, QStackedLayout, QLineEdit, QScrollArea, QCompleter)
from PyQt5.QtCore import Qt,QSize, QDate, QTime, QTimer, pyqtSignal
from PyQt5.QtGui import QKeyEvent, QPixmap

from util.logger import Logger
from util.security.access import AccessManager

from widget.link_button import LinkButton
from panel.section_panel import SectionPanel

from SECTION_INDEXES import SUB_SECTION_INDEXES, KEYWORDS_MAP
####################### end of import files ##########################
global connection, logger, accessManager
connection : mysql.MySQLConnection = None
logger : Logger = None
accessManager : AccessManager = None

class SystemPanel(QWidget):

    quitSignal = pyqtSignal()

    def __init__(self, _connection : mysql.MySQLConnection, _logger : Logger, _access_manager : AccessManager, *args, **kwargs):
        super(SystemPanel, self).__init__()
        global connection, logger, accessManager
        connection = _connection
        logger = _logger
        accessManager = _access_manager
        # initiate the UI
        self.initializeUI()

    def initializeUI(self):

        # create stack layout
        self.stackLayout = QStackedLayout()
        self.stackLayout.setContentsMargins(0, 0, 0, 0)

        self.createIndexPanel()

        self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.stackLayout)

    def createIndexPanel(self):

        self.panelStack = {}

        # index panel widget
        self.indexPanel = QWidget()
        self.indexPanel.setObjectName("main")
        self.indexPanel.setContentsMargins(0, 0, 0, 0)

        # create top bar of the index panel
        top_grid = self.createTopIndexPanel()
        # create links layout
        linkScrollArea = self.createLinkLayout()

        # create bottom bar of index panel
        bottom_grid = QGridLayout()
        bottom_grid.addWidget(QPushButton("Logger"), 0, 0, alignment=Qt.AlignLeft)

        # setup index panel
        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addLayout(top_grid)
        vbox.addWidget(linkScrollArea)
        vbox.addLayout(bottom_grid)
        self.indexPanel.setLayout(vbox)

        self.stackLayout.addWidget(self.indexPanel)

    def createTopIndexPanel(self) -> QGridLayout:
        self.timeLabel = QLabel(QTime.currentTime().toString("hh:mm"))
        self.dateLabel = QLabel(QDate.currentDate().toString("dddd, MMM dd"))

        self.timeLabel.setObjectName("time-label")
        self.dateLabel.setObjectName("date-label")

        # create timer for update date and time
        self.timer = QTimer()
        self.timer.start(1000)
        self.timer.timeout.connect(self.updateDateAndTime)

        completer = QCompleter([str(item[1]) for item in SUB_SECTION_INDEXES.values()])
        completer.setCompletionMode(QCompleter.CaseInsensitivelySortedModel)

        # create search bar
        self.searchBar = QLineEdit()
        self.searchBar.setMaximumWidth(500)
        self.searchBar.setPlaceholderText("Find Sections and Sub Sections")
        self.searchBar.setObjectName("search-bar")
        self.searchBar.returnPressed.connect(self.searchSections)
        self.searchBar.setCompleter(completer)

        searchIcon = QLabel()
        searchIcon.setPixmap(QPixmap("resources/icons/search.png").scaled(QSize(30, 30), Qt.KeepAspectRatio,
                                                                          Qt.FastTransformation))
        hbox = QHBoxLayout()
        hbox.addSpacing(150)
        hbox.addWidget(searchIcon)
        hbox.addSpacing(10)
        hbox.addWidget(self.searchBar)
        hbox.addStretch()

        close_button = QPushButton("X")
        close_button.pressed.connect(lambda: self.quitSignal.emit())

        # create grid layout
        top_grid = QGridLayout()
        top_grid.setContentsMargins(0, 0, 0, 0)
        top_grid.addWidget(self.timeLabel, 0, 0, alignment=Qt.AlignLeft)
        top_grid.addWidget(self.dateLabel, 1, 0, alignment=Qt.AlignLeft)
        top_grid.addLayout(hbox, 0, 1, 2, 1, alignment=Qt.AlignCenter)
        top_grid.addWidget(close_button, 0, 2, alignment=Qt.AlignTop | Qt.AlignRight)

        return top_grid

    def createLinkLayout(self) -> QScrollArea:
        # create command link section of index panel
        linkScrollArea = QScrollArea()
        linkScrollArea.setObjectName("link-scroll-pane")
        linkScrollArea.setWidgetResizable(True)
        linkScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        linkScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        linkWidget = QWidget()
        linkScrollArea.setWidget(linkWidget)

        self.linkLayout = QGridLayout()
        self.linkLayout.setSpacing(20)
        linkWidget.setLayout(self.linkLayout)

        for i in range(6):
            linkButton = LinkButton("Student", "add student, update and viewing ad more", "resources/icons/widget.png", i)
            linkButton.clicked_signal.connect(self.addPanel)

            self.linkLayout.addWidget(linkButton, i//5 ,i%5)


        return linkScrollArea

    def updateDateAndTime(self):

        self.dateLabel.setText(QDate.currentDate().toString("dddd MMM, dd"))
        self.timeLabel.setText(QTime.currentTime().toString("hh:mm"))

    def addPanel(self, section_id : int, sub_section_id : int = 0):

        if section_id in self.panelStack.keys():
            self.stackLayout.setCurrentIndex(self.panelStack.get(section_id, 0))
        else:
            # create instance of panel that matches to section id that pass to method
            panel = self.createPanel(section_id, sub_section_id)
            # add to stack layout
            self.stackLayout.addWidget(panel)
            self.stackLayout.setCurrentWidget(panel)

            # add to panel stack
            self.panelStack[section_id] = self.stackLayout.currentIndex()

    def createPanel(self, section_id : int, sub_section_id : int) -> QWidget:

        if section_id == 0:
            panel = SectionPanel(["Student Table", "Add Student", "Student Search"], "student manager", sub_section_id)
        elif section_id == 1:
            return QLabel("Class")
        else:
            return QLabel("Register")

        panel.back_signal.connect(lambda : self.stackLayout.setCurrentWidget(self.indexPanel))
        return panel

    def fetchSectionIndexes(self, keyword : str) -> tuple[int]:

        sub_section_id = None
        for value, key_id in KEYWORDS_MAP.items():
            if keyword.lower().strip() in value:
                sub_section_id = key_id
                break

        if sub_section_id is not None:
            index_details = SUB_SECTION_INDEXES.get(sub_section_id)
        else:
            return None

        if index_details:
            return (index_details[0], index_details[2])
        return None

    def searchSections(self, *args):

        section_details = self.fetchSectionIndexes(self.searchBar.text())
        if section_details:
            self.addPanel(*section_details)
            return


    def keyPressEvent(self, event : QKeyEvent) -> None:

        if event.key() == Qt.Key_Backspace:
            self.stackLayout.setCurrentWidget(self.indexPanel)



