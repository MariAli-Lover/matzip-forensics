class Item:
    #버리는코드. 코딩하다보니 이거 쓸데가없음
    #파일하나 클래스임
    #근데 파일하나하나 클래스에 저장할필요없이 한번 바로db에박으면 그이후로는쓸데없는듯 메모리만먹고
    def __init__(self, name, path, size, md5, sha1, modify_time, access_time, create_time, index_num, folder) :
        self.name = name
        self.path = path
        self.size = size
        self.md5 = md5
        self.sha1 = sha1
        self.modify_time = modify_time
        self.access_time = access_time
        self.create_time = create_time
        self.index_num = index_num
        self.folder = folder

    def showInfo(self) :
        print(self.name + ", " + self.path + ", " + str(self.size) + "byte, "
                + str(self.md5) + ", " + str(self.sha1) + ", " + str(self.modify_time)
              + ", " + str(self.access_time)  + ", " + str(self.create_time)  + ", " +  str(self.index_num) + ", " +  str(self.folder))

