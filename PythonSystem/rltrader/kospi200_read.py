import pandas as pd
# pip install lxml

class CodeReaderKOSPI:
    def __init__(self):
        self.stock_codes=[]
        self.stock_names=[]
        
    def read_kospi200_xls(self):
        kospi_list=pd.read_html("E:\학교\학교개인프로젝트모음\\rltrader\data\상장법인목록_KOSPI200.xls")
        kospi_list[0].종목코드=kospi_list[0].종목코드.map("{:06d}".format)
        
        df=kospi_list[0].sort_values(by='종목코드')
        
        self.stock_codes=[code for code in df.종목코드]
        self.stock_names=[name for name in df.회사명]
        
        return self.stock_codes, self.stock_names

"""
if __name__=="__main__":
    reader=CodeReaderKOSPI()
    codes,names=reader.read_kospi200_xls()
    
    print(f"(종목코드, 회사명) (회사 개수: {len(codes)})")
    for code, name in zip(codes,names):
        print(code, ",", name)
    print()
"""