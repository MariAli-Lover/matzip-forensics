import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.uic.uiparser import QtWidgets
from PyQt5 import QtGui, QtCore

from AddToBookmarkWindow import *
from AddToBookmarkWindow import AddToBookmarkWindow_new
from AddToBookmarkWindow import AddToBookmarkWindow_delete
from hfs import *
from PyQt5.QtWidgets import QDialog

form_class = uic.loadUiType(".\\UI\MainWindow.ui")[0]
#

class MainWindow(QMainWindow, form_class):
    global selected_phydrive_num
    global path
    global check_item_list

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.check_item_list = []

    def ls_UI(self, QModelIndex):
        if self.itemView.rowCount() > 0 :
            for i in range(self.itemView.rowCount()) :
                self.itemView.removeRow(i)
        #선택한 폴더의 번호를 알기 위해 경로를 구해야함.
        path = ""
        qmi = QModelIndex # 경로를 알기위한 재귀
        while True :
            qmi = qmi.parent()
            path = str(qmi.data()) + "/" + path
            if not qmi.parent().isValid() :
                break
        self.path = path # path 저장
        #경로로 폴더를 찾음
        folder_location = main.db1.executeOneQuery("SELECT * FROM FOLDER WHERE PATH is '/" + path + "' AND NAME is '" + str(QModelIndex.data()) +"'" )[0]
        row_folder, row_evidences = main.db1.getItemList(folder_location)
        file_icon = QtGui.QIcon()
        file_icon.addPixmap(QtGui.QPixmap(":/UI_resource/documents-document-blank@32px.png"), QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)
        for row_num, row_data in enumerate(row_evidences):
            self.itemView.insertRow(row_num)
            for column_num, data in enumerate(row_data):
                self.itemView.setItem(row_num, column_num, QTableWidgetItem(str(data)))
            self.itemView.item(row_num, 0).setIcon(file_icon)
            self.itemView.item(row_num, 0).setCheckState(QtCore.Qt.Unchecked)

    def ItemView_checked_UI(self, QTableWidgetItem): # 북마크하려고 체크할때 어떤거 체크했는지 parsing
        if QTableWidgetItem.checkState() == 2 : #체크가 되면
            check_item_flag = False #체크리스트에 파일 있는지여부

            for check_item_tmp in self.check_item_list : # 이미 체크리스트에 파일 있는지 확인
                if check_item_tmp == QTableWidgetItem.data(0) :
                    check_item_flag = True #있으면 False
                    break

            if check_item_flag == False : # 체크리스트에 파일이 없으면
                self.check_item_list.append(QTableWidgetItem.data(0)) # 체크리스트에 파일명 추가

        else : #체크가 풀리면
            check_item_flag = False #체크리스트에 파일 있는지여부
            for check_item_tmp in self.check_item_list : # 이미 체크리스트에 파일 있는지 확인
                if check_item_tmp == QTableWidgetItem.data(0) :
                    print("true")
                    check_item_flag = True #있으면 False
                    break
            if check_item_flag == True : # 체크리스트에 파일이 있으면
                self.check_item_list.remove(QTableWidgetItem.data(0)) #체크 풀린거 삭제

        print(self.check_item_list)

    def AddToBookmark_button_UI(self):
        if len(self.check_item_list) != 0 :
           addToBookmarkWindow = AddToBookmarkWindow_main(self.check_item_list, self.path) # 체크리스트, 경로 넘김
#    def parseHFS_event(self):

def showDirectoryTree_UI() :
    row_dict = {}
    folders = main.db1.executeOneQueryMany("SELECT * FROM FOLDER")
    root_folder_flag = True
    folder_icon = QtGui.QIcon()
    folder_icon.addPixmap(QtGui.QPixmap(":/UI_resource/documents-folder@32px.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    for folder in folders :
        if root_folder_flag == True : #최상위 폴더일 때
            row = QTreeWidgetItem() # 새 QTreeWidgetItem 생성
            row.setText(0, folder[1]) # 최상위폴더 이름적어줌
            row.setIcon(0, folder_icon)
            row_dict[folder[0]] = row
            mainWindow.treeWidget.addTopLevelItem(row)
            root_folder_flag = False #앞으로 최상위폴더 파싱 X
        else :
            row = QTreeWidgetItem()  # 새 QTreeWidgetItem 생성
            row.setText(0, folder[1])  # 최상위폴더 이름적어줌
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(":/UI_resource/documents-folder@32px.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            row.setIcon(0, folder_icon)
            row_dict[folder[0]] = row # row_dict에 자신의 폴더넘버로 row 추가item_0 = QtWidgets.QTreeWidgetItem(mainWindow.treeWidget)
            row_dict[folder[3]].addChild(row) #상위 row에 자신을 추가

def showBookmark_UI() :
    row_dict = {}
    bookmarks = main.db1.executeOneQueryMany("SELECT * FROM BOOKMARK")
    for bookmark in bookmarks :
        row = QTreeWidgetItem()  # 새 QTreeWidgetItem 생성
        row.setText(0, bookmark[1])  # 최상위폴더 이름적어줌
        #row.setIcon(0, folder_icon)
        mainWindow.bookmark_treeWidget.addTopLevelItem(row)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    mainWindow.treeWidget.headerItem().setText(0, "Name")


    showDirectoryTree_UI()
    showBookmark_UI()
    app.exec_()

    # app = QtWidgets.QApplication(sys.argv)
    # Wizard = QtWidgets.QWizard()
    # ui = Ui_Wizard()
    # ui.setupUi(Wizard)
    # Wizard.show()
    # sys.exit(app.exec_())



