import sys
from PyQt5.QtWidgets import QDialog, QApplication, QTableWidgetItem, QTreeWidgetItem
from PyQt5 import uic

import main

form_class_main = uic.loadUiType(".\\UI\AddToBookmarkWindow.ui")[0]
form_class_new = uic.loadUiType(".\\UI\AddToBookmarkWindow_NewBookmark.ui")[0] #
form_class_delete = uic.loadUiType(".\\UI\AddToBookmarkWindow_DeleteBookmark.ui")[0]

class AddToBookmarkWindow_main(QDialog, form_class_main):

    global selected_bookmark_num
    global check_item_list
    global path

    def __init__(self, check_item_list, path):
        self.check_item_list = check_item_list
        self.path = path
        super().__init__()
        self.setupUi(self)
        #self.buttonBox.accepted.setEnabled(False)
        self.refresh_bookmark_list()
        self.exec_()


    def refresh_bookmark_list(self):
        bookmark_row = main.db1.executeOneQueryMany("SELECT * FROM BOOKMARK") #북마크 전체 불러옴
        for bookmark in bookmark_row:
            row = QTreeWidgetItem()  # 새 QTreeWidgetItem 생성
            row.setText(0, str(bookmark[1]))  # 최상위폴더 이름적어줌
            row.setText(1, "0")
            #row.setIcon(0, folder_icon)
            self.bookmark_list_treeWidget.addTopLevelItem(row)
            #self.itemView.item(row_num, 0).setIcon(file_icon)
            #self.itemView.item(row_num, 0).setCheckState(QtCore.Qt.Unchecked)


    def new_bookmark_button_UI(self):
        addToBookmarkWindow_new = AddToBookmarkWindow_new()
        self.refresh_bookmark_list()

    def select_bookmark_button_UI(self, QModelIndex) :
        self.selected_bookmark_num = QModelIndex.row() + 1 #북마크는 1부터 시작하기 때문


    def accept(self):
        item_dict = {}
        print("1")
        for check_item in self.check_item_list:
            item_dict['bookmark_num'] = self.selected_bookmark_num
            item_dict['name'] = check_item
            item_dict['path'] = "/"+self.path
            print(item_dict)
            main.db1.updateDB("BOOKMARK_ITEM", item_dict)
            main.db1.commit()


class AddToBookmarkWindow_new(QDialog, form_class_new):
    def __init__(self):

        super().__init__()
        self.setupUi(self)
        self.exec_()
    def accept(self) :
        print("1")
        bookmark_name = self.bookmarkName_textEdit.toPlainText()
        print("2")
        row = main.db1.executeOneQuery("SELECT COUNT(*) FROM BOOKMARK WHERE NAME is '" + bookmark_name +"'")[0]
        print("3")
        if row == 0 :
            item_dict = {}
            item_dict['num'] = 1
            item_dict['name'] = bookmark_name
            main.db1.insertDB("BOOKMARK", item_dict)
            main.db1.commit()
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