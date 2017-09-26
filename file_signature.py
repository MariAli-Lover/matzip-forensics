import os
import struct
import sqlite3
import datetime
import re
import binascii

header_signature_field = 0
footer_signature_field = 1
header_offset_field = 2
footer_offset_field = 3

def is_next_redible(pattern, offset,teststring):
    m = teststring.find(pattern)
    offset_len = offset
    try:
        if teststring[m+len(pattern)+offset_len+1]:
            return True

    except:
        return False

def is_bad_signature(file_name_list):

    flag_header_matched = 0

    conn = sqlite3.connect("./db/file_signature22.db")# 파일 시그니처 들어가있는 DB
    cur = conn.cursor()
    extension = os.path.splitext(file_name_list)[1].replace(".", "")#확장자 파싱
    pass_footer_key = 0

    if extension is '':
        print("no extension file")
        return "no extension file" #메인쪽에 기능을 어떻게 할지 정하면 됨

    sql = "select header_signature , footer_signature , header_offset , footer_offset from file_signature where extension= :Extension"
    cur.execute(sql, {'Extension' : extension})
    db_row = cur.fetchall()
    print(db_row, len(db_row))

    if not db_row: #db에서 확장자를 확인 할수 없는 경우
        print("unknown extension")
        return "unknown extension" #메인쪽에 기능을 어떻게 할지 정하면 됨

    f = open(file_name_list, "rb")

    for index in range(len(db_row)):

        if(flag_header_matched == 1):
            print("only header matched!!!! , suspicious file which can hide file in the file")
            return "only header matched!!!! , suspicious file which can hide file in the file"

        f.seek(int(db_row[index][header_offset_field]))
        sp = f.read(int(len(db_row[index][header_signature_field]) / 2))
        hlist = [db_row[index][header_signature_field][i:i + 2] for i in
                 range(0, len(db_row[index][header_signature_field]), 2)]  # 대조군 한바이트씩 끊어서 프로그램이 사용할수 있게 만든부분

        if (db_row[index][footer_signature_field] != "none"):
            flist = [db_row[index][footer_signature_field][i:i + 2] for i in range(0, len(db_row[index][footer_signature_field]), 2)]
            footer_offset_len = db_row[index][footer_offset_field]
        else:
            pass_footer_key = 1
            footer_offset_len = 0

        i = 0
        varii = hex(struct.unpack_from(">B", sp, 0x0 + 0)[0])

        print(varii , type(varii) , varii[0:1] , varii[1:2] , varii[2:3] , hlist[0][1])

        print(hex(struct.unpack_from(">B", sp, 0x0 + i)[0]))
        print(re.match("0x"+hlist[0], hex(struct.unpack_from(">B", sp, 0x0 + 0)[0])))


        while re.match('0x'+hlist[i], format(struct.unpack_from(">B", sp, 0x0 + i)[0],'#04x')):
            i += 1

            if (i+1 == int(len(db_row[index][header_signature_field])) / 2):
                flag_header_matched = 1
                if (pass_footer_key == 1):
                    print("match success , header signature only")
                    return "match success , header signature only"


                if (int(db_row[index][footer_offset_field]) != 0):
                    f.seek(-(int(db_row[index][footer_offset_field])), 2)
                    sp = f.read(int(len(db_row[index][footer_signature_field]) / 2))
                else:
                    f.seek(-(int((len(db_row[index][footer_signature_field]) / 2))), 2)
                    sp = f.read(int(len(db_row[index][footer_signature_field]) / 2))

                k = 0

                while re.match("0x"+flist[k], format(struct.unpack_from(">B", sp, 0x0+k)[0],'#04x')):

                    k += 1

                    if (k + 1 == int(len(db_row[index][footer_signature_field])) / 2):
                        with open(file_name_list, 'rb') as t:
                            content = t.read()
                        target = str(binascii.hexlify(content))
                        if(is_next_redible(db_row[index][footer_signature_field],footer_offset_len,target)):
                            print("there is data behind footer signature")
                            return "there is data behind footer signature"
                        else:
                            print("match success , header and footer")
                            return "match success , header and footer"  # 메인쪽에 기능을 어떻게 할지 정하면 됨

    f.close()
    conn.close()

    if (flag_header_matched == 1):
        print("only header matched!!!! , suspicious file which can hide file in the file")
        return "only header matched!!!! , suspicious file which can hide file in the file"

    print("header signature not matched")
    return "header not matched" #메인쪽에 기능을 어떻게 할지 정하면 됨

#####!!!TEST!!!#####
file_name_list = ['C:/Users/조재민/Desktop/출결/출결통합_9_19.xlsx']
a = datetime.datetime.now()
is_bad_signature(file_name_list[0]) # 0.015630 초 소요
c = datetime.datetime.now() - a
print(c.seconds , c.microseconds , c)