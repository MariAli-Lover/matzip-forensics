"""
from __future__ import unicode_literals
import os
# import Item
from PyQt5 import QtWidgets
from PyQt5 import uic
from file_hash import *
from get_file_path import *
from explorer import *
from hfs import *
from dbManager import *
from globals import *


gl.db.createTableIfNotExist()  # db 테이블 없으면 만들기
print("DB 연결완료")

# readDisk()
# system_warning()
# hfsp = HPSP()
# beginExplorer() #explorer 실행import sys

item_dict = {}
item_dict['bookmark_num'] = 1
item_dict['name'] = ".DS_Store"
item_dict['path'] = "/무제/"
print(item_dict)
gl.db.updateDB("BOOKMARK_ITEM", item_dict)

# QtWidgets.QDialog.__init__(None)
# ui = uic.loadUi("MainWindow.ui")
# ui.show()
# printItemList()
# makeCSV(itemList)
# gl.db.printDB()
gl.db.conn.close() #db연결종료
"""
