import globals as gl
# from file_signature import *
from disk import *
from debug import *


def beginExplorer() :
    location = 2
    upper_location = 0
    gl.default_path = "/무제/"
    while(True) : #무한반복
        row_result = []
        print(main.default_path + ">", end = "") # C:\test> 같은거
        cmd = input()
        if cmd == "ls" :
            row_folder, row_evidences = gl.db.getItemList(location)
            print("FOLDER")
            for i in row_folder :
                print(i[1], end = " ") #NAME만 출력
            print("\nFILES")
            for i in row_evidences :
                print(i[0], end = " ") #NAME만 출력
                dbgmsg("file_node : " + str(i[11]))
            print("\n")


        if cmd == "bd" :
            row_folder, row_evidences = gl.db.getItemList(location)
            for i in row_evidences :
                is_bad_signature(gl.default_path + "\\" + i[0])

        if cmd == "csv" :
            makeCSV()

        #if cmd == "pd" :
            #carvingData(f, location, "asdfasdf")

        if cmd[:2] == "cd" : # 앞 두글자가 cd이면
            dir_name = cmd.split(" ", 1)[1] #앞에 공백하나 기준으로 앞뒤쪼깨서 뒤에것 dir_name에넣음
            item_dict = {} #db에 넣기위한 dict
            if dir_name == ".." : #상위폴더
                row_result = gl.db.executeOneQuery("SELECT * FROM FOLDER WHERE NUM is '" + str(upper_location)+"'")
                location = row_result[0] #현재 위치 바꿔줌
                upper_location = row_result[3] #상위폴더위치 바꿔줌
                gl.default_path = row_result[2] + "/" + row_result[1] if row_result[2] != "/" else "/"+row_result[1] #"# C:\test> 같은거, 앞에 // 되는거 막기위해 3항연산자씀
                dbgmsg("location : " + str(location))


            else :
                    item_dict['dirname'] = dir_name #디렉토리이름
                    item_dict['location'] = location #location 이 정보로 쿼리에서 원하는폴더정보 찾음
                    #fixed_default_path = main.default_path.replace(":", "':")
                    row_result = gl.db.executeOneQuery(
                        "SELECT COUNT(*) FROM FOLDER WHERE PATH is '" + gl.default_path +"/"+ "' AND NAME is '" + dir_name + "' AND PARSED is 1")
                    dbgmsg("row_result : " + str(row_result[0]))
                    if row_result[0] == 1 :
                        row_result = gl.db.executeOneQueryWithDict("SELECT * FROM FOLDER WHERE NAME is :dirname AND UPPER_NUM is :location", item_dict)
                        dbgmsg(dir_name + "폴더 쿼리에 있음")
                        location = row_result[0] #현재 위치 바꿔줌
                        upper_location = row_result[3] #상위폴더위치 바꿔줌
                        gl.default_path = row_result[2] + "/" + row_result[1] # C:\test> 같은거
                    else :
                        dbgmsg(dir_name + "폴더 쿼리에없어서 추가중")
                        #get_one_file_path(main.default_path + "\\" + dir_name ,main.db1) # 폴더 파싱해서 DB에 넣음
                        row_result = gl.db.executeOneQueryWithDict(
                            "SELECT * FROM FOLDER WHERE NAME is :dirname AND UPPER_NUM is :location", item_dict)
                        if row_result != None:
                            dbgmsg(dir_name + "폴더 쿼리에있음")
                            location = row_result[0]  # 현재 위치 바꿔줌
                            upper_location = row_result[3]  # 상위폴더위치 바꿔줌
                            gl.default_path = row_result[2] + "/" + row_result[1]  # C:\test> 같은거



