import subprocess
import pymysql
import pandas as pd
import time
from datetime import datetime
from kospi200_read import CodeReaderKOSPI

"""server_main.py : 서버에서 돌릴 main login"""

class DBUpdaterAI:
    ### 생성자 ###
    def __init__(self):
        self.dict_stocks={} # {'종목코드' : PV값}
        self.conn="" # mysql 연결자
        
        ## DB 연결 ##
        try: 
            self.conn=pymysql.connect(host="127.0.0.1", user="root", password="비밀번호", db="testcapstone", charset="utf8")
            print("### [Success][server_main.py] DB: testcapstone ###")
        except:
            print("### [Failed][server_main.py] DB: testcapstone ###]")
            exit(0)

        ## recommend 테이블 생성(기존 drop 후, new)##
        try:
            with self.conn.cursor() as cur:
                cur.execute("DROP TABLE IF EXISTS recommend")
                sql="""
                CREATE TABLE recommend (
                    code VARCHAR(20),
                    last_pv int,
                    PRIMARY KEY (code)
                )
                """
                cur.execute(sql)
            self.conn.commit()
            print("### [Success][server_main.py][__init__] created table recommend ###")
        except:
            print("### [Failed][server_main.py][__init__] Error created table recommend ###")
            exit(0)
    
    ### 소멸자 ###
    def __del__(self):
        self.conn.close()
    
    ### 강화학습 결과 데이터를 담고 있는 aimodel 테이블에서 전체 레코드 가져오기 ###
    def get_aimodel_table(self, today=""):
        df=""
        ## aimodel에서 전체 레코드 가져와, df에 저장 ##
        with self.conn.cursor() as cur:
            cur.execute("SELECT * FROM aimodel")
            result=cur.fetchall()
            df=pd.DataFrame(result)
        
        ## df의 컬럼명 변경 ##
        df.columns=['code', 'last_pv', 'date']
        
        ## df에서 target date 필터링 ##
        if today=="": # Test Code
            target_date=df.iloc[-1]['date'] # 마지막 레코드의 date 사용
            df=df[(df['date'] == target_date)] # 기간 필터링
        else: # Run code
            target_date=today # execute_cmd > main.py > learners.py에서 aimodel에 저장할때 사용된 date
            df=df[(df['date'] == target_date)]
        
        ## df 한 행씩 읽어서, dict_stocks에 저장하기 ##
        for e in df.itertuples():
            self.dict_stocks[e[1]]=e[2]
        #print(self.dict_stocks)
    
    ### 상위 10개 종목 recommend 테이블에 저장 ###
    def insert_record_recommend(self):
        ## 딕셔너리 내림차순 정렬 ##
        self.dict_stocks=sorted(self.dict_stocks.items(), reverse=True, key=lambda x:x[1])
        #print(self.dict_stocks)
        
        ## recommend에 저장 ##
        try:
            with self.conn.cursor() as cur:
                cnt=0
                for key,value in self.dict_stocks:
                    if cnt>=10:
                        break
                    sql=f"INSERT INTO recommend VALUES ('{key}','{value}')"
                    cur.execute(sql)
                    cnt+=1
                    print(f"[상위10개 종목] (종목코드, PV값)")
                    print(f"{key} {value}")
                    
            self.conn.commit()
            print("### [Success][server_main.py][insert_record_recommend] inserted record in recommend table ###")
        except:
            print("### [Failed][server_main.py][ainsert_record_recommend] Error insert record in recommend table ###")
            exit(0)
    
    ### daily_chart에 존재하는 종목코드만 선별하기 위한 함수 ###
    def process_code(self):
        ## KOSPI_200 종목코드 및 종목명 가져오기 ##
        stock_reader=CodeReaderKOSPI() # 모듈 가져오기
        codes,names=stock_reader.read_kospi200_xls() # 종목코드리스트, 종목명리스트
        
        process_codes,process_names=[],[]
        idx=0
        try:
            with self.conn.cursor() as curs:
                for code in codes:
                    #if idx==1:
                    #    break
                    curs.execute(f"SELECT count(*) FROM daily_chart WHERE code={code}")
                    result=curs.fetchall()
                    #print(result[0][0], type(result[0][0]))
                    if result[0][0]>0:
                        process_codes.append(code)
                        process_names.append(names[idx])
                    idx+=1
            print(f"### [Success][server_main.py][process_code] Select to Stocks in KOSPI200 ###")
        except:
            print(f"### [Failed][server_main.py][process_code] Error ###")
            exit(0)
        
        #for i,j in zip(process_codes,process_names):
        #    print(i,j)
        return process_codes, process_names
    
    ### cmd에서 main.py 다중 실행 ###
    def execute_cmd(self):
        """
        [Issue] : epoch 시간이 너무 오래 걸림
        [Solution]
            1. 종목 개수 조절
                : 전체 종목 -> KOSPI 200 
            2. main.py의 탐험수 조절
                : 1000 -> 100
                : 50 고려
        """
        """
        ## KOSPI_200 종목코드 및 종목명 가져오기 ##
        stock_reader=CodeReaderKOSPI() # 모듈 가져오기
        codes,names=stock_reader.read_kospi200_xls() # 종목코드리스트, 종목명리스트
        """
        codes,names=self.process_code()
        
        ## execute_cmd() 얼마나 걸리는지 체크를 위한 시간 변수 ##
        start_time=time.strftime('%Y-%m-%d %H:%M:%S') # run 시작 시간
        today=datetime.strptime(time.strftime('%Y-%m-%d'),'%Y-%m-%d').date() # 오늘 날짜(동적)
        
        ## KOSPI 200 상장 종목들 학습 및 수행결과를 위한 다중 main.py 실행 ##
        for code in codes:
            subprocess.call(['python','main.py','--mode','train','--stock_code',f'{code}','--rl_method','pg','--net','dnn'])
            time.sleep(1)
        
        end_time=time.strftime('%Y-%m-%d %H:%M:%S') # run 종료 시간
        print(f"### [Success][server_main.py][execute_cmd] start_time: {start_time} / end_time: {end_time} ###")
        
        return today
    
    ### Run 함수 ###
    def run(self): # use today
        td=self.execute_cmd()
        self.get_aimodel_table(td)
        self.insert_record_recommend()
    
    ### Run 함수 ###
    def run_test(self): # not use today(== use last record date)
        td=self.execute_cmd()
        self.get_aimodel_table()
        self.insert_record_recommend()

if __name__=="__main__":
    db=DBUpdaterAI()
    ## Run Code ##
    #db.run()
    
    ## Test Code ##
    #today_date=db.execute_cmd()
    #db.get_aimodel_table(today_date)
    #db.get_aimodel_table()
    #db.insert_record_recommend()
    #db.process_code()
    db.run_test()