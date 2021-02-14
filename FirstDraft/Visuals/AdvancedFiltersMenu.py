import itertools
from functools import partial
from PyQt5 import uic
from PyQt5.QtGui import QRegion
from PyQt5.QtWidgets import *
from Database import CoreDatabase as Db


class AdvancedFiltersMenu:
    """Sets up and runs the menu that allows the application of advanced character features."""

    controller = None
    selectedSpells = set()
    selectedEquipment = set()

    def __init__(self):
        """
        Sets up the advanced filters menu visuals.
        """
        Form, Window = uic.loadUiType("Visuals/AdvancedFiltersMenu.ui")
        self.window = Window()
        self.form = Form()
        self.form.setupUi(self.window)
        self.centre = self.window.findChild(QWidget, "centralwidget")

    def begin(self, controller):
        """
        Begins the advanced filters menu and visualises it.
        :param controller: the controller for the applications visuals
        :type controller: VisualsController
        """
        self.controller = controller
        if self.centre.findChild(QScrollArea, "chosenEquipmentOptions")\
                .findChild(QWidget, "chosenEquipmentContents").layout() is None:
            self.centre.findChild(QScrollArea, "chosenEquipmentOptions")\
                .findChild(QWidget, "chosenEquipmentContents").setLayout(QVBoxLayout())
            self.centre.findChild(QScrollArea, "chosenSpellOptions") \
                .findChild(QWidget, "chosenSpellContents").setLayout(QVBoxLayout())

        shadowItems = {"coreStatsView": QGraphicsView, "spellsView": QGraphicsView, "equipmentView": QGraphicsView,
                       "proficienciesView": QGraphicsView, "saveAdvancedOptions": QPushButton}
        self.centre = self.controller.setup_shadows(self.centre, shadowItems)
        self.setup_core_stats()
        self.setup_spell_and_equipment()

        btn = self.centre.findChild(QPushButton, "saveAdvancedOptions")
        btn.clicked.connect(partial(self.save_btn_clicked))

        self.window.show()

    def save_btn_clicked(self):
        """
        Reacts to the save advanced options button being placed, by calling the controller.
        """
        self.controller.stop_advanced_filters_menu()

    def setup_core_stats(self):
        """
        Sets up the core stats subsections' dropdown boxes.
        """
        for element in ["Class", "Race", "Background"]:
            dropdownBox = self.centre.findChild(QComboBox, "select" + element)
            if element != "Background":
                dropdownBox.currentTextChanged.connect(self.setup_core_subgroup_stats)
            Db.cursor.execute(f"SELECT {element.lower()}Name FROM {element}")
            names = list(itertools.chain(*Db.cursor.fetchall()))
            dropdownBox.addItems(names)

    def setup_core_subgroup_stats(self, value):
        """
        Sets up the subgroup dropdown boxes options when it's parent box has it's value changed.
        This subgroup gets all options applicable to the parent group, such as the subclasses available to a cleric if
        the parent is the class dropdown and selects Cleric.
        :param value: the value selected within the parent subclass
        :type value: str
        """
        if value not in ["", "Select Class", "Select Race"]:
            Db.cursor.execute("SELECT raceName FROM Race")
            races = list(itertools.chain(*Db.cursor.fetchall()))
            table = ["class", "race"].pop(int(value in races))
            dropdownBox = self.centre.findChild(QComboBox, "selectSub" + table)

            Db.cursor.execute(f"SELECT sub{table}Name FROM Sub{table} WHERE {table}Id="
                              f"{str(Db.get_id(value, table.capitalize()))}")
            suboptions = ["Select Sub"+table] + list(itertools.chain(*Db.cursor.fetchall()))

            dropdownBox.clear()
            dropdownBox.addItems(suboptions)

    def setup_spell_and_equipment(self):
        """
        Sets up the area which allows for spells to be searched for, selected and deselected.
        """
        spellBtn = self.centre.findChild(QPushButton, "spellSearchBtn")
        equipmentBtn = self.centre.findChild(QPushButton, "equipmentSearchBtn")

        spellBtn.clicked.connect(partial(self.populate_scroll_area, scroll_type="spell"))
        equipmentBtn.clicked.connect(partial(self.populate_scroll_area, scroll_type="equipment"))

    def populate_scroll_area(self, scroll_type):
        """
        Populates a scroll area with the appropriate contents based on the value entered into it's search bar.
        :param scroll_type: the group the scroll area is part of - spell or equipment
        :type scroll_type: str
        """
        options = self.centre.findChild(QScrollArea, scroll_type + "Options")
        searchBar = self.centre.findChild(QTextEdit, scroll_type + "SearchBar")
        Db.cursor.execute(f"SELECT {scroll_type}Name FROM {scroll_type.capitalize()} WHERE "
                          f"{scroll_type}Name LIKE '%{searchBar.toPlainText()}%'")

        if scroll_type == "spell":
            selectedItems = self.selectedSpells
        else:
            selectedItems = self.selectedEquipment

        vbox = QVBoxLayout()
        for element in set(itertools.chain(*Db.cursor.fetchall())).difference(selectedItems):
            btn = QPushButton(element)
            btn.setStyleSheet("background-color: rgb(23, 134, 3); color: rgb(255, 255, 255); "
                              "font: 87 8pt 'Arial Black'; Text-align:left;")
            btn.clicked.connect(partial(self.selected_item, scroll_type=scroll_type, name=element))
            vbox.addWidget(btn)
        widget = QWidget()
        widget.setLayout(vbox)
        options.setWidget(widget)

    def selected_item(self, scroll_type, name):
        """
        Marks an item as selected, and moves it to the selected scrollbar.
        :param scroll_type: the group the scroll area is part of - spell or equipment
        :type scroll_type: str
        :param name: the name of the selected item
        :type name: str
        """
        options = self.centre.findChild(QScrollArea, "chosen" + scroll_type.capitalize() + "Options")
        vbox = options.findChild(QWidget, "chosen" + scroll_type.capitalize() + "Contents").children()[0]

        if scroll_type == "spell":
            selectedItems = self.selectedSpells
        else:
            selectedItems = self.selectedEquipment

        if name != "":
            selectedItems.add(name)
            self.populate_scroll_area(scroll_type)
            btn = QPushButton(name)
            btn.setStyleSheet("background-color: rgb(23, 134, 3); color: rgb(255, 255, 255); "
                              "font: 87 8pt 'Arial Black'; Text-align:left;")
            vbox.addWidget(btn)
            btn.clicked.connect(lambda: self.deselected_item(scroll_type=scroll_type, name=btn.text()))

        options.verticalScrollBar().setValue(0)
        if scroll_type == "spell":
            self.selectedSpells = selectedItems
        else:
            self.selectedEquipment = selectedItems

    def deselected_item(self, scroll_type, name):
        """
        Unmarks the selection of an item, returning it to the options scrollbar.
        :param scroll_type: the group the scroll area is part of - spell or equipment
        :type scroll_type: str
        :param name: the name of the deselected item
        :type name: str
        """
        if scroll_type == "spell":
            selectedItems = self.selectedSpells
        else:
            selectedItems = self.selectedEquipment

        options = self.centre.findChild(QScrollArea, "chosen" + scroll_type.capitalize() + "Options")
        selectedItems.remove(name)

        vbox = options.findChild(QWidget, "chosen" + scroll_type.capitalize() + "Contents").layout()
        for i in reversed(range(vbox.count())):
            vbox.itemAt(i).widget().setParent(None)
        for element in selectedItems.difference(set(name)):
            btn = QPushButton(element)
            btn.setStyleSheet("background-color: rgb(23, 134, 3); color: rgb(255, 255, 255); "
                              "font: 87 8pt 'Arial Black'; Text-align:left;")
            btn.clicked.connect(lambda: self.deselected_item(scroll_type=scroll_type, name=btn.text()))
            vbox.addWidget(btn)

        self.populate_scroll_area(scroll_type)
        if scroll_type == "spell":
            self.selectedSpells = selectedItems
        else:
            self.selectedEquipment = selectedItems

    def setup_language_options(self, amnt):
        """
        Sets up dropdown boxes equal to the amount of languages specified.
        :param amnt: the amount of languages
        :type amnt: int
        """
        holder = self.centre.findChild(QScrollArea, "languagesScroller").findChild(QWidget, "scrollAreaWidgetContents")
