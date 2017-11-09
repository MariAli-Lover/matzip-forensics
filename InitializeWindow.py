import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.uic.uiparser import QtCore

from hfs import *

form_class = uic.loadUiType("Initialize.ui")[0]

WIZARD_PAGE1 = 0
WIZARD_PAGE2 = 1
WIZARD_PAGE3 = 2
#

class InitializeWindow(QWizard, form_class):
    global selected_phydrive_num

    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def setNewCase_button(self, a):
        print(a)

    def selectPhyDrive_button(self, a):
        self.selected_phydrive_num = a.row()  # 선택된 드라이브번호 저장
        print(self.selected_phydrive_num)
    def validateCurrentPage(self):
        if self.nextId() == WIZARD_PAGE2:
            phy_drive_list = HFSP.getPhysicalDrives(self)
            phy_drive_num = 0

            for phy_drive in phy_drive_list :
                item = self.listWidget.addItem(phy_drive)
                #item
                phy_drive_num += 1
            #self.listWidget.setSortingEnabled(__sortingEnabled)
        if self.nextId() == WIZARD_PAGE3:
            hfs = HFSP(self.selected_phydrive_num, self)
        return 1
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