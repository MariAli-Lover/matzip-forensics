import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic, QtGui, Qt
from PyQt5.uic.uiparser import QtCore

from hfs import *

if main.os_mode == "WINDOWS" :
    form_class = uic.loadUiType(".\\UI\\Initialize.ui")[0]
elif main.os_mode == "MACOS" :
    form_class = uic.loadUiType("./UI/Initialize.ui")[0]

WIZARD_PAGE1 = 0
WIZARD_PAGE2 = 1
WIZARD_PAGE3 = 2
#

class InitializeWindow(QWizard, form_class):
    global selected_phydrive_num

    global loading_flag

    def __init__(self):
        self.loading_flag = False
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
            self.setDisabled(True) # 화면 disabled
            #loadingImage = QtGui.QMovie(":/UI_resource/loading.gif")
            #loadingImage.start()
            #player = ImagePlayer(loadingImage, "was")
            #self.loadingImage_label.setMovie(loadingImage)
            #self.loadingImage_label.setAttribute(Qt.WA_NoSystemBackground)
            hfs = HFSP(self.selected_phydrive_num)
            main.db1.updateDB_setup("DISK_NUM", str(self.selected_phydrive_num))
            main.db1.updateDB_setup("LOGICALIMAGING_OUTPUT_PATH", "C:\\" if main.os_mode == "WINDOWS" else "/")
            main.disk_num = self.selected_phydrive_num
            hfs.beginParsing(self)
            self.setEnabled(True) # 화면 enabled
        return 1


#    def parseHFS_event(self):



if __name__ == "__main__":
    app = QApplication(sys.argv)
    initWindow = InitializeWindow()
    initWindow.show()
    app.exec_()
    sys.exit()

    # app = QtWidgets.QApplication(sys.argv)
    # Wizard = QtWidgets.QWizard()
    # ui = Ui_Wizard()
    # ui.setupUi(Wizard)
    # Wizard.show()
    # sys.exit(app.exec_())
