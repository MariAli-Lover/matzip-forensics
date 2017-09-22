from main import *

def beginExplorer() :
    location = 0
    upper_location = 0
    while(True) : #무한반복
        row_result = []
        print(main.default_path + ">", end = "") # C:\test> 같은거
        cmd = input()
        if cmd == "ls" :
            row_folder, row_evidences = main.db1.getItemList(location)
            print("FOLDER")
            for i in row_folder :
                print(i[1], end = " ") #NAME만 출력
            print("\nFILES")
            for i in row_evidences :
                print(i[0], end = " ") #NAME만 출력
            print("\n")

        if cmd[:2] == "cd" : # 앞 두글자가 cd이면
            dir_name = cmd.split(" ", 1)[1] #앞에 공백하나 기준으로 앞뒤쪼깨서 뒤에것 dir_name에넣음
            item_dict = {} #db에 넣기위한 dict
            if dir_name == ".." : #상위폴더
                row_result = main.db1.executeOneQuery("SELECT * FROM FOLDER WHERE NUM is " + str(upper_location))
                location = row_result[0] #현재 위치 바꿔줌
                upper_location = row_result[3] #상위폴더위치 바꿔줌
                main.default_path = row_result[2] + "\\" + row_result[1] # C:\test> 같은거


            else :
                item_dict['dirname'] = dir_name #디렉토리이름
                item_dict['location'] = location #location 이 정보로 쿼리에서 원하는폴더정보 찾음
                row_result = main.db1.executeOneQueryWithDict("SELECT * FROM FOLDER WHERE NAME is :dirname AND UPPER_NUM is :location", item_dict)
                if row_result != None :
                    location = row_result[0] #현재 위치 바꿔줌
                    upper_location = row_result[3] #상위폴더위치 바꿔줌
                    main.default_path = row_result[2] + "\\" + row_result[1] # C:\test> 같은거
                else :
                    print("폴더를 찾을 수 없습니다")


