from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout, QGridLayout, QStackedWidget, QHBoxLayout,
                              QLineEdit, QScrollArea, QCompleter)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QIcon

from widget.link_button import SubLinkButton

from SECTION_INDEXES import SUB_SECTION_INDEXES

from util.common_functions import getAccessIndexes, checkAccessPreviliage


################### end of import section ###################
global accessManager, logger, connection

class SectionPanel(QWidget):

    # size constant of widget
    NAVIGATE_LINKS_WIDTH = 400
    # pyqt signals for this widget
    back_signal = pyqtSignal()

    def __init__(self, section_id : int ,sub_sections : list, title : str , current_sub_section_id : int = 0, parent = None, * , connection_ = None, access_manager_ = None, logger_ = None):
        super(SectionPanel, self).__init__()
        self.current_sub_section_id = current_sub_section_id
        self.section_id = section_id
        self.sub_sections = sub_sections
        self.title = title
        self.parent = parent

        global connection, accessManager, logger
        connection = connection_
        logger = logger_
        accessManager = access_manager_

        self.initializeUI()
        self.setObjectName("section-panel")

    # static part of UI
    def initializeUI(self):

        # create stack layout and panel stack dictionary
        self.panelStack = {}

        staticBar = QWidget()
        staticBar.setObjectName("static-bar")
        staticBar.setContentsMargins(0, 0, 0, 0)

        # create show and hide button
        showHideButton = QPushButton()
        showHideButton.setIcon(QIcon("resources/icons/menu.png"))
        showHideButton.setObjectName("show-button")
        showHideButton.pressed.connect(self.showAndHide)

        back_button = QPushButton()
        back_button.setIcon(QIcon("resources/icons/back.png"))
        back_button.setObjectName("show-button")
        back_button.pressed.connect(lambda : self.back_signal.emit())

        homeButton = QPushButton()
        homeButton.setIcon(QIcon("resources/icons/home-white.png"))
        homeButton.setObjectName("show-button")
        homeButton.pressed.connect(lambda : self.parent.stackLayout.setCurrentWidget(self.parent.indexPanel))

        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(back_button)
        vbox.addWidget(showHideButton)
        vbox.addWidget(homeButton)
        vbox.addStretch()
        staticBar.setLayout(vbox)

        # create two spaces for section area and navigation area
        self.navigationWidget = QWidget()
        self.navigationWidget.setObjectName("navigate")
        self.navigationWidget.setContentsMargins(0, 0, 0, 0)
        # arrange the navigate links
        self.setUpNavigates(self.navigationWidget)

        # stack Widget
        self.stackWidget = QStackedWidget()
        self.stackWidget.setContentsMargins(0, 0, 0, 0)
        # set current widget
        self.setCurrentPanel(self.current_sub_section_id, self.navigateButtons[self.current_sub_section_id])
        # create h box
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)
        hbox.addWidget(staticBar)
        hbox.addWidget(self.navigationWidget)
        hbox.addWidget(self.stackWidget)


        self.setLayout(hbox)

    def setUpNavigates(self, navigateWidget : QWidget):

        navigateWidget.setMaximumWidth(self.NAVIGATE_LINKS_WIDTH)
        self.navigateButtons = []

        vbox = QVBoxLayout()
        vbox.setSpacing(0)
        vbox.setContentsMargins(0, 0, 0, 0)

        titleLabel = QLabel(self.title)
        titleLabel.setObjectName("title")

        completer = QCompleter([str(item[1]) for item in SUB_SECTION_INDEXES.values()])
        completer.setCaseSensitivity(Qt.CaseInsensitive)

        self.searchBar = QLineEdit()
        self.searchBar.setPlaceholderText("find sections")
        self.searchBar.setObjectName("search-bar")
        self.searchBar.returnPressed.connect(self.searchSections)
        self.searchBar.setCompleter(completer)

        vbox.addWidget(titleLabel)
        vbox.addSpacing(30)
        vbox.addWidget(self.searchBar)
        vbox.addSpacing(35)

        # get access privileged indexes
        accessIndexes = getAccessIndexes(1, self.section_id)

        for i, section in enumerate(self.sub_sections):
            linkButton = SubLinkButton(section, i)
            self.navigateButtons.append(linkButton)
            linkButton.clicked_signal.connect(lambda i, e = linkButton : self.setCurrentPanel(i, e))
            vbox.addWidget(linkButton)

            # set disables or enables
            if not checkAccessPreviliage(accessIndexes, i, accessManager.session["level"]):
                linkButton.setDisabled(True)

        vbox.addStretch()
        navigateWidget.setLayout(vbox)


    # dynamic part of UI
    def setCurrentLinkButton(self, linkButton : SubLinkButton):

        # set the link button market for selected one
        for button in self.navigateButtons:
            if button == linkButton:
                button.select()
            else:
                button.unselect()

    def setCurrentLinkButtonByIndex(self, index : int):

        linkButton = self.navigateButtons[index]
        self.setCurrentLinkButton(linkButton)

    def setCurrentPanel(self,  panel_id : int, linkButton : SubLinkButton):

        self.setCurrentLinkButton(linkButton)
        self.displayPanel(panel_id)

    def displayPanel(self, panel_id : int):

        if panel_id in self.panelStack.keys():
            self.stackWidget.setCurrentIndex(self.panelStack.get(panel_id, 0))
            self.current_sub_section_id = panel_id

        else:
            # create subsection panels and display it
            subPanel = self.createSubPanel(panel_id)
            self.stackWidget.addWidget(subPanel)
            self.stackWidget.setCurrentWidget(subPanel)

            self.current_sub_section_id = panel_id
            # add to panel stack
            self.panelStack[panel_id] = self.stackWidget.currentIndex()

    def createSubPanel(self, panel_id : int):

        if panel_id == 0:
            return QLabel("Panel 1")
        elif panel_id == 1:
            return QLabel("Panel 2")
        else:
            return QLabel("Panel 3")

    def showAndHide(self):

        self.animation = QPropertyAnimation(self.navigationWidget, b'maximumWidth')
        self.animation.setStartValue(self.navigationWidget.width())

        if self.navigationWidget.width() == 0:
            self.animation.setEndValue(self.NAVIGATE_LINKS_WIDTH)
        else:
            self.animation.setEndValue(0)

        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.setDuration(500)
        self.animation.start()


    # search functionalty of UI
    def searchSections(self, *args):

        keyword = self.searchBar.text().strip()
        if self.parent.isDirectKeyWord(keyword):
            section_id, sub_section_id = self.parent.getDirectIndexes(keyword)
            self.parent.addPanel(section_id, sub_section_id)

        else:

            self.parent.searchResultPanel.searching(keyword)
            self.parent.stackLayout.setCurrentWidget(self.parent.searchResultPanel)