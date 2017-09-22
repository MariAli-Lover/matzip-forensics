import os

from file_hash import *
from makeCSV import *
from file_info import *
import Item
from dbManager import *
from get_file_path import *
from explorer import *
itemList = [] #Item.py랑 같이쓰던건데 사용목적희미해짐
default_path = "" # explorer에서 최상위폴더 경로
debug_mode = False #디버그
def printDebugMessage(message) : #디버그메세지
    if debug_mode == True :
        print(message)

def printItemList() : #Item.py랑 같이쓰던건데 사용목적희미해짐
    for i in itemList :
        print(i.showInfo())

def makeCSV(itemList) : #CSV떨구기
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

def makeDD(path) : #DD떨구기 1도모름
    with open("E:\\test.txt", "rb") as f:
        i = open("test.dd", "wb")
        while True:
            if i.write(f.read(512)) == 0:
                break

def readDisk():
    print("Please input path > ") # 최상위폴더 입력받기
    default_path = input() #입력받음

    item_dict = {}
    item_dict['name'] = "DEFAULT_PATH"
    item_dict['contents'] = default_path

    db1.updateDB("SETUP", item_dict) # 최상위폴더경로 (default_path) db에 저장

    #directory = os.listdir(default_path)
    get_file_path(default_path, db1) # 최상위폴더부터 파일폴더 쭉긁어옴
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
db1 = db(); #db 객체생성
db1.createTableIfNotExist() #db 테이블 없으면 만들기
print("DB 연결완료")
#readDisk()
beginExplorer() #explorer 실행
#printItemList()
#makeCSV(itemList)
#db1.printDB()
db1.conn.close() #db연결종료


