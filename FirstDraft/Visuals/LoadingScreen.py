import math

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel, QGridLayout

from Database import DataConverter, CharacterBuilder


class LoadingScreen:
    """Sets up and runs the loading screen between filters and optimisation."""

    controller = None
    filterVbox = QVBoxLayout()
    filters = None

    def __init__(self):
        """
        Sets up the loading screen visuals.
        """
        Form, Window = uic.loadUiType("Visuals/QtFiles/LoadingMenu.ui")
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

        self.utilise_filters()
        self.window.show()

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

    def utilise_filters(self):
        print(self.filters)
        convertedFilters = []
        for heading, elements in self.filters.items():
            choiceType = heading[:-1]
            whereFrom = ["Background", "ClassOptions", "RaceOptions"]
            if heading in ("Proficiencies", "Skills"):
                choiceType = "Proficiency"
            elif heading == "Spells":
                whereFrom = ["Race", "Class"]
            elif heading == "Equipment":
                choiceType = "Equipment"
                whereFrom = "Class"
            elif heading != "Languages":
                choiceType = ""

            if choiceType != "":
                for element in elements:
                    convertedFilters.append([element, choiceType, whereFrom])
        convertedFilters = CharacterBuilder.take_choices(convertedFilters)
        chr = DataConverter.create_character(1, convertedFilters)
        print(chr)

