import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.uic.uiparser import QtCore

from hfs import *

form_class = uic.loadUiType("untitled.ui")[0]

WIZARD_PAGE1 = 0
WIZARD_PAGE2 = 1
WIZARD_PAGE3 = 2
#

class InitializeWindow(QWidget, form_class):
    global selected_phydrive_num

    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def asdfasdf(self):
        self.label.setText("asdasdasasdasd")
#    def parseHFS_event(self):



if __name__ == "__main__":
    app = QApplication(sys.argv)
    initWindow = InitializeWindow()
    initWindow.show()
    app.exec_()

    # app = QtWidgets.QApplication(sys.argv)
    # Wizard = QtWidgets.QWizard()
    # ui = Ui_Wizard()
    # ui.setupUi(Wizard)
    # Wizard.show()
    # sys.exit(app.exec_())