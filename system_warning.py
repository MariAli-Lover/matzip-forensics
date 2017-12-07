from artifact import *
from log_file_parser import *
import datetime

# def system_warning() :
#     dict_r = {}
#     fp = open("C:\Users\Kang\Desktop\강성철\BOB\프로젝트\plist\com.teamviewer.teamviewer.preferences.plist", "r")
#     load(fp, dict_r, fmt=None, use_builtin_types=True, dict_type=dict)
#     print(dict_r)

import hfs , main
path_plist_file = {"os_install_log" : {"name" : "InstallHistory.plist" , "path" : "\/Library\/Receipts" },


                   }


def get_analysis():
    print("begin to get plist file")
    give_dict = {}
    file_sql = "select SIZE , DATA_LOCATION from evidences where NAME is \""+path_plist_file["os_install_log"]["name"]+"\" and PATH regexp '"+path_plist_file["os_install_log"]["path"]+"'"
    print(file_sql)
    result = (main.db1.executeOneQuery(file_sql))
    print(result)
    if(result != None):
        # os install time
        hfs_util = hfs.HFSP(1)
        print(result[1], result[0])
        hfs_util.parsingData(result[1], "tmp" + "os_install.plist", result[0])
        info = plist_parser("tmp" + "os_install.plist")
        for i in range(5):
            if info[i]['processName'] in ('macOS Installer' , "OS X Installer"):
                give_dict['os_install_time'] = (info[0]['date'])


    else:
        give_dict['os_install_time'] = "can not detect"

    #user install time
    folder_sql = "select CREATE_TIME from folder where NAME = 'Users' and PATH = '" + main.root_folder_path + "'"
    info = (main.db1.executeOneQuery(folder_sql))
    give_dict['user_creation_time'] = datetime.datetime.fromtimestamp(int(info[0]) - 2082844800).strftime('%Y-%m-%d %H:%M:%S')

    #application install.log -> installed Nov  2 13:11:12 allenui-MacBook-Pro installd[402]: Installed "Python" ()
    #anti forensic S/W
    file_sql = "select SIZE , DATA_LOCATION from evidences where NAME is \""+"install.log"+"\" and PATH is \"" +main.root_folder_path+"private/var/log/" + "\""
    print(file_sql)
    result = (main.db1.executeOneQuery(file_sql))
    print(result)
    if (result != None):
        # os install time
        hfs_util = hfs.HFSP(1)
        print(result[1], result[0])
        hfs_util.parsingData(result[1], "tmp" + "install.log", result[0])

    give_dict["application"] = certain_service_word("tmp"+"install.log", "Installed")

    #system.log 0이 제일 최신 나머지 다까서 airportd boot shutdown reboot 찾아보셈 wifi.log도 그럼

    #usb com.apple.sidebarlist.plist -> entryType : 515 number of usb

    #WIFI com.apple.airport.preferences.plist -> bssidstring : , ssid , last connected en1 -> wireless interface

    #image file(disk image?) counts



    #time machine 백업 관련 alias -> bytes object로 기록/ /var/db/com.apple.TimeMachine.SnapshotDates.plist

    #blue tooth /Library/Preferences/com.apple.Bluetooth.plist

    # monthly.out -> monthly user loged in 900.12 hours
    return give_dict



