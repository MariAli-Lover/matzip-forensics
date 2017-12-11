import sqlite3
from get_file_path import *
import main
import math


class DB :
    global conn
    global cur
    def __init__(self): # db 커넥터 생성
        self.conn = sqlite3.connect("test1.db")
        self.cur = self.conn.cursor()

    def createTableIfNotExist(self): # 맨처음 프로그램 실행 시 DB가 없다면 새로 생성함
        #evidences 테이블
        self.sql = "Select count(*) from sqlite_master Where Name = 'evidences';"
        self.cur.execute(self.sql) #evidences라는 테이블이 있는지 본다. 있으면 1 없으면 0
        self.row = self.cur.fetchone() #결과를 가져옴
        self.created = True #DB가 처음만들어지는건지
        if self.row[0] == 0 : #evidences 없으면
            print("evidences 테이블이 존재하지 않음")
            # hfs+에서 최대 파일명길이?
            # MD5 길이
            # SHA1 길이
            self.sql = "CREATE TABLE evidences(" \
                  "NUM NUMBER(100) PRIMARY KEY, NAME    CHAR(255),PATH    CHAR(1024),SIZE    NUMBER(15), MD5     CHAR(30), SHA1    CHAR(30), MODIFY_TIME NUMBER(10), ACCESS_TIME NUMBER(10), CREATE_TIME NUMBER(10), MODIFY_ATTRIBUTE_TIME NUMBER(10), BACKUP_TIME  NUMBER(10), INDEX_NUM NUMBER(10), FILE_NODE_NUM NUMBER(10), KEY_LENGTH NUMBER(10), DATA_LOCATION NUMBER(10), FOLDER NUMBER(10), TYPE NUMBER(2), BOOKMARK NUMBER(10))"
            self.cur.execute(self.sql)
            self.created = False #DB가 처음만들어졌다 (후에 if문에 사용)

        #folder 테이블
        self.sql = "Select count(*) from sqlite_master Where Name = 'folder';"
        self.cur.execute(self.sql)  # folder라는 테이블이 있는지 본다.
        self.row = self.cur.fetchone()  # 결과를 가져옴
        if self.row[0] == 0:  # evidences 존재X
            print("evidences 테이블이 존재하지 않음")
            # hfs+에서 최대 파일명길이?
            # MD5 길이
            # SHA1 길이
            self.sql = "CREATE TABLE folder(" \
                       " NUM NUMBER(10) PRIMARY KEY, NAME    CHAR(255), PATH CHAR(255),  MODIFY_TIME NUMBER(10), ACCESS_TIME NUMBER(10), CREATE_TIME NUMBER(10), MODIFY_ATTRIBUTE_TIME NUMBER(10), BACKUP_TIME  NUMBER(10), UPPER_NUM NUMBER(10), PARSED NUMBER(1), FOLDER_COUNT NUMBER(10), EVIDENCE_COUNT NUMBER(10))"
            self.cur.execute(self.sql)
            self.created = False #DB가 처음만들어졌다 (후에 if문에 사용)

        #setup

        self.sql = "Select count(*) from sqlite_master Where Name = 'setup';"
        self.cur.execute(self.sql)  # evidences라는 테이블이 있는지 본다.
        self.row = self.cur.fetchone()  # 결과를 가져옴
        if self.row[0] == 0:  # evidences 존재X
            print("setup 테이블이 존재하지 않음")
            # hfs+에서 최대 파일명길이?
            # MD5 길이
            # SHA1 길이
            self.sql = "CREATE TABLE setup(" \
                       "NAME CHAR(20), CONTENTS CHAR(255))"
            self.cur.execute(self.sql)
            self.created = False #DB가 처음만들어졌다 (후에 if문에 사용)
            item_dict = {}
            item_dict['name'] = "DISK_NUM"
            item_dict['contents'] = "0"
            self.insertDB("SETUP", item_dict)
            item_dict['name'] = "BLOCK_SIZE"
            item_dict['contents'] = "0"
            self.insertDB("SETUP", item_dict)
            item_dict['name'] = "DEFAULT_PATH"
            item_dict['contents'] = ""
            self.insertDB("SETUP", item_dict)
            item_dict['name'] = "BOOKMARK_NUM"
            item_dict['contents'] = "0"
            self.insertDB("SETUP", item_dict)
            item_dict['name'] = "LOGICALIMAGING_OUTPUT_PATH"
            item_dict['contents'] = ""
            self.insertDB("SETUP", item_dict)
            self.commit()

        #북마크
        self.sql = "Select count(*) from sqlite_master Where Name = 'bookmark';"
        self.cur.execute(self.sql)  # evidences라는 테이블이 있는지 본다.
        self.row = self.cur.fetchone()  # 결과를 가져옴
        if self.row[0] == 0:  # evidences 존재X
            print("bookmark 테이블이 존재하지 않음 ")
            self.sql = "CREATE TABLE bookmark(" \
                       "NUM NUMBER(100) PRIMARY KEY, NAME CHAR(255), EDITOR CHAR(255), CREATE_TIME NUMBER(20), EXPLANATION CHAR(255))"
            self.cur.execute(self.sql)


            #if self.created == True : #이미 DB가 만들어져있으면 DEFAULT_PATH를 불러온다 (탐색기 맨처음 시작위치)
            load_path = [] #SELECT * FROM FOLDER WHERE NAME is :dirname AND UPPER_NUM is :location

        #북마크 파일
        self.sql = "Select count(*) from sqlite_master Where Name = 'bookmark_evidences';"
        self.cur.execute(self.sql)  # evidences라는 테이블이 있는지 본다.
        self.row = self.cur.fetchone()  # 결과를 가져옴
        if self.row[0] == 0:  # evidences 존재X
            print("bookmark_evidences 테이블이 존재하지 않음 ")
            self.sql = "CREATE TABLE bookmark_evidences(" \
                       "BOOKMARK_NUM NUMBER(100), EVIDENCE_NUM NUMBER(100))"
        self.cur.execute(self.sql)

        #홈플레이트 리스트
        self.sql = "Select count(*) from sqlite_master Where Name = 'homeplate_folder';"
        self.cur.execute(self.sql)  # evidences라는 테이블이 있는지 본다.
        self.row = self.cur.fetchone()  # 결과를 가져옴
        if self.row[0] == 0:  # evidences 존재X
            print("homeplate_folder 테이블이 존재하지 않음 ")
            self.sql = "CREATE TABLE homeplate_folder(" \
                       "FOLDER_NUM NUMBER(100), LOWER_FOLDER_NUM NUMBER(100))"
            self.cur.execute(self.sql)

                #   self.sql = "SELECT * FROM SETUP"
         #   self.cur.execute(self.sql)
         #   self.conn.commit()
         #   self.row = self.cur.fetchone()
            #load_path = self.row
            #load_path = self.executeOneQuery("SELECT * FROM setup WHERE NAME is default_path")
            #if load_path != None :
            #    main.default_path = load_path[1]
            #else :
            #    print("DEFAULT_PATH 읽는 도중 에러 발생")
        #else :
        #main.readDisk()

    def insertDBMany(self, opcode, item_list):
        if opcode == "EVIDENCE" :
            self.sql = "INSERT INTO evidences (NUM, NAME, PATH, SIZE, MD5, SHA1, " \
                       "MODIFY_TIME, ACCESS_TIME, CREATE_TIME, MODIFY_ATTRIBUTE_TIME, BACKUP_TIME, INDEX_NUM, FILE_NODE_NUM, KEY_LENGTH, DATA_LOCATION, FOLDER, TYPE, BOOKMARK)" \
                       " VALUES (:num, :name, :path, :size, :md5, :sha1, :modify_time, :access_time, :create_time, :modify_attribute_time, :backup_time, :index_num, :file_node_num, :key_length, :data_location, :folder, :type, :bookmark)"

            main.printDebugMessage("sql : " + self.sql)
            self.cur.executemany(self.sql, item_list)
        if opcode == "FOLDER" :
            self.sql = "INSERT INTO FOLDER (NUM, NAME, PATH,  MODIFY_TIME, ACCESS_TIME, CREATE_TIME, MODIFY_ATTRIBUTE_TIME, BACKUP_TIME, UPPER_NUM, PARSED, FOLDER_COUNT, EVIDENCE_COUNT) VALUES (:num, :name, :path, :modify_time, :access_time, :create_time, :modify_attribute_time, :backup_time,   :upper_num, :parsed, :folder_count, :evidence_count)"
            main.printDebugMessage("sql : " + self.sql)
            self.cur.executemany(self.sql, item_list)

        if opcode == "HOMEPLATE_FOLDER" :
            self.sql = "INSERT INTO HOMEPLATE_FOLDER (FOLDER_NUM, LOWER_FOLDER_NUM) VALUES (:folder_num, :lower_folder_num)"
            main.printDebugMessage("sql : " + self.sql)
            self.cur.executemany(self.sql, item_list)

    def insertDB(self, opcode, item_dict): # insertDB("EVIDENCE", 사전정보) 이런식
        #evidence
        if opcode == "EVIDENCE" :
            self.sql = "INSERT INTO evidences (NUM, NAME, PATH, SIZE, MD5, SHA1, "\
                                        "MODIFY_TIME, ACCESS_TIME, CREATE_TIME, MODIFY_ATTRIBUTE_TIME, BACKUP_TIME, INDEX_NUM, FILE_NODE_NUM, KEY_LENGTH, DATA_LOCATION, FOLDER, BOOKMARK)" \
                                        " VALUES (:num, :name, :path, :size, :md5, :sha1, :modify_time, :access_time, :create_time, :modify_attribute_time, :backup_time, :index_num, :file_node_num, :key_length, :data_location, :folder, :bookmark)"

            main.printDebugMessage("sql : " + self.sql)
            self.cur.execute(self.sql, item_dict)

        #folder
        if opcode == "FOLDER" :
            self.sql = "INSERT INTO FOLDER (NUM, NAME, PATH, MODIFY_TIME, ACCESS_TIME, CREATE_TIME, MODIFY_ATTRIBUTE_TIME, BACKUP_TIME, UPPER_NUM, PARSED, FOLDER_COUNT, EVIDENCE_COUNT) VALUES (:num, :name, :path, :modify_time, :access_time, :create_time, :modify_attribute_time, :backup_time,  :upper_num, :parsed, :folder_count, :evidence_count)"
            main.printDebugMessage("sql : " + self.sql)
            self.cur.execute(self.sql, item_dict)

        if opcode == "FOLDER_PARSED" :
            self.sql = "UPDATE FOLDER SET PARSED = 1 WHERE NAME is :name AND PATH is :path"
            main.printDebugMessage("sql : " + self.sql)
            self.cur.execute(self.sql, item_dict)

        if opcode == "SETUP" :
            self.sql = "INSERT INTO SETUP(NAME, CONTENTS) VALUES (:name, :contents)"
            main.printDebugMessage("sql : " + self.sql)
            self.cur.execute(self.sql, item_dict)

        if opcode == "BOOKMARK" :
            self.sql = "INSERT INTO BOOKMARK(NUM, NAME, EDITOR, CREATE_TIME, EXPLANATION) VALUES (:num, :name, :editor, :create_time, :explanation)"
            main.printDebugMessage("sql : " + self.sql)
            self.cur.execute(self.sql, item_dict)

        if opcode == "BOOKMARK_EVIDENCES":
            self.sql = "Select count(*) from BOOKMARK_EVIDENCES Where BOOKMARK_NUM = :bookmark_num AND EVIDENCE_NUM = :evidence_num" #이미 bookmark_evidences있는지 탐색
            main.printDebugMessage("sql : " + self.sql)
            self.cur.execute(self.sql, item_dict)  # evidences라는 테이블이 있는지 본다.
            self.row = self.cur.fetchone()  # 결과를 가져옴

            if self.row[0] == 0 :
                self.sql = "INSERT INTO BOOKMARK_EVIDENCES(BOOKMARK_NUM, EVIDENCE_NUM) VALUES (:bookmark_num, :evidence_num)"
                main.printDebugMessage("sql : " + self.sql)
                self.cur.execute(self.sql, item_dict)

    def updateDB(self, opcode, item_dict):  # insertDB("EVIDENCE", 사전정보) 이런식
        # evidence
        if opcode == "BOOKMARK_ITEM":
            self.sql = "UPDATE evidences SET BOOKMARK = :bookmark_num WHERE NAME is :name AND PATH is :path"
            main.printDebugMessage("sql : " + self.sql)
            self.cur.execute(self.sql, item_dict)


        if opcode == "FOLDER_COUNT":
            self.sql = "UPDATE folder SET FOLDER_COUNT = :folder_count WHERE NUM is :num"
            main.printDebugMessage("sql : " + self.sql)
            self.cur.execute(self.sql, item_dict)

        if opcode == "EVIDENCE_COUNT":
            self.sql = "UPDATE folder SET EVIDENCE_COUNT = :evidence_count WHERE NUM is :num"
            main.printDebugMessage("sql : " + self.sql)
            self.cur.execute(self.sql, item_dict)

    def updateDB_setup(self, opcode, value):
        if type(value) == str :
            value = "'" + value + "'"
        self.sql = "UPDATE setup SET CONTENTS = " + value + " WHERE NAME is '" + opcode+"'"
        main.printDebugMessage("sql : " + self.sql)
        self.cur.execute(self.sql)
        self.commit()

    def selectDB_setup(self, opcode):
        self.sql = "SELECT CONTENTS FROM setup WHERE NAME = '" + opcode + "'"
        main.printDebugMessage("sql : " + self.sql)
        self.cur.execute(self.sql)
        self.row = self.cur.fetchone()
        return self.row[0]

    def deleteDB_bookmark_evidence(self, bookmark_num, evidence_num) :
        self.sql = "DELETE FROM bookmark_evidences WHERE BOOKMARK_NUM = " + str(bookmark_num) + " AND EVIDENCE_NUM = " + str(evidence_num)
        main.printDebugMessage("sql : " + self.sql)
        self.cur.execute(self.sql)


    def commit(self):

        self.conn.commit()  # 트랜잭션 처리

    def getItemList(self, location) : #탐색기에서 ls할때 DB에서 가져오는거

        self.sql = "SELECT NUM, NAME, TYPE, PATH, SIZE, MODIFY_TIME, ACCESS_TIME, CREATE_TIME, MODIFY_ATTRIBUTE_TIME, BACKUP_TIME FROM evidences WHERE FOLDER is " + str(location) # 현재 위치가 location인 증거들 가져옴
        self.cur.execute(self.sql)
        self.conn.commit()
        self.row_evidences = self.cur.fetchall()

        self.sql = "SELECT NUM, NAME, PATH, MODIFY_TIME, ACCESS_TIME, CREATE_TIME, MODIFY_ATTRIBUTE_TIME, BACKUP_TIME FROM folder WHERE UPPER_NUM is " + str(location) # 현재 위치가 location인 증거들 가져옴
        self.cur.execute(self.sql)
        self.conn.commit()
        self.row_folders = self.cur.fetchall()

        return self.row_evidences, self.row_folders

    def getItemList_homeplate(self, homeplate_folder_list):
        self.sql = "SELECT NUM, NAME, TYPE, PATH, SIZE, MODIFY_TIME, ACCESS_TIME, CREATE_TIME, MODIFY_ATTRIBUTE_TIME, BACKUP_TIME FROM evidences WHERE FOLDER = "
        self.sql += " OR FOLDER = ".join(str(tmp[0]) for tmp in homeplate_folder_list)
        main.printDebugMessage("getItemList_homeplate sql : " + self.sql)
        self.cur.execute(self.sql)

        return self.cur.fetchall()

    def getItemList_homeplate_root(self, ):
        self.sql = "SELECT NUM, NAME, TYPE, PATH, SIZE, MODIFY_TIME, ACCESS_TIME, CREATE_TIME, MODIFY_ATTRIBUTE_TIME, BACKUP_TIME FROM evidences"
        main.printDebugMessage("make sql string :" +  self.sql)
        self.cur.execute(self.sql)
        main.printDebugMessage("execute sql ")

        return self.cur.fetchall()


    def getItemList_bookmark(self, bookmark_evidence_list) :
        self.sql = "SELECT NUM, NAME, TYPE, PATH, SIZE, MODIFY_TIME, ACCESS_TIME, CREATE_TIME, MODIFY_ATTRIBUTE_TIME, BACKUP_TIME FROM EVIDENCES WHERE NUM = "
        self.sql += " OR NUM = ".join(str(tmp[1]) for tmp in bookmark_evidence_list)
        self.cur.execute(self.sql)
        main.printDebugMessage("sql : " + self.sql)

        return self.cur.fetchall()

    def getItemList_search(self, keyword) : #탐색기에서 ls할때 DB에서 가져오는거

        self.sql = "SELECT NUM, NAME, TYPE, PATH, SIZE, MODIFY_TIME, ACCESS_TIME, CREATE_TIME, MODIFY_ATTRIBUTE_TIME, BACKUP_TIME FROM evidences WHERE NAME REGEXP \"" + keyword + "\"" # 정규표현식으로 keyword포함된 evidences 가져옴
        self.cur.execute(self.sql)
        self.conn.commit()
        self.row_evidences = self.cur.fetchall()
        main.printDebugMessage("sql : " + self.sql)

        self.sql = "SELECT NUM, NAME, PATH, MODIFY_TIME, ACCESS_TIME, CREATE_TIME, MODIFY_ATTRIBUTE_TIME, BACKUP_TIME FROM folder WHERE NAME REGEXP \"" + keyword + "\""# 정규표현식으로 keyword포함된 folders 가져옴
        self.cur.execute(self.sql)
        self.conn.commit()
        self.row_folders = self.cur.fetchall()
        main.printDebugMessage("sql : " + self.sql)

        return self.row_evidences, self.row_folders

    def executeOneQueryWithDict(self, sql, item_dict): # dictionary 붙을때 SQL실행시켜주는 함수 executeOneQueryWithDict("SELECT * FROM asdas WHERE NAME IS :ASdfasdf", item_dict)
        try :
            self.sql = sql
            self.cur.execute(self.sql, item_dict)
            #self.conn.commit()
            self.row = self.cur.fetchone()

        except :
            print("DB에러 발생1")
            self.row = None

        return self.row
    def executeOneQuery(self, sql): # dictionary 안붙을떄 SQL실행시켜주는 함수 executeOneQuery("SELECT * FROM asdf WHERE NAME IS ASDF")
        try :
            main.printDebugMessage("sql : " + sql)
            self.sql = sql
            self.cur.execute(self.sql)
            #self.conn.commit()
            self.row = self.cur.fetchone()

        except :
            print("DB에러 발생1")
            self.row = None
        return self.row

    def executeOneQueryMany(self, sql) :
        try :
            main.printDebugMessage("sql : " + sql)
            self.sql = sql
            self.cur.execute(self.sql)
            #self.conn.commit()
            self.row = self.cur.fetchall()

        except :
            print("DB에러 발생2")
            self.row = None


        return self.row

#evidenceList = ["name", "path", "size", "md5", "sha1", "modify_time", "access_time", "create_time", "index"]
