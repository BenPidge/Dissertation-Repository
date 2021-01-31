from functools import partial

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *


class SelectorMenu:
    archetypes = {"Monster Hunter": "The monster hunter is an expert in killing large creatures, typically using "
                                    "equally large weapons to do so. They’re brave and strong, with heavy experience "
                                    "and knowledge in hunting their enemies for reward.",
                  "Sage": "Wise old advisors, sages are known for their magical capabilities, often with nature. "
                          "They’re the first to aid others, and are often good at treating wounded allies or "
                          "handling their problems.",
                  "Entertainer": "Entertainers focus on their charm and musical capabilities to get through life. Some "
                                 "may use this to support their friends, while others use it to manipulate and fool.",
                  "Cultist": "Cultists are creepy practitioners in the dark arts, normally to fulfil evil intentions. "
                             "They lay themselves as mysterious to others, while they use forbidden magic to "
                             "manipulate others into following them in a hivemind-esque mentality."}

    abilitySpinners = dict()
    skillCheckBoxes = []

    def __init__(self):
        """
        Sets up the selector menu visuals.
        """
        Form, Window = uic.loadUiType("Visuals/SelectorMenu.ui")
        self.app = QApplication([])
        self.window = Window()
        self.form = Form()
        self.form.setupUi(self.window)
        self.centre = self.window.findChild(QWidget, "centralwidget")

    def begin(self):
        """
        Begins the selector menu and visualises it.
        """
        self.setupArchetypeButtons()
        self.setupArchetypeDropdowns()
        self.setupSpinBoxes()
        self.setupCheckBoxes()
        shadowItems = {"graphicsView": QGraphicsView,
                       "graphicsView_2": QGraphicsView,
                       "startProgram": QPushButton,
                       "advancedFeatures": QPushButton}
        self.setupShadows(shadowItems)
        self.centre.findChild(QLabel, "error").setAlignment(Qt.AlignCenter)

        self.centre.findChild(QPushButton, "startProgram").clicked.\
            connect(partial(self.setupStartButton))

        self.window.show()
        self.app.exec_()

    def setupArchetypeButtons(self):
        """
        Sets up the button selections for choosing an archetype description to view.
        """
        scrollArea = self.centre.findChild(QScrollArea, "archetypeDescSelect")
        vbox = QVBoxLayout()
        widget = QWidget()

        for name, desc in self.archetypes.items():
            btn = QPushButton(text=name)
            btn.setStyleSheet("background-color: rgb(255, 255, 255);")
            btn.clicked.connect(partial(self.archetypeButtonPressed, arch_desc=desc))
            vbox.addWidget(btn)
        widget.setLayout(vbox)
        scrollArea.setWidget(widget)

    def setupStartButton(self):
        values = [["str"], ["dex"], ["con"], ["int"], ["wis"], ["cha"]]
        spinners = self.abilitySpinners
        for x in range(0, len(spinners.items())):
            values[x].append(list(spinners.values())[x][0].value())

        errorCode = self.checkAbilityBoundaries(values) + " " + self.checkSkills()
        self.centre.findChild(QLabel, "error").setText(errorCode)
        if errorCode == " ":
            # start the program
            pass

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
        for archetype in list(self.archetypes.keys()):
            primaryDropdown.addItem(archetype)
            secondaryDropdown.addItem(archetype)

    def setupShadows(self, shadow_items):
        """
        Sets up the shadows for all widgets passed through.
        :param shadow_items: a name:type dictionary of widgets to give shadows
        :type shadow_items: dict
        """
        for item, obj in shadow_items.items():
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(15)
            self.centre.findChild(obj, item).setGraphicsEffect(shadow)

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

