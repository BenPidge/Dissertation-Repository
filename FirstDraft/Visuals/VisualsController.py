from PyQt5.QtWidgets import QApplication, QGraphicsDropShadowEffect

from Visuals import SelectorMenu, AdvancedFiltersMenu


class VisualsController:
    """Controls all visual elements of the program."""

    app = QApplication([])
    selectorMenu = SelectorMenu.SelectorMenu()
    advancedFiltersMenu = AdvancedFiltersMenu.AdvancedFiltersMenu()

    def begin(self):
        """
        Begins the program visuals.
        """
        self.selectorMenu.begin(self)
        self.app.exec_()

    def start_advanced_filters_menu(self):
        """
        Starts up the advanced filters menu window.
        """
        self.advancedFiltersMenu.begin(self)
        self.selectorMenu.window.hide()

    def stop_advanced_filters_menu(self):
        """
        Visually stops the advanced filters menu window.
        """
        self.advancedFiltersMenu.window.hide()
        self.selectorMenu.window.show()

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
