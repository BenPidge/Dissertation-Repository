from functools import partial

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from Database import CoreDatabase as Db


class SelectorMenu:
    """Sets up and runs the menu that allows the basic character selection and filtering."""

    archetypes = dict()
    abilitySpinners = dict()
    skillCheckBoxes = []
    controller = None

    def __init__(self):
        """
        Sets up the selector menu visuals.
        """
        Form, Window = uic.loadUiType("Visuals/SelectorMenu.ui")
        self.window = Window()
        self.form = Form()
        self.form.setupUi(self.window)
        self.centre = self.window.findChild(QWidget, "centralwidget")

    def begin(self, controller):
        """
        Begins the selector menu and visualises it.
        :param controller: the controller for the programs visuals
        :type controller: VisualsController
        """
        self.controller = controller

        self.setupArchetypes()
        self.setupArchetypeBtns()
        self.setupArchetypeDropdowns()
        self.setupSpinBoxes()
        self.setupCheckBoxes()
        self.setupAdvancedBtn()
        shadowItems = {"graphicsView": QGraphicsView,
                       "graphicsView_2": QGraphicsView,
                       "startProgram": QPushButton}
        self.centre = self.controller.setupShadows(self.centre, shadowItems)

        self.centre.findChild(QLabel, "error").setAlignment(Qt.AlignCenter)
        self.centre.findChild(QPushButton, "startProgram").clicked.\
            connect(partial(self.setupStartBtn))

        self.window.show()

    def setupArchetypes(self):
        """
        Sets up the global archetypes dictionary to be filled with the database contents
        """
        Db.cursor.execute("SELECT archetypeName, description FROM Archetype")
        for name, desc in Db.cursor.fetchall():
            self.archetypes.update({name: desc})

    def setupArchetypeBtns(self):
        """
        Sets up the button selections for choosing an archetype description to view.
        """
        scrollArea = self.centre.findChild(QScrollArea, "archetypeDescSelect")
        vbox = QVBoxLayout()
        widget = QWidget()

        for name, desc in sorted(self.archetypes.items()):
            btn = QPushButton(text=name)
            btn.setStyleSheet("background-color: rgb(255, 255, 255);")
            btn.clicked.connect(partial(self.archetypeButtonPressed, arch_desc=desc))
            vbox.addWidget(btn)
        widget.setLayout(vbox)
        scrollArea.setWidget(widget)

    def setupStartBtn(self):
        values = [["str"], ["dex"], ["con"], ["int"], ["wis"], ["cha"]]
        spinners = self.abilitySpinners
        for x in range(0, len(spinners.items())):
            values[x].append(list(spinners.values())[x][0].value())

        errorCode = self.checkAbilityBoundaries(values) + " " + self.checkSkills()
        self.centre.findChild(QLabel, "error").setText(errorCode)
        if errorCode == " ":
            # start the program
            pass

    def setupAdvancedBtn(self):
        """
        Sets up the advanced filters button.
        """
        advFilters = QPushButton("Advanced Filters ►")
        advFilters.setStyleSheet("font: 10pt;")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        advFilters.setGraphicsEffect(shadow)
        advFilters.clicked.connect(partial(self.controller.startAdvancedFiltersMenu))
        self.centre.findChild(QVBoxLayout, "filtersLayout").addWidget(advFilters)

    def archetypeButtonPressed(self, arch_desc):
        """
        When pressed, the button sets the text box to the buttons' archetype description.
        :param arch_desc: the description of the selected archetype
        :type arch_desc: str
        """
        archDesc = self.centre.findChild(QTextEdit, "archetypeDesc")
        archDesc.setPlainText(arch_desc)

    def setupArchetypeDropdowns(self):
        """
        Sets up the dropdown boxes to show all archetypes.
        """
        primaryDropdown = self.centre.findChild(QComboBox, "primaryArchetypes")
        secondaryDropdown = self.centre.findChild(QComboBox, "secondaryArchetypes")
        for archetype in sorted(list(self.archetypes.keys())):
            primaryDropdown.addItem(archetype)
            secondaryDropdown.addItem(archetype)

    def setupSpinBoxes(self):
        """
        Creates and stores all spinners for the abilities.
        """
        abilityLayout = self.centre.findChild(QHBoxLayout, "abilities")
        abilities = ["str", "dex", "con", "int", "wis", "cha"]
        directions = ["left", "mid", "right"]
        for x in range(0, len(abilities)):
            column = abilityLayout.findChild(QVBoxLayout, directions[x % 3] + "Column")
            layout = column.findChild(QHBoxLayout, abilities[x] + "Layout")
            spinMin, spinMax = self.setupAbilitiesBoxes(layout)
            self.abilitySpinners.update({abilities[x]: [spinMin, spinMax]})

    def setupCheckBoxes(self):
        """
        Creates all skill check boxes in their appropriate location.
        """
        skillLayout = self.centre.findChild(QHBoxLayout, "skills")
        boxNames = [["Acrobatics", "Insight", "Performance"], ["Animal Handling", "Intimidation", "Persuasion"],
                    ["Arcana", "Investigation", "Religion"], ["Athletics", "Medicine", "Sleight of Hand"],
                    ["Deception", "Nature", "Stealth"], ["History", "Perception", "Survival"]]
        for x in range(6):
            column = skillLayout.findChild(QVBoxLayout, "skillColumn" + str(x+1))
            for y in range(3):
                nextBox = QCheckBox()
                nextBox.setText(boxNames[x][y])
                column.addWidget(nextBox)
                self.skillCheckBoxes.append(nextBox)

    def checkSkills(self):
        """
        Checks there isn't an excess amount of skills selected.
        :return: the error code, or lack of, the spinners produce
        """
        skillsLeft = 8
        for box in self.skillCheckBoxes:
            if box.isChecked():
                skillsLeft -= 1
        if skillsLeft < 0:
            return "Too many skills selected."
        else:
            return ""

    @staticmethod
    def setupAbilitiesBoxes(layout):
        """
        Creates two spinners for an ability, separated with a "to" label.
        :param layout: the layout to append these to
        :return: the two spinners created
        """
        minSpin = QSpinBox()
        minSpin.setMinimum(8)
        minSpin.setMaximum(17)
        label = QLabel("to")
        maxSpin = QSpinBox()
        maxSpin.setMinimum(8)
        maxSpin.setMaximum(17)
        maxSpin.setValue(17)
        layout.addWidget(minSpin)
        layout.addWidget(label)
        layout.addWidget(maxSpin)
        return minSpin, maxSpin

    @staticmethod
    def checkAbilityBoundaries(spinners):
        """
        Checks if the lowest abilities meet the point-buy maximum.
        :param spinners: the name and value of the lowest value spinners, in a 2D array
        :type spinners: list
        :return: the error code, or lack of, the spinners produce
        """
        pointsLeft = 27
        racePoints = {"str": ["con", "cha"], "dex": ["con", "int", "wis", "cha"], "con": ["str", "str", "wis"],
                      "int": ["dex", "con"], "cha": ["str", "dex", "con", "int", "wis"]}
        mainOptions = ["str", "dex", "con", "int", "wis", "cha"]
        secondaryOptions = ["str", "dex", "con", "int", "wis", "cha"]
        valid = True
        spinners.sort(key=(lambda x: x[1]), reverse=True)

        for spinner in spinners:
            newVal = spinner[1]
            if newVal < 14:
                newVal -= 8
                pointsLeft -= newVal
            elif newVal < 16:
                newVal = 7 + (newVal % 2) * 2
                pointsLeft -= newVal
            elif newVal == 16:
                pointsLeft -= 7
                if spinner[0] in secondaryOptions:
                    mainOptions, secondaryOptions = [], []
                    for main, second in racePoints.items():
                        if spinner[0] in second:
                            mainOptions.append(spinner[0])
                else:
                    valid = False
            else:
                pointsLeft -= 9
                if spinner[0] in mainOptions:
                    mainOptions = []
                    secondaryOptions = racePoints[spinner[0]]
                else:
                    valid = False

        if valid is True:
            valid = pointsLeft >= 0
        if valid is False:
            return "Abilities set too high."
        else:
            return ""
