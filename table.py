# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\조재민\Desktop\table_widget.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

import sqlite3

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    db_original={}
    db_changed={}
    #db_current_cursor=[]
    i=0
    def loaddata(self):
        connection = sqlite3.connect('file_signature22.db')
        query = "SELECT * FROM file_signature"
        result = connection.execute(query)
        for row_number , row_data in enumerate(result):
            self.tableWidget.insertRow(row_number)
            self.store_list = ()
            for column_number , data in enumerate(row_data):
                self.tableWidget.setItem(row_number , column_number , QtWidgets.QTableWidgetItem(str(data)))
                self.store_list = self.store_list + (data,)
            self.db_original.update({row_number:self.store_list})
        connection.close()

    def change(self, action_vector):
        if(action_vector == "add"):
            rowposition = self.tableWidget.rowCount()
            self.tableWidget.insertRow(rowposition)
        if(action_vector == "delete"):
            print("hello")
        if(action_vector == "save"):
            self.save_query = "INSERT INTO file_signature (extension, header_signature, footer_signature, header_offset , footer_offset) VALUES (?,?,?,?,?)"
            self.update_query = 'UPDATE file_signature SET extension = ?, header_signature = ?, footer_signature = ?, header_offset = ?, footer_offset = ? WHERE extension = ? AND header_signature = ? AND footer_signature = ? AND header_offset = ? AND footer_offset = ?'
            connection = sqlite3.connect('file_signature22.db')
            cur = connection.cursor()
            for key in self.db_changed.keys():
                try:
                    cur.execute(self.update_query, self.db_changed[key] + self.db_original[key])
                    self.db_original[key] = self.db_changed[key]
                except:
                    #if you want add new element to your db make except
                    self.db_original.update({key : self.db_changed[key]})
                    cur.execute(self.save_query ,self.db_original[key])
                finally:
                    del self.db_changed[key]
                    connection.commit()
            connection.close()

                #if(self.db_original[key] is None):
                #    print("new raw")
                    #connection.execute(self.save_query , self.db_changed[key])
                #else:
                #    print("already exists")
                    #connection.excute()




    def item_changed(self):
        self.current = self.tableWidget.currentRow()
        if(self.current == -1):
            return
        else:
            try:
                self.tuple_store = ((str(self.tableWidget.item(self.current, 0).text()),
                                     str(self.tableWidget.item(self.current, 1).text()),
                                     str(self.tableWidget.item(self.current, 2).text()),
                                     str(self.tableWidget.item(self.current, 3).text()),
                                     str(self.tableWidget.item(self.current, 4).text())))
            except:
                #when you tried to add row and give new element you'll get error
                return

            self.db_changed.update({self.current : self.tuple_store})



    def current_cursor(self):
        self.current = self.tableWidget.currentRow()

        print("you just clicked current %d row" % self.current)
        #self.list_collect = [self.tableWidget.item(self.current,0),
        #                     self.tableWidget.item(self.current, 1),
        #                     self.tableWidget.item(self.current, 2),
        #                     self.tableWidget.item(self.current, 3),
        #                     self.tableWidget.item(self.current, 4)]
        #self.db_original.update({self.current: self.list_collect})




    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1161, 640)
        self.tableWidget = QtWidgets.QTableWidget(Form)
        self.tableWidget.setGeometry(QtCore.QRect(10, 10, 891, 611))
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setObjectName("tableWidget")
        self.btn_add_row = QtWidgets.QPushButton(Form)
        self.btn_save = QtWidgets.QPushButton(Form)

        self.btn_load = QtWidgets.QPushButton(Form)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(4, item)

        self.btn_load.setGeometry(QtCore.QRect(980, 40, 93, 28))
        self.btn_load.setObjectName("btn_load")
        #self.btn_load.clicked.connect(self.loaddata)

        self.btn_add_row.setGeometry(QtCore.QRect(980,70,93,28))
        self.btn_add_row.setObjectName(("btn_add_row"))
        self.btn_add_row.clicked.connect(lambda : self.change("add"))

        self.btn_save.setGeometry(QtCore.QRect(980,100,93,28))
        self.btn_save.setObjectName("btn_save")
        self.btn_save.clicked.connect(lambda  : self.change("save"))

        #self.tableWidget.itemChanged.connect(self.item_changed)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("Form", "EXTENSION"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("Form", "HSIGNATURE"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("Form", "FSIGNATURE"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("Form", "HOFFSET"))
        item = self.tableWidget.horizontalHeaderItem(4)
        item.setText(_translate("Form", "FOFFSET"))
        self.btn_load.setText(_translate("Form", "Load"))
        self.btn_add_row.setText(_translate("Form", "Add_Row"))
        self.btn_save.setText(_translate("Form", "Save"))

        self.loaddata()
        print(self.db_original)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

