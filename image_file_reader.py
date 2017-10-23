import hashlib
import os
import struct
import sqlite3
data_tuple = []
#import binascii # 개발시 확인용으로 쓰는거 str(binascii.hexlify(reader))

BLOCKSIZE = 65536 # hashfunc에서 쓰는곳
default_SECTOR_size = 512 # sector size는 파서에서 씀

def hash_func(hasher):
    mdhasher = hashlib.md5()
    mdhasher.update(hasher)
    return str(mdhasher.hexdigest())

#hashstr = hash_func("C:\\Users\\조재민\\Desktop\\write.reg")
#print(hashstr)

def dd_file_reader(file_name_path):
    file_handler = open(os.path.abspath(file_name_path),'rb')
    return file_handler

def reserved_area_locator(read_file):
    read_file.seek(0)
    reader = read_file.read(default_SECTOR_size)
    p = struct.unpack_from("<H", reader, 0x1c6)[0]
    return p

def root_directory_parser(read_file , number_of_sector): # return root directory position
    read_file.seek(number_of_sector * default_SECTOR_size)
    reader = read_file.read(default_SECTOR_size)
    Bytes_per_sector = struct.unpack_from("<H", reader, 0x0B)[0]

    CLUSTER_size = struct.unpack_from("<B", reader, 0x0D)[0]
    reserved_sector_count = struct.unpack_from("<H", reader, 0x0E)[0]
    FAT1_location = (reserved_sector_count + number_of_sector) # FAT1 위치구하는 구문
    root_directory = FAT1_location + struct.unpack_from("<i", reader, 0x24)[0]  * 2 # FAT2 이후에 바로 root directory 나오니까 , 섹터크기까지 곱해야함

    return_struct = {"root_direc" : root_directory , "cluster" : CLUSTER_size , "bytes_per_sector" : Bytes_per_sector}

    return return_struct

def file_track_hashing(read_file,track_info,list_data,folder_name):
    file_name = struct.pack('<Q', list_data[0]).decode("cp949",'ignore')
    extender = list_data[1].decode("utf8").lower()
    #create_time = list_data[5]
    #create_date = list_data[6]
    #last_access_date = list_data[7]
    cluster_high = list_data[8]
    #write_time = list_data[9]
    #write_date = list_data[10]
    cluster_low = list_data[11]
    file_size = list_data[12]
    read_file.seek((track_info['root_direc'] + ((cluster_high + cluster_low) - 2) * track_info['cluster']) * track_info['bytes_per_sector'])
    reader = read_file.read(file_size)
    file_hash = hash_func(reader)
    data_tuple.append(tuple((folder_name+"/"+file_name+"."+extender,file_hash)))

def folder_track(read_file,track_info,list_data):
    folder_name = list_data[0]
    if (hex(folder_name) == "0x202020202020202e" or hex(folder_name) == "0x2020202020202e2e"):
        return False
    cluster_high = list_data[8]
    cluster_low = list_data[11]
    return {"offset" : (track_info['root_direc'] + ((cluster_high + cluster_low) - 2) * track_info['cluster']) * track_info['bytes_per_sector'],
            "path" : folder_name}

def file_tracker(read_file , track_info , offset , addtional_path):
    start_of_root = track_info["root_direc"] * track_info["bytes_per_sector"]
    path = "."
    if(addtional_path is not None):
        path = addtional_path
    if(offset is not None):
        start_of_root = offset

    read_file.seek(start_of_root)
    reader = read_file.read(32)
    list_data = struct.unpack("<Q3sBBBHHHHHHHL", reader)

    focus = 0

    while True:

        if (all(v is 0 for v in struct.unpack("3b", list_data[1]))):
            if (all(val is 0 for val in list_data[:0] + list_data[2:])):
                break

        if(list_data[2] == 0x20):
            file_track_hashing(read_file,track_info,list_data,path)

        elif(list_data[2] == 0x10):
            TF = folder_track(read_file,track_info,list_data)
            if(TF):
                path = path + "/" + str(struct.pack('<Q', TF["path"]),'utf-8')
                file_tracker(read_file, track_info, TF["offset"],path)

        focus += 32
        read_file.seek(start_of_root + focus)
        reader = read_file.read(32)
        list_data = struct.unpack("<Q3sBBBHHHHHHHL", reader)





##### 함수 실행부분
input1 = os.path.abspath(input("please show your image file path : "))
dd_file_handle = dd_file_reader(input1)
file_parse_struct = root_directory_parser( dd_file_handle , reserved_area_locator(dd_file_handle) )
file_tracker(dd_file_handle , file_parse_struct,None,None)

conn = sqlite3.connect("./dd_hasher.db")  # 파일 시그니처 들어가있는 DB
cur = conn.cursor()
sql = "insert into hash_list(file_path,hash_value) values (?, ?)"
for value in data_tuple:
    cur.execute(sql, value)
    conn.commit()
conn.close()
print("Job finished!")