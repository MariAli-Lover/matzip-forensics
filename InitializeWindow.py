import sys
from PyQt5.QtWidgets import QApplication
from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QWizard
from hfs import *
import ctypes , os
form_class = uic.loadUiType(".\\UI\Initialize.ui")[0]

WIZARD_PAGE1 = 0
WIZARD_PAGE2 = 1
WIZARD_PAGE3 = 2
#

class InitializeWindow(QWizard, form_class):
    global selected_phydrive_num

    def __init__(self):
        super().__init__()
        self.setupUi(self)
    def setTabletTracking(self, a):
        print("zz")
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

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if __name__ == "__main__":
    if is_admin():
        print("it's admin!")
    else:
        ASADMIN = "asadmin"
        script = os.path.abspath(sys.argv[0])
        params = " ".join([script] + sys.argv[1:] + [ASADMIN])
        ctypes.windll.shell32.ShellExecuteW(None, u"runas", sys.executable, params, None, 0)

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