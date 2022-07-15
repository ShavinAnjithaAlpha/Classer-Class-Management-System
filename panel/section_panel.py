from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QGridLayout, QStackedWidget, QHBoxLayout,
                             QCheckBox, QStackedLayout, QLineEdit, QScrollArea)
from PyQt5.QtCore import Qt,QSize, QDate, QTime, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QIcon

from widget.link_button import SubLinkButton


class SectionPanel(QWidget):

    NAVIGATE_LINKS_WIDTH = 500

    back_signal = pyqtSignal()

    def __init__(self, sub_sections : list, title : str ,sub_section_id : int = 0, *args, **kwargs):
        super(SectionPanel, self).__init__()
        self.current_sub_section_id = sub_section_id
        self.sub_sections = sub_sections
        self.title = title

        self.initializeUI()
        self.setObjectName("section-panel")

    def initializeUI(self):

        # create stack layout and panel stack dictionary
        self.panelStack = {}

        staticBar = QWidget()
        staticBar.setObjectName("static-bar")
        staticBar.setContentsMargins(0, 0, 0, 0)

        # create show and hide button
        showHideButton = QPushButton("=")
        showHideButton.setObjectName("show-button")
        showHideButton.pressed.connect(self.showAndHide)

        back_button = QPushButton("<")
        back_button.setObjectName("show-button")
        back_button.pressed.connect(lambda : self.back_signal.emit())

        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(back_button)
        vbox.addWidget(showHideButton)
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
        self.displayPanel(self.current_sub_section_id)

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
        vbox.addWidget(titleLabel)
        vbox.addSpacing(35)

        for i, section in enumerate(self.sub_sections):
            linkButton = SubLinkButton(section, i)
            self.navigateButtons.append(linkButton)
            linkButton.clicked_signal.connect(lambda i, e = linkButton : self.setCurrentPanel(i, e))
            vbox.addWidget(linkButton)

        vbox.addStretch()
        navigateWidget.setLayout(vbox)

    def setCurrentPanel(self,  panel_id : int, linkButton : SubLinkButton):

        # set the link button market for selected one
        for button in self.navigateButtons:
            if button == linkButton:
                button.select()
            else:
                button.unselect()


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

