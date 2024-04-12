import pymysql,calendar
import datetime, time
import pandas as pd
from data_load import DataLoad
from stockcode_read import CodeReader

class DBUpdater:
    ### 생성자 ###
    def __init__(self):
        self.loader=DataLoad() # API 조회 모듈 가져오기
        self.code_reader=CodeReader() # 엑셀파일 조회 모듈 가져오기
        self.stock_codes,self.stock_names=self.code_reader.read_xls() # 종목코드리스트, 종목명리스트
        self.conn="" # mysql 연결자
        
        try: ## DB 연결 ##
            self.conn=pymysql.connect(host="127.0.0.1", user="root", password="비밀번호", db="testcapstone", charset="utf8")
            print("### [Success] DB: testcapstone ###")
        except:
            print("### [Failed] DB: testcapstone ###]")
            exit(0)
        
        try: ## DB Table 만들기 ##
            with self.conn.cursor() as curs:
                sql = """
                CREATE TABLE IF NOT EXISTS company_info (
                    code VARCHAR(20),
                    company VARCHAR(40),
                    PRIMARY KEY (code)
                )
                """
                curs.execute(sql)
                
                sql = """
                CREATE TABLE IF NOT EXISTS daily_chart (
                    code VARCHAR(20),
                    date DATE,
                    open int,
                    high int,
                    low int,
                    close int,
                    volume int,
                    PRIMARY KEY (code,date)
                )
                """
                curs.execute(sql)
            self.conn.commit()
            print("### [Success] Created company_info table ###")
            print("### [Success] Created daily_chart table ###")
        except:
            print("### [Failed] Created company_info table ###")
            print("### [Failed] Created daily_chart table ###")
    
    ### 소멸자 ###
    def __del__(self):
        self.conn.close()
    
    ### 상장목록 DB 업데이트 ###
    def update_comp_info(self):
        try:
            with self.conn.cursor() as curs:
                for code,name in zip(self.stock_codes, self.stock_names):
                    sql = f"INSERT INTO company_info VALUES ('{code}','{name}') ON DUPLICATE KEY UPDATE code='{code}', company='{name}'"
                    curs.execute(sql)
            self.conn.commit()
            print("### [Success] Insert record in company_info ###")
        except:
            print("### [Failed] Insert record in company_info ###")
    
    ### 차트 데이터 DB 업데이트 ###
    def update_daily_chart(self):
        chart_datas={}
        today = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())
        print(today)
        
        today_str = today.strftime('%Y%m%d')
        today_int = int(today_str)
        
        try:
            idx=1
            for code,name in zip(self.stock_codes, self.stock_names):
                #if idx==10:
                #    break
                # value 설정
                successFlag,v=self.loader.creon_7400(code,20200101,today_int) # getFlag, dataframe
                
                # CreonAPI가 지원안하는 종목코드인 경우, SKIP
                if(successFlag==False):
                    print(f"[Continue #{idx}][{name}][{code}] Not Failed: CreonAPI not support to this stock ")
                    continue
                    
                code_df=pd.DataFrame({'code':[code for _ in range(len(v))]})
                df=pd.concat([code_df,v], axis=1)
                df=df.sort_values('date')
                df=df.drop_duplicates(['date'],keep='first') # date값이 중복된 행 존재시, 중복행제거
                
                chart_datas[code]=df # {'000020' : DataFrame}
                time.sleep(1) # 크레온API 오버 트리픽 방지
                print(f"[Success #{idx}][{name}][{code}] read ...")
                idx+=1
        except:
            print(f"[Failed][update_daily_chart()] data read error")
        
        #print()
        #print([i for i in chart_datas.keys()])
        #print(chart_datas['000020'])
        #print()
        
        try:
            with self.conn.cursor() as curs:
                curs.execute("DROP TABLE IF EXISTS daily_chart")
                sql = """
                CREATE TABLE IF NOT EXISTS daily_chart (
                    code VARCHAR(20),
                    date DATE,
                    time int,
                    open int,
                    high int,
                    low int,
                    close int,
                    volume int,
                    PRIMARY KEY (code,date)
                )
                """
                curs.execute(sql)
                sql = "INSERT INTO daily_chart VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
                for df in chart_datas.values():
                    #print("####", df)
                    for idx in range(len(df)):
                        #print("3333", tuple(df.values[idx]))
                        curs.execute(sql,tuple(df.values[idx]))
                        #print("44444")
            #print(5555)
            self.conn.commit()
            #print(66666)
            print("### [Success] Insert record in daily_chart ###")
        except:
            print("### [Failed] Insert record in daily_chart ###")
        

if __name__=="__main__":
    db=DBUpdater()
    db.update_comp_info()
    db.update_daily_chart()


"""
1. data_manager.py
    - pd.read_csv() ==> mysql로 데이터프레임 가져오기 코드 변경
2. main.py
    - model_stock 테이블 추가
    - 이 테이블에 (종목코드, PV값) 형식으로 레코드 삽입 코드 추가
3. real_main.py
    - model_stock 테이블 전체 레코드 가져오기
    - d_pv 리스트 값 내림차순 정렬 => d_stock 상위 10개 종목 추려내기
    - d_stock 리스트를 recommend 테이블에 전체 레코드 추가하기.

(급우선)
1. Python환경.
2. RLTrader요구하는 라이브러리 환경.(tanserflow, ...)

(추후)
1. 차트데이터 DBUpdater 자동 실행.
2. main.py 자동 실행.

<하루 루틴>
오후 5시에 새로운 차트 데이터 DB에 업데이트
오후 6시에 추가된 학습 데이터로 강화학습 새 결과 만들기
"""
