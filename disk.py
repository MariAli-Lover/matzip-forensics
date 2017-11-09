## 이전 main 모듈의 함수를 옮겨옴


import os
import globals as gl
from file_hash import *
from get_file_path import *


def printItemList() : #Item.py랑 같이쓰던건데 사용목적희미해짐
    for i in itemList :
        print(i.showInfo())


def makeCSV() : #CSV떨구기
    f = open("list.csv", 'w')
    double_hash_md5 = ""
    double_hash_sha1 = ""
    f.write("\"이름\" \"경로\"  \"크기\"  \"MD5\" \"SHA-1\"   \"마지막 수정시간\"   \"마지막 접근시간\"   \"생성시간\"   \"색인\"\n")
    row_evidences = gl.db.executeOneQueryMany("SELECT * FROM EVIDENCES")
    for i in row_evidences :
        double_hash_md5 += i[3]
        double_hash_sha1 += i[4]
        f.write("\""+i[0] + "\" \"" + i[1] + "\" \"" + str(i[2])
                + "\" \"" + i[3] + "\" \"" + i[4] + "\" \"" + str(i[5])
                + "\" \"" + str(i[6])  + "\" \"" + str(i[7])
                + "\" \"" + str(i[8]) + "\"\n")
    f.write("\ndouble_hash_sha1 : " + sha1_for_string(double_hash_sha1))
    f.write("\ndouble_hash_md5 : " + sha1_for_string(double_hash_md5))
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
    print("Please input path > ", end = "") # 최상위폴더 입력받기
    gl.default_path = input() #입력받음

    item_dict = {}
    item_dict['name'] = "DEFAULT_PATH"
    item_dict['contents'] = default_path
    gl.db.insertDB("SETUP", item_dict) # 최상위폴더경로 (default_path) db에 저장
    item_dict.clear()
    item_dict['num'] = 0
    item_dict['name'] = os.path.basename(default_path)
    item_dict['path'] = os.path.dirname(default_path)[:-1] if os.path.dirname(default_path)[-1] == "\\" else os.path.dirname(default_path)# 경로끝에 \ 붙을 시 \ 떼줌
    item_dict['upper_num'] = -1
    item_dict['parsed'] = 1
    gl.db.insertDB("FOLDER", item_dict) # 최상위폴더정보저장
    addRootFolderNum(default_path, 0)
    addRootFolderNum(item_dict['path'], -1)
    #directory = os.listdir(default_path)
    #get_file_path(default_path, db1) # 최상위폴더부터 파일폴더 쭉긁어옴
    get_one_file_path(default_path, db1)
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
            #db1.insertDB("INSERT", file_inform)"""