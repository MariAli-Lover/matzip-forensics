import os
from file_signature import file_signature
import struct
import math
import sqlite3

def file_hex(file_name_list):
    for file_name in file_name_list:
        with open(file_name, "rb") as f:
            byte = f.read(1)
            i = 1
            while len(byte) is not 0 :
                if( i % 16 ==0): print("")
                print('%02X' % int(ord(byte)),end=' ')
                # Do stuff with byte.
                byte = f.read(1)
                i += 1
            f.close()

#def is_bad_signature(file_name_list):
#    extension = os.path.splitext(file_name_list)[1].replace(".","") #[1] = extension ex) .extension
#    f = open(file_name_list, "rb")
#    f.seek(file_signature[extension]['offset'])
#    sp = f.read(50) # 50 is around value
#    print("next one is what i read")
#    print(hex(struct.unpack_from(">I", sp, 0x0)[0]))
    #if file_signature[extension]['signature'] == hex(struct.unpack_from(">I", sp, 0x0)[0]):
    #    print("match!!!")
    #else:
    #    print("not match!!!")

signature_field = 0
offset_field = 1

def is_bad_signature(file_name_list):
    conn = sqlite3.connect("./db/file_signature.db")
    cur = conn.cursor()
    extension = os.path.splitext(file_name_list)[1].replace(".", "")  # [1] = extension ex) .extension
    sql = "select signature , offset from file_signature where extension= :Extension"
    cur.execute(sql, {'Extension' : extension})
    db_row = cur.fetchall()[0]
    f = open(file_name_list, "rb")
    f.seek(db_row[offset_field])
    sp = f.read(int(len(db_row[signature_field])/2))  # 50 is around value
    hlist = [db_row[signature_field][i:i + 2] for i in range(0, len(db_row[signature_field]), 2)] # 한 바이트씩 끊어서 읽는 부분
    i=0
    while ('0x'+hlist[i]) == format(struct.unpack_from(">b", sp, 0x0+i)[0],'#04x'):
        print("thisis",hex(struct.unpack_from(">b", sp, 0x0+i)[0]))
        i+=1
        if(i==int(len(db_row[signature_field]))/2):
            return "match!!!"
    f.close()
    conn.close()
    return "not match!!!"

file_name_list = ['C:/Users/조재민/Desktop/출결/출결통합_9_13.xlsx']
#file_MAC_time(file_name_list)
#file_hex(file_name_list)
print(is_bad_signature(file_name_list[0]))
#file_test = file_hashing(file_name_list[0])
#print(file_test.['Modify_time'])
