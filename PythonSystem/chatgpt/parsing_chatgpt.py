# API Keys
# 

import pymysql
import pandas as pd
import time,re
from datetime import datetime
from openai import OpenAI

class GPTEngine:
    ### 생성자 ###
    def __init__(self):
        self.conn="" # mysql 연결자
        
        ## DB 연결 ##
        try: 
            self.conn=pymysql.connect(host="127.0.0.1", user="root", password="비밀번호", db="testcapstone", charset="utf8")
            print("### [Success][parsing_chatgpt.py][__init__] DB: testcapstone ###")
        except:
            print("### [Failed][parsing_chatgpt.py][__init__] DB: testcapstone ###]")
            exit(0)

        ## DB Table Create : chatgpt_recommend_trend ##
        try:
            with self.conn.cursor() as cur:
                cur.execute("DROP TABLE IF EXISTS chatgpt_recommend_trend")
                sql="""
                CREATE TABLE IF NOT EXISTS chatgpt_recommend_trend (
                    code VARCHAR(20),
                    content TEXT,
                    PRIMARY KEY (code)
                )
                """
                cur.execute(sql)
            self.conn.commit()
            print("### [Success][parsing_chatgpt.py][__init__] Drop & Created table chatgpt_recommend_trend ###")
        except:
            print("### [Failed][parsing_chatgpt.py][__init__] Error created table chatgpt_recommend_trend ###")
            exit(0)
            
        ## DB Table Create : recommend_news_articles_keywords ##
        try:
            with self.conn.cursor() as cur:
                cur.execute("DROP TABLE IF EXISTS recommend_news_articles_keywords")
                sql="""
                CREATE TABLE IF NOT EXISTS recommend_news_articles_keywords (
                    code VARCHAR(20),
                    keyword1 TEXT,
                    keyword2 TEXT,
                    keyword3 TEXT,
                    keyword4 TEXT,
                    keyword5 TEXT,
                    PRIMARY KEY (code)
                )
                """
                cur.execute(sql)
            self.conn.commit()
            print("### [Success][parsing_chatgpt.py][__init__] Drop & Created table recommend_news_articles_keywords ###")
        except:
            print("### [Failed][parsing_chatgpt.py][__init__] Error created table recommend_news_articles_keywords ###")
            exit(0)
        
        ## DB Table Create : recommend_news_articles_emotion ##
        try:
            with self.conn.cursor() as cur:
                cur.execute("DROP TABLE IF EXISTS recommend_news_articles_emotion") #수정코드
                sql="""
                CREATE TABLE IF NOT EXISTS recommend_news_articles_emotion (
                    code VARCHAR(20),
                    date DATETIME,
                    title VARCHAR(255),
                    score int,
                    PRIMARY KEY (code,date,title)
                )
                """
                cur.execute(sql)
            self.conn.commit()
            print("### [Success][parsing_chatgpt.py][__init__] Drop & Created table recommend_news_articles_emotion ###")
        except:
            print("### [Failed][parsing_chatgpt.py][__init__] Error created table recommend_news_articles_emotion ###")
            exit(0)
        
        
    ### 소멸자 ###
    def __del__(self):
        self.conn.close()
    
    
    ### 차트 데이터 가져오기 : recommend, daily_chart###
    def get_daily_chart(self):
        df=""
        with self.conn.cursor() as curs:
            sql="""
            SELECT r.code, d.date, d.open, d.high, d.low, d.close, d.volume
            FROM recommend r, daily_chart d
            WHERE r.code=d.code
            """
            curs.execute(sql)
            result=curs.fetchall()
            df=pd.DataFrame(result)
        
        df.columns=['code','date','open','high','low','close','volume']
        #df=df[df['date'] >= datetime.strptime('2024-03-14', '%Y-%m-%d').date()]
        
        #print(df)
        print("### [Success][parsing_chatgpt.py][get_daily_chart] Getted to All Records On daily_chart Table ###")
        return df
    
    ### Token Limit Test: 특정 종목코드 차트 데이터 가져오기 ###
    def get_daily_chart_test(self):
        df=""
        with self.conn.cursor() as curs:
            sql="""
            SELECT code, date, open, high, low, close, volume FROM daily_chart WHERE code='006110';
            """
            curs.execute(sql)
            result=curs.fetchall()
            df=pd.DataFrame(result)
        
        #print(df)
        df.columns=['code','date','open','high','low','close','volume']
        return df
    
    ### 뉴스 데이터 가져오기 : recommend, news_articles###
    def get_news_table(self):
        df=""
        with self.conn.cursor() as curs:
            sql="""
            SELECT r.code, n.date, n.title, n.content 
            FROM recommend r, news_articles n
            WHERE r.code=n.code
            """
            curs.execute(sql)
            result=curs.fetchall()
            df=pd.DataFrame(result)
        
        df.columns=['code','date','title','content']
        df=df.sort_values('date')
        ## 기간 필터링 생략
        #print(df)
        print("### [Success][parsing_chatgpt.py][get_news_table] Getted to All Records On news_articles Table ###")
        return df
    
    ### Token Limit Test: 특정 종목코드 뉴스 데이터 가져오기 ###
    def get_news_table_test(self):
        df=""
        with self.conn.cursor() as curs:
            sql="""
            SELECT code,date,title,content FROM news_articles WHERE code='006110'
            """
            curs.execute(sql)
            result=curs.fetchall()
            df=pd.DataFrame(result)
        
        df.columns=['code','date','title','content']
        df=df.sort_values('date')
        return df
    
    ### 데이터 정제 : 각 종목 뉴스 데이터의 시작등록일, 종료등록일을 이용하여 차트데이터 기간 필터링 ###
    def preprocess(self):
        chart_df=self.get_daily_chart() # 전체 차트 데이터
        news_df=self.get_news_table() # 전체 뉴스 데이터
        pre_chart_df=pd.DataFrame() # 기간 필터링된 df (초기: 빈 데이터프레임)
        
        #print(chart_df)
        
        # 고유 종목코드들을 순회
        for code in pd.unique(chart_df['code']):
            tmp_df=news_df[news_df['code']==code] # 해당 종목코드만 담고있는 뉴스 데이터프레임
            tmp_chart_df=chart_df[chart_df['code']==code] # 해당 종목코드만 담고있는 차트 데이터프레임
            start_date=datetime.strptime(str(tmp_df.iloc[0]['date']),'%Y-%m-%d %H:%M:%S').date() # 뉴스 등록일 시작
            end_date=datetime.strptime(str(tmp_df.iloc[-1]['date']),'%Y-%m-%d %H:%M:%S').date() # 뉴스 등록일 마지막
            ## 수정: 해당 종목코드의 차트 데이터프레임 개수가 150개 이상이면, 마지막 행 기준 150개 슬라이스 ##
            concat_tmp_df=tmp_chart_df[(tmp_chart_df['date']>=start_date) & (tmp_chart_df['date']<=end_date)]
            if len(concat_tmp_df)>150: # Token 개수 조절은 이 숫자 바꾸면 됨.
                concat_tmp_df=concat_tmp_df.tail(150) # 얘도 마찬가지
            pre_chart_df=pd.concat([pre_chart_df, concat_tmp_df])
            ##########
        
        """
        print("####### preprocess ########")
        print(pre_chart_df[pre_chart_df['code']=='267260'].shape)
        print()
        print()
        print(news_df[news_df['code']=='267260'].shape)
        print("###########################")
        #print(pre_chart_df)
        """
        
        # 출력문 수정 : pre_chart_df 및 news_df 개수 출력 추가
        print(f"""### [Success][parsing_chatgpt.py][preprocess] chart_df Date-Filtering >> len(chart): {len(pre_chart_df)} / len(news): {len(news_df)} ###
        """)
        return pre_chart_df,news_df # 뉴스 기간에 맞춘 차트데이터, 뉴스데이터 리턴
    
    ### Token Limit Test : 특정 코드 데이터로 데이터 정제 ###
    def preprocess_test(self):
        chart_df=self.get_daily_chart_test() # 전체 차트 데이터
        news_df=self.get_news_table_test() # 전체 뉴스 데이터
        pre_chart_df=pd.DataFrame() # 기간 필터링된 df (초기: 빈 데이터프레임)
        
        start_date=datetime.strptime(str(news_df.iloc[0]['date']),'%Y-%m-%d %H:%M:%S').date() # 뉴스 등록일 시작
        end_date=datetime.strptime(str(news_df.iloc[-1]['date']),'%Y-%m-%d %H:%M:%S').date() # 뉴스 등록일 마지막

        pre_chart_df=pd.concat([pre_chart_df, chart_df[(chart_df['date']>=start_date) & (chart_df['date']<=end_date)]])
        pre_chart_df=pre_chart_df.tail(150)
        print()
        print("####### preprocess_test #########")
        print(pre_chart_df.shape)
        print(len(pre_chart_df))
        print(f"start date: {pre_chart_df.iloc[0]['date']}")
        print(f"end date: {pre_chart_df.iloc[-1]['date']}")
        print()
        print(news_df.shape)
        print(f"start date: {news_df.iloc[0]['date']}")
        print(f"end date: {news_df.iloc[-1]['date']}")
        print("#################################")
        return pre_chart_df, news_df
        
    ### 추천종목-차트 데이터와 뉴스 데이터 chatgpt 요청 : 차트데이터와 뉴스데이터 상관관계 분석을 통한 주가 동향 분석 ###
    def request_chatgpt_chart_news(self):
        print()
        print("###################### [request_chatgpt_chart_news_test] ########################")
        print()
        
        chart_df, news_df = self.preprocess()
        result_list=[] # recommend 종목코드들 content를 모두 담는 리스트
        
        ## 종목코드마다, 주가 동향 분석 chatgpt에 요청하기 ##
        idx=1; print()
        for code in pd.unique(chart_df['code']):
            # Data Set
            code_chart_df=chart_df[chart_df['code']==code]
            code_news_df=news_df[news_df['code']==code]
            
            # 수정 : code_chart_df 및 code_news_df 개수 출력
            print(f"### [Success #{code}][request_chatgpt_chart_news > preprocess callback] len(chart):{len(code_chart_df)} / len(news):{len(code_news_df)} ###")
            # Prompt
            messages = []
            messages.append({"role": "system", "content": "You are a helpful assistant."})
            messages.append({"role": "user", "content": f"""
                    {code} 종목코드에 대한 차트 데이터와 뉴스 데이터의 상관관계 분석을 바탕으로, 주가 동향 분석 결과 설명을 요청드립니다."""})
            
            # Data-Tuning : daily_chart
            for _, row in code_chart_df.iterrows():
                # 수정 : Token 개수 조절을 위해 code는 메시지에 안넣음.
                messages.append({"role": "user", "content": f"{row['date']} {row['open']} {row['high']} {row['low']} {row['close']} {row['volume']}"})
            
            # Data-Tuning : news_articles
            for _, row in code_news_df.iterrows():
                # 수정: Token 개수 조절을 위해 code는 메시지에 안넣음.
                messages.append({"role": "user", "content": f"""{row['date']} {row['title']} {row['content']}"""})
            
            # Setting ChatGPT
            openai = OpenAI(api_key="")
            
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            
            # chatgpt 결과 받기
            result=response.choices[0].message.content
            
            # 리스트에 추가
            result_list.append([code, result])
            
            # 성공 결과 출력
            print(f"[Success #{idx}][parsing_chatgpt.py][request_chatgpt_chart_news] {code} / {result[:len(result)//2+1]}...")
            print()
            idx+=1
            # 혹시 모를 트래픽 방지
            time.sleep(3)
        
        ## 각 종목코드에 대한 분석 결과 확인 ##
        """
        for code,content in result_list:
            print(f"######## {code} ##########")
            print(content)
            print(f"##########################")
            print()
        """
        ## chatgpt_recommend_trend 테이블에 삽입 ##
        #try:
        with self.conn.cursor() as curs:
            for code,content in result_list:
                sql=f"""INSERT INTO chatgpt_recommend_trend VALUES ('{code}',"{content}")"""
                curs.execute(sql)
        self.conn.commit()
        print()
        print("### [Success][parsing_chatgpt.py][request_chatgpt_chart_news] MySQL: Inserted Records to Table ###")
        print("######################################################################")
        print()
        #except:
            #print("### [Failed][parsing_chatgpt.py][request_chatgpt_chart_news] Error MySQL: Insert Record to Table ###")
        
    ### Token Limit Test : 추천종목-차트 데이터와 뉴스 데이터 chatgpt 요청 : 차트데이터와 뉴스데이터 상관관계 분석을 통한 주가 동향 분석 ###
    def request_chatgpt_chart_news_test(self):
        print()
        print("###################### [request_chatgpt_chart_news_test] ########################")
        print()
        
        chart_df, news_df = self.preprocess_test()
        code=chart_df.iloc[0]['code']
        
        # Prompt
        messages = []
        messages.append({"role": "system", "content": "You are a helpful assistant."})
        messages.append({"role": "user", "content": 
            f"""
            {code} 종목코드에 대한 차트 데이터와 뉴스 데이터의 상관관계 분석을 바탕으로, 주가 동향 분석 결과 설명을 요청드립니다.
            """})
            
        # Data-Tuning : daily_chart
        for _, row in chart_df.iterrows():
            messages.append({"role": "user", "content": f"{row['date']} {row['open']} {row['high']} {row['low']} {row['close']} {row['volume']}"})
            
        # Data-Tuning : news_articles
        for _, row in news_df.iterrows():
            messages.append({"role": "user", "content": f"""{row['date']} {row['title']} {row['content']}"""})

        # Setting ChatGPT
        openai = OpenAI(api_key="")
            
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
            
        # chatgpt 결과 받기
        result=response.choices[0].message.content
        
        print(f"[Success Test][parsing_chatgpt.py][request_chatgpt_chart_news_test] {code} / {result[:len(result)//2+1]}...")
        print()
        print("######################################################################")
        
        
        
    ### 추천종목-뉴스 데이터 chatgpt 요청: 주요키워드 ###
    def request_chatgpt_news_keywords(self):
        print()
        print("###################### [request_chatgpt_news_keywords] ########################")
        print()
        
        news_df=self.get_news_table()
        result_list=[]
        
        ## 종목코드마다, 주요키워드 chatgpt에게 요청 ##
        print()
        idx=1
        for code in pd.unique(news_df['code']):
            # Data Set
            code_news_df=news_df[news_df['code']==code]
            
            # Prompt
            messages = []

            messages.append({"role": "system", "content": "You are a helpful assistant."})
            
            # Data-Tuning : news_articles
            for _, row in code_news_df.iterrows():
                messages.append({"role": "user", "content": f"{row['code']} {row['date']} {row['title']} {row['content']}"})
                
            messages.append({"role":"user", "content": """
                            각 뉴스 기사를 종합하여, 주가와 사업성과 관련된 주요 단어 5개 선정하여, '결과: 주요단어1, 주요단어2, 주요단어3, 주요단어4, 주요단어5' 형식으로만 출력되도록 요청드립니다."""})
            
            # Setting ChatGPT
            openai = OpenAI(api_key="")
            
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            
            # 결과받기
            result=response.choices[0].message.content
            #print(result)
            
            # 결과 필터링
            result_filter=[code]
            for item in result.replace(' ','')[3:].split(','):
                result_filter.append(item[6:]) if "주요단어" in item else result_filter.append(item)
            #print(result_filter)
            result_list.append(result_filter)
            
            # 성공 결과 출력
            print(f"[Success #{idx}][parsing_chatgpt.py][request_chatgpt_news_keywords] {code} / {result_filter}")
            print()
            idx+=1
            time.sleep(3)
        
        ## recommend_news_articles_keywords 테이블에 삽입 ##
        with self.conn.cursor() as curs:
            for code,word1,word2,word3,word4,word5 in result_list:
                sql=f"""INSERT INTO recommend_news_articles_keywords VALUES ("{code}","{word1}","{word2}","{word3}","{word4}","{word5}")"""
                curs.execute(sql)
        self.conn.commit()
        print()
        print("### [Success][parsing_chatgpt.py][request_chatgpt_news_keywords] MySQL: Inserted Records to Table ###")
        print("######################################################################")
        print()
    
    
    ### 추천종목-뉴스 데이터 chatgpt 요청: 긍정/중립/부정 ###
    def request_chatgpt_news_emotion(self):
        print()
        print("###################### [request_chatgpt_news_emotion] ########################")
        print()
        
        news_df=self.get_news_table() # Data Set
        result_list=[] # 결과 저장 리스트
        
        ## 각 기사 데이터 감성점수 매기기 ##
        print()
        idx=1
        for _,row in news_df.iterrows():
            #if idx==5: break
            # Prompt
            messages = []
            messages.append({"role": "system", "content": "You are a helpful assistant."})
            messages.append({"role": "user", "content": f"{row['code']} {row['date']} {row['title']} {row['content']}"})
            messages.append({"role":"user", "content": 
                        "해당 종목코드 관련 뉴스 내용에 대해 감성 분석을 수행합니다.\n" + 
                        f"종목코드: {row['code']}\n" +
                        f"등록일: {row['date']}\n" +
                        f"제목: {row['title']}\n" +
                        f"내용: {row['content']}\n" +
                        f"감성을 분석하여 해당 내용이 긍정적인지, 중립적인지, 부정적인지 판단하여 '결과: 긍정적' 형식으로만 출력되도록 요청합니다."})

            # Setting ChatGPT
            openai = OpenAI(api_key="")
            
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            
            # 결과받기
            result=response.choices[0].message.content
            #print(result)
            
            # 결과 필터링
            result_filter=1 if "긍정" in result else 0 if "중립" in result else -1
            #print(result_filter)
            
            # 결과 저장 리스트에 추가.
            result_list.append([row['code'], row['date'], row['title'], result_filter])
            
            # 성공 결과 출력
            print(f"[Success #{idx}][parsing_chatgpt.py][request_chatgpt_news_emotion] {row['code']} / {result} / {result_filter}")
            print()
            idx+=1
            time.sleep(1)

        ## recommend_news_articles_emotion 테이블에 삽입 ## 
        with self.conn.cursor() as curs:
            for code,date,title,score in result_list:
                sql = f"""
                INSERT INTO recommend_news_articles_emotion (code, date, title, score) 
                VALUES ('{code}', '{date}', "{title}", {score})
                ON DUPLICATE KEY UPDATE
                code = VALUES(code),
                date = VALUES(date),
                title = VALUES(title),
                score = VALUES(score)
                """
                curs.execute(sql)
        self.conn.commit()
        print()
        print("### [Success][parsing_chatgpt.py][request_chatgpt_news_emotion] MySQL: Inserted Records to Table ###")
        print("######################################################################")
        print()
    
    ### run 추천종목 메서드들 : 주가동향분석, 주요키워드, 감성점수 ###
    def recommend_run(self):
        self.request_chatgpt_chart_news()
        time.sleep(1)
        self.request_chatgpt_news_keywords()
        time.sleep(1)
        self.request_chatgpt_news_emotion()  


if __name__=="__main__":
    engine=GPTEngine()
    
    ## TEST : Token Limit ##
    #c,d=engine.preprocess_test() # Token Limit Test : 특정 코드 데이터 정제
    #engine.request_chatgpt_chart_news_test() # Token Limit Test : 주가 동향분석
    
    ## TEST ##
    #print(engine.get_daily_chart()) # 차트 데이터 가져오기
    #print(engine.get_news_table()) # 뉴스 데이터 가져오기
    #a,b=engine.preprocess() # 데이터 정제
    #print(engine.get_daily_chart_test()) # Token Limit Test : 특정 코드 차트 데이터 가져오기
    #print(engine.get_news_table_test()) # Token Limit Test : 특정 코드 뉴스 데이터 가져오기
    #engine.request_chatgpt_chart_news() # 추천종목: 차트데이터+뉴스데이터 주가 동향 분석
    #engine.request_chatgpt_news_keywords() # 추천종목: 뉴스데이터 키워드 선정
    #engine.request_chatgpt_news_emotion() # 추천종목: 뉴스데이터 감성점수
    
    ## RUN : 추천종목 ##
    engine.recommend_run()