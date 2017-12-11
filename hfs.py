import threading
from io import BufferedReader
import binascii
import subprocess
import io
import struct
import time
import datetime
import re
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QApplication

from Item import *
import main
from nodes import *

if main.os_mode == "WINDOWS" :
    import wmi

#need wmi, win32com module
class HFSP() :

    global f
    global signature
    global block_size
    global catalog_file
    global node_size
    global root_node
    global first_leaf_node
    global last_leaf_node

    global volume_start
    global catalog_file_location
    global dir_dict
    global file_list

    global UI

    global parse_leaf_node_progress_one_node_time
    global leaf_node_count_max
    global leaf_node_count

    global file_count

    global phy_disk_num

    global folder_list
    global evidence_list
    global homplate_folder_list

    global folder_count_dict
    global evidence_count_dict

    global root_folder_path

    

    def parsingdata22(self,location):
        print("parsingdata22")
        self.iter_num = 0
        self.block_size = 4096
        self.f.seek(location - location % self.block_size, 0)  # 계속 에러나길래 blocksize단위로 읽게 약간 뒤로 감
        fr = self.f.read(self.block_size)
        start_location = location % self.block_size
        extent_discriptor_list = []
        total_block = struct.unpack_from(">I", fr, start_location + 0xC)[0]

        i_block = 0  # carving하고있는 block의 위치
        i_count = 0  # block위치를 센 횟수
        while i_block < total_block:
            ed = ExtentDiscriptor()

            ed.start_block = struct.unpack_from(">I", fr, start_location + 0x10 + i_count * 4)[0]
            ed.block_count = struct.unpack_from(">I", fr, start_location + 0x14 + i_count * 4)[0]

            i_block += ed.block_count
            extent_discriptor_list.append(ed)

        yield total_block

        for i in extent_discriptor_list:
            self.f.seek((self.volume_start + i.start_block * self.block_size), 0)
            for j in range((i.block_count)):
                #yield binascii.hexlify(self.f.read(self.block_size)).decode("ISO-8859-1")
                yield self.f.read(self.block_size)
        print("done")

    def __init__(self, phy_disk_num):
        self.phy_disk_num = phy_disk_num
        self.volume_start = 0xC805000  # 시그니쳐 위치 기록
        self.file_count = 1
        try :
            if main.os_mode == "WINDOWS" :
                self.f = open("\\\\.\\PhysicalDrive" + str(self.phy_disk_num), "rb")
            elif main.os_mode == "MACOS" :
                self.f = open("/dev/disk" + str(self.phy_disk_num), "rb" )
        except :
            print("Disk Open Error")
        #self.parsingdata22(3433228784)#,"testfile")
    def beginParsing(self, UI):
        self.UI = UI
        self.node_list = []
        self.dir_dict = {}
        self.file_list = []
        self.folder_list = []
        self.evidence_list = []
        self.folder_count_dict = {}
        self.evidence_count_dict = {}
        self.homplate_folder_list = []
        self.getPhysicalDrives()
        #시그니처 위치 찾는 부분 추후 추가 예정
        self.f.seek(0xC805400, 0) # initalize 0xC805400
        fr = self.f.read(4096) #block size는 아직 모르지만, 일단 4096 읽기
        self.signature = struct.unpack_from(">I", fr, 0x0 + 0)[0]
        if self.signature != 0x482B0004 :
            print("It is not HFS+ FileSystem, " + str(self.signature) + " " + str(self.volume_start))
            exit(-1)
        else :
            print("It is HFS+ FileSysem")
        self.block_size = struct.unpack_from(">I", fr, 0x0 + 0x28)[0]
        main.db1.updateDB_setup("BLOCK_SIZE", str(self.block_size))
        self.catalog_file = struct.unpack_from(">I", fr, 0x0 + 0x120)[0]
        main.printDebugMessage("signature : " + str(self.signature) + " block_size : " + str(self.block_size) + " catalog_file : " + str(self.catalog_file))
        self.catalog_file_location = self.volume_start + self.block_size * self.catalog_file #카탈로그파일 위치 기록
        self.make_tree(UI)

        #self.carvingData(f, 0x14e80702, "asdf1.jpg")f
        #self.carvingData(f, 0x14e8093e, "asdf2.jpg")
    def make_tree(self, UI):
        self.f.seek(self.catalog_file_location, 0)
        fr = self.f.read(self.block_size)
        self.node_size = struct.unpack_from(">H", fr, 0x0 + 0x20)[0]
        self.root_node = struct.unpack_from(">I", fr, 0x0 + 0x10)[0]
        self.first_leaf_node = struct.unpack_from(">I", fr, 0x0 + 0x18)[0]
        self.last_leaf_node = struct.unpack_from(">I", fr, 0x0 + 0x1C)[0]
        main.printDebugMessage("ns : " + str(self.node_size) + " rn : " + str(self.root_node) + " fl : " + str(self.first_leaf_node))
#        self.parse_root_node()

        self.leaf_node_count_max = self.first_leaf_node - self.last_leaf_node #UI ProgressBar
        self.leaf_node_count = 0
        self.parse_leaf_node_progress_one_node_time = 0
        flink = self.first_leaf_node # 재귀형식을 갖기위하여 flink를 first_leaf_node로 설정해놓음
        start_time = time.time()
        t = threading.Thread(target=self.parse_leaf_node_progress_UI, args=(UI,start_time))
        t.start()

        while flink != 0 : #flink가 더 이상 없을 때 까지
            before_time = time.time()
            flink = self.parse_leaf_node(flink)
            self.parse_leaf_node_progress_one_node_time = (self.parse_leaf_node_progress_one_node_time *
                                        self.leaf_node_count + time.time() - before_time) / (self.leaf_node_count + 1)  #계속하여 시간 업데이트

            UI.progressBar.setProperty("value", str(int((self.leaf_node_count / self.leaf_node_count_max) * 100))) # UI Progress bar
            QApplication.processEvents()
            self.leaf_node_count += 1

        #db에 넣기

        main.db1.insertDBMany("FOLDER", self.folder_list)
        main.db1.insertDBMany("EVIDENCE", self.evidence_list)

        #홈플레이트 트리구조 저장
        main.db1.insertDBMany("HOMEPLATE_FOLDER", self.homplate_folder_list)

        #폴더갯수, 파일갯수저장
        for folder_count_tmp in self.folder_count_dict.items() :
            item_dict = {}
            item_dict["num"] = folder_count_tmp[0] #어떤 폴더인지
            item_dict["folder_count"] = folder_count_tmp[1] #그 폴더 안의 폴더갯수
            main.db1.updateDB("FOLDER_COUNT", item_dict)

        for evidence_count_tmp in self.evidence_count_dict.items():
            item_dict = {}
            item_dict["num"] = evidence_count_tmp[0]  # 어떤 폴더인지
            item_dict["evidence_count"] = evidence_count_tmp[1]  # 그 폴더 안의 폴더갯수
            main.db1.updateDB("EVIDENCE_COUNT", item_dict)


        main.db1.commit()
        main.printDebugMessage("dicts > ")
        for a in self.dir_dict.keys() :
            main.printDebugMessage("이름 : " + str(self.dir_dict[a].name) + " object_id : " + str(self.dir_dict[a].object_id) + " parent_node : "
                                   + str(self.dir_dict[a].parent_node) + "경로 : " + str(self.dir_dict[a].path))
            #for b in self.file_list :
#                print(str(a) + "and " + str(b.parent_node))
#                if int(a) == int(b.parent_node) :
#                    print(str(b.name)+ " ",end="")
#            print("")

        return 0

    def parse_leaf_node_progress_UI(self, UI, start_time):
        while(True) :
            elapsed_time = time.time() - start_time
            expected_time = time.time() - start_time + (self.leaf_node_count_max - self.leaf_node_count) * self.parse_leaf_node_progress_one_node_time
            #UI.expectedTime_label.setText("예상시간 : ( " + str(elapsed_time.min) + " : " + str(elapsed_time.seconds)
            #                              + " / " +  str(expected_time.min) + " : " + str(expected_time.seconds) + " )")
            UI.expectedTime_label.setText("예상시간 : ( " + str(int(elapsed_time / 60)) + " : " + str(int(elapsed_time % 60))
                                          + " / " +  str(int(expected_time / 60)) + " : " + str(int(expected_time % 60)) + " )")
            QApplication.processEvents()
            time.sleep(0.5)

            if self.leaf_node_count == self.leaf_node_count_max :
                break


    def parse_root_node(self):
        self.f.seek(self.catalog_file_location + self.node_size * self.root_node,0) #f pointer 해당 노드위치로 변경
        fr = self.f.read(self.block_size) #block size만큼 읽어옴
        parse_location = 0xE #레코드 위치 쭉 따라가기 위한 변수, 0xE부터 첫 번째 레코드 시작
        record_num = struct.unpack_from(">H", fr, 0x0 + 0xA)[0]
        for i in range(record_num) :
            n = RootNode()

            key_length = struct.unpack_from(">H", fr, parse_location + 0x0)[0] + 4#레코드의 길이
            main.printDebugMessage("key_length : " + str(key_length))
            name_length = struct.unpack_from(">H", fr, parse_location + 0x6)[0] #이름길이 파싱

            n.parent_node_id = struct.unpack_from(">I", fr, parse_location + 0x2)[0] #부모노드 id 파싱
            n.name = ""
            for i in range(name_length) :
                n.name += chr(struct.unpack_from(">"+str(name_length)+"H", fr, parse_location + 0x8 + i * 2)[0]) #이름 파싱
            main.printDebugMessage("n.name : " + n.name)

            n.child_node_id = struct.unpack_from(">I", fr, parse_location + 0x8 + name_length * 2)[0]

            parse_location += key_length #다음 레코드 파싱을 위해 현재 위치 기록해둠

            #self.node_list.append(n)
            main.printDebugMessage("node added")
        main.printDebugMessage("parse_rootnode_end")

    def parse_leaf_node(self, node_num) : #node_num에 해당하는 node를 한번 파싱해줌
        """

        :rtype: int
        """
        self.f.seek(self.catalog_file_location + self.node_size * node_num, 0) #f pointer 해당 노드위치로 변경
        main.printDebugMessage("location : " + str(self.catalog_file_location + self.node_size * node_num))
        fr = self.f.read(self.block_size * 2) #block size * 2만큼 읽어옴
        flink = struct.unpack_from(">I", fr, 0x0 + 0x0)[0]
        blink = struct.unpack_from(">I", fr, 0x0 + 0x4)[0]
        type = struct.unpack_from(">B", fr, 0x0 + 0x8)[0]
        height = struct.unpack_from(">B", fr, 0x0 + 0x9)[0]
        record_num = struct.unpack_from(">H", fr, 0x0 + 0xA)[0]
        main.printDebugMessage("record_num : " + str(record_num) + " " + str(node_num))
        # 2 byte reserved
        for i in range(record_num):
            oi = ObjectItem() #파일 및 폴더
            record_location = struct.unpack_from(">H", fr, self.block_size*2  - (i + 1) * 2)[0]  # 2000 - (n + 1) * 2
            main.printDebugMessage("i : " + str(i) + " record_location : " + str(record_location) + " block size : " + str(self.block_size))
            oi.key_length = struct.unpack_from(">H", fr, record_location)[0]
            oi.parent_node = struct.unpack_from(">I", fr, record_location + 0x2)[0]
            name_length = struct.unpack_from(">H", fr, record_location + 0x6)[0]  # 이름길이 파싱
            oi.name = "" #파일 및 폴더의 이름 구하기
            for i in range(name_length):
                oi.name += chr(
                    struct.unpack_from(">H", fr, record_location + 0x8 + i * 2)[0])  # 이름 파싱
            oi.type = struct.unpack_from(">H", fr, record_location + 0x8 + name_length * 2)[0] # 1 폴더 2 파일
            if int(oi.type) == 3 or int(oi.type) == 4 :
                continue
            oi.object_id = struct.unpack_from(">I", fr, record_location + 0x8 + name_length * 2 + 0x8)[0]
            oi.create_time = struct.unpack_from(">I", fr, record_location + 0x8 + name_length * 2 + 0xC)[0]
            oi.modify_time = struct.unpack_from(">I", fr, record_location + 0x8 + name_length * 2 + 0x10)[0]
            oi.modify_attribute_time = struct.unpack_from(">I", fr, record_location + 0x8 + name_length * 2 + 0x14)[0]
            oi.access_time = struct.unpack_from(">I", fr, record_location + 0x8 + name_length * 2 + 0x18)[0]
            oi.backup_time = struct.unpack_from(">I", fr, record_location + 0x8 + name_length * 2 + 0x1C)[0]
            oi.permission = 0
            oi.user_inform = 0
            oi.finder_inform = 0
            oi.text_encoding = struct.unpack_from(">I", fr, record_location + 0x8 + name_length * 2 + 0x4C)[0]
            #reserved 4byte
            oi.data_location = self.catalog_file_location + self.node_size * node_num + record_location + 0x8 + name_length * 2 + 0x58
            #print(str(struct.unpack_from(">Q", fr,  record_location + 0x8 + name_length * 2 + 0x58)[0]) + " blocksize : " + str(self.block_size))
            #if oi.type == 2 : #이 object가 파일이면
            #    next_record_location = struct.unpack_from(">B", fr, self.block_size - (i + 2) * 2)[0]  # 2000 - (n + 1) * 2
            #    for j in range((next_record_location - record_location - 0x8 - name_length * 2 - 0x4E) / 4) : # start_block, block_count 몇 번 나올지 예상
            #        oi.start_block = struct.unpack_from(">I", fr, record_location + 0x8 + name_length * 2 + 0x52)[0]
            #        oi.block_count = struct.unpack_from(">I", fr, record_location + 0x8 + name_length * 2 + 0x56)[0]
                #

            main.printDebugMessage("n.name : " + oi.name + " parent_node : " + str(oi.parent_node) + " type : " + str(oi.type) + " name_length : " + str(name_length))
            if oi.type == 1 : #이 object가 폴더면
                self.dir_dict[oi.object_id] = oi
                if oi.object_id == 2 : # if root
                    self.root_folder_path = "/" + oi.name + "/"
                object_id_temp = oi.parent_node #경로명을 알기위한 임시변수, 재귀형식을 갖기 위해 oi.parent_node로 설정
                object_id_temp2 = oi.object_id #홈플레이트 트리구조 만들기 위한 임시변수, 재귀형식 갖기 위해 oi.parent_node로 설정
                folder_path_parsed = 0 #경로가 파싱되었는지
                #print("object_id_temp : " + str(folder_path_parsed) + " folder_path_parsed : " + str(folder_path_parsed))
                while object_id_temp != 1 and folder_path_parsed == 0 : #경로명 구하기
                    object_id_temp, string, folder_path_parsed = self.get_parent_name(object_id_temp)
                    if object_id_temp == -1 :
                        break
                    oi.path = string + "/" + oi.path
                #oi.path = oi.path + "/"# 끝 마무리 / 붙여주기
                #oi.path = oi.path[:-1]
                if oi.path == "" : # 경로가 공백이면 / 붙여줌 (root)
                    oi.path = "/"
                oi.path_parsed = 1

                item_dict_tmp = {}
                item_dict_tmp['folder_num'] = str(object_id_temp2)
                item_dict_tmp['lower_folder_num'] = str(oi.object_id)
                self.homplate_folder_list.append(item_dict_tmp)
                while object_id_temp2 != 1 : #홈플레이트 트리구조
                    object_id_temp2 = self.get_homeplate_tree(object_id_temp2)
                    if object_id_temp2 == -1 :
                        break
                    item_dict = {}
                    item_dict['folder_num'] = str(object_id_temp2)
                    item_dict['lower_folder_num'] = str(oi.object_id)
                    #print("folder_num : " + item_dict['folder_num'] + " lower_folder_num : " + item_dict['lower_folder_num'])
                    self.homplate_folder_list.append(item_dict)
                item_dict = {}
                item_dict['num'] = oi.object_id
                item_dict['name'] = oi.name
                item_dict['path'] = oi.path
                item_dict['modify_time'] = oi.modify_time
                item_dict['access_time'] = oi.access_time
                item_dict['create_time'] = oi.create_time
                item_dict['modify_attribute_time'] = oi.modify_attribute_time
                item_dict['backup_time'] = oi.backup_time
                item_dict['upper_num'] = oi.parent_node  # db 업데이트를 위한 사전
                item_dict['parsed'] = 1
                item_dict['folder_count'] = 0
                item_dict['evidence_count'] = 0
                #main.db1.insertDB("FOLDER", item_dict)  # db에 저장
                self.folder_list.append(item_dict) #리스트에 저장

                self.folder_count_dict[oi.object_id] = 0 #폴더갯수 세기
                self.evidence_count_dict[oi.object_id] = 0  # 폴더갯수 세기
                if oi.object_id != 2 and oi.parent_node in self.folder_count_dict:
                    self.folder_count_dict[oi.parent_node] += 1 #상위폴더의 폴더갯수 +=1
            else : #이 object가 파일이면

                #데이터 먼저 추출
                self.file_list.append(oi)

                object_id_temp = oi.parent_node  # 경로명을 알기위한 임시변수, 재귀형식을 갖기 위해 oi.parent_node로 설정
                folder_path_parsed = 0  # 경로가 파싱되었는지
                #print(
                   # "object_id_temp : " + str(folder_path_parsed) + " folder_path_parsed : " + str(folder_path_parsed))
                while object_id_temp != 1 and folder_path_parsed == 0:  # 경로명 구하기
                    object_id_temp, string, folder_path_parsed = self.get_parent_name(object_id_temp)
                    if object_id_temp == -1 :
                        break
                    oi.path = string + "/" + oi.path
                # oi.path = oi.path + "/"# 끝 마무리 / 붙여주기
                # oi.path = oi.path[:-1]
                if oi.path == "":  # 경로가 공백이면 / 붙여줌 (root)
                    oi.path = "/"
                oi.path_parsed = 1


                while(True) :
                    regex = re.compile('(\.otf)|(\.pdf)|(\.txt)|(\.ttxt)|(\.xlsx)|(\.ppt)|(\.pptx)|(\.hwp)')
                    condition1 = regex.search(oi.name) is not None #포함

                    regex = re.compile('(' + self.root_folder_path.replace('/', '\/') + 'Users)')
                    #print('(' + self.root_folder_path.replace('/', '\/') + 'Users)')
                    #regex = re.compile('(/)')
                    condition2 = regex.search(oi.path) is not None #포함
                    regex = re.compile('(' + self.root_folder_path.replace('/', '\/') +'Users\/(.*?)\/Library)')
                    condition3 = regex.search(oi.path) is None # 제외
                    if condition1 and condition2 and condition3 == True:
                        oi.keyfile_type = 1
                        break
                    regex = re.compile('(\.zip)|(\.tar)|(\.tar\.gz)|(\.alz)|(\.gz)|(\.7z)')
                    condition1 = regex.search(oi.name) is not None
                    if condition1 and condition2 and condition3  == True:
                        oi.keyfile_type = 2
                        break
                    regex = re.compile('(\.jpg)|(\.jpeg)|(\.png)|(\.icns)|(\.thm)|(\.aae)|(\.itc)|(\.itc2)|(\.pict)|(\.pictclipping)')
                    condition1 = regex.search(oi.name) is not None
                    if condition1 and condition2 and condition3 ==True:
                        oi.keyfile_type = 3
                        break
                    regex = re.compile('(\.snd)|(\.song)|(\.avi)|(\.mp4)|(\.mp3)')
                    condition1 = regex.search(oi.name) is not None
                    if condition1 and condition2 and condition3 == True:
                        oi.keyfile_type = 4
                        break


                    regex = re.compile('(\.plist)')
                    condition1 = regex.search(oi.name) is not None
                    if condition1 and condition2 == True:
                        oi.keyfile_type = 5
                        break
                    regex = re.compile('(\/Library\/Safari\/)|(/Library/Application Support/Firefox/Profiles/*.default/places.sqlite)|(\/Library\/Application \\ Support\/com.operasoftware.Opera/history)')
                    condition1 = regex.search(oi.path) is not None
                    if condition1 == True:
                        oi.keyfile_type = 6
                        break

                    oi.keyfile_type = 0
                    break
                oi.size = int(struct.unpack_from(">Q", fr, record_location + 0x8 + name_length * 2 + 0x58)[0]) #파일 size
                #print(str(struct.unpack_from(">Q", fr, record_location + 0x8 + name_length * 2 + 0x58)[0]) + " block size : " + str(self.block_size))
                file_inform = {}
                file_inform['num'] = self.file_count
                main.printDebugMessage("parsing NAME")
                file_inform['name'] = oi.name  # 파일이름 파싱
                main.printDebugMessage("parsing PATH")
                file_inform['path'] = oi.path  # 파일 path 파싱
                main.printDebugMessage("parsing SIZE")
                file_inform['size'] = oi.size
                # file_inform['size'] = 0
                main.printDebugMessage("parsing MD5")
                #file_inform['md5'] = file_hash.md5_for_largefile(path + "\\" + file_inform['name'], 4096)
                file_inform['md5'] = 0  # 일딴뺐음
                main.printDebugMessage("parsing SHA1")
                #file_inform['sha1'] = file_hash.sha1_for_largefile(path + "\\" + file_inform['name'], 4096)
                file_inform['sha1'] = 0  # 속도떄문에 일딴뺐음
                main.printDebugMessage("parsing MAC")
                file_inform['modify_time'] = oi.modify_time
                file_inform['access_time'] = oi.access_time
                file_inform['create_time'] = oi.create_time
                file_inform['modify_attribute_time'] = oi.modify_attribute_time
                file_inform['backup_time'] = oi.backup_time
                file_inform['index_num'] = 0  # 나중에 중복처리하는부분
                file_inform['file_node_num'] = oi.object_id
                file_inform['key_length'] = oi.key_length
                file_inform['folder'] = oi.parent_node
                file_inform['type'] = oi.keyfile_type
                file_inform['data_location'] = oi.data_location
                file_inform['parsed'] = 1
                file_inform['bookmark'] = 0
                # item_tuple = tuple(file_inform.values()) # db 업데이트를위한 튜플화

                #main.db1.insertDB("EVIDENCE", file_inform)  # db에 저장
                self.evidence_list.append(file_inform)  # 리스트에 저장

                self.file_count += 1 #파일갯수 카운트
                if oi.parent_node in self.evidence_count_dict :
                    self.evidence_count_dict[oi.parent_node] += 1
            main.printDebugMessage("node added")
        return flink

    def get_parent_name(self, folder_id):
        try :
            if self.dir_dict[folder_id].path_parsed == 0  :
                #print("parse, folder_id : " + str(folder_id) + " name : " + str(self.dir_dict[folder_id].name))
                return self.dir_dict[folder_id].parent_node, self.dir_dict[folder_id].name, 0
            else :
                #print("parse end , folder_id : " + str(folder_id) + " name : " + str(self.dir_dict[folder_id].name) + " path : " + str(self.dir_dict[folder_id].path))
                return 0, self.dir_dict[folder_id].path  + self.dir_dict[folder_id].name, 1 # path_parsed 1이면 경로파싱 끝
        except :
            return -1, 0, 0
    def get_homeplate_tree(self, folder_id):
        try :
            return self.dir_dict[folder_id].parent_node
        except :
            return -1

    def parsingData(self, location, name, size):
        self.block_size = 4096
        self.f.seek(location - location % self.block_size, 0)  # 계속 에러나길래 blocksize단위로 읽게 약간 뒤로 감
        fr = self.f.read(self.block_size)
        fw = open(name, "wb")
        start_location = location % self.block_size
        extent_discriptor_list = []
        total_block = struct.unpack_from(">I", fr, start_location + 0xC)[0]
        #        main.printDebugMessage("carving total_block : " + str(total_block))
        i_block = 0  # carving하고있는 block의 위치
        i_count = 0  # block위치를 센 횟수
        while i_block < total_block:
            ed = ExtentDiscriptor()

            ed.start_block = struct.unpack_from(">I", fr, start_location + 0x10 + i_count * 8)[0]
            ed.block_count = struct.unpack_from(">I", fr, start_location + 0x14 + i_count * 8)[0]
            if ed.block_count == 0 :
                break
            i_count += 1
            i_block += ed.block_count
            extent_discriptor_list.append(ed)
            main.printDebugMessage("block : " + str(i_block) + " start_block : " + str(ed.start_block) + " block_count : " + str(ed.block_count))

        test_index = 0
        for i in extent_discriptor_list:
            for j in range((i.block_count)):
                test_index = test_index + 1
        test_index = test_index - 1

        count = 0
        for i in extent_discriptor_list:
            self.f.seek((self.volume_start + i.start_block * self.block_size), 0)
            for j in range((i.block_count)):
                if (test_index == count):
                    fw.write(self.f.read(size % self.block_size))
                    break
                fw.write(self.f.read(self.block_size))
                count = count + 1
        fw.close()

    def parsingMetadata(self, location, name):
        self.block_size = 4096
        self.f.seek(location - location % self.block_size, 0) #계속 에러나길래 blocksize단위로 읽게 약간 뒤로 감
        fr = self.f.read(self.block_size)
        fw = open(name + ".mzmd",  "wb")
        start_location = location % self.block_size
        name_len = len(name)

        main.printDebugMessage("location : " + str(location) + " name_len : " + str(name_len))
        i = 0
        while i < 96 + name_len * 2 :
            fw.write(struct.unpack_from("c", fr, start_location + i)[0])
            i += 1
        fw.close()


    def binarytofilehandler(self,location,size):
        self.block_size = 4096
        self.f.seek(location - location % self.block_size, 0)  # 계속 에러나길래 blocksize단위로 읽게 약간 뒤로 감
        fr = self.f.read(self.block_size)
        start_location = location % self.block_size
        extent_discriptor_list = []
        total_block = struct.unpack_from(">I", fr, start_location + 0xC)[0]

        i_block = 0  # carving하고있는 block의 위치
        i_count = 0  # block위치를 센 횟수
        while i_block < total_block:
            ed = ExtentDiscriptor()

            ed.start_block = struct.unpack_from(">I", fr, start_location + 0x10 + i_count * 8)[0]
            ed.block_count = struct.unpack_from(">I", fr, start_location + 0x14 + i_count * 8)[0]
            if ed.block_count == 0 :
                break
            i_count += 1
            i_block += ed.block_count
            extent_discriptor_list.append(ed)

        str_return = b""
        for i in extent_discriptor_list:
            self.f.seek((self.volume_start + i.start_block * self.block_size), 0)
            for j in range((i.block_count)):
                str_return += self.f.read(self.block_size)
        print("done")

        return str_return

    def binarytofile_maker(self,location,size):
        print("done?1")
        return io.BytesIO(self.binarytofilehandler(location,size))

    def getPhysicalDrives(self):
        physicalDrivesList = []
        if main.os_mode == "WINDOWS" :
            w = wmi.WMI()
            for drive in w.Win32_DiskDrive() :
                physicalDrivesList.append(drive.Model + "   " + drive.DeviceID + "  " + drive.SIZE)
        elif main.os_mode == "MACOS" :
            cmd_result = subprocess.check_output('diskutil list | grep 0:', shell=True, universal_newlines=True)
            physicalDrivesList = cmd_result.splitlines()
            main.printDebugMessage(cmd_result.splitlines())
        return physicalDrivesList


    def signaturehandler(self,location,hoffset,foffset , size):

        self.block_size = 4096

        h_flag = 0
        f_flag = 0
        header_offset = 0
        footer_offset = 0

        if(hoffset != "none"):
            h_flag = 1
            header_offset = 0
            if (int(hoffset) > self.block_size):
                header_read = int(int(hoffset) / self.block_size)
        if(foffset != "none"):
            f_flag = 1
            footer_offset = 0
            if (int(foffset) > self.block_size):
                footer_offset = int(int(foffset) / self.block_size)
        main.printDebugMessage("footer offset was : " + str(footer_offset))


        self.f.seek(location - location % self.block_size, 0)  # 계속 에러나길래 blocksize단위로 읽게 약간 뒤로 감
        if location == 3432911502 :
            print("1")
        fr = self.f.read(self.block_size)
        if location == 3432911502 :
            print("1")
        start_location = location % self.block_size
        if location == 3432911502 :
            print("1")
        extent_discriptor_list = []
        if location == 3432911502 :
            print("1")
        total_block = struct.unpack_from(">I", fr, start_location + 0xC)[0]
        if location == 3432911502 :
            print("1")

        i_block = 0  # carving하고있는 block의 위치
        i_count = 0  # block위치를 센 횟수

        while i_block < total_block:
            ed = ExtentDiscriptor()
            #print("i_block : " + str(i_block) + " total_block : " + str(total_block))
            try :
                ed.start_block = struct.unpack_from(">I", fr, start_location + 0x10 + i_count * 4)[0]
                ed.block_count = struct.unpack_from(">I", fr, start_location + 0x14 + i_count * 4)[0]
                if i_block + ed.block_count > total_block :
                    break
                i_count += 1
                i_block += ed.block_count
                extent_discriptor_list.append(ed)
                #ㄴㅁㅇㄹㄴㅁㅇㄹㄴㅇㅁㄻㄴㅇㄹㄴㅇㅁㄹㄴㅁㅇㄹㄴㅁㅇㄻㄴㅇ db파일 block_count 수정
                if location == 3432911502:
                    print("i_block : " + str(i_block) + " total_block : " + str(total_block) + " location : " + str(location))
            except :
                break

        index = 0

        test_index = 0
        for i in extent_discriptor_list:
            for j in range((i.block_count)):
                test_index = test_index+1
        test_index = test_index - 1

        header_str_return = b""
        footer_str_return = b""

        for i in extent_discriptor_list:
            self.f.seek((self.volume_start + i.start_block * self.block_size), 0)
            for j in range((i.block_count)):
                # print("_____________________")
                # print("idex is " , index)
                # print(binascii.hexlify(self.f.read(self.block_size).rstrip(b"\x00")).decode("ISO-8859-1"))#binascii.hexlify(self.f.read(self.block_size)).decode("ISO-8859-1"))
                if(index == test_index):
                    result = self.f.read(size % self.block_size)
                else:
                    result = self.f.read(self.block_size)
                if(h_flag == 1):
                    if(header_offset >= index):
                        header_str_return = header_str_return + result
                        #print("header")
                        #print(binascii.hexlify(header_str_return).decode("ISO-8859-1"))
                if(f_flag == 1):
                    if(test_index - footer_offset <= index):
                        #print("what i read index was :" , index , "test index was : " , test_index - footer_offset)
                        footer_str_return = footer_str_return + result
                        #print(binascii.hexlify(footer_str_return).decode("ISO-8859-1"))
                index = index + 1

        main.printDebugMessage("done" + " index number is : " + str(index))
        result111 = {"h_offset_block": header_str_return, "f_offset_block" : footer_str_return}
        return result111
        #return

    def signature_maker(self,location,hoffset,foffset , size):
        main.printDebugMessage("done?1")
        return self.signaturehandler(location , hoffset , foffset , size)



#구해야하는 것
#루트노드에서 하위노드들 배열로 return해주는 함수
#리프노드 넘버 넣으면 디렉토리,폴더 파싱해오는 함수
#디렉토리, 폴더
