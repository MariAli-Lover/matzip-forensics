from PyQt5.QtWidgets import QDialog, QApplication, QTableWidgetItem, QTreeWidgetItem
from PyQt5 import uic
from PyQt5 import QtGui

import main

if main.os_mode == "WINDOWS" :
    print("current mode : " + main.os_mode)
    form_class_main = uic.loadUiType(".\\UI\SearchWindow.ui")[0]

elif main.os_mode == "MACOS" :
    form_class_main = uic.loadUiType("./UI/SearchWindow.ui")[0]


class SearchWindow(QDialog, form_class_main):

    global selected_bookmark_num
    global mainWindow # 메인윈도우 건드릴때 사용

    def __init__(self, mainWindow):
        self.mainWindow = mainWindow
        self.selected_bookmark_num = 0
        super().__init__()
        self.setupUi(self)
        #self.buttonBox.accepted.setEnabled(False)
        self.exec_()

    def accept(self) :
        keyword = self.textEdit.toPlainText()
        self.mainWindow.ls_search_UI(keyword)
        self.close()
