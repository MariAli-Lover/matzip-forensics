import sys
import time
from PyQt5.QtWidgets import QDialog, QApplication, QTableWidgetItem, QTreeWidgetItem
from PyQt5 import uic
from PyQt5 import QtGui

import main

if main.os_mode == "WINDOWS" :
    print("current mode : " + main.os_mode)
    form_class_main = uic.loadUiType(".\\UI\AddToBookmarkWindow.ui")[0]
    form_class_new = uic.loadUiType(".\\UI\AddToBookmarkWindow_NewBookmark.ui")[0] #
    form_class_delete = uic.loadUiType(".\\UI\AddToBookmarkWindow_DeleteBookmark.ui")[0]

elif main.os_mode == "MACOS" :
    form_class_main = uic.loadUiType("./UI/AddToBookmarkWindow.ui")[0]
    form_class_new = uic.loadUiType("./UI/AddToBookmarkWindow_NewBookmark.ui")[0] #
    form_class_delete = uic.loadUiType("./UI/AddToBookmarkWindow_DeleteBookmark.ui")[0]


class AddToBookmarkWindow_main(QDialog, form_class_main):

    global selected_bookmark_num
    global mainWindow # 메인윈도우 건드릴때 사용

    def __init__(self, mainWindow):
        self.mainWindow = mainWindow
        self.selected_bookmark_num = 0
        super().__init__()
        self.setupUi(self)
        #self.buttonBox.accepted.setEnabled(False)
        self.refresh_bookmark_list()
        self.exec_()


    def refresh_bookmark_list(self):
        self.bookmark_list_treeWidget.clear()
        bookmark_row = main.db1.executeOneQueryMany("SELECT * FROM BOOKMARK") #북마크 전체 불러옴
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/UI_resource_Add_to_Bookmark/bookmarks-bookmark@32px.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        for bookmark in bookmark_row:
            bookmark_file_count = main.db1.executeOneQuery("SELECT COUNT(*) FROM BOOKMARK_EVIDENCES WHERE BOOKMARK_NUM = " + str(bookmark[0]))[0]  # 북마크 파일갯수
            row = QTreeWidgetItem()  # 새 QTreeWidgetItem 생성
            row.setText(0, str(bookmark[1]))  # 최상위폴더 이름적어줌
            row.setIcon(0, icon)
            row.setText(1, str(bookmark_file_count))
            #row.setIcon(0, folder_icon)
            self.bookmark_list_treeWidget.addTopLevelItem(row)
            #self.itemView.item(row_num, 0).setIcon(file_icon)
            #self.itemView.item(row_num, 0).setCheckState(QtCore.Qt.Unchecked)


    def new_bookmark_button_UI(self):
        addToBookmarkWindow_new = AddToBookmarkWindow_new(self.mainWindow)
        self.refresh_bookmark_list()

    def select_bookmark_button_UI(self, QModelIndex) :
        self.selected_bookmark_num = QModelIndex.row() + 1 #북마크는 1부터 시작하기 때문


    def accept(self):
        if self.selected_bookmark_num != 0 :
            item_dict = {}
            for check_item in self.mainWindow.check_item_list:
                item_dict['bookmark_num'] = self.selected_bookmark_num
                item_dict['evidence_num'] = check_item

                print(item_dict)
                main.db1.insertDB("BOOKMARK_EVIDENCES", item_dict)

            main.db1.commit()
            self.close()


class AddToBookmarkWindow_new(QDialog, form_class_new):
    global mainWindow
    def __init__(self, mainWindow):
        self.mainWindow = mainWindow
        super().__init__()
        self.setupUi(self)
        self.exec_()
    def accept(self) :
        bookmark_name = self.bookmarkName_textEdit.toPlainText()
        bookmark_editor = self.bookmarkEditor_textEdit.toPlainText()
        bookmark_explanation = self.bookmarkExplanation_textEdit.toPlainText()
        bookmark_time = time.time()
        bookmark_num = int(main.db1.executeOneQuery("SELECT * FROM SETUP WHERE NAME is 'BOOKMARK_NUM'")[1])
        row = main.db1.executeOneQuery("SELECT COUNT(*) FROM BOOKMARK WHERE NAME is '" + bookmark_name +"'")[0]
        if row == 0 :
            item_dict = {}
            item_dict['num'] = bookmark_num + 1
            item_dict['name'] = bookmark_name
            item_dict['editor'] = bookmark_editor
            item_dict['create_time'] = bookmark_time
            item_dict['explanation'] = bookmark_explanation
            main.db1.insertDB("BOOKMARK", item_dict)
            main.db1.updateDB_setup("BOOKMARK_NUM", str(bookmark_num + 1))
            main.db1.commit()
            self.mainWindow.showBookmark_UI()
            self.close()

class AddToBookmarkWindow_delete(QDialog, form_class_delete):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = AddToBookmarkWindow_main()

    app.exec_()
