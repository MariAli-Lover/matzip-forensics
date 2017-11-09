from hfs import *

class RootNode() :
    global flink
    global blink
    global type
    global height
    global record_num
    global parent_node_id
    global name_length
    global name
    global child_node_id
    global offset_to_record_list #레코드들의 위치

    def __init__(self):
        self.offset_to_record_list = ()



class LeafNode() :
    global flink
    global blink
    global type
    global height
    global record_num
    global parent_node_id
    global name_length
    global name
    global record_type
    #global flag                 #
    #global valence              #?byte
    global object_id            #4byte
    global create_time
    global modify_time
    global attribute_modify_time
    global access_time
    global backup_time
    global permission           #16byte
    global user_inform           #16byte
    global finder_inform           #16byte
    global text_encoding           #4byte
    #global reserved            #4byte

    ##############file###################

    global start_block          #4byte
    global block_count          #4byte

