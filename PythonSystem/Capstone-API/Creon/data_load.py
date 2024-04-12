import time
import win32com.client
import pandas as pd
import datetime, time
from stockcode_read import CodeReader

"""
C:\\Users\\jksoh\\AppData\\Local\\Programs\\Python\\Python37-32
"""
"""
win32com 라이브러리를 통해, 크레온API의 3가지 모듈 접근

1. CpUtil.CpCodeMgr
=> 각종 종목코드 정보 및 코드 리스트 get 가능한 모듈

2. CpUtil.CpCybos
=> CYBOS의 각종 상태 확인 가능.

3. CpSysDib.StockChart
=> 주식, 업종, ELW의 차트 데이터 제공.
=> 통신종류 : Request / Reply
=> 관련 CYBOS : HTS [7400 통합차트 메뉴] - 일,주,월,분,틱
"""

class DataLoad:
    def __init__(self):
        self.obj_CpCodeMgr = win32com.client.Dispatch("CpUtil.CpCodeMgr")
        self.obj_CpCybos = win32com.client.Dispatch("CpUtil.CpCybos")
        self.obj_StockChart = win32com.client.Dispatch("CpSysDib.StockChart")
    
    # 차트 데이터 획득 함수
    def creon_7400(self, code, date_from, date_to): # 종목코드, 시작일, 종료일
        #print(date_from, type(date_from))
        #print(date_to, type(date_to))
        try:
            ### API와 연결###
            conn_flag = self.obj_CpCybos.IsConnect
            if conn_flag==0: # 1: 정상
                print("####연결 실패####")
                exit(0)
            
            ### 필요한 차트 데이터 지표 설정###
            field_keys = [0,1,2,3,4,5,8] # 0:날짜 1:시간(hhmm) 2:시가 3:고가 4:저가 5:종가 6:전일대비 8:거래량 9:거래대금
            field_names = ["date","time","open","high","low","close","volume"]
            chart={name: [] for name in field_names}
            
            ### API 호출을 위한 필요 인자들 설정###
            self.obj_StockChart.SetInputValue(0, "A"+code) # 종목코드
            self.obj_StockChart.SetInputValue(1, ord('1')) # 조회 방식(0:개수, 1:기간 == 아스키코드)
            self.obj_StockChart.SetInputValue(2, date_to) # 종료일
            self.obj_StockChart.SetInputValue(3, date_from) # 시작일
            self.obj_StockChart.SetInputValue(5, field_keys) # 차트 지표
            self.obj_StockChart.SetInputValue(6, ord('D')) # 차트 주가 단위(D:일, W:주, M:월, m:분, T:틱)
            
            ### 입력한 설정(인자들)에 따라 API에 데이터 요청###
            self.obj_StockChart.BlockRequest()
            
            ### 요청 결과 상태 정상인지 확인###
            status = self.obj_StockChart.GetDibStatus()
            msg = self.obj_StockChart.GetDibMsg1()
            #print(f"###통신 상태###: {status}: {msg}")
            if status!=0: # 0: 정상
                return None
            
            ### 응답 결과물 받기###
            stock_code=self.obj_StockChart.GetHeaderValue(0) # 종목코드
            field_cnt=self.obj_StockChart.GetHeaderValue(1) # 필드개수
            cnt=self.obj_StockChart.GetHeaderValue(3) # 수신 개수
            for i in range(cnt):
                dict_item=(
                    {name: self.obj_StockChart.GetDataValue(pos,i) for pos,name in zip(
                        range(len(field_names)), field_names
                    )}
                )
                for k,v in dict_item.items():
                    chart[k].append(v)
            
            #print(f"차트: {cnt} {dict_chart}")
            #print(f"[종목코드] {stock_code}")
            #print(f"[차트지표개수] {field_cnt}개")
            #print(f"[응답수신개수] {cnt}개")
            ### hashmap 형태를 DataFrame으로 치환###
            return True, pd.DataFrame(chart, columns=field_names) # 해당 코드 get 정상
        except:
            return False, None # 해당 코드 get 비정상
        
        

"""
if __name__ == "__main__":
    ### 객체 생성 ###
    loader=DataLoad()
    code_reader=CodeReader()
    
    ### 필요 변수 준비 ###
    chart_datas={} # 구조: {'종목코드' : ['종목명', 차트데이터_데이터프레임]}
    stock_codes,stock_names=code_reader.read_xls() # 종목코드리스트, 종목명리스트 가져오기
    if(stock_codes==None):
        print("### [Error][stockcode_read] Codes Read Failed ###")
        exit(0)
    if(stock_names==None):
        print("### [Error][stockcode_read] Names Read Failed ###")
        exit(0)
    
    #print(stock_codes)
    #print(stock_names)
    #print(loader.creon_7400("000020",20200101,20221231))
    
    ### 차트 데이터 넣기 - 종목수가 많기에 10개만 테스트 ###
    idx=1
    for code,name in zip(stock_codes, stock_names):
        if idx==10:
            break
        # value 설정
        v_list=[name] # value=[종목명]
        v_list.append(loader.creon_7400(code,20200101,20221231)) # value=[종목명, 차트데이터_데이터프레임]
        chart_datas[code]=v_list # {'000020' : ['동화약품', DataFrame]}
        time.sleep(1) # 크레온API 오버 트리픽 방지
        print(f"[{name}][{code}] save success ...")
        idx+=1
    
    print()
    print(f"[종목명] {chart_datas['000020'][0]}")
    print(chart_datas['000020'][1])
"""

"""
if __name__=="__main__":
    loader=DataLoad()
    successFlag,df=loader.creon_7400("000020",20200101,20240331)
    print(successFlag)
    print(df)
"""
