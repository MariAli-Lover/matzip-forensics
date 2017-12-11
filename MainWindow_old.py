import sys
from multiprocessing.pool import Pool
import binascii
from PyQt5.QtCore import QEventLoop, pyqtSlot
from PyQt5.QtGui import QPixmap, QMovie
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.uic.uiparser import QtWidgets
from PyQt5 import QtGui, QtCore

from AddToBookmarkWindow import AddToBookmarkWindow_main
from AddToBookmarkWindow import AddToBookmarkWindow_new
from AddToBookmarkWindow import AddToBookmarkWindow_delete
from hfs import *
from PyQt5.QtWidgets import QDialog

from makedd import MakeDD

if main.os_mode == "WINDOWS" :
    form_class = uic.loadUiType(".\\UI\MainWindow.ui")[0]
elif main.os_mode == "MACOS" :
    form_class = uic.loadUiType("./UI/MainWindow.ui")[0]

#form_class = uic.loadUiType(".\\UI\MainWindow.ui")[0]


class MySplashScreen(QSplashScreen):
    def __init__(self, animation, flags):
        # run event dispatching in another thread
        QSplashScreen.__init__(self, QPixmap(), flags)
        self.movie = QMovie(animation)
        self.movie.frameChanged.connect(self.onNextFrame)
        self.movie.start()

    @pyqtSlot()
    def onNextFrame(self):
        pixmap = self.movie.currentPixmap()
        self.setPixmap(pixmap)
        self.setMask(pixmap.mask())

class MainWindow(QMainWindow, form_class):
    global selected_phydrive_num
    global path
    global check_item_list
    global loading_flag

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.check_item_list = []
        self.loading_flag = False

    def ls_hex_UI(self):
        self.current = self.itemView.currentRow()

        if (self.current == -1):
            return
        else:
            try:
                self.tuple_store = int(str(self.itemView.item(self.current, 14).text()))
                print(self.tuple_store, type(self.tuple_store))
                hex_data = HFSP(1).parsingdata22(self.tuple_store)
                self.textBrowser.setText(hex_data)
            except:
                # when you tried to add row and give new element you'll get error
                return

    def ls_key_UI(self):
        print("1")
        if self.itemView.rowCount() > 0 : #뷰에 띄워져있던거 다초기화
            row_count = self.itemView.rowCount()
            for i in range(row_count) :
                main.printDebugMessage("remove row : " + str(i))
                self.itemView.removeRow(0)
        self.check_item_list.clear() # 체크리스트 초기화
        para = self.keyfile_treeWidget.currentItem().text(0)
        result = None
        if(para == "Document Files"):
            print("1")
            document_sql = "SELECT * FROM evidences WHERE NAME REGEXP '(\.otf)|(\.pdf)|(\.txt)|(\.ttxt)|(\.xlsx)' AND PATH REGEXP '(\/무제\/Users)' AND PATH NOT REGEXP '(\/무제\/Users\/allen\/Library)'"
            result = main.db1.cur.execute(document_sql)
        if (para == "Compressed Files"):
            document_sql = "SELECT * FROM evidences WHERE NAME REGEXP '(\.zip)|(\.tar)|(\.tar\.gz)|(\.alz)|(\.gz)|(\.7z)' AND PATH REGEXP '(\/무제\/Users)' AND PATH NOT REGEXP '(\/무제\/Users\/allen\/Library)'"
            result = main.db1.cur.execute(document_sql)
        if (para == "Graphic Files"):
            document_sql = "SELECT * FROM evidences WHERE NAME REGEXP '(\.jpeg)|(\.png)|(\.icns)|(\.thm)|(\.aae)|(\.itc)|(\.itc2)|(\.pict)|(\.pictclipping)' AND PATH REGEXP '(\/무제\/Users)' AND PATH NOT REGEXP '(\/무제\/Users\/allen\/Library)'"
            result = main.db1.cur.execute(document_sql)
        if (para == "Multimedia Files"):
            document_sql = "SELECT * FROM evidences WHERE NAME REGEXP '(\.snd)|(\.song)|(\.avi)|(\.mp4)|(\.mp3)' AND PATH REGEXP '(\/무제\/Users)' AND PATH NOT REGEXP '(\/무제\/Users\/allen\/Library)'"
            result = main.db1.cur.execute(document_sql)

        if (para == "System Log Files"):
            document_sql = "SELECT * FROM evidences WHERE NAME REGEXP '(\.plist)' OR PATH REGEXP '(\/무제\/Users)'"
            result = main.db1.cur.execute(document_sql)
        if (para == "Web Browser Log Files"):
            document_sql = "SELECT * FROM evidences WHERE PATH REGEXP '(\/Library\/Safari\/)|(/Library/Application Support/Firefox/Profiles/*.default/places.sqlite)|(\/Library\/Application \\ Support\/com.operasoftware.Opera/history)'"
            result = main.db1.cur.execute(document_sql)
        file_icon = QtGui.QIcon()
        file_icon.addPixmap(QtGui.QPixmap(":/UI_resource/documents-document-blank@32px.png"), QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)
        for row_num, row_data in enumerate(result):
            self.itemView.insertRow(row_num)
            for column_num, data in enumerate(row_data):
                self.itemView.setItem(row_num, column_num, QTableWidgetItem(str(data)))
            self.itemView.item(row_num, 0).setIcon(file_icon)
            self.itemView.item(row_num, 1).setCheckState(QtCore.Qt.Unchecked) # 체크버튼 넣어줌
        print("1")

    def ls_UI(self, QModelIndex):
        #self.itemView.clear()
        if self.itemView.rowCount() > 0 : #뷰에 띄워져있던거 다초기화
            row_count = self.itemView.rowCount()
            for i in range(row_count) :
                main.printDebugMessage("remove row : " + str(i))
                self.itemView.removeRow(0)
        self.check_item_list.clear() # 체크리스트 초기화
        #선택한 폴더의 번호를 알기 위해 경로를 구해야함.
        path = ""
        qmi = QModelIndex # 경로를 알기위한 재귀
        while True :
            qmi = qmi.parent()
            path = str(qmi.data()) + "/" + path
            if not qmi.parent().isValid() :
                break
        self.path = path + str(QModelIndex.data()) + "/"# 자신의 폴더명을 포함한 path 저장 (나중에 체크리스트 위해)
        #경로로 폴더를 찾음
        folder_location = main.db1.executeOneQuery("SELECT * FROM FOLDER WHERE PATH is '/" + path + "' AND NAME is '" + str(QModelIndex.data()) +"'" )[0]
        row_folder, row_evidences = main.db1.getItemList(folder_location)
        file_icon = QtGui.QIcon()
        file_icon.addPixmap(QtGui.QPixmap(":/UI_resource/documents-document-blank@32px.png"), QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)
        for row_num, row_data in enumerate(row_evidences):
            self.itemView.insertRow(row_num)
            main.printDebugMessage("insert row : " + str(row_num) + "name : " + str(row_data[1]) + "path : " + str(row_data[2]))
            for column_num, data in enumerate(row_data):
                self.itemView.setItem(row_num, column_num, QTableWidgetItem(str(data)))
            self.itemView.item(row_num, 0).setIcon(file_icon)
            self.itemView.item(row_num, 1).setCheckState(QtCore.Qt.Unchecked) # 체크버튼 넣어줌


    def ls_bookmark_UI(self, QModelIndex):
        #self.itemView.clear()
        if self.itemView.rowCount() > 0 : #뷰에 띄워져있던거 다초기화
            row_count = self.itemView.rowCount()
            for i in range(row_count) :
                main.printDebugMessage("remove row : " + str(i))
                self.itemView.removeRow(0)
        self.check_item_list.clear() # 체크리스트 초기화

        #선택한 북마크의 번호를 찾음
        bookmark_location = main.db1.executeOneQuery("SELECT * FROM BOOKMARK WHERE NAME is '" + str(QModelIndex.data()) +"'" )[0]
        main.printDebugMessage("bookmark_location : " + str(bookmark_location))
        row_evidences = main.db1.getItemList_bookmark(bookmark_location)
        file_icon = QtGui.QIcon()
        file_icon.addPixmap(QtGui.QPixmap(":/UI_resource/documents-document-blank@32px.png"), QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)
        main.printDebugMessage("getItemList_bookmark")
        for row_num, row_data in enumerate(row_evidences):
            self.itemView.insertRow(row_num)
            main.printDebugMessage("insert row : " + str(row_num) + "name : " + row_data[1] + "path : " + row_data[2])
            for column_num, data in enumerate(row_data):
                self.itemView.setItem(row_num, column_num, QTableWidgetItem(str(data)))
            self.itemView.item(row_num, 0).setIcon(file_icon)
            self.itemView.item(row_num, 0).setCheckState(QtCore.Qt.Unchecked) # 체크버튼 넣어줌

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
           addToBookmarkWindow = AddToBookmarkWindow_main(self) # 체크리스트, 현재 경로 넘김

    def makeDD_button_UI(self):
        bookmark_file_num_list = []
        evidences_row = main.db1.executeOneQueryMany("SELECT * FROM EVIDENCES WHERE BOOKMARK = '1'")
        for evidences in evidences_row :
            bookmark_file_num_list.append(evidences[0])
            main.printDebugMessage("evidence 추가")
        makedd = MakeDD()
        makedd.moveEvidence(bookmark_file_num_list)
        makedd.dumpMetadata(bookmark_file_num_list)
        makedd.detach()

    def showDirectoryTree_UI(self):
        row_dict = {}
        folders = main.db1.executeOneQueryMany("SELECT * FROM FOLDER")
        root_folder_flag = True
        folder_icon = QtGui.QIcon()
        folder_icon.addPixmap(QtGui.QPixmap(":/UI_resource/documents-folder@32px.png"), QtGui.QIcon.Normal,
                              QtGui.QIcon.Off)
        for folder in folders:
            if root_folder_flag == True:  # 최상위 폴더일 때
                row = QTreeWidgetItem()  # 새 QTreeWidgetItem 생성
                row.setText(0, folder[1])  # 최상위폴더 이름적어줌
                row.setIcon(0, folder_icon)
                row_dict[folder[0]] = row
                self.treeWidget.addTopLevelItem(row)
                root_folder_flag = False  # 앞으로 최상위폴더 파싱 X
            else:
                row = QTreeWidgetItem()  # 새 QTreeWidgetItem 생성
                row.setText(0, folder[1])  # 최상위폴더 이름적어줌
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap(":/UI_resource/documents-folder@32px.png"), QtGui.QIcon.Normal,
                               QtGui.QIcon.Off)
                row.setIcon(0, folder_icon)
                row_dict[folder[0]] = row  # row_dict에 자신의 폴더넘버로 row 추가item_0 = QtWidgets.QTreeWidgetItem(mainWindow.treeWidget)
                row_dict[folder[3]].addChild(row)  # 상위 row에 자신을 추가

    def showBookmark_UI(self):
        self.bookmark_treeWidget.clear()
        row_dict = {}
        bookmarks = main.db1.executeOneQueryMany("SELECT * FROM BOOKMARK")
        bookmark_icon = QtGui.QIcon()
        bookmark_icon.addPixmap(QtGui.QPixmap(":/UI_resource/bookmarks-bookmark@32px.png"), QtGui.QIcon.Normal,
                                QtGui.QIcon.Off)
        for bookmark in bookmarks:
            row = QTreeWidgetItem()  # 새 QTreeWidgetItem 생성
            row.setText(0, bookmark[1])  # 최상위폴더 이름적어줌
            row.setIcon(0, bookmark_icon)
            # row.setIcon(0, folder_icon)
            self.bookmark_treeWidget.addTopLevelItem(row)
#    def parseHFS_event(self):
    #def processEvents_thread(self, loadingLoop):
    #    while self.loading_flag == False :
    #        loadingLoop.processEvents()
    #        time.sleep(0.1)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    mainWindow.treeWidget.headerItem().setText(0, "Name")
    mainWindow.setDisabled(True)
    app.processEvents()
    #loading_QSplashScreen = MySplashScreen(":/UI_resource/loading.gif", QtCore.Qt.WindowStaysOnTopHint)
    #loading_QSplashScreen.show()

    #loadingLoop = QEventLoop()
    #pool = Pool(processes=1)
    #pool.apply_async(mainWindow.processEvents_thread, [loadingLoop], callback=lambda exitCode: loadingLoop.exit(exitCode))
    #loadingLoop.exec_()


    mainWindow.showDirectoryTree_UI()
    mainWindow.showBookmark_UI()
    #mainWindow.loading_flag = True

    mainWindow.setEnabled(True)
#    main.disk_num = int(main.db1.executeOneQuery("SELECT * FROM setup WHERE name = 'DISK_NUM'")[1])
#    main.block_size = int(main.db1.executeOneQuery("SELECT * FROM setup WHERE name = 'BLOCK_SIZE'")[1])
    #loading_QSplashScreen.close()
    app.exec_()

    # app = QtWidgets.QApplication(sys.argv)
    # Wizard = QtWidgets.QWizard()
    # ui = Ui_Wizard()
    # ui.setupUi(Wizard)
    # Wizard.show()
    # sys.exit(app.exec_())



