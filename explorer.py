from main import *

def beginExplorer() :
    location = 0
    upper_location = 0
    while(True) :
        row_result = []
        print(main.default_path + ">", end = "")
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

        if cmd[:2] == "cd" :
            dir_name = cmd.split(" ", 1)[1] #앞에 공백하나 기준으로 앞뒤쪼갬
            item_dict = {} #db에 넣기위한 dict
            if dir_name == ".." : #상위폴더
                row_result = main.db1.executeOneQuery("SELECT * FROM FOLDER WHERE NUM is " + str(upper_location))
                location = row_result[0]
                upper_location = row_result[3]
                main.default_path = row_result[2] + "\\" + row_result[1]


            else :
                item_dict['dirname'] = dir_name
                item_dict['location'] = location
                row_result = main.db1.executeOneQueryWithDict("SELECT * FROM FOLDER WHERE NAME is :dirname AND UPPER_NUM is :location", item_dict)
                if row_result != None :
                    location = row_result[0]
                    upper_location = row_result[3]
                    main.default_path = row_result[2] + "\\" + row_result[1]
                else :
                    print("폴더를 찾을 수 없습니다")


