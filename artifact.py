from plistlib import *
import os

from os import walk

def get_file_path(): # get file pathes and return pathes
    f = []
    all_file_path = []
    input_mypath = os.path.abspath(input("enter path : "))
    for (dirpath, dirnames, filenames) in walk(input_mypath):
        f.extend(filenames)
        for files in filenames:
            all_file_path.append(dirpath+'\\'+files)
    return all_file_path

def plist_parser():
    path_list = get_file_path()
    plist_dict = {}
    for path in path_list:
        try:
            file_path = open(os.path.abspath(path), 'rb')
            temp = {}
            load_result = load(file_path)
        except:
            continue
        temp[path] = load_result
        plist_dict.update(temp)
    return plist_dict

test = plist_parser()
for key,value in test.items():
    print(key,value)
