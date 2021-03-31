from PyQt5 import uic
import altair as alt
import pandas as pd
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QWidget, QHBoxLayout

from Optimisation import ChromosomeController


class CharacterReviewController:
    """Sets up and runs the menu that allows the user to visually review a character."""

    controller = None
    selector = None

    def __init__(self):
        """
        Sets up the selector menu visuals.
        """
        Form, Window = uic.loadUiType("Visuals/QtFiles/CharacterReview.ui")
        self.window = Window()
        self.form = Form()
        self.form.setupUi(self.window)
        self.centre = self.window.findChild(QWidget, "centralwidget")

    def begin(self, controller):
        """
        Begins the character review menu and visualises it.
        :param controller: the controller for the programs visuals
        :type controller: VisualsController
        """
        self.controller = controller
        radar_view = self.create_web_view("radarBox")
        self.radar_chart(radar_view)



    def create_web_view(self, widget):
        """
        Sets up a web view within a widget, and returns a pointer to it.
        :param widget: the widget for the view to be nested within
        :type widget: str
        :return: a pointer to the QWebEngineView
        """
        widget = self.centre.findChild(QWidget, widget)
        webview = QWebEngineView()
        hbox = QHBoxLayout()
        hbox.addWidget(webview)
        widget.setLayout(hbox)
        return webview

    def radar_chart(self, widget):
        """
        Creates a radar chart for a chromosome.
        :param widget: the widget to place the radar chart into
        :type widget: QWidget
        """
        headings = list()
        counter = 1
        for chromosome in ChromosomeController.nondominatedFront:
            name = str(counter) + ". " + chromosome.character.chrClass.name + " " + chromosome.character.race.name
            for tag in chromosome.tags:
                headings.append({"Character": name, "key": tag[0], "value": tag[2], "category": 0})
            counter += 1

        chromosome = ChromosomeController.nondominatedFront[0]
        firstName = "1. " + chromosome.character.chrClass.name + " " + chromosome.character.race.name
        self.selector = alt.selection_single(encodings=['y'], init={'y': firstName})

        data = pd.DataFrame(headings)
        chart = alt.Chart(data).mark_bar(size=20, angle=20).encode(
            x="key",
            y="value"
        ).properties(
            title="Character Tags",
            width=200,
            height=200
        ).transform_filter(self.selector)

        result = chart & self.select_radar()
        self.controller.load_chart(widget, result)

    def select_radar(self):
        """
        Creates a chart that allows you to select which chromosome to view the radar chart of.
        """
        data = list()
        counter = 1
        for chromosome in ChromosomeController.nondominatedFront:
            name = str(counter) + ". " + chromosome.character.chrClass.name + " " + chromosome.character.race.name
            for tag in chromosome.tags:
                data.append({"Character": name, "Tag": tag[0], "Weighting": tag[2]})
            counter += 1

        data = pd.DataFrame(data)
        chart = alt.Chart(data).mark_bar(size=20).encode(
            x="Weighting",
            y=alt.Y("Character:N", sort="-x"),
            color=alt.condition(self.selector, alt.value("Gold"), "Tag:N")
        ).add_selection(self.selector)

        return chart
