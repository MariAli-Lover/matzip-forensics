from PyQt5.QtWidgets import QDialog, QApplication, QTableWidgetItem, QTreeWidgetItem, QFileDialog
from PyQt5 import uic
from PyQt5 import QtGui

import main

if main.os_mode == "WINDOWS" :
    print("current mode : " + main.os_mode)
    form_class_main = uic.loadUiType(".\\UI\LogicalImagingWindow.ui")[0]

elif main.os_mode == "MACOS" :
    form_class_main = uic.loadUiType("./UI/LogicalImagingWindow.ui")[0]


class LogicalImagingWindow(QDialog, form_class_main):

    global mainWindow # 메인윈도우 건드릴때 사용

    def __init__(self, mainWindow):
        self.mainWindow = mainWindow
        super().__init__()
        self.setupUi(self)
        #self.buttonBox.accepted.setEnabled(False)
        if main.os_mode == "WINDOWS" :
            self.btn_hfs_4.setDisabled(True) # 윈도우는 HFS+ 미지원
        #elif main.os_mode == "MACOS" :
        self.refresh_bookmark_list()
        self.lineEdit_path_4.setText(main.logicalImaging_output_path)
        self.exec_()

    def refresh_bookmark_list(self):
        self.treeWidget_ib_4.clear()
        bookmark_row = main.db1.executeOneQueryMany("SELECT * FROM BOOKMARK") #북마크 전체 불러옴
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/UI_resource_Add_to_Bookmark/bookmarks-bookmark@32px.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        main.printDebugMessage("len_bookmark_row : " + str(len(bookmark_row)))
        if len(bookmark_row) > 0 : #북마크가 한 개 이상 있을 시
            for bookmark in bookmark_row:
                bookmark_file_count = main.db1.executeOneQuery("SELECT COUNT(*) FROM BOOKMARK_EVIDENCES WHERE BOOKMARK_NUM = " + str(bookmark[0]))[0] #북마크 파일갯수
                row = QTreeWidgetItem()  # 새 QTreeWidgetItem 생성
                row.setText(0, str(bookmark[1]))  # 최상위폴더 이름적어줌
                row.setIcon(0, icon)
                row.setText(1, str(bookmark_file_count))
                #row.setIcon(0, folder_icon)
                self.treeWidget_ib_4.addTopLevelItem(row)
                #self.itemView.item(row_num, 0).setIcon(file_icon)
                #self.itemView.item(row_num, 0).setCheckState(QtCore.Qt.Unchecked)
        else : #북마크 한 개도 없으면
            row = QTreeWidgetItem()
            row.setText(0, "북마크를 한 개 이상 추가해주세요.")
            self.treeWidget_ib_4.addTopLevelItem(row)

    def get_output_path_button_UI(self):
        #fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "", "All Files (*);;Disk Image Files (*.dd *.vhd)", options=options)
        main.logicalImaging_output_path = QFileDialog.getExistingDirectory(self, "Output path", "C:\\" if main.os_mode == "WINDOWS" else "/")
        self.lineEdit_path_4.setText(main.logicalImaging_output_path) # output_path 띄워줌
        main.db1.updateDB_setup("LOGICALIMAGING_OUTPUT_PATH", main.logicalImaging_output_path)
        #fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
         #                                         "All Files (*);;Disk Image Files (*.dd *.vhd)", options=options)

    def accept(self):
        self.mainWindow.logicalImaging()