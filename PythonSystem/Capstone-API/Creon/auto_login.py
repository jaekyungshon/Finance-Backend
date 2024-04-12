import os,time
from pywinauto import application

class AutoLogin():
    def __init__(self):
        self.obj_CpCybos=None
    
    def connect(self):
        try:
            os.system('taskkill /IM coStarter* /F /T')
            os.system('taskkill /IM CpStart* /F /T')
            os.system('taskkill /IM DibServer* /F /T')
            os.system('wmic process where "name like \'%coStarter%\'" call terminate')
            os.system('wmic process where "name like \'%CpStart%\'" call terminate')
            os.system('wmic process where "name like \'%DibServer%\'" call terminate')
        except:
            print("### Kill Failed ###")
            pass
        
        time.sleep(4)
        app=application.Application()
        app.start("F:\CREON\STARTER\coStarter.exe /prj:cp /id:아이디 /pwd:비번 /pwdcert:인증서비번 /autostart")
        time.sleep(5)
        print("### [Success][AutoLogin] 자동 로그인 성공 ###")
if __name__=="__main__":
    obj=AutoLogin()
    obj.connect()