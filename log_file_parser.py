import re

reg = '[a-zA-Z]{3}\s[0-9]{2}\s[0-9]{2}\:[0-9]{2}\:[0-9]{2}\s(.*?)\s(.*?)\[[0-9]+\]\:\s'

def log_read_line(file_name):
    return [line.rstrip('\n') for line in open(file_name , "r+" , encoding="utf-8")]

def certain_service_word(file_name,key_word):
    result = []
    for item in log_read_line("tmpinstall.log"):
        if(re.search(reg+key_word , item)):
            result.append(item)
    return result


#install.log , system.log -> log regex
#[a-zA-Z]{3}\s[0-9]{2}\s[0-9]{2}\:[0-9]{2}\:[0-9]{2}\s(.*?)\s(.*?)\[[0-9]+\]\:\s
#Oct 18 21:02:56 allenui-MacBook-Pro softwareupdate_download_service[282]: Creating background NSURLSession configuration

# index = 0
# for item in log_read_line("install.log"):
#     print(index , item)
#     index = index + 1

#certain_service_word("install.log" , "Installed")