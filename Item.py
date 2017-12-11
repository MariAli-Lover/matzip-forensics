class ObjectItem:
    global key_length
    global parent_node
    global name
    # global flag                 #
    # global valence              #?byte
    global type # 2byte
    global object_id  # 4byte
    global create_time
    global modify_time
    global access_time
    global modify_attribute_time
    global backup_time
    global permission  # 16byte
    global user_inform  # 16byte
    global finder_inform  # 16byte
    global text_encoding  # 4byte
    global data_location

    global path #경로
    global path_parsed

    global keyfile_type #
    # global reserved            #4byte
    ##############file###################

    #global extent_discriptor_list
    global size
    def __init__(self):
        self.path = ""
        self.path_parsed = 0
        self.extent_discriptor_list = []
    #def __init__(self, name, folder_id, create_time, modify_time, attribute_modify_time, access_time, backup_time, permission, user_inform, finder_inform, text_encoding, start_block = 0, block_count = 0) :
    #    self.name = name
    #    self.folder_id = folder_id
    #    self.create_time = create_time
    #    self.modify_time = modify_time
    #    self.attribute_modify_time = attribute_modify_time
    #    self.access_time = access_time
    #    self.backup_time = backup_time
    #    self.permission = permission
    #    self.user_inform = user_inform
    #    self.finder_inform = finder_inform
    #    self.text_encoding = text_encoding

        ####### file ######
    #    self.start_block = start_block
    #    self.block_count = block_count

    def showInfo(self) :
        print(self.name + ", " + self.path + ", " + str(self.size) + "byte, "
                + str(self.md5) + ", " + str(self.sha1) + ", " + str(self.modify_time)
              + ", " + str(self.access_time)  + ", " + str(self.create_time)  + ", " +  str(self.index_num) + ", " +  str(self.folder))



class ExtentDiscriptor :
    global start_block
    global block_count