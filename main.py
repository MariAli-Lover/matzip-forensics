import os

from file_hash import *
from makeCSV import *
from file_info import *
import Item
from dbManager import *
from get_file_path import *
from explorer import *
itemList = []
default_path = ""
debug_mode = False
def printDebugMessage(message) :
    if debug_mode == True :
        print(message)

def printItemList() :
    for i in itemList :
        print(i.showInfo())

def makeCSV(itemList) :
    f = open("list.csv", 'w')
    f.write("\"이름\" \"경로\"  \"크기\"  \"MD5\" \"SHA-1\"   \"마지막 수정시간\"   \"마지막 접근시간\"   \"생성시간\"   \"색인\"\n")
    for i in itemList :
        f.write("\""+i.name + "\" \"" + i.path + "\" \"" + str(i.size)
                + "\" \"" + str(i.md5) + "\" \"" + str(i.sha1) + "\" \"" + str(i.modify_time)
                + "\" \"" + str(i.access_time)  + "\" \"" + str(i.create_time)
                + "\" \"" + str(i.index) + "\"\n")
    print("make CSV")
    f.close()
    f = open("list_csv_hash.txt", 'w') # CSV에 대한 hash값을 담은 list_csv_hast.txt파일을 생성
    f.write("md5 : " + str(md5_for_largefile("list.csv")) + "\nsha-1 : "
            + str(sha1_for_largefile("list.csv")))
    f.close()

def makeDD(path) :
    with open("E:\\test.txt", "rb") as f:
        i = open("test.dd", "wb")
        while True:
            if i.write(f.read(512)) == 0:
                break

def readDisk():
    print("Pleas input path > ")
    default_path = input()

    item_dict = {}
    item_dict['name'] = "DEFAULT_PATH"
    item_dict['contents'] = default_path

    db1.updateDB("SETUP", item_dict)

    #directory = os.listdir(default_path)
    get_file_path(default_path, db1)
    """for items in directory:
        one_item = os.path.join(default_path, items)  # 디렉토리에있는 파일 및 폴더 읽어온다.

        if os.path.isfile(one_item):  # 파일이면, itemList에 집어넣을 것
            file_inform = file_info(one_item)
            item = Item.Item(file_inform['name'], file_inform['path']
                             , file_inform['size'], file_inform['md5']
                             , file_inform['sha1'], file_inform['modify_time']
                             , file_inform['access_time'], file_inform['create_time']
                             , file_inform['index'])  # 새로운 Item객체 만듬, 정보대입
            itemList.append(item)  # itemList에 item객체를 넣는다
            #db1.updateDB("INSERT", file_inform)"""
db1 = db();
db1.createTableIfNotExist()
print("DB 연결완료")
#readDisk()
beginExplorer()
#printItemList()
#makeCSV(itemList)
#db1.printDB()
db1.conn.close()


