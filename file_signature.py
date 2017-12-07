import os
import struct
import sqlite3
import datetime
import re
import binascii
from hfs import *
import io

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

def is_bad_signature(file_name_list, mode , size): #mode = {'mode_num' = 1 means i will do it with bytes object , 'file_location' = '~~~~' indicates byte objects of file if mode_num is not 1 then it is useless }
    main.printDebugMessage("start signaturing")
    flag_header_matched = 0

    conn = sqlite3.connect("./file_signature.db")# 파일 시그니처 들어가있는 DB
    cur = conn.cursor()
    extension = os.path.splitext(file_name_list)[1].replace(".", "")#확장자 파싱
    pass_footer_key = 0
    main.printDebugMessage("extension : " + extension + " name : " + file_name_list)
    if extension in ("txt" , "plist" , "ttxt" , "log" , "jpeg", "db" ):
        main.printDebugMessage("exception")
        return "zzzzz"


    if extension is '':
        main.printDebugMessage("no extension file")
        return "2" #메인쪽에 기능을 어떻게 할지 정하면 됨

    sql = "select header_signature , footer_signature , header_offset , footer_offset from file_signature where extension= :Extension"
    cur.execute(sql, {'Extension' : extension})
    db_row = cur.fetchall()
    conn.close()

    if not db_row: #db에서 확장자를 확인 할수 없는 경우
        main.printDebugMessage("unknown extension : " + extension)#file_name_list)
        return "3" #메인쪽에 기능을 어떻게 할지 정하면 됨


    for index in range(len(db_row)):

        f = HFSP(1).signature_maker(mode["file_location"], db_row[index][header_offset_field],db_row[index][footer_offset_field] , size)
        if(f["h_offset_block"] == b"" and f["f_offset_block"] == b""):
            main.printDebugMessage("this is compressed file use other tool!")
            return "use other tool!"
        # print("f has")
        # print( f["h_offset_block"])
        # print(binascii.hexlify(f["f_offset_block"]).decode("ISO-8859-1"))
        #print(db_row[index][header_signature_field],db_row[index][footer_signature_field])
        if(db_row[index][header_signature_field] != "none"):
            header = io.BytesIO(f["h_offset_block"])
        if(db_row[index][footer_signature_field] != "none"):
            footer = io.BytesIO(f["f_offset_block"])

        # if(flag_header_matched == 1):
        #     print("only header matched!!!! , suspicious file which can hide file in the file")
        #     return 1#"only header matched!!!! , suspicious file which can hide file in the file"
        header.seek(int(db_row[index][header_offset_field]))
        sp = header.read(int(len(db_row[index][header_signature_field]) / 2))
        hlist = [db_row[index][header_signature_field][i:i + 2] for i in range(0, len(db_row[index][header_signature_field]), 2)]  # 대조군 한바이트씩 끊어서 프로그램이 사용할수 있게 만든부분
        if (db_row[index][footer_signature_field] != "none"):
            flist = [db_row[index][footer_signature_field][i:i + 2] for i in range(0, len(db_row[index][footer_signature_field]), 2)]
            footer_offset_len = db_row[index][footer_offset_field]
        else:
            pass_footer_key = 1
            footer_offset_len = 0

        i = 0

        while re.match('0x'+hlist[i], format(struct.unpack_from(">B", sp, 0x0 + i)[0],'#04x')):
            main.printDebugMessage('0x'+hlist[i])
            main.printDebugMessage("loop entered")
            i += 1

            if (i == int(len(db_row[index][header_signature_field])) / 2):
                flag_header_matched = 1
                if (pass_footer_key == 1):
                    main.printDebugMessage("match success , header signature only")
                    return "match success , header signature only"


                if (int(db_row[index][footer_offset_field]) != 0):
                    footer.seek(-(int(db_row[index][footer_offset_field])), 2)
                    sp_f = footer.read(int(len(db_row[index][footer_signature_field]) / 2))
                else:
                    footer.seek(-(int((len(db_row[index][footer_signature_field]) / 2))), 2)
                    sp_f = footer.read(int(len(db_row[index][footer_signature_field]) / 2))

                k=0


                while re.match('0x'+flist[k], format(struct.unpack_from(">B", sp_f, 0x0 + k)[0], '#04x')):
                    main.printDebugMessage("second loop entered")

                    k += 1

                    if (k == int(len(db_row[index][footer_signature_field])) / 2):

                        footer.seek(0)
                        content = footer.read()
                        target = str(binascii.hexlify(content))
                        if (is_next_redible(db_row[index][footer_signature_field], footer_offset_len, target)):
                            main.printDebugMessage("there is data behind footer signature")
                            return "1"#"there is data behind footer signature"
                        else:
                            main.printDebugMessage("match success , header and footer")
                            return "match success , header and footer"  # 메인쪽에 기능을 어떻게 할지 정하면 됨
                break

    if (flag_header_matched == 1):
        main.printDebugMessage("only header matched!!!! , suspicious file which can hide file in the file")
        return "1"#"only header matched!!!! , suspicious file which can hide file in the file"

    main.printDebugMessage("header signature not matched")
    return "1"#"header not matched" #메인쪽에 기능을 어떻게 할지 정하면 됨

#C:\Users\조재민\Desktop\출결\출결통합_11_23.xlsx , 새 Microsoft Excel 워크시트.xlsx
# if __name__ == "__main__" :
#     print("test1 file op")
#     input1 = "C:\\Users\\조재민\\Desktop\\출결\\새 Microsoft Excel 워크시트.xlsx"
#     mode = {"mode_num" : 1 , "file_location" : test_file.file_read_bytesdump()}
#     is_bad_signature(input1 , mode)