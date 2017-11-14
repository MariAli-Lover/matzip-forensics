import wmi
import io
import struct

from Item import *
import globals as gl
from debug import *
from nodes import *


# need wmi, win32com module
class HFSP():
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

    def __init__(self, phy_disk_num, UI):
        self.UI = UI
        self.node_list = []
        self.dir_dict = {}
        self.file_list = []
        self.volume_start = 0xC805000  # 시그니쳐 위치 기록
        self.getPhysicalDrives()
        try:
            f = open("\\\\.\\PhysicalDrive" + str(phy_disk_num), "rb")
        except:
            print("Disk Open Error")
        # 시그니처 위치 찾는 부분 추후 추가 예정
        f.seek(0xC805400, 0)  # initalize 0xC805400
        fr = f.read(4096)  # block size는 아직 모르지만, 일단 4096 읽기
        self.signature = struct.unpack_from(">I", fr, 0x0 + 0)[0]
        if self.signature != 0x482B0004:
            print("It is not HFS+ FileSystem, " + str(self.signature) + " " + str(self.volume_start))
            exit(-1)
        else:
            # self.carvingData(f, 0x14e80702, "asdf1.jpg")f
            print("It is HFS+ FileSysem")
        self.block_size = struct.unpack_from(">I", fr, 0x0 + 0x28)[0]
        self.catalog_file = struct.unpack_from(">I", fr, 0x0 + 0x120)[0]
        dbgmsg(
            "signature : " + str(self.signature) + " block_size : " + str(self.block_size) + " catalog_file : " + str(
                self.catalog_file))
        self.catalog_file_location = self.volume_start + self.block_size * self.catalog_file  # 카탈로그파일 위치 기록
        self.make_tree(f, UI)

        # self.carvingData(f, 0x14e8093e, "asdf2.jpg")

    def make_tree(self, f, UI):
        f.seek(self.catalog_file_location, 0)
        fr = f.read(self.block_size)
        self.node_size = struct.unpack_from(">H", fr, 0x0 + 0x20)[0]
        self.root_node = struct.unpack_from(">I", fr, 0x0 + 0x10)[0]
        self.first_leaf_node = struct.unpack_from(">I", fr, 0x0 + 0x18)[0]
        self.last_leaf_node = struct.unpack_from(">I", fr, 0x0 + 0x1C)[0]
        dbgmsg("ns : " + str(self.node_size) + " rn : " + str(self.root_node) + " fl : " + str(self.first_leaf_node))
        # self.parse_root_node(f)

        leaf_node_count_max = self.first_leaf_node - self.last_leaf_node  # UI ProgressBar
        leaf_node_count = 0
        flink = self.first_leaf_node  # 재귀형식을 갖기위하여 flink를 first_leaf_node로 설정해놓음
        while flink != 0:  # flink가 더 이상 없을 때 까지
            flink = self.parse_leaf_node(f, flink)
            UI.progressBar.setProperty("value", str(int((leaf_node_count / leaf_node_count_max) * 100)))
            leaf_node_count += 1
        gl.db.commit()
        dbgmsg("dicts > ")
        for a in self.dir_dict.keys():
            dbgmsg("이름 : " + str(self.dir_dict[a].name) + " object_id : " + str(
                self.dir_dict[a].object_id) + " parent_node : "
                   + str(self.dir_dict[a].parent_node) + "경로 : " + str(self.dir_dict[a].path))
            # for b in self.file_list :
            # print(str(a) + "and " + str(b.parent_node))
            #    if int(a) == int(b.parent_node) :
            #        print(str(b.name)+ " ",end="")
            # print("")

        return 0

    def parse_root_node(self, f):
        f.seek(self.catalog_file_location + self.node_size * self.root_node, 0)  # f pointer 해당 노드위치로 변경
        fr = f.read(self.block_size)  # block size만큼 읽어옴
        parse_location = 0xE  # 레코드 위치 쭉 따라가기 위한 변수, 0xE부터 첫 번째 레코드 시작
        record_num = struct.unpack_from(">H", fr, 0x0 + 0xA)[0]
        for i in range(record_num):
            n = RootNode()

            key_length = struct.unpack_from(">H", fr, parse_location + 0x0)[0] + 4  # 레코드의 길이
            dbgmsg("key_length : " + str(key_length))
            name_length = struct.unpack_from(">H", fr, parse_location + 0x6)[0]  # 이름길이 파싱

            n.parent_node_id = struct.unpack_from(">I", fr, parse_location + 0x2)[0]  # 부모노드 id 파싱
            n.name = ""
            for i in range(name_length):
                n.name += chr(
                    struct.unpack_from(">" + str(name_length) + "H", fr, parse_location + 0x8 + i * 2)[0])  # 이름 파싱
            dbgmsg("n.name : " + n.name)

            n.child_node_id = struct.unpack_from(">I", fr, parse_location + 0x8 + name_length * 2)[0]

            parse_location += key_length  # 다음 레코드 파싱을 위해 현재 위치 기록해둠

            # self.node_list.append(n)
            dbgmsg("node added")
        dbgmsg("parse_rootnode_end")

    def parse_leaf_node(self, f, node_num):  # node_num에 해당하는 node를 한번 파싱해줌
        """

        :rtype: int
        """
        f.seek(self.catalog_file_location + self.node_size * node_num, 0)  # f pointer 해당 노드위치로 변경
        dbgmsg("location : " + str(self.catalog_file_location + self.node_size * node_num))
        fr = f.read(self.block_size * 2)  # block size * 2만큼 읽어옴
        flink = struct.unpack_from(">I", fr, 0x0 + 0x0)[0]
        blink = struct.unpack_from(">I", fr, 0x0 + 0x4)[0]
        type = struct.unpack_from(">B", fr, 0x0 + 0x8)[0]
        height = struct.unpack_from(">B", fr, 0x0 + 0x9)[0]
        record_num = struct.unpack_from(">H", fr, 0x0 + 0xA)[0]
        dbgmsg("record_num : " + str(record_num) + " " + str(node_num))
        # 2 byte reserved
        for i in range(record_num):
            oi = ObjectItem()  # 파일 및 폴더
            record_location = struct.unpack_from(">H", fr, self.block_size * 2 - (i + 1) * 2)[0]  # 2000 - (n + 1) * 2
            dbgmsg("i : " + str(i) + " record_location : " + str(record_location) + " block size : " + str(
                self.block_size))
            oi.parent_node = struct.unpack_from(">I", fr, record_location + 0x2)[0]
            name_length = struct.unpack_from(">H", fr, record_location + 0x6)[0]  # 이름길이 파싱
            oi.name = ""  # 파일 및 폴더의 이름 구하기
            for i in range(name_length):
                oi.name += chr(
                    struct.unpack_from(">H", fr, record_location + 0x8 + i * 2)[0])  # 이름 파싱
            oi.type = struct.unpack_from(">H", fr, record_location + 0x8 + name_length * 2)[0]  # 1 폴더 2 파일
            if int(oi.type) == 3 or int(oi.type) == 4:
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
            # reserved 4byte
            oi.data_location = self.catalog_file_location + self.node_size * node_num + record_location + 0x8 + name_length * 2 + 0x58
            # if oi.type == 2 : #이 object가 파일이면
            #    next_record_location = struct.unpack_from(">B", fr, self.block_size - (i + 2) * 2)[0]  # 2000 - (n + 1) * 2
            #    for j in range((next_record_location - record_location - 0x8 - name_length * 2 - 0x4E) / 4) : # start_block, block_count 몇 번 나올지 예상
            #        oi.start_block = struct.unpack_from(">I", fr, record_location + 0x8 + name_length * 2 + 0x52)[0]
            #        oi.block_count = struct.unpack_from(">I", fr, record_location + 0x8 + name_length * 2 + 0x56)[0]
            #

            dbgmsg("n.name : " + oi.name + " parent_node : " + str(oi.parent_node) + " type : " + str(
                oi.type) + " name_length : " + str(name_length))
            if oi.type == 1:  # 이 object가 폴더면
                self.dir_dict[oi.object_id] = oi
                object_id_temp = oi.parent_node  # 경로명을 알기위한 임시변수, 재귀형식을 갖기 위해 oi.parent_node로 설정
                folder_path_parsed = 0  # 경로가 파싱되었는지
                # print("object_id_temp : " + str(folder_path_parsed) + " folder_path_parsed : " + str(folder_path_parsed))
                while object_id_temp != 1 and folder_path_parsed == 0:  # 경로명 구하기
                    object_id_temp, string, folder_path_parsed = self.get_parent_name(object_id_temp)
                    oi.path = string + "/" + oi.path
                # oi.path = oi.path + "/"# 끝 마무리 / 붙여주기
                # oi.path = oi.path[:-1]
                if oi.path == "":  # 경로가 공백이면 / 붙여줌 (root)
                    oi.path = "/"
                oi.path_parsed = 1
                item_dict = {}
                item_dict['num'] = oi.object_id
                item_dict['name'] = oi.name
                item_dict['path'] = oi.path
                item_dict['upper_num'] = oi.parent_node  # db 업데이트를 위한 사전
                item_dict['parsed'] = 1
                gl.db.insertDB("FOLDER", item_dict)  # db에 저장
            else:  # 이 object가 파일이면
                # 데이터 먼저 추출
                oi.size = struct.unpack_from(">Q", fr, record_location + 0x8 + name_length * 2 + 0x50)[0]
                self.file_list.append(oi)

                object_id_temp = oi.parent_node  # 경로명을 알기위한 임시변수, 재귀형식을 갖기 위해 oi.parent_node로 설정
                folder_path_parsed = 0  # 경로가 파싱되었는지
                # print(
                # "object_id_temp : " + str(folder_path_parsed) + " folder_path_parsed : " + str(folder_path_parsed))
                while object_id_temp != 1 and folder_path_parsed == 0:  # 경로명 구하기
                    object_id_temp, string, folder_path_parsed = self.get_parent_name(object_id_temp)
                    oi.path = string + "/" + oi.path
                # oi.path = oi.path + "/"# 끝 마무리 / 붙여주기
                # oi.path = oi.path[:-1]
                if oi.path == "":  # 경로가 공백이면 / 붙여줌 (root)
                    oi.path = "/"
                oi.path_parsed = 1

                file_inform = {}
                dbgmsg("parsing NAME")
                file_inform['name'] = oi.name  # 파일이름 파싱
                dbgmsg("parsing PATH")
                file_inform['path'] = oi.path  # 파일 path 파싱
                dbgmsg("parsing SIZE")
                file_inform['size'] = 0
                # file_inform['size'] = 0
                dbgmsg("parsing MD5")
                # file_inform['md5'] = file_hash.md5_for_largefile(path + "\\" + file_inform['name'], 4096)
                file_inform['md5'] = 0  # 일딴뺐음
                dbgmsg("parsing SHA1")
                # file_inform['sha1'] = file_hash.sha1_for_largefile(path + "\\" + file_inform['name'], 4096)
                file_inform['sha1'] = 0  # 속도떄문에 일딴뺐음
                dbgmsg("parsing MAC")
                file_inform['modify_time'] = oi.modify_time
                file_inform['access_time'] = oi.access_time
                file_inform['create_time'] = oi.create_time
                file_inform['modify_attribute_time'] = oi.modify_attribute_time
                file_inform['backup_time'] = oi.backup_time
                file_inform['index_num'] = 0  # 나중에 중복처리하는부분
                file_inform['file_node_num'] = oi.object_id
                file_inform['folder'] = oi.parent_node
                file_inform['data_location'] = oi.data_location
                file_inform['parsed'] = 1
                file_inform['bookmark'] = 0

                # item_tuple = tuple(file_inform.values()) # db 업데이트를위한 튜플화
                gl.db.insertDB("EVIDENCE", file_inform)  # db에 저장
            dbgmsg("node added")
        return flink

    def get_parent_name(self, folder_id):
        if self.dir_dict[folder_id].path_parsed == 0:
            # print("parse, folder_id : " + str(folder_id) + " name : " + str(self.dir_dict[folder_id].name))
            return self.dir_dict[folder_id].parent_node, self.dir_dict[folder_id].name, 0
        else:
            # print("parse end , folder_id : " + str(folder_id) + " name : " + str(self.dir_dict[folder_id].name) + " path : " + str(self.dir_dict[folder_id].path))
            return 0, self.dir_dict[folder_id].path + self.dir_dict[folder_id].name, 1  # path_parsed 1이면 경로파싱 끝

    def carvingData(self, f, location, name):
        f.seek(location - location % self.block_size, 0)  # 계속 에러나길래 blocksize단위로 읽게 약간 뒤로 감
        fr = f.read(self.block_size)
        fw = open(name, "wb")
        start_location = location % self.block_size
        extent_discriptor_list = []
        total_block = struct.unpack_from(">I", fr, start_location + 0xC)[0]
        dbgmsg("carving total_block : " + str(total_block))
        i_block = 0  # carving하고있는 block의 위치
        i_count = 0  # block위치를 센 횟수
        while i_block < total_block:
            ed = ExtentDiscriptor()

            ed.start_block = struct.unpack_from(">I", fr, start_location + 0x10 + i_count * 4)[0]
            ed.block_count = struct.unpack_from(">I", fr, start_location + 0x14 + i_count * 4)[0]

            i_block += ed.block_count
            extent_discriptor_list.append(ed)
            dbgmsg("block : " + str(i_block) + " start_block : " + str(ed.start_block) + " block_count : " + str(
                ed.block_count))

        for i in extent_discriptor_list:
            f.seek((self.volume_start + i.start_block * self.block_size), 0)
            for j in range((i.block_count)):
                fw.write(f.read(self.block_size))
        fw.close()

    def getPhysicalDrives(self):
        w = wmi.WMI()
        physicalDrivesList = []
        for drive in w.Win32_DiskDrive():
            physicalDrivesList.append(drive.Model + "   " + drive.DeviceID + "  " + drive.SIZE)

        return physicalDrivesList

# 구해야하는 것
# 루트노드에서 하위노드들 배열로 return해주는 함수
# 리프노드 넘버 넣으면 디렉토리,폴더 파싱해오는 함수
# 디렉토리, 폴더
