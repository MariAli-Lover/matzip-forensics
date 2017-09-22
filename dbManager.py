import main
import Item
import sqlite3


class db :
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
                  "NAME    CHAR(255),PATH    CHAR(1024),SIZE    NUMBER(15), MD5     CHAR(30), SHA1    CHAR(30), MODIFY_TIME CHAR(110), ACCESS_TIME CHAR(110), CREATE_TIME CHAR(110), INDEX_NUM NUMBER(10), FOLDER NUMBER(10))"
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
                       " NUM NUMBER(10), NAME    CHAR(255), PATH CHAR(255), UPPER_NUM NUMBER(10))"
            self.cur.execute(self.sql)
            self.created = False #DB가 처음만들어졌다 (후에 if문에 사용)

        #setup

        # folder 테이블
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


        if self.created == True : #이미 DB가 만들어져있으면 DEFAULT_PATH를 불러온다 (탐색기 맨처음 시작위치)
            load_path = [] #SELECT * FROM FOLDER WHERE NAME is :dirname AND UPPER_NUM is :location
            self.sql = "SELECT * FROM SETUP"
            self.cur.execute(self.sql)
            self.conn.commit()
            self.row = self.cur.fetchone()
            load_path = self.row
            #load_path = self.executeOneQuery("SELECT * FROM setup WHERE NAME is default_path")
            if load_path != None :
                main.default_path = load_path[1]
            else :
                print("DEFAULT_PATH 읽는 도중 에러 발생")
        else :
            main.readDisk()


    def updateDB(self, opcode, item_dict): # updateDB("EVIDENCE", 사전정보) 이런식
        #evidence
        if opcode == "EVIDENCE" :
            self.sql = "INSERT INTO evidences (NAME, PATH, SIZE, MD5, SHA1, "\
                                        "MODIFY_TIME, ACCESS_TIME, CREATE_TIME, INDEX_NUM, FOLDER)" \
                                        " VALUES (:name, :path, :size, :md5, :sha1, :modify_time, :access_time, :create_time, :index_num, :folder)"

            main.printDebugMessage("sql : " + self.sql)
            self.cur.execute(self.sql, item_dict)
            self.conn.commit() # 트랜잭션 처리

        #folder
        if opcode == "FOLDER" :
            self.sql = "INSERT INTO FOLDER (NUM, NAME, PATH, UPPER_NUM) VALUES (:num, :name, :path, :upper_num)"
            main.printDebugMessage("sql : " + self.sql)
            self.cur.execute(self.sql, item_dict)
            self.conn.commit() # 트랜잭션 처리

        if opcode == "SETUP" :
            self.sql = "INSERT INTO SETUP(NAME, CONTENTS) VALUES (:name, :contents)"
            main.printDebugMessage("sql : " + self.sql)
            self.cur.execute(self.sql, item_dict)
            self.conn.commit()  # 트랜잭션 처리

    def getItemList(self, location) : #탐색기에서 ls할때 DB에서 가져오는거
        self.sql = "SELECT * FROM folder WHERE UPPER_NUM is " + str(location) # 상위폴더가 location인 폴더 가져옴
        self.cur.execute(self.sql)
        self.conn.commit()
        self.row_folder = self.cur.fetchall()

        self.sql = "SELECT * FROM evidences WHERE FOLDER is " + str(location) # 현재 위치가 location인 증거들 가져옴
        self.cur.execute(self.sql)
        self.conn.commit()
        self.row_evidences = self.cur.fetchall()
        return (self.row_folder, self.row_evidences)

    def executeOneQueryWithDict(self, sql, item_dict): # dictionary 붙을때 SQL실행시켜주는 함수 executeOneQueryWithDict("SELECT * FROM asdas WHERE NAME IS :ASdfasdf", item_dict)
        try :
            self.sql = sql
            self.cur.execute(self.sql, item_dict)
            self.conn.commit()
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
            self.conn.commit()
            self.row = self.cur.fetchone()

        except :
            print("DB에러 발생2")
            self.row = None

        return self.row
#evidenceList = ["name", "path", "size", "md5", "sha1", "modify_time", "access_time", "create_time", "index"]
