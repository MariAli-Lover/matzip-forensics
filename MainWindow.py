# -*- coding: <UTF-8> -*-
import sys
import datetime
import re
import math
import tempfile
from multiprocessing.pool import Pool
import binascii
from PyQt5.QtCore import QEventLoop, pyqtSlot, QThread,QObject, pyqtSignal
from PyQt5.QtGui import QPixmap, QMovie
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5 import QtGui, QtCore

from file_hash import *
from AddToBookmarkWindow import AddToBookmarkWindow_main
from AddToBookmarkWindow import AddToBookmarkWindow_new
from AddToBookmarkWindow import AddToBookmarkWindow_delete
from SearchWindow import SearchWindow
from ProgressWindow import ProgressWindow
from LogicalImagingWindow import LogicalImagingWindow
from hfs import *
from system_warning import *
from PyQt5.QtWidgets import QDialog
from image_file_reader import *
from file_signature import *

import textbox.textbox.docx as docx
import textbox.textbox.hwp as hwp
import textbox.textbox.pptx as pptx
import textbox.textbox.xlsx as xlsx
import alzfile.alzfile.__init__ as alz

from makedd import MakeDD

if main.os_mode == "WINDOWS" :
    form_class = uic.loadUiType(".\\UI\MainWindow.ui")[0]
elif main.os_mode == "MACOS" :
    form_class = uic.loadUiType("./UI/MainWindow.ui")[0]

ITEMVIEW_EVIDENCE_NUM = 0
ITEMVIEW_EVIDENCE_NAME = 1
ITEMVIEW_EVIDENCE_TYPE = 2
ITEMVIEW_EVIDENCE_PATH = 3
ITEMVIEW_EVIDENCE_SIZE = 4
ITEMVIEW_EVIDENCE_MODIFY_TIME = 5
ITEMVIEW_EVIDENCE_ACCESS_TIME = 6
ITEMVIEW_EVIDENCE_CREATE_TIME = 7
ITEMVIEW_EVIDENCE_MODIFY_ATTRIBUTE_TIME = 8
ITEMVIEW_EVIDENCE_BACKUP_TIME = 9

ITEMVIEW_FOLDER_NUM = 0
ITEMVIEW_FOLDER_NAME = 1
ITEMVIEW_FOLDER_PATH = 2
ITEMVIEW_FOLDER_MODIFY_TIME = 3
ITEMVIEW_FOLDER_ACCESS_TIME = 4
ITEMVIEW_FOLDER_CREATE_TIME = 5
ITEMVIEW_FOLDER_MODIFY_ATTRIBUTE_TIME = 6
ITEMVIEW_FOLDER_BACKUP_TIME = 7

PREVIEW_IMAGE = 0



TYPE_FOLDER = 0
TYPE_EVIDENCE = 1
TYPE_LINK = 2


#form_class = uic.loadUiType(".\\UI\MainWindow.ui")[0]
class FileSignatureSignalEmit(QObject) :
    update_progressbar_signal = pyqtSignal(int)
    update_finished_signal = pyqtSignal()
    def connectSignal(self):
        self.update_progressbar_signal.connect(mainWindow.update_progressbar_signature)
        self.update_finished_signal.connect(mainWindow.update_signature_db)
        print("connect signal")

    def emit_progressbar(self, num):
        self.update_progressbar_signal.emit(num)
        print("emit")
    def emit_finished(self):
        self.update_finished_signal.emit()
        print("emit finished")

class FileSignatureThread(QThread) :
    global result
    global mainWindow
    global update_progressbar_signal_class
    def __init__(self, mainWindow, result, parent = None):
        super().__init__(parent)
        self.result = result
        self.mainWindow = mainWindow
        self.update_progressbar_signal_class = FileSignatureSignalEmit()
        self.update_progressbar_signal_class.connectSignal()
    def __del__(self):
        self.wait()

    def run(self):


        query_list = []
        #self.result = self.result[350000:]
        len_result = len(self.result)
        for parsed_count, data in enumerate(self.result):
            if (data[2] > 30000000 or data[2] == 0):
                if parsed_count % 2500 == 0:
                    print("result : " + str(parsed_count * 100 / len_result))
                    self.update_progressbar_signal_class.emit_progressbar(int(parsed_count * 100 / len_result))
                continue
            mode = {"file_location": data[3]}
            try:
                etc_d = is_bad_signature(data[1], mode, data[2])
                if (etc_d == "1"):
                    query_list.append({"type": 7, "num": data[0]})  # bad signature
                elif (etc_d == "2"):
                    query_list.append({"type": 8, "num": data[0]})  # no extension
                elif (etc_d == "3"):
                    query_list.append({"type": 9, "num": data[0]})  # unknown extension
                else:
                    continue
            except:
                continue
            if parsed_count % 2500 == 0 :
                print("result : " + str(parsed_count * 100 / len_result))
                self.update_progressbar_signal_class.emit_progressbar(int(parsed_count * 100 / len_result))

        self.mainWindow.signature_query_list_tmp = query_list
        self.update_progressbar_signal_class.emit_finished()
        #self.mainWindow.tray_icon = QSystemTrayIcon(self.mainWindow)
        #self.mainWindow.tray_icon.setIcon(self.mainWindow.style().standardIcon(QStyle.SP_ComputerIcon))
        #self.mainWindow.tray_icon.showMessage("Matzip_Forensics", "Finished file signaturing", QSystemTrayIcon.Information,2000)
        return None



class MyPreviewWidget(QWidget) :
    global imageLabel
    def __init(self, type):
        if type == PREVIEW_IMAGE : #이미지이면
            print("z")



class MyItemViewWidget(QWidget) :
    global itemView
    global mainWindow
    global check_all
    global bookmark_num #북마크일시만 사용
    global status_path #아래 status창에 나오는 path
    global check_item_list
    global check_all_icon
    global uncheck_all_icon

    def __init__(self, mainWindow, tableWidget):
        super(QWidget, self).__init__()
        self.mainWindow = mainWindow
        self.setObjectName("tw_table")
        self.check_all = True # 전체체크, 전체체크해제 플래그
        self.bookmark_num = 0 # 0일시 북마크 없음
        self.check_item_list = []
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setContentsMargins(2, 2, 2, 2)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName("gridLayout")

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(4)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")

        font = QtGui.QFont()
        font.setFamily("맑은 고딕")
        font.setPointSize(7)
        font.setBold(True)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(75)
        font.setStrikeOut(False)

        self.check_all_button = QPushButton(self)
        self.check_all_button.setMaximumSize(QtCore.QSize(100, 20))
        self.check_all_button.setFont(font)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/UI_resource/uncheck_all.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.check_all_button.setIcon(icon5)
        self.check_all_button.setIconSize(QtCore.QSize(18, 18))
        self.check_all_button.setCheckable(False)
        self.check_all_button.setAutoDefault(False)
        self.check_all_button.setDefault(True)
        self.check_all_button.setFlat(True)
        self.check_all_button.setObjectName("check_all_button")
        self.check_all_button.clicked.connect(self.mainWindow.check_all_button_UI)
        self.check_all_button.setText("Check All")
        self.delete_button = QPushButton(self)
        self.delete_button.setMaximumSize(QtCore.QSize(80, 20))
        self.delete_button.setFont(font)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/UI_resource/controls-editor-trash.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.delete_button.setIcon(icon6)
        self.delete_button.setIconSize(QtCore.QSize(24, 24))
        self.delete_button.setCheckable(False)
        self.delete_button.setAutoDefault(False)
        self.delete_button.setDefault(True)
        self.delete_button.setFlat(True)
        self.delete_button.setObjectName("delete_button")
        self.delete_button.setText("Delete")
        self.delete_button.clicked.connect(self.mainWindow.delete_button_UI)

        self.add_to_bookmark_button = QPushButton(self)
        self.add_to_bookmark_button.setMaximumSize(QtCore.QSize(150, 20))
        self.add_to_bookmark_button.setFont(font)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(":/UI_resource/bookmarks-bookmark-add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.add_to_bookmark_button.setIcon(icon8)
        self.add_to_bookmark_button.setIconSize(QtCore.QSize(24, 24))
        self.add_to_bookmark_button.setCheckable(False)
        self.add_to_bookmark_button.setAutoDefault(False)
        self.add_to_bookmark_button.setDefault(True)
        self.add_to_bookmark_button.setFlat(True)
        self.add_to_bookmark_button.setObjectName("add_to_bookmark_button")
        self.add_to_bookmark_button.setText("Add To Bookmark")
        self.add_to_bookmark_button.clicked.connect(self.mainWindow.AddToBookmark_button_UI)

        spacerItem1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addWidget(self.check_all_button)
        self.horizontalLayout_2.addWidget(self.delete_button)
        self.horizontalLayout_2.addWidget(self.add_to_bookmark_button)
        self.horizontalLayout_2.addItem(spacerItem1)


        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 1, 2, 1)

        self.itemView = MyQTreeWidget(self)
        self.itemView.setLineWidth(0)
        self.itemView.setItemsExpandable(False)
        self.itemView.setAnimated(True)
        self.itemView.setObjectName("itemView")
        self.itemView.header().setCascadingSectionResizes(False)
        self.itemView.itemClicked['QTreeWidgetItem*','int'].connect(self.mainWindow.itemView_checked_UI)
        self.itemView.itemDoubleClicked['QTreeWidgetItem*','int'].connect(self.mainWindow.itemView_doubleClicked)
        #self.itemView.itemClicked['QTreeWidgetItem*','int'].connect(self.mainWindow.ls_transcript_UI)
        #self.itemView.itemClicked['QTreeWidgetItem*','int'].connect(self.mainWindow.ls_hex_UI)
        self.itemView.setSortingEnabled(True)
        self.itemView.headerItem().setText(0, "Name")
        self.itemView.headerItem().setText(1, "Extension")
        self.itemView.headerItem().setText(2, "Category")
        self.itemView.headerItem().setText(3, "Path")
        self.itemView.headerItem().setText(4,  "Size")
        self.itemView.headerItem().setText(5, "MODIFY_TIME")
        self.itemView.headerItem().setText(6, "ACCESS_TIME")
        self.itemView.headerItem().setText(7, "CREATE_TIME")
        self.itemView.headerItem().setText(8, "MODIFY_ATTRIBUTE_TIME")
        self.itemView.headerItem().setText(9,  "BACKUP_TIME")

        self.itemView.setUniformRowHeights(20) # 한 창에 20개만 뜨게

        self.gridLayout.addWidget(self.itemView, 3, 1, 1, 1)

class MyQTreeWidget(QTreeWidget) :
    def onContextMenu(self, event):
        """ ContextMenuPolicy --> DefaultContextMenu """

        print(event.pos())
        print(self.mapToGlobal(event.pos()))
        menu = QMenu(self)
        hex_view_action = menu.addAction("Hex View")
        transcript_view_action = menu.addAction("Transcript View")
        run_action = menu.addAction("Run")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == hex_view_action:
            mainWindow.ls_hex_UI()
        elif action == transcript_view_action:
            mainWindow.ls_transcript_UI(self)
        elif action == run_action:
            mainWindow.itemView_doubleClicked(self)

class MyQTreeWidgetItem(QTreeWidgetItem) :
    global num
    global name
    global path
    global parsed
    global type
    global isInExplorer
    global bookmark_num

    def __lt__(self, other):
        column = self.treeWidget().sortColumn()
        try :
            if self.type == other.type:
                return_value = self.name > other.name

            elif self.type > other.type : #왼쪽이 파일이고 오른쪽이 폴더일때
                return_value = True
            else :
                return_value = False
        except :
            key1 = self.text(column)
            key2 = other.text(column)
            return_value = key1 > key2
        return return_value



class MyQPushButton(QPushButton) :
    global num
    global name
    global path
    global checked

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

class MyHeader(QHeaderView) :
    global isOn
    def paintSection(self, painter, rect, logicalIndex) :
        painter.save()
        #self.paintSection()
        painter.restore()
        if logicalIndex == 0 :
            option = QStyleOptionButton
            option.rect = QRect(10, 10, 10, 10)
            if self.isOn :
                option.state = QSytle.State_On
            else :
                option.state = QStyle.State_Off
            self.style().drawPrimitive(QSytle.PE_IndicatorCheckBox, option, painter)
    def mousePressEvent(self, event):
        if self.isOn :
            self.isOn = false
        else :
            self.isOn = true
        self.update()

class  MySortFilterProxyModel(QtCore.QSortFilterProxyModel) :
    def lessThan(self, left, right):
        leftData = self.sourceModel().data(left)
        rightData = self.sourceModel().data(right)
        return_value = False
        # << 일시 True, 위
        if leftData.type < rightData.type : #왼쪽이 파일이고 오른쪽이 폴더일때
            return_value = True
        if leftData.type == rightData.type :
            return_value = leftData.name < rightData.type

        return return_value

class homeplate_folder_tree() :
    global folder_tree_list
    def __init__(self, folder_num):
        self.folder_tree_list = []
        main.homeplate_folder_list.append(folder_num) #homeplate_folder_list에 폴더넘버 넣어줌
        folders = main.db1.executeOneQueryMany("SELECT NUM FROM FOLDER WHERE UPPER_NUM = " + str(folder_num))
        for folder in folders :
            tmp_folder = homeplate_folder_tree(folder[0]) #폴더넘버로 또 하위 폴더넘버 재귀적으로 파싱

class MainWindow(QMainWindow, form_class):
    global context_menu
    global context_menu_action_hex_view
    global context_menu_action_transcript_view
    global context_menu_action_run
    global context_menu_action_image
    global selected_phydrive_num
    global path
    global num
    global check_item_list
    global loading_flag
    global row_dict
    global row_widget_dict

    global signature_query_list_tmp

    global itemViewModel #Sort
    global itemViewProxyModel

    global itemView_currentNum

    global hex_data_iter
    global hex_data
    global hex_data_read_block_count
    global hex_data_total_block_count
    global hex_data_added_byte

    global statusbar_progressbar

    global homeplate_icon_on
    global homeplate_icon_off
    global folder_icon
    global file_icon
    global search_icon
    global check_all_icon
    global uncheck_all_icon
    global link_icon
    global bookmark_icon
    
    global check_all_main # 전체체크, 체크해제 플래그 메인탭전용

    global box_green_icon
    global box_apricot_icon
    global box_black_icon
    global box_blue_icon
    global box_brown_icon
    global box_gray_icon
    global box_green_icon
    global box_orange_icon
    global box_pink_icon
    global box_red_icon

    global _3ds_icon
    global ai_icon
    global avi_icon
    global bmp_icon
    global cad_icon
    global cdr_icon
    global css_icon
    global dat_icon
    global dll_icon
    global dmg_icon
    global doc_icon
    global eps_icon
    global fla_icon
    global flv_icon
    global gif_icon
    global html_icon
    global indd_icon
    global iso_icon
    global jpg_icon
    global js_icon
    global midi_icon
    global mov_icon
    global mp3_icon
    global mpg_icon
    global pdf_icon
    global php_icon
    global png_icon
    global ppt_icon
    global ps_icon
    global psd_icon
    global raw_icon
    global sql_icon
    global svg_icon
    global tif_icon
    global txt_icon
    global wmv_icon
    global xls_icon
    global xml_icon
    global zip_icon
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.addContextMenu()
        self.itemView.setSortingEnabled(True)
        self.itemView.customContextMenuRequested.connect(self.showContextMenu)
        self.itemViewModel = self.itemView.model()
        self.itemViewProxyModel = MySortFilterProxyModel()
        self.itemViewProxyModel.setSourceModel(self.itemView.model())
        self.itemView.header().setSectionsClickable(True)
        self.itemView.header().setSortIndicatorShown(True)
        self.check_all_main = True
        self.itemView.header().sectionClicked.connect(self.itemViewHeaderClicked)

        #self.itemView.setModel(self.itemViewProxyModel)

        self.homeplate_icon_on = QtGui.QIcon()
        self.homeplate_icon_on.addPixmap(QtGui.QPixmap(":/UI_resource/homeplate_on.png"), QtGui.QIcon.Normal)
        self.homeplate_icon_off = QtGui.QIcon()
        self.homeplate_icon_off.addPixmap(QtGui.QPixmap(":/UI_resource/homeplate_off.png"), QtGui.QIcon.Normal)
        self.folder_icon = QtGui.QIcon()
        self.folder_icon.addPixmap(QtGui.QPixmap(":/UI_resource/documents-folder@32px.png"), QtGui.QIcon.Normal,
                              QtGui.QIcon.Off)
        self.file_icon = QtGui.QIcon()
        self.file_icon.addPixmap(QtGui.QPixmap(":/UI_resource/documents-document-blank@32px.png"), QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)

        self.search_icon = QtGui.QIcon()
        self.search_icon.addPixmap(QtGui.QPixmap(":/UI_resource/controls-editor-search@32px.png"), QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)

        self.check_all_icon = QtGui.QIcon()
        self.check_all_icon.addPixmap(QtGui.QPixmap(":/UI_resource/check_all.png"), QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)
        self.uncheck_all_icon = QtGui.QIcon()
        self.uncheck_all_icon.addPixmap(QtGui.QPixmap(":/UI_resource/uncheck_all.png"), QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)

        self.bookmark_icon = QtGui.QIcon()
        self.bookmark_icon.addPixmap(QtGui.QPixmap(":/UI_resource/bookmarks-bookmark@32px.png"), QtGui.QIcon.Normal,
                                QtGui.QIcon.Off)

        self.link_icon = QtGui.QIcon()
        self.link_icon.addPixmap(QtGui.QPixmap(":/UI_resource/controls-editor-link@32px.png"), QtGui.QIcon.Normal,
                                        QtGui.QIcon.Off)

        self.box_apricot_icon = QtGui.QIcon()
        self.box_apricot_icon.addPixmap(QtGui.QPixmap(":/box/box_apricot.png"), QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)
        self.box_black_icon = QtGui.QIcon()
        self.box_black_icon.addPixmap(QtGui.QPixmap(":/box/box_black.png"), QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)
        self.box_blue_icon = QtGui.QIcon()
        self.box_blue_icon.addPixmap(QtGui.QPixmap(":/box/box_blue.png"), QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)
        self.box_brown_icon = QtGui.QIcon()
        self.box_brown_icon.addPixmap(QtGui.QPixmap(":/box/box_brown.png"), QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)
        self.box_gray_icon = QtGui.QIcon()
        self.box_gray_icon.addPixmap(QtGui.QPixmap(":/box/box_gray.png"), QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)
        self.box_green_icon = QtGui.QIcon()
        self.box_green_icon.addPixmap(QtGui.QPixmap(":/box/box_green.png"), QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)
        self.box_orange_icon = QtGui.QIcon()
        self.box_orange_icon.addPixmap(QtGui.QPixmap(":/box/box_orange.png"), QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)
        self.box_pink_icon = QtGui.QIcon()
        self.box_pink_icon.addPixmap(QtGui.QPixmap(":/box/box_pink.png"), QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)
        self.box_red_icon = QtGui.QIcon()
        self.box_red_icon.addPixmap(QtGui.QPixmap(":/box/box_red.png"), QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)

        self._3ds_icon = QtGui.QIcon()
        self._3ds_icon.addPixmap(QtGui.QPixmap(":/file_icon/3ds.png"), QtGui.QIcon.Normal)
        self.ai_icon = QtGui.QIcon()
        self.ai_icon.addPixmap(QtGui.QPixmap(":/file_icon/ai.png"), QtGui.QIcon.Normal)
        self.avi_icon = QtGui.QIcon()
        self.avi_icon.addPixmap(QtGui.QPixmap(":/file_icon/avi.png"), QtGui.QIcon.Normal)
        self.bmp_icon = QtGui.QIcon()
        self.bmp_icon.addPixmap(QtGui.QPixmap(":/file_icon/bmp.png"), QtGui.QIcon.Normal)
        self.cad_icon = QtGui.QIcon()
        self.cad_icon.addPixmap(QtGui.QPixmap(":/file_icon/cad.png"), QtGui.QIcon.Normal)
        self.cdr_icon = QtGui.QIcon()
        self.cdr_icon.addPixmap(QtGui.QPixmap(":/file_icon/cdr.png"), QtGui.QIcon.Normal)
        self.css_icon = QtGui.QIcon()
        self.css_icon.addPixmap(QtGui.QPixmap(":/file_icon/css.png"), QtGui.QIcon.Normal)
        self.dat_icon = QtGui.QIcon()
        self.dat_icon.addPixmap(QtGui.QPixmap(":/file_icon/dat.png"), QtGui.QIcon.Normal)
        self.dll_icon = QtGui.QIcon()
        self.dll_icon.addPixmap(QtGui.QPixmap(":/file_icon/dll.png"), QtGui.QIcon.Normal)
        self.dmg_icon = QtGui.QIcon()
        self.dmg_icon.addPixmap(QtGui.QPixmap(":/file_icon/dmg.png"), QtGui.QIcon.Normal)
        self.doc_icon = QtGui.QIcon()
        self.doc_icon.addPixmap(QtGui.QPixmap(":/file_icon/doc.png"), QtGui.QIcon.Normal)
        self.eps_icon = QtGui.QIcon()
        self.eps_icon.addPixmap(QtGui.QPixmap(":/file_icon/eps.png"), QtGui.QIcon.Normal)
        self.fla_icon = QtGui.QIcon()
        self.fla_icon.addPixmap(QtGui.QPixmap(":/file_icon/fla.png"), QtGui.QIcon.Normal)
        self.flv_icon = QtGui.QIcon()
        self.flv_icon.addPixmap(QtGui.QPixmap(":/file_icon/flv.png"), QtGui.QIcon.Normal)
        self.gif_icon = QtGui.QIcon()
        self.gif_icon.addPixmap(QtGui.QPixmap(":/file_icon/gif.png"), QtGui.QIcon.Normal)
        self.html_icon = QtGui.QIcon()
        self.html_icon.addPixmap(QtGui.QPixmap(":/file_icon/html.png"), QtGui.QIcon.Normal)
        self.indd_icon = QtGui.QIcon()
        self.indd_icon.addPixmap(QtGui.QPixmap(":/file_icon/indd.png"), QtGui.QIcon.Normal)
        self.iso_icon = QtGui.QIcon()
        self.iso_icon.addPixmap(QtGui.QPixmap(":/file_icon/iso.png"), QtGui.QIcon.Normal)
        self.jpg_icon = QtGui.QIcon()
        self.jpg_icon.addPixmap(QtGui.QPixmap(":/file_icon/jpg.png"), QtGui.QIcon.Normal)
        self.js_icon = QtGui.QIcon()
        self.js_icon.addPixmap(QtGui.QPixmap(":/file_icon/js.png"), QtGui.QIcon.Normal)
        self.midi_icon = QtGui.QIcon()
        self.midi_icon.addPixmap(QtGui.QPixmap(":/file_icon/midi.png"), QtGui.QIcon.Normal)
        self.mov_icon = QtGui.QIcon()
        self.mov_icon.addPixmap(QtGui.QPixmap(":/file_icon/mov.png"), QtGui.QIcon.Normal)
        self.mp3_icon = QtGui.QIcon()
        self.mp3_icon.addPixmap(QtGui.QPixmap(":/file_icon/mp3.png"), QtGui.QIcon.Normal)
        self.mpg_icon = QtGui.QIcon()
        self.mpg_icon.addPixmap(QtGui.QPixmap(":/file_icon/mpg.png"), QtGui.QIcon.Normal)
        self.pdf_icon = QtGui.QIcon()
        self.pdf_icon.addPixmap(QtGui.QPixmap(":/file_icon/pdf.png"), QtGui.QIcon.Normal)
        self.php_icon = QtGui.QIcon()
        self.php_icon.addPixmap(QtGui.QPixmap(":/file_icon/php.png"), QtGui.QIcon.Normal)
        self.png_icon = QtGui.QIcon()
        self.png_icon.addPixmap(QtGui.QPixmap(":/file_icon/png.png"), QtGui.QIcon.Normal)
        self.ppt_icon = QtGui.QIcon()
        self.ppt_icon.addPixmap(QtGui.QPixmap(":/file_icon/ppt.png"), QtGui.QIcon.Normal)
        self.ps_icon = QtGui.QIcon()
        self.ps_icon.addPixmap(QtGui.QPixmap(":/file_icon/ps.png"), QtGui.QIcon.Normal)
        self.psd_icon = QtGui.QIcon()
        self.psd_icon.addPixmap(QtGui.QPixmap(":/file_icon/psd.png"), QtGui.QIcon.Normal)
        self.raw_icon = QtGui.QIcon()
        self.raw_icon.addPixmap(QtGui.QPixmap(":/file_icon/raw.png"), QtGui.QIcon.Normal)
        self.sql_icon = QtGui.QIcon()
        self.sql_icon.addPixmap(QtGui.QPixmap(":/file_icon/sql.png"), QtGui.QIcon.Normal)
        self.svg_icon = QtGui.QIcon()
        self.svg_icon.addPixmap(QtGui.QPixmap(":/file_icon/svg.png"), QtGui.QIcon.Normal)
        self.tif_icon = QtGui.QIcon()
        self.tif_icon.addPixmap(QtGui.QPixmap(":/file_icon/tif.png"), QtGui.QIcon.Normal)
        self.txt_icon = QtGui.QIcon()
        self.txt_icon.addPixmap(QtGui.QPixmap(":/file_icon/txt.png"), QtGui.QIcon.Normal)
        self.wmv_icon = QtGui.QIcon()
        self.wmv_icon.addPixmap(QtGui.QPixmap(":/file_icon/wmv.png"), QtGui.QIcon.Normal)
        self.xls_icon = QtGui.QIcon()
        self.xls_icon.addPixmap(QtGui.QPixmap(":/file_icon/xls.png"), QtGui.QIcon.Normal)
        self.xml_icon = QtGui.QIcon()
        self.xml_icon.addPixmap(QtGui.QPixmap(":/file_icon/xml.png"), QtGui.QIcon.Normal)
        self.zip_icon = QtGui.QIcon()
        self.zip_icon.addPixmap(QtGui.QPixmap(":/file_icon/zip.png"), QtGui.QIcon.Normal)


        self.statusbar_progressBar = QProgressBar(self)
        self.statusbar_progressBar.setMaximumSize(QtCore.QSize(200, 20))
        self.statusbar_progressBar.setValue(0)
        spacerItem1 = QSpacerItem(10000, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
#        self.statusbar.addWidget(spacerItem1)
        self.statusbar.addWidget(self.statusbar_progressBar)

        self.check_item_list = []
        self.itemView.headerItem().setCheckState(0, QtCore.Qt.Unchecked)
        self.loading_flag = False
    def addContextMenu(self):
        self.context_menu = QMenu(self)
        self.context_menu_action_hex_view = self.context_menu.addAction("Hex View")
        self.context_menu_action_transcript_view = self.context_menu.addAction("Transcript View")
        self.context_menu_action_run = self.context_menu.addAction("Run")
        self.context_menu_action_image = self.context_menu.addAction("image view")
    def showContextMenu(self, pos):
        action = self.context_menu.exec_(self.itemView.viewport().mapToGlobal(pos))
        if action == self.context_menu_action_hex_view:
            self.ls_hex_UI()
        elif action == self.context_menu_action_transcript_view:
            self.ls_transcript_UI(self.itemView.itemAt(pos), 0)
        elif action == self.context_menu_action_run:
            self.itemView_doubleClicked(self.itemView.itemAt(pos), 0)
        elif action == self.context_menu_action_image:
            self.ls_image_UI()

    def ls_hex_UI(self):
        self.current = self.itemView.currentItem()
        self.tabWidget_4.setCurrentIndex(0)
        self.hex_data_read_block_count = 0
        self.hex_data_iter = ""
        self.hex_data = open("temp", "ab")
        if (self.current == -1 or self.current.type == TYPE_FOLDER):
            return
        else:
            #try:
                print("done? ls_hex_UI")
                location = main.db1.executeOneQuery("SELECT DATA_LOCATION FROM EVIDENCES WHERE NUM = " + str(self.current.num))[0]
                self.hex_data_iter = HFSP(main.disk_num).parsingdata22(location)
                self.hex_data_total_block_count = next(self.hex_data_iter)
                #print("done ls_hex_UI" , iter_num)
                self.ls_hex_add_data(1)
                self.ls_hex_show_data(0)

            #except:
                # when you tried to add row and give new element you'll get error
            #    print("error")
            #    return
            #finally:
                print("hex UI is done")
                return None

    def ls_key_UI(self):
        print("1")
        self.clearItemView() #ItemView 다 초기화
        para = self.keyfile_treeWidget.currentItem().text(0)
        result = None
        if(para == "Document Files"):
            print("1")
            document_sql = "SELECT NUM, NAME, TYPE, PATH, SIZE, MODIFY_TIME, ACCESS_TIME, CREATE_TIME, MODIFY_ATTRIBUTE_TIME, BACKUP_TIME FROM evidences WHERE TYPE = 1"
            result = main.db1.cur.execute(document_sql)
        if (para == "Compressed Files"):
            document_sql = "SELECT NUM, NAME, TYPE, PATH, SIZE, MODIFY_TIME, ACCESS_TIME, CREATE_TIME, MODIFY_ATTRIBUTE_TIME, BACKUP_TIME FROM evidences WHERE TYPE = 2"
            result = main.db1.cur.execute(document_sql)
        if (para == "Graphic Files"):
            document_sql = "SELECT NUM, NAME, TYPE, PATH, SIZE, MODIFY_TIME, ACCESS_TIME, CREATE_TIME, MODIFY_ATTRIBUTE_TIME, BACKUP_TIME FROM evidences WHERE TYPE = 3"
            result = main.db1.cur.execute(document_sql)
        if (para == "Multimedia Files"):
            document_sql = "SELECT NUM, NAME, TYPE, PATH, SIZE, MODIFY_TIME, ACCESS_TIME, CREATE_TIME, MODIFY_ATTRIBUTE_TIME, BACKUP_TIME FROM evidences WHERE TYPE = 4"
            result = main.db1.cur.execute(document_sql)

        if (para == "System Log Files"):
            document_sql = "SELECT NUM, NAME, TYPE, PATH, SIZE, MODIFY_TIME, ACCESS_TIME, CREATE_TIME, MODIFY_ATTRIBUTE_TIME, BACKUP_TIME FROM evidences WHERE TYPE = 5"
            result = main.db1.cur.execute(document_sql)
        if (para == "Web Browser Log Files"):
            document_sql = "SELECT NUM, NAME, TYPE, PATH, SIZE, MODIFY_TIME, ACCESS_TIME, CREATE_TIME, MODIFY_ATTRIBUTE_TIME, BACKUP_TIME FROM evidences WHERE TYPE = 6"
            result = main.db1.cur.execute(document_sql)

        if (para == "Unknown Extension Files"):
            document_sql = "SELECT NUM, NAME, TYPE, PATH, SIZE, MODIFY_TIME, ACCESS_TIME, CREATE_TIME, MODIFY_ATTRIBUTE_TIME, BACKUP_TIME FROM evidences WHERE TYPE = 9"
            result = main.db1.cur.execute(document_sql)
        if (para == "Bad Signature Files"):
            document_sql = "SELECT NUM, NAME, TYPE, PATH, SIZE, MODIFY_TIME, ACCESS_TIME, CREATE_TIME, MODIFY_ATTRIBUTE_TIME, BACKUP_TIME FROM evidences WHERE TYPE = 7"
            result = main.db1.cur.execute(document_sql)
        if (para == "No Extension Files"):
            document_sql = "SELECT NUM, NAME, TYPE, PATH, SIZE, MODIFY_TIME, ACCESS_TIME, CREATE_TIME, MODIFY_ATTRIBUTE_TIME, BACKUP_TIME FROM evidences WHERE TYPE = 8"
            result = main.db1.cur.execute(document_sql)
        self.addItemViewEvidence(result.fetchall(), self.itemView) #itemView에 result 추가
        self.tabWidget_2.setCurrentIndex(0)
        self.update_status_label()
        print("1")

    def ls_image_UI(self):
        self.current = self.itemView.currentItem()
        self.tabWidget_4.setCurrentIndex(5)
        self.image_label.clear()
        print("current : " , self.current)
        if (self.current == -1):
            return
        else:
            try:
                sql = "select NAME , SIZE, DATA_LOCATION from evidences where num = " + str(self.current.num)
                result11 = main.db1.executeOneQuery(sql)
                self.name = result11[0]
                extension = os.path.splitext(self.name)[1].replace(".", "")
                if not extension in ("jpg", "jpeg", "png", "ico", "gif", "jpg", "jfif"):
                    print("this is not image file!!!!")
                    return
                self.size = result11[1]
                self.file_location = result11[2]

                file_name = "temporary" + self.name  # delete all temporary image file when _app.exit()
                if (not (os.path.exists("./" + file_name))):
                    HFSP(1).parsingData(self.file_location, file_name, self.size)
                pixmap = QPixmap("./"+file_name)
                self.image_label.setPixmap(pixmap)
                self.image_label.resize(pixmap.width(), pixmap.height())
            finally:
                print("what ever done!")

    def ls_homeplate_UI(self, button):
        del main.homeplate_folder_list[:] #homeplate_folder_list 초기화
        self.clearItemView()
        self.itemView.blockSignals(True);
        self.itemView.setUpdatesEnabled(False)
        #한 폴더 파싱, 그 하위
        folder_num = main.db1.executeOneQuery("SELECT NUM FROM FOLDER WHERE PATH is '" + button.path + "' AND NAME is '" + button.name + "'")[0]
        if folder_num != 2 : #root가 아니면
            main.homeplate_folder_list = main.db1.executeOneQueryMany("SELECT LOWER_FOLDER_NUM FROM HOMEPLATE_FOLDER WHERE FOLDER_NUM =" + str(button.num))
            print("홈플레이트 폴더 파싱 끝")
            self.check_item_list.clear()  # 체크리스트 초기화
            len_homeplate_folder_list = len(main.homeplate_folder_list)
            if len_homeplate_folder_list > 0 : #홈플레이트해서 파일 1개이상 있으면
                read_once_size = 1000 #최대 1000개
                if len_homeplate_folder_list < read_once_size : # 999개 이하있으면
                    row_evidences = main.db1.getItemList_homeplate(main.homeplate_folder_list)
                    self.addItemViewEvidence(row_evidences, self.itemView)
                else : #1000개 이상있으면
                    count = math.ceil(float(len_homeplate_folder_list) / read_once_size)  # 만약 1001개 -> 2
                    for i in range(count):
                        main.printDebugMessage("i : " + str(i) + " count : " + str(count))
                        homeplate_folder_list_tmp = main.homeplate_folder_list[i * read_once_size: (i + 1) * read_once_size - 1]  # 앞에꺼 넣어주고 뺌
                        row_evidences = main.db1.getItemList_homeplate(homeplate_folder_list_tmp)
                        self.addItemViewEvidence(row_evidences, self.itemView)
                        main.printDebugMessage("한 사이클 추가 완료")
        else : #root면
            main.printDebugMessage("homplate_root : row_evidences")
            row_evidences = main.db1.getItemList_homeplate_root()
            main.printDebugMessage("homeplate_root : addItemViewEvidence")
            self.itemView.setSortingEnabled(False)
            self.addItemViewEvidence(row_evidences, self.itemView)
        self.itemView.blockSignals(False);

        self.itemView.setUpdatesEnabled(True)

        main.status_path = button.path + button.name + "/(HOMEPLATE)"
        self.update_status_label() #아래 status 업데이트

    def ls_UI1(self, QModelIndex): #UI 시그널/슬롯 때문에 이렇게따로해줌
        main.printDebugMessage("ls_UI1")
        currentItem = self.treeWidget.currentItem()

        if currentItem.type == TYPE_LINK :
            if self.row_dict[2].isExpanded() == False :
                self.row_dict[2].setExpanded(True)
            self.itemView_doubleClicked(currentItem, 0)

        else :
            currentItem = self.treeWidget.currentItem()
            num = currentItem.num
            self.tabWidget_2.setCurrentIndex(0)
            self.ls_UI(QModelIndex, num)
            main.button_folder_num_list = main.button_folder_num_list[:main.button_folder_num_list_location + 1]
            main.button_folder_num_list.append(num) #다음을 현재위치로
            main.button_folder_num_list.append(0) #그다음은 없다
            main.button_folder_num_list_location += 1
            main.next_folder_num = main.button_folder_num_list[main.button_folder_num_list_location + 1]
            main.current_folder_num = main.button_folder_num_list[main.button_folder_num_list_location]
            main.previous_folder_num = main.button_folder_num_list[main.button_folder_num_list_location -1]
            self.folder_button_status_refresh()
        
    def ls_UI(self, QModelIndex, num, signal = ""):
        #self.itemView.clear()
        self.num = num
        row = main.db1.executeOneQuery("SELECT NAME, PATH, UPPER_NUM, FOLDER_COUNT FROM FOLDER WHERE NUM = " + str(num))
        name = row[0]
        path = row[1]
        folder_count = row[3]
        self.clearItemView()
        self.check_item_list.clear() # 체크리스트 초기화

        row_evidences, row_folders = main.db1.getItemList(num)

        self.addItemViewFolder(row_folders, self.itemView)
        self.addItemViewEvidence(row_evidences, self.itemView) #itemView에 evidences들 추가
        main.status_path =  path + name
        main.upper_folder_num = row[2] # 상위폴더위치 저장
        self.update_status_label()



    def ls_bookmark_UI(self):
        #self.itemView.clear()
        currentItem = self.bookmark_treeWidget.currentItem()
        already_exist = False
        already_location = 0  # 이미 창 열려있을시 그 창으로 탭 이동시켜주기 위해
        for i in range(self.tabWidget_2.count() - 1) : #이미 창이 켜져있는지 검사
            #첫번째는 main이니까 거름
            tmp = self.tabWidget_2.widget(i + 1)                 #main.tabWidget_2_bookmark_dict 구조 : key = 북마크넘버  value = tabWidget 인덱스
            if tmp.bookmark_num == currentItem.bookmark_num : #이미 창이 켜져있다면
                already_exist = True
                already_location = i + 1                   #그 index로 탭 이동시켜주기 위해
                
        if already_exist == True : #이미 열려있으면
            self.tabWidget_2.setCurrentIndex(already_location)
        else : #안열려 있으면
            widget = MyItemViewWidget(self, self.tabWidget_2)  # 새로운 탭 추가
            #row_evidences, row_folder = main.db1.getItemList_search(keyword)
            widget.bookmark_num = currentItem.num # 중복방지
            widget.status_path = "(BOOKMARK) " + currentItem.name
            self.tabWidget_2.addTab(widget, self.bookmark_icon, "북마크 : " + currentItem.name)
            self.tabWidget_2.setCurrentIndex(self.tabWidget_2.count() - 1)  # 제일 뒤의 탭으로 포커싱
            main.printDebugMessage("tab index : " + str(self.tabWidget_2.count()))

            widget.check_item_list.clear() # 체크리스트 초기화

            #선택한 북마크의 번호를 찾음
            bookmark_location = currentItem.num
            bookmark_evidence_list = main.db1.executeOneQueryMany("SELECT * FROM BOOKMARK_EVIDENCES WHERE BOOKMARK_NUM = " + str(bookmark_location))
            len_bookmark_evidence_list = len(bookmark_evidence_list)
            main.printDebugMessage("getItemList_bookmark")

            if len_bookmark_evidence_list > 0:  # 북마크 파일 1개이상 있으면
                read_once_size = 1000  # 최대 1000개
                if len_bookmark_evidence_list < read_once_size:  # 999개 이하있으면
                    row_evidences = main.db1.getItemList_bookmark(bookmark_evidence_list)
                    self.addItemViewEvidence(row_evidences, self.tabWidget_2.currentWidget().itemView)
                else:  # 1000개 이상있으면
                    count = math.ceil(float(len_bookmark_evidence_list) / read_once_size)  # 만약 1001개 -> 2
                    for i in range(count):
                        main.printDebugMessage("i : " + str(i) + " count : " + str(count))
                        bookmark_evidence_list_tmp = bookmark_evidence_list[
                                                    i * read_once_size: (i + 1) * read_once_size - 1]  # 앞에꺼 넣어주고 뺌
                        row_evidences = main.db1.getItemList_bookmark(bookmark_evidence_list_tmp)
                        self.addItemViewEvidence(row_evidences, self.tabWidget_2.currentWidget().itemView)
                        main.printDebugMessage("한 사이클 추가 완료")
        self.update_status_label()


    def ls_search_UI(self, keyword):
        widget = MyItemViewWidget(self, self.tabWidget_2) #새로운 탭 추가
        widget.status_path = "(SEARCH) " + keyword
        row_evidences, row_folder = main.db1.getItemList_search(keyword)
        self.addItemViewEvidence(row_evidences, widget.itemView)
        self.addItemViewFolder(row_folder, widget.itemView)
        self.tabWidget_2.addTab(widget, self.search_icon, "검색 : " + keyword)
        self.tabWidget_2.setCurrentIndex(self.tabWidget_2.count() -1) #제일 뒤의 탭으로 포커싱
        main.printDebugMessage("tab index : " + str(self.tabWidget_2.count()))


    def ls_transcript_UI(self, QTreeWidgetItem, int):
        self.textBrowser_2.setText("None")
        self.tabWidget_4.setCurrentIndex(2)
        self.current = QTreeWidgetItem.num

        if (self.current == -1):
            return
        else:
            try:
                print(str(self.current))
                sql = "select SIZE, DATA_LOCATION from evidences where num = " + str(self.current)
                print("1")
                result11 = main.db1.executeOneQuery(sql)
                print("1")
                self.tuple_store = QTreeWidgetItem.name
                print("1")
                print(self.tuple_store)
                extension = os.path.splitext(self.tuple_store)[1].replace(".", "")
                self.size = result11[0]
                self.file_location = result11[1]
                if(extension == "docx"):
                    print(str(main.disk_num))
                    self.textBrowser_2.setText(docx.DOCXExtractor(HFSP(main.disk_num).binarytofile_maker(self.file_location , self.size)).get_text())
                if(extension == "hwp"):
                    self.textBrowser_2.setText(hwp.HWPExtractor(HFSP(main.disk_num).binarytofile_maker(self.file_location , self.size)).get_text())
                if(extension == "pptx"):
                    self.textBrowser_2.setText(pptx.PPTXExtractor(HFSP(main.disk_num).binarytofile_maker(self.file_location , self.size)).get_text())
                if(extension == "xlsx"):
                    self.textBrowser_2.setText(xlsx.XLSXExtractor(HFSP(main.disk_num).binarytofile_maker(self.file_location , self.size)).get_text())
                if (extension == "alz"):
                    ALZIP = alz.AlzFile(HFSP(1).binarytofile_maker(self.file_location, self.size))
                    dir = ALZIP.dirs()
                    for d in dir:
                        self.textBrowser_2.setText(d["name"].decode("cp949", 'ignore'), d["compress_method"],
                                                   d["compressed_size"], d["size"], d["crc"], d["data_pos"],
                                                   d["next_pos"])
            except:
                print("error")
                # when you tried to add row and give new element you'll get error
                return
    def itemView_checked_UI(self, QTreeWidgetItem): # 북마크하려고 체크할때 어떤거 체크했는지 parsing
        if self.tabWidget_2.currentIndex() == 0 : #현재 보고있는탭이 메인이면
            if QTreeWidgetItem.checkState(0) == 2 : #체크가 되면
                check_item_flag = False #체크리스트에 파일 있는지여부

                for check_item_tmp in self.check_item_list : # 이미 체크리스트에 파일 있는지 확인
                    if check_item_tmp == QTreeWidgetItem.num :
                        check_item_flag = True #있으면 False
                        break

                if check_item_flag == False : # 체크리스트에 파일이 없으면
                    self.check_item_list.append(QTreeWidgetItem.num) # 체크리스트에 파일명 추가

            else : #체크가 풀리면
                check_item_flag = False #체크리스트에 파일 있는지여부
                for check_item_tmp in self.check_item_list : # 이미 체크리스트에 파일 있는지 확인
                    if check_item_tmp == QTreeWidgetItem.num :
                        print("true")
                        check_item_flag = True #있으면 False
                        break
                if check_item_flag == True : # 체크리스트에 파일이 있으면
                    self.check_item_list.remove(QTreeWidgetItem.num) #체크 풀린거 삭제
        else : #현재 보고있는탭이 메인이아니면
            currentItem = self.tabWidget_2.currentWidget()
            if QTreeWidgetItem.checkState(0) == 2:  # 체크가 되면
                check_item_flag = False  # 체크리스트에 파일 있는지여부

                for check_item_tmp in currentItem.check_item_list:  # 이미 체크리스트에 파일 있는지 확인
                    if check_item_tmp == QTreeWidgetItem.num:
                        check_item_flag = True  # 있으면 False
                        break

                if check_item_flag == False:  # 체크리스트에 파일이 없으면
                    currentItem.check_item_list.append(QTreeWidgetItem.num)  # 체크리스트에 파일명 추가

            else:  # 체크가 풀리면
                check_item_flag = False  # 체크리스트에 파일 있는지여부
                for check_item_tmp in currentItem.check_item_list:  # 이미 체크리스트에 파일 있는지 확인
                    if check_item_tmp == QTreeWidgetItem.num:
                        print("true")
                        check_item_flag = True  # 있으면 False
                        break
                if check_item_flag == True:  # 체크리스트에 파일이 있으면
                    currentItem.check_item_list.remove(QTreeWidgetItem.num)  # 체크 풀린거 삭제

        self.update_status_label()

    def itemView_doubleClicked(self, QTreeWidgetItem, int):

            currentItem = QTreeWidgetItem
            if currentItem.type == TYPE_FOLDER or currentItem.type == TYPE_LINK: #더블클릭한게 폴더나 링크면
                new_parse = False
                self.tabWidget_3.setCurrentIndex(0)
                self.tabWidget_2.setCurrentIndex(0)

                if currentItem.num not in self.row_dict.keys(): #row_dict에 없으면
                    new_parse = True
                elif self.row_dict[currentItem.num].num == True: #왼쪽 Explorer가 이 폴더까지 Expanded되어있으면:
                    new_parse = False
                else : #Expanded 안되어있으면
                    new_parse = True
                
                if new_parse == False :
                    self.treeWidget.expandItem(self.row_dict[self.num])
                    self.treeWidget.setCurrentItem(self.row_dict[currentItem.num])
                    self.ls_UI(None, currentItem.num)
                else : 
                    self.ls_UI(None, currentItem.num)
                    tmp_row = main.db1.executeOneQuery("SELECT UPPER_NUM FROM folder WHERE NUM =" + str(currentItem.num))[0]
                    tmp_row_list = []
                    main.printDebugMessage(
                        "tmp_row : " + str(tmp_row) + " is in ? : " + str(tmp_row in self.row_dict.keys()))

                    while tmp_row not in self.row_dict.keys() : #Expanded 되있는데까지 탐색
                        main.printDebugMessage(
                            "tmp_row : " + str(tmp_row) + " is in ? : " + str(tmp_row in self.row_dict.keys()))

                        tmp_row_list.append(tmp_row) #탐색하면서 계속 목록에 추가
                        tmp_row = main.db1.executeOneQuery("SELECT UPPER_NUM FROM folder WHERE NUM =" + str(tmp_row))[0]
                    tmp_row_list.append(tmp_row)  # 탐색하면서 계속 목록에 추가

                    #tmp_row = main.db1.executeOneQuery("SELECT UPPER_NUM FROM folder WHERE NUM =" + str(tmp_row))[0]
                    if tmp_row != 1 :
                        tmp_row_list.append(tmp_row)  # 탐색하면서 계속 목록에 추가
                    tmp_row_list.reverse() #뒤부터 추가해야함
                    for tmp_add_row in tmp_row_list :
                        if self.row_dict[tmp_add_row].parsed == False :
                            self.showDirectoryTree_UI(tmp_add_row)
                            self.row_dict[tmp_add_row].parsed = True
                            self.treeWidget.expandItem(self.row_dict[tmp_add_row])
                            self.treeWidget.setCurrentItem(self.row_dict[tmp_add_row])
                            QApplication.processEvents()
                self.treeWidget.setCurrentItem(self.row_dict[currentItem.num])


                main.button_folder_num_list = main.button_folder_num_list[:main.button_folder_num_list_location + 1]
                main.button_folder_num_list.append(currentItem.num) #다음을 현재위치
                main.button_folder_num_list.append(0) #그다음은 없다
                main.button_folder_num_list_location += 1
                main.next_folder_num = main.button_folder_num_list[main.button_folder_num_list_location + 1]
                main.current_folder_num = main.button_folder_num_list[main.button_folder_num_list_location]
                main.previous_folder_num = main.button_folder_num_list[main.button_folder_num_list_location -1]
                self.folder_button_status_refresh()
            else : #더블클릭한게 파일이면
                try:
                    file_data = main.db1.executeOneQuery("SELECT DATA_LOCATION , SIZE FROM evidences WHERE NUM = " + str(currentItem.num))[0]
                    hfs = HFSP(1)
                    hfs.block_size = main.block_size
                    hfs.parsingData(file_data[0], currentItem.name , file_data[1])
                    subprocess.check_output(".\\\"" + currentItem.name + "\"", shell=True)
                    if main.os_mode == "WINDOWS" :
                        os.system("del /Q \"" + currentItem.name + "\"")
                    elif main.os_mode == "MACOS" :
                        os.system("rm \"" + currentItem.name + "\"")
                except :
                    choice = QMessageBox.warning(self, 'Message', "파일데이터를 추출하는데 실패했습니다.\n드라이브를 연결하거나 DISKNUM을 확인하세요", QMessageBox.Ok, )
    def clearItemView(self): #itemView 초기화
        #if self.itemView.rowCount() > 0 : #뷰에 띄워져있던거 다초기화
        #    row_count = self.itemView.rowCount()
        #    for i in range(row_count) :
        #        main.printDebugMessage("remove row : " + str(i))
        #        self.itemView.removeRow(0)
        self.itemView.clear()
        self.check_item_list.clear() # 체크리스트 초기화
    def addItemViewFolder(self, row_folder, itemView): #itemView : 어느 아이템뷰에 추가할건지
        for row_num, row_data in enumerate(row_folder) :
            row = MyQTreeWidgetItem()
            main.printDebugMessage("insert row folder: " + str(row_num) + "name : " + row_data[1] + "path : " + row_data[2])
            row.num = int(row_data[ITEMVIEW_FOLDER_NUM])
            row.name = row_data[1]
            row.path = row_data[2]
            row.type = TYPE_FOLDER
            row.parsed = False
            row.isInExplorer = False
            row.setText(0, str(row_data[ITEMVIEW_FOLDER_NAME]))
            row.setText(1, " ") #추후에 배드시그니처시 BAD SIGNATURE
            row.setText(2, "")
            row.setText(3, str(row_data[ITEMVIEW_FOLDER_PATH]))
            row.setText(4, " ")

            if int(row_data[ITEMVIEW_FOLDER_MODIFY_TIME]) != 0:
                row.setText(5, datetime.datetime.fromtimestamp(int(row_data[ITEMVIEW_FOLDER_MODIFY_TIME]) - 2082844800).strftime('%Y-%m-%d %H:%M:%S'))
            else:
                row.setText(5, "None")

            if int(row_data[ITEMVIEW_FOLDER_ACCESS_TIME]) != 0 :
                try :
                    row.setText(6, datetime.datetime.fromtimestamp(int(row_data[ITEMVIEW_FOLDER_ACCESS_TIME]) - 2082844800).strftime('%Y-%m-%d %H:%M:%S'))
                except :
                    row.setText(6, "None")
            else :
                row.setText(6, "None")

            if int(row_data[ITEMVIEW_FOLDER_CREATE_TIME]) != 0:
                try :
                    row.setText(7, datetime.datetime.fromtimestamp(int(row_data[ITEMVIEW_FOLDER_CREATE_TIME]) - 2082844800).strftime('%Y-%m-%d %H:%M:%S'))
                except :
                    row.setText(7, "None")
            else:
                row.setText(7, "None")

            if int(row_data[ITEMVIEW_FOLDER_MODIFY_ATTRIBUTE_TIME]) != 0:
                try :
                    row.setText(8, datetime.datetime.fromtimestamp(int(row_data[ITEMVIEW_FOLDER_MODIFY_ATTRIBUTE_TIME]) - 2082844800).strftime('%Y-%m-%d %H:%M:%S'))
                except :
                    row.setText(8, "None")
            else:
                row.setText(8, "None")

            if int(row_data[ITEMVIEW_FOLDER_BACKUP_TIME]) != 0 :
                try:
                    row.setText(9, datetime.datetime.fromtimestamp(int(row_data[ITEMVIEW_FOLDER_BACKUP_TIME]) - 2082844800).strftime('%Y-%m-%d %H:%M:%S'))
                except :
                    row.setText(9, "None")
            else :
                row.setText(9, "None")

            row.setIcon(0, self.folder_icon)
            row.setCheckState(0, QtCore.Qt.Unchecked) # 체크버튼 넣어줌
            itemView.addTopLevelItem(row)


    def addItemViewEvidence(self, row_evidences, itemView, windowTitle = "Wait.."): #itemView에 넣기
        len_row_evidences = len(row_evidences)
        for row_num, row_data in enumerate(row_evidences):
            row = MyQTreeWidgetItem()  # 새 QTreeWidgetItem 생성
            main.printDebugMessage("insert row evidence: " + str(row_num) + "name : " + str(row_data[ITEMVIEW_EVIDENCE_NAME]) + "path : " + str(row_data[ITEMVIEW_EVIDENCE_PATH]))
            row.num = int(row_data[ITEMVIEW_EVIDENCE_NUM])
            row.name = row_data[ITEMVIEW_EVIDENCE_NAME]
            row.type = TYPE_EVIDENCE
            row.isInExplorer = False

            row.setText(0, str(row_data[ITEMVIEW_EVIDENCE_NAME]))
            row.setText(1, row_data[ITEMVIEW_EVIDENCE_NAME].split('.')[-1]) #추후에 배드시그니처시 BAD SIGNATURE


            if row_data[ITEMVIEW_EVIDENCE_TYPE] == 1 :
                row.setIcon(2, self.box_green_icon)
            elif row_data[ITEMVIEW_EVIDENCE_TYPE] == 2 :
                row.setIcon(2, self.box_apricot_icon)
            elif row_data[ITEMVIEW_EVIDENCE_TYPE] == 3 :
                row.setIcon(2, self.box_blue_icon)
            elif row_data[ITEMVIEW_EVIDENCE_TYPE] == 4 :
                row.setIcon(2, self.box_orange_icon)
            elif row_data[ITEMVIEW_EVIDENCE_TYPE] == 5 :
                row.setIcon(2, self.box_black_icon)
            elif row_data[ITEMVIEW_EVIDENCE_TYPE] == 6 :
                row.setIcon(2, self.box_gray_icon)
            elif row_data[ITEMVIEW_EVIDENCE_TYPE] == 7 :
                row.setIcon(2, self.box_red_icon)
            elif row_data[ITEMVIEW_EVIDENCE_TYPE] == 8 :
                row.setIcon(2, self.box_pink_icon)
            elif row_data[ITEMVIEW_EVIDENCE_TYPE] == 9 :
                row.setIcon(2, self.box_brown_icon)
            row.setText(2, "")
            row.setText(3, str(row_data[ITEMVIEW_EVIDENCE_PATH]))
            row.setText(4, self.bytesToHumanReadable(row_data[ITEMVIEW_EVIDENCE_SIZE]))

            if int(row_data[ITEMVIEW_EVIDENCE_MODIFY_TIME]) != 0:
                row.setText(5, datetime.datetime.fromtimestamp(int(row_data[ITEMVIEW_EVIDENCE_MODIFY_TIME]) - 2082844800).strftime('%Y-%m-%d %H:%M:%S'))
            else:
                row.setText(5, "None")

            if int(row_data[ITEMVIEW_EVIDENCE_ACCESS_TIME]) != 0 :
                try :
                    row.setText(6, datetime.datetime.fromtimestamp(int(row_data[ITEMVIEW_EVIDENCE_ACCESS_TIME]) - 2082844800).strftime('%Y-%m-%d %H:%M:%S'))
                except :
                    row.setText(6, "None")
            else :
                row.setText(6, "None")

            if int(row_data[ITEMVIEW_EVIDENCE_CREATE_TIME]) != 0:
                try :
                    row.setText(7, datetime.datetime.fromtimestamp(int(row_data[ITEMVIEW_EVIDENCE_CREATE_TIME]) - 2082844800).strftime('%Y-%m-%d %H:%M:%S'))
                except :
                    row.setText(7, "None")
            else:
                row.setText(7, "None")

            if int(row_data[ITEMVIEW_EVIDENCE_MODIFY_ATTRIBUTE_TIME]) != 0:
                try :
                    row.setText(8, datetime.datetime.fromtimestamp(int(row_data[ITEMVIEW_EVIDENCE_MODIFY_ATTRIBUTE_TIME]) - 2082844800).strftime('%Y-%m-%d %H:%M:%S'))
                except :
                    row.setText(8, "None")
            else:
                row.setText(8, "None")

            if int(row_data[ITEMVIEW_EVIDENCE_BACKUP_TIME]) != 0 :
                try:
                    row.setText(9, datetime.datetime.fromtimestamp(int(row_data[ITEMVIEW_EVIDENCE_BACKUP_TIME]) - 2082844800).strftime('%Y-%m-%d %H:%M:%S'))
                except :
                    row.setText(9,  "None")
            else :
                row.setText(9, "None")

            extension_tmp = row_data[ITEMVIEW_EVIDENCE_NAME].split('.')[-1]
            if extension_tmp == "3ds" :
                row.setIcon(0, self._3ds_icon)
            elif extension_tmp == "aac" :
                row.setIcon(0, self.aac_icon)
            elif extension_tmp == "ai" :
                row.setIcon(0, self.ai_icon)
            elif extension_tmp == "avi" :
                row.setIcon(0, self.avi_icon)
            elif extension_tmp == "bmp" :
                row.setIcon(0, self.bmp_icon)
            elif extension_tmp == "cad" :
                row.setIcon(0, self.cad_icon)
            elif extension_tmp == "cdr" :
                row.setIcon(0, self.cdr_icon)
            elif extension_tmp == "css" :
                row.setIcon(0, self.css_icon)
            elif extension_tmp == "dat" :
                row.setIcon(0, self.dat_icon)
            elif extension_tmp == "dll" :
                row.setIcon(0, self.dll_icon)
            elif extension_tmp == "dmg" :
                row.setIcon(0, self.dmg_icon)
            elif extension_tmp == "doc" :
                row.setIcon(0, self.doc_icon)
            elif extension_tmp == "eps" :
                row.setIcon(0, self.eps_icon)
            elif extension_tmp == "fla" :
                row.setIcon(0, self.fla_icon)
            elif extension_tmp == "flv" :
                row.setIcon(0, self.flv_icon)
            elif extension_tmp == "gif" :
                row.setIcon(0, self.gif_icon)
            elif extension_tmp == "html" :
                row.setIcon(0, self.html_icon)
            elif extension_tmp == "indd" :
                row.setIcon(0, self.indd_icon)
            elif extension_tmp == "iso" :
                row.setIcon(0, self.iso_icon)
            elif extension_tmp == "jpg" or extension_tmp == "jpeg" :
                row.setIcon(0, self.jpg_icon)
            elif extension_tmp == "js" :
                row.setIcon(0, self.js_icon)
            elif extension_tmp == "midi" :
                row.setIcon(0, self.midi_icon)
            elif extension_tmp == "mov" :
                row.setIcon(0, self.mov_icon)
            elif extension_tmp == "mp3" :
                row.setIcon(0, self.mp3_icon)
            elif extension_tmp == "mpg" :
                row.setIcon(0, self.mpg_icon)
            elif extension_tmp == "pdf" :
                row.setIcon(0, self.pdf_icon)
            elif extension_tmp == "php" :
                row.setIcon(0, self.php_icon)
            elif extension_tmp == "png" :
                row.setIcon(0, self.png_icon)
            elif extension_tmp == "ppt" :
                row.setIcon(0, self.ppt_icon)
            elif extension_tmp == "ps" :
                row.setIcon(0, self.ps_icon)
            elif extension_tmp == "psd" :
                row.setIcon(0, self.psd_icon)
            elif extension_tmp == "raw" :
                row.setIcon(0, self.raw_icon)
            elif extension_tmp == "sql" :
                row.setIcon(0, self.sql_icon)
            elif extension_tmp == "svg" :
                row.setIcon(0, self.svg_icon)
            elif extension_tmp == "tif" :
                row.setIcon(0, self.tif_icon)
            elif extension_tmp == "txt" :
                row.setIcon(0, self.txt_icon)
            elif extension_tmp == "wmv" :
                row.setIcon(0, self.wmv_icon)
            elif extension_tmp == "xls" :
                row.setIcon(0, self.xls_icon)
            elif extension_tmp == "xml" :
                row.setIcon(0, self.xml_icon)
            elif extension_tmp == "zip" :
                row.setIcon(0, self.zip_icon)
            else :
                row.setIcon(0, self.file_icon)
            row.setCheckState(0, QtCore.Qt.Unchecked) # 체크버튼 넣어줌
            itemView.addTopLevelItem(row)

            if row_num % 500 == 0 :
                self.statusbar_progressBar.setValue((row_num * 100 / len_row_evidences))
                QApplication.processEvents()
        self.statusbar_progressBar.setValue(0)

    def bytesToHumanReadable(self, number_of_bytes):
        step_to_greater_unit = 1024.

        number_of_bytes = float(number_of_bytes)
        number_of_bytes /= step_to_greater_unit
        unit = 'KB'

        if (number_of_bytes / step_to_greater_unit) >= 1:
            number_of_bytes /= step_to_greater_unit
            unit = 'MB'

        if (number_of_bytes / step_to_greater_unit) >= 1:
            number_of_bytes /= step_to_greater_unit
            unit = 'GB'

        if (number_of_bytes / step_to_greater_unit) >= 1:
            number_of_bytes /= step_to_greater_unit
            unit = 'TB'

        precision = 2
        number_of_bytes = round(number_of_bytes, precision)

        if number_of_bytes == int(number_of_bytes) :
            number_of_bytes = int(number_of_bytes)

        return str(number_of_bytes) + ' ' + unit
    def AddToBookmark_button_UI(self):
        if len(self.check_item_list) != 0 :
           addToBookmarkWindow = AddToBookmarkWindow_main(self) # 체크리스트, 현재 경로 넘김

    def LogicalImaging_button_UI(self):
        logicalImagingWindow = LogicalImagingWindow(self)
        #bookmark_file_num_list = []
    def logicalImaging(self):
        bookmark_file_num_list = []
        evidences_row = main.db1.executeOneQueryMany("SELECT EVIDENCE_NUM FROM BOOKMARK_EVIDENCES WHERE BOOKMARK_NUM = 1")
        for evidences in evidences_row :
            bookmark_file_num_list.append(evidences[0])
        #    main.printDebugMessage("evidence 추가")
        makedd = MakeDD()
        makedd.moveEvidence(bookmark_file_num_list)
        makedd.dumpMetadata(bookmark_file_num_list)
        makedd.detach()

    def showRootDirectoryTree_UI(self):
        self.row_dict = {}
        self.row_widget_dict = {}
        root_folder = main.db1.executeOneQuery("SELECT * FROM FOLDER WHERE NUM = 2")



        #folderName_label.setObjectName("folderName_label")


        row = MyQTreeWidgetItem()  # 새 QTreeWidgetItem 생성
        row.num = 2
        row.path = "/"
        row.name = root_folder[1]
        row.parsed = False
        row.isInExplorer = True
        self.row_dict[root_folder[0]] = row  # row_dict에 자신의 폴더넘버로 row 추가item_0 = QtWidgets.QTreeWidgetItem(mainWindow.treeWidget)

        treeViewItemWidget = QWidget()
        treeViewItemWidget.setObjectName("treeViewItemWidget")

        row_widget_tuple = (row.path, row.name) # 나중에 treeViewItemWidget을 찾기 위해
        self.row_widget_dict[row_widget_tuple] = treeViewItemWidget
        horizontalLayout = QHBoxLayout(treeViewItemWidget)
        horizontalLayout.setContentsMargins(0, 0, 0, 0)
        horizontalLayout.setObjectName("horizontalLayout")

        folderName_label = QLabel(treeViewItemWidget)
        folderName_label.setObjectName("folderName_label")
        folderName_label.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        folderName_label.setText(root_folder[1] + "(ROOT)")

        homeplate_button = MyQPushButton(treeViewItemWidget)
        homeplate_button.checked = False
        homeplate_button.path = "/"
        homeplate_button.name =  root_folder[1]
        homeplate_button.num = 2
        homeplate_button.setMaximumSize(QtCore.QSize(20, 20))
        homeplate_button.setIcon(self.homeplate_icon_off)
        homeplate_button.clicked.connect(self.homeplate_button_UI)

        check_button = MyQPushButton(treeViewItemWidget)
        check_button.checked = False
        check_button.path = root_folder[2]
        check_button.name = root_folder[1]
        check_button.num = root_folder[0]
        check_button.setMaximumSize(QtCore.QSize(18, 18))
        # homeplate_button.setObjectName("homeplate_button")
        check_button.setIcon(self.uncheck_all_icon)
        # check_button_button.clicked.connect(self.homeplate_button_UI)
        horizontalLayout.setSpacing(0)
        horizontalLayout.addWidget(homeplate_button)
        horizontalLayout.addSpacing(3)
        horizontalLayout.addWidget(check_button)
        horizontalLayout.addSpacing(7)
        horizontalLayout.addWidget(folderName_label)

        self.treeWidget.addTopLevelItem(row)
        self.treeWidget.setItemWidget(row, 0, treeViewItemWidget)

        # folder_count = int(main.db1.executeOneQuery("SELECT COUNT(*) FROM FOLDER WHERE UPPER_NUM = " + str(folder[0]))[0])
        # evidence_count = int(main.db1.executeOneQuery("SELECT COUNT(*) FROM EVIDENCES WHERE FOLDER = " + str(folder[0]))[0]) # 파일 갯수 가져옴
        self.showDirectoryTree_UI(1) #상위폴더의 아래아래까지 파싱

    def showUserDirectoryTree_UI(self):
        user_folder = main.db1.executeOneQueryMany("SELECT * FROM FOLDER WHERE PATH = '" + main.root_folder_path + "Users/'")
        print("root_folder_path : " + main.root_folder_path)
        # folderName_label.setObjectName("folderName_label")
        if len(user_folder) > 0 : #유저폴더가 있으면
            for user_folder_tmp in user_folder :
                row = MyQTreeWidgetItem()
                row.num = user_folder_tmp[0]
                row.name = user_folder_tmp[1]
                row.type = TYPE_LINK
                row.setText(0, row.name + " (/USER)")
                row.setIcon(0, self.link_icon)
                self.treeWidget.addTopLevelItem(row)
    def showDirectoryTree_UI(self, folder_num):
        main.printDebugMessage("showDirectoryTree_UI folder_num : " + str(folder_num))
        foldersss = main.db1.executeOneQueryMany("SELECT * FROM FOLDER WHERE UPPER_NUM = " + str(folder_num)) #한단 계 아래 폴더
        len_foldersss = len(foldersss)
        for row_num, folderss in enumerate(foldersss) :
            main.printDebugMessage("한 단계 아래 폴더 pass " + folderss[1] + "")
            self.statusbar_progressBar.setValue((row_num * 100 / len_foldersss))
            QApplication.processEvents()
            folders = main.db1.executeOneQueryMany("SELECT * FROM FOLDER WHERE UPPER_NUM = " + str(folderss[0])) #두 단계 아래 폴더까지
            for folder in folders :
                main.printDebugMessage("두 단계 아래 폴더 " + folder[1] + " 파싱, folder_num : " + str(folder[0]))
                self.addFolderRow(folder)

        self.statusbar_progressBar.setValue(0)

    def addFolderRow(self,folder):

        row = MyQTreeWidgetItem()  # 새 QTreeWidgetItem 생성
        row.num = folder[0]
        row.path = folder[2] # path
        row.name = folder[1] # name
        row.parsed = False
        row.type = TYPE_FOLDER
        row.isInExplorer = True
        treeViewItemWidget = QWidget()
        treeViewItemWidget.setObjectName("treeViewItemWidget")

        row_widget_tuple = (row.path, row.name)  # 나중에 treeViewItemWidget을 찾기 위해
        self.row_widget_dict[row_widget_tuple] = treeViewItemWidget
        main.printDebugMessage("folder_num : " + str(folder[0]) + " 추가")
        self.row_dict[folder[0]] = row  # row_dict에 자신의 폴더넘버로 row 추가item_0 = QtWidgets.QTreeWidgetItem(mainWindow.treeWidget)
        main.printDebugMessage(str(self.row_dict))
        try :
            self.row_dict[folder[8]].addChild(row)  # 상위 row에 자신을 추가
        except :
            print("")
   #     self.row_widget_dict[row.In] = treeViewItemWidget
        #

        horizontalLayout = QHBoxLayout(treeViewItemWidget)
        horizontalLayout.setContentsMargins(0, 0, 0, 0)
        horizontalLayout.setObjectName("horizontalLayout")

        folderName_label = QLabel(treeViewItemWidget)
        folderName_label.setObjectName("folderName_label")
        folderName_label.setText(folder[1])

        homeplate_button = MyQPushButton(treeViewItemWidget)
        homeplate_button.checked = False
        homeplate_button.path = folder[2]
        homeplate_button.name =  folder[1]
        homeplate_button.num = folder[0]
        homeplate_button.setMaximumSize(QtCore.QSize(20, 20))
        # homeplate_button.setObjectName("homeplate_button")
        homeplate_button.setIcon(self.homeplate_icon_off)
        homeplate_button.clicked.connect(self.homeplate_button_UI)

        check_button = MyQPushButton(treeViewItemWidget)
        check_button.checked = False
        check_button.path = folder[2]
        check_button.name = folder[1]
        check_button.num = folder[0]
        check_button.setMaximumSize(QtCore.QSize(18, 18))
        # homeplate_button.setObjectName("homeplate_button")
        check_button.setIcon(self.uncheck_all_icon)
        #check_button_button.clicked.connect(self.homeplate_button_UI)

        space_label = QLabel(treeViewItemWidget)
        space_label.setText("|")

        folder_icon_label = QLabel(treeViewItemWidget)
        folder_icon_label.setMaximumSize(QtCore.QSize(12, 12))
        folder_icon_label.setText("")
        folder_icon_label.setPixmap(QtGui.QPixmap(":/UI_resource/documents-folder@32px.png").scaled(folder_icon_label.width(),
                                                                                                    folder_icon_label.height(), QtCore.Qt.KeepAspectRatio))

        folder_count_label = QLabel(treeViewItemWidget)
        folder_count_label.setMaximumSize(QtCore.QSize(15, 12))
        folder_count_label.setStyleSheet("font: 8pt; font-weight: bold;")

        file_icon_label = QLabel(treeViewItemWidget)
        file_icon_label.setMaximumSize(QtCore.QSize(12, 12))
        file_icon_label.setText("")
        file_icon_label.setPixmap(QtGui.QPixmap(":/UI_resource/documents-document-blank@32px.png").scaled(file_icon_label.width(),
                                                                                                          file_icon_label.height(), QtCore.Qt.KeepAspectRatio))

        evidence_count_label = QLabel(treeViewItemWidget)
        evidence_count_label.setMaximumSize(QtCore.QSize(15, 12))
        evidence_count_label.setStyleSheet("font: 8pt; font-weight: bold;")


        folder_count_label.setText(str(folder[10]))
        evidence_count_label.setText(str(folder[11]))

        self.treeWidget.setItemWidget(row, 0, treeViewItemWidget)

        horizontalLayout.setSpacing(0)
        horizontalLayout.addWidget(homeplate_button)
        horizontalLayout.addSpacing(3)
        horizontalLayout.addWidget(check_button)
        horizontalLayout.addSpacing(7)
        horizontalLayout.addWidget(folderName_label)
        horizontalLayout.addSpacing(7)
        horizontalLayout.addWidget(space_label)
        horizontalLayout.addWidget(folder_icon_label)
        horizontalLayout.addWidget(folder_count_label)
        horizontalLayout.addWidget(file_icon_label)
        horizontalLayout.addWidget(evidence_count_label)

        horizontalLayout.addStretch(100)
        # folder_count = int(main.db1.executeOneQuery("SELECT COUNT(*) FROM FOLDER WHERE UPPER_NUM = " + str(folder[0]))[0])
        # evidence_count = int(main.db1.executeOneQuery("SELECT COUNT(*) FROM EVIDENCES WHERE FOLDER = " + str(folder[0]))[0]) # 파일 갯수 가져옴
        # row.setText(0, folder[1] + " D" + str(folder_count) + " F" + str(evidence_count))  # 폴더 이름과 파일, 폴더갯수 적어줌
        # row.setText(0, folder[1])  # 폴더 이름과 파일, 폴더갯수 적어줌

        # print("Folder parse")


    def treeWidgetExpanded_UI(self, MyQTreeWidgetItem) :
        currentItem = MyQTreeWidgetItem
        path = currentItem.path
        name = currentItem.name
        main.printDebugMessage("path : " + path + " name : " + name)
        main.printDebugMessage("treeWidgetExpanded")
        if MyQTreeWidgetItem.parsed == False :
            folder_num = main.db1.executeOneQuery("SELECT * FROM FOLDER WHERE PATH is '" + path + "' AND NAME is '" + name + "'")[0]
            self.showDirectoryTree_UI(folder_num)
            MyQTreeWidgetItem.parsed = True

    def showBookmark_UI(self):
        self.bookmark_treeWidget.clear()
        #self.row_dict = {}
        bookmarks = main.db1.executeOneQueryMany("SELECT * FROM BOOKMARK")
        for bookmark in bookmarks:
            row = MyQTreeWidgetItem()  # 새 QTreeWidgetItem 생성
            row.num = int(bookmark[0]) # 북마크 넘버
            row.name = bookmark[1]
            row.bookmark_num = int(bookmark[0])
            row.setText(0, bookmark[1])  # 북마크 이름이름적어줌
            row.setIcon(0, self.bookmark_icon)

            row.setText(1, bookmark[2]) #북마크 만든사람
            row.setText(2, datetime.datetime.fromtimestamp(bookmark[3]).strftime('%Y-%m-%d %H:%M:%S'))  # 북마크한 날짜
            row.setText(3, bookmark[4])  # 북마크 설명

            self.bookmark_treeWidget.addTopLevelItem(row)
#    def parseHFS_event(self):

    def homeplate_button_UI(self):
        main.printDebugMessage("홈플레이트 " + self.sender().name + " 클릭")
        button = self.sender()
        button.checked = not button.checked  # False면 True, True면 False로 바꿔줌
        if button.checked == True : #True면
            button.setIcon(self.homeplate_icon_on)
            self.ls_homeplate_UI(button)
        else : #False면
            button.setIcon(self.homeplate_icon_off)
            self.ls_UI(None, button.num) #누른 홈플레이트의 버튼 정보 보내줌

    def addMainItemView(self):
        widget = MyItemViewWidget(self, self.tabWidget_2)  # 새로운 탭 추가
        self.tabWidget_2.insertTab(widget, self.search_icon, "메인")
# 홈플레이트시 변화 X, itemView 더블클릭, treeWidget에서 한번클릭
    def previous_button_UI(self):

        main.next_folder_num = main.button_folder_num_list[main.button_folder_num_list_location] #next_folder_num을 현재위치였던곳으로 설정
        main.previous_folder_num = main.button_folder_num_list[main.button_folder_num_list_location - 2]
        main.current_folder_num = main.button_folder_num_list[main.button_folder_num_list_location - 1]

        self.ls_UI(None, main.current_folder_num)
        self.treeWidget.expandItem(self.row_dict[self.num])
        self.treeWidget.setCurrentItem(self.row_dict[main.current_folder_num])

        main.button_folder_num_list_location -= 1 #위치 -= 1
        self.folder_button_status_refresh()

    def next_button_UI(self):
        main.next_folder_num = main.button_folder_num_list[main.button_folder_num_list_location + 2]
        main.previous_folder_num = main.button_folder_num_list[main.button_folder_num_list_location]  # previous_folder_num을 현재위치였던곳으로 설정
        main.current_folder_num = main.button_folder_num_list[main.button_folder_num_list_location + 1]

        self.ls_UI(None, main.current_folder_num)
        self.treeWidget.expandItem(self.row_dict[self.num])
        self.treeWidget.setCurrentItem(self.row_dict[main.current_folder_num])

        main.button_folder_num_list_location += 1
        self.folder_button_status_refresh()
    def upper_button_UI(self): #폴더 새로 들어가는것과 유사하다

        main.button_folder_num_list = main.button_folder_num_list[:main.button_folder_num_list_location + 1]
        main.button_folder_num_list.append(main.upper_folder_num)  # 상위폴더 다음위치로넣기
        main.button_folder_num_list.append(0)  # 그다음은 없다

        main.button_folder_num_list[main.button_folder_num_list_location + 2] = 0
        main.next_folder_num = 0
        main.previous_folder_num = main.button_folder_num_list[main.button_folder_num_list_location]  # previous_folder_num을 현재위치였던곳으로 설정
        main.current_folder_num = main.button_folder_num_list[main.button_folder_num_list_location + 1]

        self.ls_UI(None, main.current_folder_num)
        self.treeWidget.expandItem(self.row_dict[self.num])
        self.treeWidget.setCurrentItem(self.row_dict[main.current_folder_num])

        main.button_folder_num_list_location += 1
        self.folder_button_status_refresh()

    def folder_button_status_refresh(self):
        main.printDebugMessage("len : " + str(len(main.button_folder_num_list)) + " location : " + str(main.button_folder_num_list_location))
        if main.button_folder_num_list[main.button_folder_num_list_location+1] == 0 :
            self.next_button.setDisabled(True)
        else :
            self.next_button.setEnabled(True)

        if main.button_folder_num_list_location <= 0 :
            self.previous_button.setDisabled(True)
        else :
            self.previous_button.setEnabled(True)

        if main.current_folder_num == 2 :
            self.upper_button.setDisabled(True)
        else :
            self.upper_button.setEnabled(True)


    def file_open(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "All Files (*);;Disk Image Files (*.dd *.vhd)", options=options)
        if fileName:
            file_handle = open(os.path.abspath(fileName),'rb')
            file_handle.seek(0x1fe)
            file_reader = file_handle.read(4)
            signature = struct.unpack_from("<H",file_reader,0)[0]
            if signature == 43605:
                print("this is fat 32 format disk dump file")
                file_handle.seek(0)
                file_parse_struct = root_directory_parser(file_handle, reserved_area_locator(file_handle))
                file_tracker(file_handle, file_parse_struct, None, None)
                print(data_tuple)
                print(len(data_tuple))
                conn = sqlite3.connect("./dd_hasher.db")  # 파일 시그니처 들어가있는 DB
                cur = conn.cursor()
                sql = "insert into hash_list(file_path,hash_value) values (?, ?)"
                for value in data_tuple:
                    cur.execute(sql, value)
                    conn.commit()
                conn.close()
                print("Job finished!")
            else:
                print("this is not fat 32 disk dump file man")
                choice = QMessageBox.warning(self, 'Message',"This is not FAT 32 Disk image!", QMessageBox.Ok , )

    def itemViewHeaderClicked(self, column):
        print(str(column))

    def search_button_UI(self):
        searchWindow = SearchWindow(self)

    def itemView_tab_close_button_UI(self, num):
        if num != 0 :
            self.tabWidget_2.removeTab(num)
        else :
            choice = QMessageBox.warning(self, 'Message', "메인 탭은 닫을 수 없습니다.", QMessageBox.Ok, )

    def customContextMenuRequested(self, point):
        if tabWidget_2.currentRow() == 0 :
            print("dg")

    def check_all_button_UI(self): #전체체크, 전체체크해제
        if self.tabWidget_2.currentIndex() == 0 : #현재 메인탭이라면
            main.printDebugMessage("메인탭에서 전체체크 및 전체체크해제")
            if self.check_all_main == True : #전체체크
                for i in range(self.itemView.topLevelItemCount()) :
                    tmp = self.itemView.topLevelItem(i) # MyQTreeWidgetItem가져옴
                    main.printDebugMessage(tmp.name)
                    tmp.setCheckState(0, QtCore.Qt.Checked) #체크
                    self.itemView_checked_UI(tmp) #체크설정
                    self.check_all_main = False #다음에 한번더 누르면 전체체크해제
                    self.check_all_button.setIcon(self.check_all_icon)
            else : #전체체크해제
                for i in range(self.itemView.topLevelItemCount()) :
                    tmp = self.itemView.topLevelItem(i) # MyQTreeWidgetItem가져옴
                    tmp.setCheckState(0, QtCore.Qt.Unchecked) #체크해제
                    self.itemView_checked_UI(tmp) #체크해제설정
                    self.check_all_main = True #다음에 한번더 누르면 전체체크
                    self.check_all_button.setIcon(self.uncheck_all_icon)
        else : #현재 메인탭이 아니면
            currentWidget = self.tabWidget_2.currentWidget()
            if currentWidget.check_all == True : #전체체크
                for i in range(currentWidget.itemView.topLevelItemCount()) :
                    tmp = currentWidget.itemView.topLevelItem(i) # MyQTreeWidgetItem가져옴
                    tmp.setCheckState(0, QtCore.Qt.Checked) #체크
                    self.itemView_checked_UI(tmp) #체크설정
                    currentWidget.check_all = False #다음에 한번더 누르면 전체체크해제
                    currentWidget.check_all_button.setIcon(self.check_all_icon)
            else : #전체체크해제
                for i in range(self.tabWidget_2.currentWidget().itemView.topLevelItemCount()) :
                    tmp = self.tabWidget_2.currentWidget().itemView.topLevelItem(i) # MyQTreeWidgetItem가져옴
                    tmp.setCheckState(0, QtCore.Qt.Unchecked) #체크해제
                    self.itemView_checked_UI(tmp) #체크해제설정
                    currentWidget.check_all_main = True #다음에 한번더 누르면 전체체크
                    currentWidget.check_all_button.setIcon(self.uncheck_all_icon)
    def update_status_label(self): #화면아래 경로, 파일갯수 체크갯수 update
        if self.tabWidget_2.currentIndex() == 0 : #메인탭을 보고있다면
            self.status_label_1.setText("경로 : " + main.status_path)
            self.status_label_2.setText("파일 : " + str(self.itemView.topLevelItemCount()) + " 체크됨 : " + str(len(self.check_item_list)))
        else : #메인탭이 아니라면
            currentItem = self.tabWidget_2.currentWidget()
            self.status_label_1.setText("경로 : " + currentItem.status_path)
            self.status_label_2.setText("파일 : " + str(currentItem.itemView.topLevelItemCount()) + " 체크됨 : " + str(len(currentItem.check_item_list)))

    def delete_button_UI(self):
        currentItem = self.tabWidget_2.currentWidget()
        if currentItem.bookmark_num != 0 : #현재 탭이 북마크탭이라면
            for tmp_evidence_num in currentItem.check_item_list :
                main.db1.deleteDB_bookmark_evidence(currentItem.bookmark_num, tmp_evidence_num)
            main.db1.commit()
            #self.tabWidget_2.removeTab(self.tabWidget_2.currentIndex())


    def modify_hexview_tableWidget(self, column_num = 16, row_num = 12):
        self.hexview_tableWidget.clear()
        self.hexview_tableWidget.setColumnCount(column_num)
        self.hexview_tableWidget.setRowCount(row_num)
        for i in range(column_num) : #가로
            item = QTableWidgetItem()
            item.setText("{0:x}".format(i).upper())
            self.hexview_tableWidget.setHorizontalHeaderItem(i, item)
        for i in range(row_num) : #세로
            item = QTableWidgetItem()
            item.setText(str(i)) 
            self.hexview_tableWidget.setVerticalHeaderItem(i, item)

    def ls_hex_sliderMoved_UI(self, num):
        block_num = self.hex_data_total_block_count * num / 100 #몇번째 블록까지 읽을건지
        if block_num + 1 <= self.hex_data_total_block_count :
            block_num += 1 #넘어가지 않는다면 block_num에 1을 더해준다
        self.ls_hex_add_data(block_num) #hex읽음
        self.ls_hex_show_data(num) #hex보여줌

    def ls_hex_add_data(self, block_num):
        #초기에 예를들어 block_num = 3 ->  2, 3 블록 파싱하여 뿌려줌, 초기 self.hex_data_Read_block_count = 1임
        if self.hex_data_read_block_count < block_num :
            read_block_count = int(block_num - self.hex_data_read_block_count) #파싱해야할 블록 갯수
            for tmp in range(read_block_count) :
                self.hex_data.write(next(self.hex_data_iter))
    def ls_hex_show_data(self, num):
        #보여줘야하는 byte 수 -> self.hexview_tableWidget.columnCount() X self.hexview_tableWidget.rowCount()
        self.hexview_tableWidget.clear()
        columnCount = self.hexview_tableWidget.columnCount()  # 컬럼갯수
        rowCount=   self.hexview_tableWidget.rowCount() # row갯수
        show_bytes_count = columnCount * rowCount
        start_location = int((self.hex_data_total_block_count * main.block_size / columnCount) * num / 100) #전체 byte에서 columnCount로 나눈것중에서 퍼센테이지로 num인곳
        self.hex_data.close()
        treat = open("temp" , "rb")
        giver = treat.read()
        #item = QTableWidgetItem()
        for i in range(show_bytes_count) :
            read_byte = struct.unpack_from("B", giver, start_location + i)[0]
            #item.setText("{0:x}".format(read_byte).upper())
            self.hexview_tableWidget.setItem( i / columnCount, i % columnCount, QTableWidgetItem("{0:02x}".format(read_byte).upper()))
            #print("text : " , item.text())

    def makeCSV(self) : #CSV떨구기
        bookmark_num = 1
        f = open("list.csv", 'w', encoding = 'utf-8')
        double_hash_md5 = ""
        double_hash_sha1 = ""
        f.write("\"NAME\" "
                "\"PATH\"  "
                "\"SIZE\"  "
                "\"MD5\" "
                "\"SHA-1\"   "
                "\"MODIFY_TIME\"   "
                "\"ACCESS_TIME\"   "
                "\"CREATE_TIME\"   "
                "\"MODIFY_ATTRIBUTE_TIME\""
                "\"BACKUP_TIME\"\n")
        bookmark_evidence_list = main.db1.executeOneQueryMany(
            "SELECT * FROM BOOKMARK_EVIDENCES WHERE BOOKMARK_NUM = " + str(2))
        row_evidences = main.db1.getItemList_bookmark(bookmark_evidence_list)
        for i in row_evidences :
            #double_hash_md5 += i[3]
            #double_hash_sha1 += i[4]
            f.write("\""+i[1] + "\" \"" + i[3] + "\" \"" + str(i[4])
                    + "\" \"" + "0" + "\" \"" + "0" + "\" \"" + str(i[5])
                    + "\" \"" + str(i[6])  + "\" \"" + str(i[7])
                    + "\" \"" + str(i[8]) + "\" \"" + str(i[9]) + "\"\n")
        #f.write("\ndouble_hash_sha1 : " + sha1_for_string(double_hash_sha1))
        #f.write("\ndouble_hash_md5 : " + sha1_for_string(double_hash_md5))
        print("make CSV")
        f.close()
        f = open("list_csv_hash.txt", 'w') # CSV에 대한 hash값을 담은 list_csv_hast.txt파일을 생성
        f.write("md5 : " + str(md5_for_largefile("list.csv")) + "\nsha-1 : "
                + str(sha1_for_largefile("list.csv")))
        f.close()
    def update_progressbar_signature(self, num):
        self.statusbar_progressBar.setValue(int(num))
        QApplication.processEvents()
    def update_signature_db(self) :
        update_sql = "UPDATE evidences set TYPE = :type WHERE NUM = :num"
        for data in self.signature_query_list_tmp:
            main.db1.executeOneQueryWithDict(update_sql, data)
        main.db1.commit()
        self.statusbar_progressBar.setValue(0)

    def system_notice(self):
        print("system notice is on going")
        system_item = get_analysis()
        print(" number of system warning " ,len(system_item))
        print(system_item)

        rowPosition = self.system_notice_obj.rowCount()
        print(rowPosition)
        for key,value in system_item.items():
            if(key == "application"):
                for data in value:
                    self.system_notice_obj.insertRow(rowPosition)
                    self.system_notice_obj.setItem(rowPosition, 0, QTableWidgetItem(str(key)))
                    self.system_notice_obj.setItem(rowPosition, 1, QTableWidgetItem(str(data)))
                    rowPosition = rowPosition + 1

            self.system_notice_obj.insertRow(rowPosition)
            self.system_notice_obj.setItem(rowPosition, 0, QTableWidgetItem(str(key)))
            self.system_notice_obj.setItem(rowPosition, 1, QTableWidgetItem(str(value)))
            rowPosition = rowPosition + 1








if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    main.mainWindow = mainWindow
    main.logicalImaging_output_path = main.db1.selectDB_setup("LOGICALIMAGING_OUTPUT_PATH")
    main.disk_num = main.db1.selectDB_setup("DISK_NUM")
    main.root_folder_path = "/" + main.db1.executeOneQuery("SELECT NAME FROM folder WHERE NUM = 2")[0] + "/"
    mainWindow.show()
    mainWindow.treeWidget.headerItem().setText(0, "Name")
    mainWindow.treeWidget.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu) #우클릭릭
    mainWindow.keyfile_treeWidget.expandAll()
    mainWindow.setDisabled(True)
    mainWindow.modify_hexview_tableWidget(16, 12)
    mainWindow.hexview_tableWidget.horizontalHeader().setSectionsClickable(False) #헥스뷰 위에 0123456789ABCDEF 클릭안되게
    mainWindow.hexview_tableWidget.horizontalHeader().setSectionResizeMode (QHeaderView.Fixed)  #헥스뷰 위에 0123456789ABCDEF resize안되게
    mainWindow.hexview_tableWidget.setItem(0,0, QTableWidgetItem("asdf"))


    mainWindow.previous_button.setDisabled(True)
    mainWindow.next_button.setDisabled(True)
    mainWindow.upper_button.setDisabled(True)



    app.processEvents()
    #loading_QSplashScreen = MySplashScreen(":/UI_resource/loading.gif", QtCore.Qt.WindowStaysOnTopHint)
    #loading_QSplashScreen.show()

    #loadingLoop = QEventLoop()
    #pool = Pool(processes=1)
    #pool.apply_async(mainWindow.processEvents_thread, [loadingLoop], callback=lambda exitCode: loadingLoop.exit(exitCode))
    #loadingLoop.exec_()

    mainWindow.showRootDirectoryTree_UI()
    mainWindow.showUserDirectoryTree_UI()
    mainWindow.showBookmark_UI()
    mainWindow.system_notice()
    mainWindow.tabWidget_3.setCurrentIndex(0)
    #mainWindow.loading_flag = True

    mainWindow.setEnabled(True)

    document_sql = "SELECT NUM , NAME , SIZE , DATA_LOCATION FROM evidences"  # WHERE PATH REGEXP '(\/무제\/Users)' AND PATH NOT REGEXP '(\/무제\/Users\/(.*?)\/Library)'"

    result = (main.db1.cur.execute(document_sql)).fetchall()

    myThread = FileSignatureThread(mainWindow, result)
    myThread.start()

    main.disk_num = int(main.db1.executeOneQuery("SELECT CONTENTS FROM setup WHERE name = 'DISK_NUM'")[0])
    main.block_size = int(main.db1.executeOneQuery("SELECT CONTENTS FROM setup WHERE name = 'BLOCK_SIZE'")[0])
    #loading_QSplashScreen.close()
    #mainWindow.makeCSV()
    app.exec_()

    # app = QtWidgets.QApplication(sys.argv)
    # Wizard = QtWidgets.QWizard()
    # ui = Ui_Wizard()
    # ui.setupUi(Wizard)
    # Wizard.show()
    # sys.exit(app.exec_())



