from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QPixmap


class LinkButton(QWidget):
    clicked_signal = pyqtSignal(int)

    ICON_SIZE = QSize(100, 80)
    WIDGET_SIZE = QSize(320, 250)
    DEFAULT_ICON = ""

    def __init__(self, title: str, description: str, icon: str = None, section_id=None):
        super(LinkButton, self).__init__()
        self.section_id = section_id

        # create base widget
        base_widget = QWidget()
        base_widget.setObjectName("link-base-widget")
        base_widget.setContentsMargins(0, 0, 0, 0)

        self.iconLabel = QLabel()
        self.iconLabel.setContentsMargins(5, 15, 5, 5)
        try:
            if icon:
                self.iconLabel.setPixmap(
                    QPixmap(icon).scaled(self.ICON_SIZE, Qt.KeepAspectRatio, Qt.FastTransformation))
            else:
                self.iconLabel.setPixmap(
                    QPixmap(self.DEFAULT_ICON).scaled(self.ICON_SIZE, Qt.KeepAspectRatio, Qt.FastTransformation))
        except:
            pass

        titleLabel = QLabel(title)
        titleLabel.setObjectName("title-label")

        descriptionLabel = QLabel(description)
        descriptionLabel.setWordWrap(True)
        descriptionLabel.setObjectName("des-label")

        vbox = QVBoxLayout()
        vbox.setSpacing(0)
        vbox.setContentsMargins(0, 0, 0, 0)

        vbox.addWidget(self.iconLabel, alignment=Qt.AlignCenter)
        vbox.addWidget(titleLabel, alignment=Qt.AlignHCenter)
        vbox.addWidget(descriptionLabel, alignment=Qt.AlignTop | Qt.AlignHCenter)

        base_widget.setLayout(vbox)
        _vbox = QVBoxLayout()
        _vbox.setContentsMargins(0, 0, 0, 0)
        _vbox.addWidget(base_widget)
        self.setLayout(_vbox)

        self.setFixedSize(self.WIDGET_SIZE)

    def mousePressEvent(self, event) -> None:

        self.clicked_signal.emit(self.section_id)


class SubLinkButton(QWidget):
    ICON_SIZE = QSize(35, 35)

    clicked_signal = pyqtSignal(int)

    def __init__(self, text: str, section_id: int, icon: str = None):
        super(SubLinkButton, self).__init__()
        self.section_id = section_id
        self.setObjectName("sub-link-button")

        # create icon and text labels
        iconLabel = QLabel()
        if icon:
            iconLabel.setPixmap(QPixmap(icon).scaled(self.ICON_SIZE, Qt.KeepAspectRatio, Qt.FastTransformation))

        textLabel = QLabel(text)
        textLabel.setAlignment(Qt.AlignRight)

        self.selectMarker = QLabel()
        self.selectMarker.setFixedWidth(7)
        self.selectMarker.setObjectName("marker")
        self.selectMarker.hide()

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(self.selectMarker)
        hbox.addWidget(iconLabel)
        hbox.addWidget(textLabel)

        widget = QWidget()
        widget.setLayout(hbox)

        _hbox = QHBoxLayout()
        _hbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(_hbox)
        self.layout().addWidget(widget)

    def mousePressEvent(self, event) -> None:
        self.clicked_signal.emit(self.section_id)

    def select(self):
        self.selectMarker.show()

    def unselect(self):
        self.selectMarker.hide()


class CommandLinkButton(QWidget):
    ICON_SIZE = QSize(70, 70)

    def __init__(self, text: str, description: str, icon: str = None, section_id: int = None):
        super(CommandLinkButton, self).__init__()
        self.section_id = section_id
        self.setObjectName("command-link-button")

        textLabel = QLabel(text)
        textLabel.setObjectName("text")

        desLabel = QLabel(description)
        desLabel.setWordWrap(True)
        desLabel.setObjectName("des")

        iconLabel = QLabel()
        if icon:
            iconLabel.setPixmap(QPixmap(icon).scaled(self.ICON_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        grid = QGridLayout()
        grid.addWidget(iconLabel, 0, 0, 2, 1, alignment=Qt.AlignCenter)
        grid.addWidget(textLabel, 0, 1, alignment=Qt.AlignHCenter)
        grid.addWidget(desLabel, 1, 1, alignment=Qt.AlignLeft)

        widget = QWidget()
        widget.setLayout(grid)

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(widget)
        self.setMaximumWidth(300)
        self.setMinimumHeight(200)
        self.setMaximumHeight(300)
