from PyQt5 import uic
from PyQt5.QtWidgets import QApplication

# sets up the selector menu visuals
Form, Window = uic.loadUiType("SelectorMenu.ui")
app = QApplication([])
window = Window()
form = Form()
form.setupUi(window)
window.show()
app.exec_()

