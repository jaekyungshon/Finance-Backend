import pandas as pd

class CodeReader:
    def __init__(self):
        self.code_list=None
        self.code_name_list=None
    
    def read_xls(self):
        krx_list=pd.read_html("D:\학교\학교개인프로젝트모음\Capstone-API\Creon\data\상장법인목록.xls")
        krx_list[0].종목코드=krx_list[0].종목코드.map("{:06d}".format)
        #print(len(krx_list))
        
        df=krx_list[0].sort_values(by='종목코드')
        #print(df)
        
        self.code_list=[code for code in df.종목코드]
        #print(self.code_list)
        
        self.code_name_list=[name for name in df.회사명]
        #print(self.code_name_list)
        return self.code_list, self.code_name_list


"""
if __name__=="__main__":
    obj=CodeReader()
    tmp1,tmp2=obj.read_xls()
"""