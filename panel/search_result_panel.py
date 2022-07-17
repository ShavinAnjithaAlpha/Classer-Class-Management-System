from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap

from SECTION_INDEXES import SUB_SECTION_INDEXES, KEYWORDS_MAP

class SearchResultPanel(QWidget):

    searchSignal = pyqtSignal(tuple)
    homeSignal = pyqtSignal()

    def __init__(self):
        super(SearchResultPanel, self).__init__()

        self.initizlizeUI()
        self.setObjectName("search-result-panel")

    def initizlizeUI(self):

        # create home button search bar and title bar
        titleBar = QLabel("Search Results")
        titleBar.setObjectName("search-title")

        homeButton = QPushButton()
        homeButton.pressed.connect(lambda : self.homeSignal.emit())
        homeButton.setIcon(QIcon("resources/icons/home-white.png"))
        homeButton.setIconSize(QSize(40, 40))
        homeButton.setObjectName("home")

        searchLabel = QLabel()
        searchLabel.setPixmap(QPixmap("resources/icons/search.png").scaled(QSize(35, 35), Qt.KeepAspectRatio,
                                                                              Qt.FastTransformation))

        self.searchBar = QLineEdit()
        self.searchBar.setPlaceholderText("Search sections, sub sections")
        self.searchBar.setObjectName("search-bar")
        self.searchBar.textChanged[str].connect(self.searching)
        self.searchBar.setFocus()

        hbox = QHBoxLayout()
        hbox.addWidget(homeButton)
        hbox.addWidget(titleBar)
        hbox.addStretch()
        hbox.addWidget(searchLabel)
        hbox.addWidget(self.searchBar)

        # search result layout for add search result buttons
        self.searchResultLayout = QVBoxLayout()
        # create search result widget list
        self.searchResultWidgets = []

        # create no search result label
        self.noResultLabel = QLabel("No search results found")
        self.noResultLabel.setObjectName("no-result")
        self.noResultLabel.hide()

        # v box layout for add the main content
        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addLayout(hbox)
        vbox.addWidget(self.noResultLabel, alignment=Qt.AlignLeft)
        vbox.addLayout(self.searchResultLayout)
        vbox.addStretch()

        w = QWidget()
        w.setContentsMargins(0, 0, 0, 0)
        w.setLayout(vbox)

        _vbox = QVBoxLayout()
        _vbox.setContentsMargins(0, 0, 0, 0)
        _vbox.addWidget(w)
        self.setLayout(_vbox)

    def addSearchResults(self, results : list) -> None:

        # hide no result label
        if self.noResultLabel.isVisible():
            self.noResultLabel.hide()
        # first clean the search result panel
        [widget.deleteLater() for widget in self.searchResultWidgets]
        self.searchResultWidgets.clear()

        if not results:
            self.noResultLabel.show()
            return

        # and then add search result with functionality
        for section_id, text, sub_section_id in results:
            searchButton = QPushButton(text)
            searchButton.pressed.connect(lambda a = section_id, b = sub_section_id : self.searchSignal.emit((a, b)))
            # add to search widget list and layout
            self.searchResultWidgets.append(searchButton)
            self.searchResultLayout.addWidget(searchButton)

    def indexingSearching(self, searchKeyword : str):

        if searchKeyword == "":
            self.addSearchResults([])

        sub_section_ids = []
        for keys, sub_section_id in KEYWORDS_MAP.items():
            if searchKeyword.lower().strip() in keys.lower():
                sub_section_ids.append(sub_section_id)
        # remove all duplicates things
        sub_section_ids = set(sub_section_ids)

        results = []
        for i in sub_section_ids:
            results.append(SUB_SECTION_INDEXES[i])

        return results

    def searching(self, searchKeyword  :str) -> None:

        # recall to method for add search result button to panel
        self.addSearchResults(self.indexingSearching(searchKeyword))




