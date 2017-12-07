from plistlib import *
import os
from os import walk

def get_plist_file():
    print("get plist file")


# def get_file_path(): # get file pathes and return pathes
#     f = []
#     all_file_path = []
#     input_mypath = os.path.abspath(input("enter path : ")) # 주로 /var/log 쪽이지만
#     for (dirpath, dirnames, filenames) in walk(input_mypath):
#         f.extend(filenames)
#         for files in filenames:
#             all_file_path.append(dirpath+'\\'+files)
#     return all_file_path

# def plist_parser():
#     path_list = get_file_path()
#     plist_dict = {}
#     for path in path_list:
#         try:
#             file_path = open(os.path.abspath(path), 'rb')
#             temp = {}
#             load_result = load(file_path)
#         except:
#             continue
#         temp[path] = load_result
#         plist_dict.update(temp)
#     return plist_dict

def plist_parser(file_name):
    #path_list = get_file_path()
    try:
        file_path = open("./"+file_name, 'rb')
        temp = {}
        load_result = load(file_path)
    except:
        return


    return load_result


# test = plist_parser('com.apple.Bluetooth.plist')
# for key,value in test.items():
#     print(key,value)
# #C:\Users\조재민\Desktop\plist\fd
# print(test["C:\\Users\\조재민\\Desktop\\plist\\fd\\InstallHistory.plist"][0]['date'] , test["C:\\Users\\조재민\\Desktop\\plist\\fd\\InstallHistory.plist"][0]["processName"])

# test = plist_parser("com.apple.sidebarlists.plist")
# print(test)