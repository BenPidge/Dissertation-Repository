from functools import partial

from PyQt5 import uic
from PyQt5.QtWidgets import *


class AdvancedFiltersMenu:
    """Sets up and runs the menu that allows the application of advanced character features."""

    controller = None

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

        shadowItems = {"graphicsView": QGraphicsView}
        self.centre = self.controller.setupShadows(self.centre, shadowItems)

        btn = self.centre.findChild(QPushButton, "saveAdvancedOptions")
        btn.clicked.connect(partial(self.saveBtnClicked))

        self.window.show()

    def saveBtnClicked(self):
        """
        Reacts to the save advanced options button being placed, by calling the controller.
        """
        self.controller.stopAdvancedFiltersMenu()
