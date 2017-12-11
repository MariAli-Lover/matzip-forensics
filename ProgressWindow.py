from PyQt5.QtWidgets import QDialog, QApplication, QTableWidgetItem, QWidget
from PyQt5 import uic
from PyQt5 import QtGui

import main

if main.os_mode == "WINDOWS" :
    print("current mode : " + main.os_mode)
    form_class_main = uic.loadUiType(".\\UI\ProgressWindow.ui")[0]

elif main.os_mode == "MACOS" :
    form_class_main = uic.loadUiType("./UI/ProgressWindow.ui")[0]


class ProgressWindow(QWidget, form_class_main):

    global mainWindow # 메인윈도우 건드릴때 사용

    def __init__(self, mainWindow, windowTitle):
        self.mainWindow = mainWindow
        super().__init__()
        self.setWindowTitle(windowTitle)
        self.setupUi(self)
        self.show()
    def prevent_destroyed(self):
        print("hi")
