import math
from functools import partial

from PyQt5 import uic
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel, QGridLayout, QPushButton

from Optimisation import ChromosomeController


class ConfirmationScreen:
    """Sets up and runs the loading screen between filters and optimisation."""

    controller = None
    filterVbox = QVBoxLayout()
    filters = None

    def __init__(self):
        """
        Sets up the loading screen visuals.
        """
        Form, Window = uic.loadUiType("Visuals/QtFiles/ConfirmationMenu.ui")
        self.window = Window()
        self.form = Form()
        self.form.setupUi(self.window)
        self.centre = self.window.findChild(QWidget, "centralwidget")

    def begin(self, controller):
        """
        Begins the loading screen and visualises it.
        :param controller: the controller for the programs visuals
        :type controller: VisualsController
        """
        self.controller = controller
        self.centre.findChild(QScrollArea, "filtersScroller")\
            .findChild(QWidget, "scrollerContents").setLayout(self.filterVbox)

        self.extract_filters()
        self.centre.findChild(QLabel, "loadingLabel").hide()
        self.setup_buttons()

        self.window.show()

    def setup_buttons(self):
        """
        Sets up the inbuilt buttons to make the appropriate calls upon being clicked.
        """
        confirm = self.centre.findChild(QPushButton, "confirmBtn")
        confirm.clicked.connect(partial(self.confirmed))
        cancel = self.centre.findChild(QPushButton, "cancelBtn")
        cancel.clicked.connect(partial(self.controller.show_selector_menu))

    def confirmed(self):
        """
        Upon the options being confirmed, the two buttons are replaced with a label, the title label is updated
        and after a short pause, the next menu is loaded.
        """
        self.centre.findChild(QPushButton, "confirmBtn").hide()
        self.centre.findChild(QPushButton, "cancelBtn").hide()
        self.centre.findChild(QLabel, "loadingLabel").show()
        self.centre.findChild(QLabel, "title").setText("Optimisation & Visualisation Processing")

        ChromosomeController.set_const_filters(self.controller.filters)
        ChromosomeController.nondominatedFront.append(ChromosomeController.build_chromosome(self.controller.filters))
        ChromosomeController.nondominatedFront.append(ChromosomeController.build_chromosome(self.controller.filters))
        ChromosomeController.nondominatedFront.append(ChromosomeController.build_chromosome(self.controller.filters))
        # ChromosomeController.begin_optimising()
        QTimer.singleShot(2000, self.controller.load_character_review)


    def extract_filters(self):
        """
        Extracts the filters applied from the previous menu, and visualises them in the loading screen.
        """
        self.filters = self.controller.filters

        self.extract_core_stats()
        self.extract_abilities()
        # goes through and adds all list-based filters
        for filterType, elements in self.filters.items():
            if type(elements) == list and len(elements) > 0:
                self.extract_filter_list(filterType, elements)

    def extract_core_stats(self):
        """
        Extracts the core statistics and adds them to the scroll area.
        """
        titleLabel = QLabel("Core Statistics")
        titleLabel.setStyleSheet('font: 20pt "Imprint MT Shadow"; color: #ffffff;')
        self.filterVbox.addWidget(titleLabel, alignment=Qt.AlignCenter)
        potentialLabels = ["Primary", "Secondary", "Class", "Subclass",
                           "Background", "Race", "Subrace", "Minimum AC"]

        for label in potentialLabels:
            if label in ["Primary", "Secondary"]:
                textAddition = " Archetype"
            else:
                textAddition = ""
            try:
                nextLabel = QLabel(f"{label + textAddition}: {self.filters[label]}")
                nextLabel.setStyleSheet('font: 14pt "Times New Roman"; color: rgb(188, 189, 177);')
                self.filterVbox.addWidget(nextLabel, alignment=Qt.AlignCenter)
            except KeyError:
                pass

    def extract_abilities(self):
        """
        Extracts the ability score boundaries and visualises them in the scroll area.
        """
        titleLabel = QLabel("Ability Scores")
        titleLabel.setStyleSheet('font: 20pt "Imprint MT Shadow"; color: #ffffff;')
        grid = QGridLayout()
        self.filterVbox.addWidget(titleLabel, alignment=Qt.AlignCenter)
        self.filterVbox.addLayout(grid)

        counter = 0
        abilities = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
        for [minVal, maxVal] in self.filters["Abilities"].values():
            nextLabel = QLabel(f"{abilities[counter]} - Between {str(minVal)} & {str(maxVal)}")
            nextLabel.setStyleSheet('font: 12pt "Times New Roman"; color: rgb(188, 189, 177);')
            grid.addWidget(nextLabel, math.floor(counter / 2), counter % 2, alignment=Qt.AlignCenter)
            counter += 1

    def extract_filter_list(self, filter_type, elements):
        """
        Extracts one filter groups' elements from it's array and adds them to the scroll area.
        :param filter_type: the name of the filter group, such as Equipment
        :type filter_type: str
        :param elements: the list of filters to be applied
        :type elements: list
        """
        titleLabel = QLabel(filter_type)
        titleLabel.setStyleSheet('font: 20pt "Imprint MT Shadow"; color: #ffffff;')
        grid = QGridLayout()
        self.filterVbox.addWidget(titleLabel, alignment=Qt.AlignCenter)
        self.filterVbox.addLayout(grid)

        counter = 0
        for element in elements:
            nextLabel = QLabel(element)
            nextLabel.setStyleSheet('font: 12pt "Times New Roman"; color: rgb(188, 189, 177);')
            grid.addWidget(nextLabel, math.floor(counter/3), counter % 3, alignment=Qt.AlignCenter)
            counter += 1

