import os

import subprocess

import main
from hfs import HFSP


class MakeDD :
    global disk_path
    global disk_real_path
    def __init__(self) :
        if main.os_mode == "WINDOWS" :
            os.system ("DISKPART /s C:\\createVdisk.txt")
            self.disk_path = "X:"
        elif main.os_mode == "MACOS" :
            os.system("hdiutil create -size 50m -fs MS-DOS -volname Matzip_forensics /Users/allen/Downloads/matzip-forensics/dist/example.dmg")
            cmd_result = subprocess.check_output("hdiutil attach -readwrite /Users/allen/Downloads/matzip-forensics/dist/example.dmg", shell=True, universal_newlines=True)
            self.disk_path = cmd_result.splitlines()[1].split("\t")[2].replace(" ", "\\ ")
 #           self.disk_real_path = cmd_result.splitlines()[1].split()[3]
            print("---------\n "+cmd_result + "\n--------\n" + cmd_result.splitlines()[1] + "\n-----------------\n" + cmd_result.splitlines()[1].split()[2].replace(" ", "\\ "))
    def moveEvidence(self, bookmark_file_list):
            if main.os_mode == "WINDOWS" :
                for bookmark_file in bookmark_file_list :
                    print(bookmark_file_list)
                    file_row = main.db1.executeOneQuery("SELECT * FROM evidences WHERE NUM = " + str(bookmark_file))
                    file_name = file_row[1]
                    file_location = file_row[14]
                    main.printDebugMessage("파싱할 파일이름 : " + file_name + " 위치 : " + str(file_location))
                    hfs = HFSP(main.disk_num)
                    hfs.block_size = main.block_size
                    file_size = file_row[3]
                    hfs.parsingData(file_location, file_name , file_size)
                    os.system("move \"C:\\Users\\Kang\\Desktop\\강성철\\BOB\\프로젝트\\matzip-forensics\\"
                          + file_name + "\" \"" + self.disk_path + "\\" + file_name + "\"")
            elif main.os_mode == "MACOS" :
                for bookmark_file in bookmark_file_list :
                    file_row = main.db1.executeOneQuery("SELECT * FROM evidences WHERE NUM is " + str(bookmark_file))
                    file_name = file_row[1].replace(" ", "\\ ") # 메타데이터 확장자 : mzmd
                    file_path = file_row[2].replace(" ", "\\ ")
                    file_path = file_path.replace("/Users", "\\ 1/Users")
                    os.system("cp /Volumes" + file_path + file_name  + " " + self.disk_path + "/" + file_name)
                    print("cp /Volumes" + file_path + file_name + " " + self.disk_path + "/" + file_name)
                
    def dumpMetadata(self, bookmark_file_list) :
        if main.os_mode == "WINDOWS" :
            os.system("mkdir " + self.disk_path + "\\Metadata")
        elif main.os_mode == "MACOS" :
            os.system("mkdir " + self.disk_path + "/Metadata")
        for bookmark_file in bookmark_file_list :
                file_row = main.db1.executeOneQuery("SELECT * FROM evidences WHERE NUM is " + str(bookmark_file))
                file_name = file_row[1]
                if main.os_mode == "MACOS" :
                    file_name = file_name.replace(" ", "\\ ") # 메타데이터 확장자 : mzmd
                file_location = file_row[14]
                file_node_location = file_location - 96 - len(file_name) * 2 # 데이터 위치로 메타데이터 시작위치를 알 수 있다.
                hfs = HFSP(2)
                hfs.block_size = main.block_size
                hfs.parsingMetadata(file_node_location, file_name)

                if main.os_mode == "WINDOWS" :
                    os.system("move C:\\Users\\Kang\\Desktop\\강성철\\BOB\\프로젝트\\matzip-forensics\\"
                          + file_name + ".mzmd " + self.disk_path + "\\Metadata\\" + file_name + ".mzmd")
                elif main.os_mode == "MACOS" :
                    os.system("mv /Users/allen/Downloads/matzip-forensics/"+ file_name
                          + ".mzmd " + self.disk_path + "/Metadata/" + file_name + ".mzmd")
            

       # print("mv /Users/allen/Downloads/matzip-forensics/"+ file_name + ".mzmd " + self.disk_path + "/Metadata/" + file_name + ".mzmd")
    def detach(self):
        if main.os_mode == "WINDOWS" :
            os.system("DISKPART /s C:\\detachVdisk.txt")
        elif main.os_mode == "MACOS" :
            os.system("hdiutil detach " + self.disk_path)


