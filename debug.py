## 디버깅 함수를 담은 모듈
## from debug import *


import globals as gl # gl.debug_mode 확인


def dbgmsg(message) : #디버그메세지
    if gl.debug_mode == True :
        print(message)