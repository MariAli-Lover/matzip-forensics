import os
import globals as gl
# from file_info import *
# from Item import *
from debug import *


# 폴더, 파일 쭉긁어오는거
f = []
folder_num = 0  # 폴더 인덱싱
folder_num_dict = {}  # 폴더 인덱싱을 위한 사전


def get_file_path(default_path, db1):  # get file pathes and return pathes

    global folder_num

    # all_file_path = []
    input_mypath = default_path
    folder_num_dict[default_path] = 0  # 폴더 인덱싱
    input_mypath.replace("\\", "/")
    for (dirpath, dirnames, filenames) in os.walk(input_mypath):
        f.extend(filenames)
        for items in filenames:  # 한 폴더의 파일 쭉긁어오기
            # all_file_path.append(dirpath+files)
            # 한 파일 혹은 폴더의 메타데이터정보를 쿼리에 넣는다.
            one_item = os.path.join(dirpath, items)  # 디렉토리에있는 파일 및 폴더 읽어온다.
            if os.path.isfile(one_item):  # 파일이면, itemList에 집어넣을 것
                # dbgmsg()("파일 탐지 : " + os.path.basename(one_item))
                file_inform = {}
                file_inform = {}
                file_stat = os.stat(one_item)
                # dbgmsg()("parsing NAME")
                file_inform['name'] = os.path.basename(one_item)  # 파일이름 파싱
                # dbgmsg()("parsing PATH")
                file_inform['path'] = os.path.dirname(one_item)  # 파일 path 파싱
                # dbgmsg()("parsing SIZE")
                # file_inform['size'] = file_stat.st_size
                file_inform['size'] = 0
                # file_inform['size'] = 0
                # dbgmsg()("parsing MD5")
                # file_inform['md5'] = file_hash.md5_for_largefile(os.path.abspath(one_item), 4096)
                file_inform['md5'] = 0  # 속도떄문에 일딴뺐음
                # dbgmsg()("parsing SHA1")
                # file_inform['sha1'] = file_hash.sha1_for_largefile(os.path.abspath(one_item), 4096)
                file_inform['sha1'] = 0  # 속도떄문에 일딴뺐음
                # dbgmsg()("parsing MAC")
                file_inform['modify_time'] = datetime.datetime.fromtimestamp(file_stat.st_mtime)
                file_inform['access_time'] = datetime.datetime.fromtimestamp(file_stat.st_atime)
                file_inform['create_time'] = datetime.datetime.fromtimestamp(file_stat.st_ctime)

                file_inform['index_num'] = 0  # 나중에 중복처리하는부분

                # folder_num = folder_num_dict[os.path.basename(one_item)] #아직에러ㅋㅋ
                file_inform['folder'] = folder_num
                """item = Item.Item(file_inform['name'], file_inform['path']
                                 , file_inform['size'], file_inform['md5']
                                 , file_inform['sha1'], file_inform['modify_time']
                                 , file_inform['access_time'], file_inform['create_time']
                                 , file_inform['index_num'], folder_num)  # 새로운 Item객체 만듬, 정보대입
                main.itemList.append(item)  # itemList에 item객체를 넣는다"""
                # item_tuple = tuple(file_inform.values()) # db 업데이트를위한 튜플화
                db1.insertDB("EVIDENCE", file_inform)  # db에 저장
        for dirs in dirnames:  # 한 폴더의 파일 쭉긁어오기
            # dbgmsg()("폴더 탐지")
            folder_num += 1;  # 폴더 인덱싱
            folder_num_dict[dirpath + "\\" + os.path.basename(dirs)] = folder_num  # 폴더 인덱싱,
            # upper_folder_num = folder_num_dict[dirpath] #상위폴더의 folder_num을 가져옴 아직에러ㅋㅋ
            upper_folder_num = 0
            # dbgmsg()("상위폴더 num : " + str(folder_num_dict[dirpath]))
            # (NUM, NAME, PATH, UPPER_NUM)
            item_dict = {}
            item_dict['num'] = folder_num
            item_dict['name'] = os.path.basename(dirs)
            item_dict['path'] = dirpath
            item_dict['upper_num'] = upper_folder_num  # db 업데이트를 위한 사전
            db1.insertDB("FOLDER", item_dict)  # db에 저장


def get_one_file_path(path, db1):  # get file pathes and return pathes
    global folder_num
    try:
        dbgmsg(path + "탐지시작")
        upper_folder_num = folder_num_dict[path[:-1] if path[-1] == "\\" else path]  # 끝에 \ 붙었을 시 \ 떼줌
        filenames = os.listdir(path)
        for one_item in filenames:  # 한 폴더의 파일 쭉긁어오기
            # all_file_path.append(dirpath+files)
            # 한 파일 혹은 폴더의 메타데이터정보를 쿼리에 넣는다.
            if os.path.isdir(path + "\\" + one_item):  # 폴더면
                dbgmsg("폴더 탐지")
                folder_num += 1;  # 폴더 인덱싱
                folder_num_dict[path + "\\" + os.path.basename(one_item)] = folder_num  # 폴더 인덱싱,
                # dbgmsg()("상위폴더 num : " + str(folder_num_dict[os.path.dirpath(one_item)]))
                # (NUM, NAME, PATH, UPPER_NUM)
                item_dict = {}
                item_dict['num'] = folder_num
                item_dict['name'] = one_item
                item_dict['path'] = path
                item_dict['upper_num'] = upper_folder_num  # db 업데이트를 위한 사전
                item_dict['parsed'] = 0
                db1.insertDB("FOLDER", item_dict)  # db에 저장
                # except:
                #    print("폴더를 찾을 수 없습니다zzz")

            else:  # 파일이라면
                dbgmsg("파일 탐지 : " + os.path.basename(one_item))
                file_inform = {}
                file_stat = os.stat(path + "\\" + os.path.basename(one_item))
                dbgmsg("parsing NAME")
                file_inform['name'] = os.path.basename(one_item)  # 파일이름 파싱
                dbgmsg("parsing PATH")
                file_inform['path'] = path  # 파일 path 파싱
                dbgmsg("parsing SIZE")
                file_inform['size'] = file_stat.st_size
                #file_inform['size'] = 0
                dbgmsg("parsing MD5")
                file_inform['md5'] = file_hash.md5_for_largefile(path + "\\" + file_inform['name'], 4096)
                #file_inform['md5'] = 0  # 속도떄문에 일딴뺐음
                dbgmsg("parsing SHA1")
                file_inform['sha1'] = file_hash.sha1_for_largefile(path  + "\\" + file_inform['name'], 4096)
                #file_inform['sha1'] = 0  # 속도떄문에 일딴뺐음
                dbgmsg("parsing MAC")
                file_inform['modify_time'] = datetime.datetime.fromtimestamp(file_stat.st_mtime)
                file_inform['access_time'] = datetime.datetime.fromtimestamp(file_stat.st_atime)
                file_inform['create_time'] = datetime.datetime.fromtimestamp(file_stat.st_ctime)

                file_inform['index_num'] = 0  # 나중에 중복처리하는부분
                file_inform['folder'] = upper_folder_num
                file_inform['parsed'] = 0
                """item = Item.Item(file_inform['name'], file_inform['path']
                                 , file_inform['size'], file_inform['md5']
                                 , file_inform['sha1'], file_inform['modify_time']
                                 , file_inform['access_time'], file_inform['create_time']
                                 , file_inform['index_num'], folder_num)  # 새로운 Item객체 만듬, 정보대입
                gl.itemList.append(item)  # itemList에 item객체를 넣는다"""
                # item_tuple = tuple(file_inform.values()) # db 업데이트를위한 튜플화
                db1.insertDB("EVIDENCE", file_inform)  # db에 저장


        item_dict = {}
        item_dict['name'] = os.path.basename(path)
        item_dict['path'] = os.path.dirname(path)
        db1.insertDB("FOLDER_PARSED", item_dict)
    except :
        print("폴더를 찾을 수 없습니다,")

