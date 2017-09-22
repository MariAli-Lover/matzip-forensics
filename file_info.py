import hashlib
import os
import datetime
import file_hash

def file_info(item) : #파일 하나정보를 불러오는함수인데, main에도 똑같은 코드를추가해놓음. 파일수천개를 파싱하는데
                        # 속도나 가독성면에서 이렇게 함수로뺴오는게나을지 아니면 함수없이 main에서 코드실행시키는게나을지..?
    file_inform = {}
    file_stat = os.stat(item)
    file_inform['name'] = os.path.basename(item)  # 파일이름 파싱
    file_inform['path'] = os.path.dirname(item)  # 파일 path 파싱
    file_inform['size'] = file_stat.st_size
    #file_inform['size'] = 0
    file_inform['md5'] = file_hash.md5_for_largefile(os.path.abspath(item), 4096)
    file_inform['sha1'] = file_hash.sha1_for_largefile(os.path.abspath(item), 4096)
    file_inform['modify_time'] = datetime.datetime.fromtimestamp(file_stat.st_mtime)
    file_inform['access_time'] = datetime.datetime.fromtimestamp(file_stat.st_atime)
    file_inform['create_time'] = datetime.datetime.fromtimestamp(file_stat.st_ctime)
    file_inform['index_num'] = 0 # default
    file_inform['folder'] = 0 # default
    return file_inform

def is_file_bad_signature(file_name_list): #BAD시그니처인지 확인
    for file_name in file_name_list:
        with open(file_name, "rb") as f:
            byte = f.read(1)
            while len(byte) is not 0 :
                print('%02X' % int(ord(byte)),end=' ')
                # Do stuff with byte.
                byte = f.read(1)
            f.close()

