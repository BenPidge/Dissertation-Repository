from io import StringIO
from PyQt5.QtWidgets import QApplication, QGraphicsDropShadowEffect
from Visuals import SelectorMenu, AdvancedFiltersMenu, LoadingScreen


class VisualsController:
    """Controls all visual elements of the program."""

    advancedFiltersUsed = False
    filters = None

    app = QApplication([])
    selectorMenu = None
    advancedFiltersMenu = None
    loadingScreen = None

    def begin(self):
        """
        Begins the program visuals.
        """
        # the declarations are done here for the potential future use of resets
        self.selectorMenu = SelectorMenu.SelectorMenu()
        self.advancedFiltersMenu = AdvancedFiltersMenu.AdvancedFiltersMenu()
        self.loadingScreen = LoadingScreen.LoadingScreen()
        self.advancedFiltersUsed = False
        self.filters = dict()

        self.selectorMenu.begin(self)
        self.app.exec_()

    def start_advanced_filters_menu(self):
        """
        Starts up the advanced filters menu window.
        """
        self.advancedFiltersMenu.begin(self)
        self.selectorMenu.window.hide()
        self.advancedFiltersUsed = True

    def stop_advanced_filters_menu(self):
        """
        Visually stops the advanced filters menu window.
        """
        self.advancedFiltersMenu.window.hide()
        self.selectorMenu.window.show()

    def retrieve_filters(self):
        """
        Retrieves the filters applied into a dictionary.
        """
        self.filters.clear()
        self.filters.update(self.selectorMenu.get_filters())
        if self.advancedFiltersUsed:
            self.filters.update(self.advancedFiltersMenu.get_filters())
        for (tag, item) in self.filters.items():
            if type(item) is list:
                self.filters[tag].sort()

    def load_optimisation(self):
        """
        Provides a visual gap between the user requesting optimisation and the time taken to run
        optimising and visualising methods.
        """
        self.retrieve_filters()

        self.loadingScreen.begin(self)
        self.selectorMenu.window.hide()
        self.loadingScreen.window.show()

    @staticmethod
    def setup_shadows(centre, shadow_items):
        """
        Sets up the shadows for all widgets passed through.
        :param shadow_items: a name:type dictionary of widgets to give shadows
        :type shadow_items: dict
        :param centre: the centre widget that the passed widgets rest on
        :type centre: widget
        :return: the modified centre
        """
        for item, obj in shadow_items.items():
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(15)
            centre.findChild(obj, item).setGraphicsEffect(shadow)
        return centre

    @staticmethod
    def load_chart(widget, chart):
        """
        Loads a pulled chart into a Qt widget.
        :param widget: the widget to place the chart within
        :type widget: class: `QtWebEngineWidgets.QWebEngineView`
        :param chart: the chart to insert into the widget
        :type chart: class: `altair.Chart`
        """
        html = StringIO()
        chart.save(html, "html")
        widget.setHtml(html.getvalue())
