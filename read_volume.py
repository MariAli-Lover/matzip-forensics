import win32api
import ctypes, sys , os
import binascii

def hard_disk_available():
    return_list = []
    for i in range(ord('a'),ord('z')+1):
        drive = chr(i)
        if(os.path.exists(drive+":\\")):
            return_list.append(drive.upper()+":")
    return return_list

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def UnsignedHex(v):
    if v >= 0: return '%08X' % v
    return '%08X' % (0x100000000 + v)

if is_admin():
    print("===========disk available list===========")
    index = 0
    hdd_list = hard_disk_available()
    for i in hard_disk_available():
        print(index+1 , "." ,i)
        result1 = win32api.GetVolumeInformation(i + "\\")
        print("Volume name : ",str(result1[0]))
        print("Volume serial number : ",UnsignedHex(result1[1]))
        print("Maximum Component Length of a file name : ", int(result1[2]))
        print("Sys flags : ", int(result1[3]))
        print("File system : ", str(result1[4]))
        index += 1
        print("---------------------------------------")
    input_disk_name = int(input("select disk : "))

    hard_disk = open("\\\\.\\"+hdd_list[input_disk_name-1], "rb")
    reader = hard_disk.read(2048)
    print(str(binascii.hexlify(reader).decode('ascii')))
    hard_disk.close()
    print("Are you happy?")
    print("1. yes 2. no")
    input1 = input("your answer? : ")



else:
    ASADMIN = "asadmin"
    script = os.path.abspath(sys.argv[0])
    params = " ".join([script] + sys.argv[1:] + [ASADMIN])

    ctypes.windll.shell32.ShellExecuteW(None, u"runas", sys.executable, params, None, 1)