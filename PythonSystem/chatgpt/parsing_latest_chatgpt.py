import pandas as pd
import pymysql
import time
from openai import OpenAI

class LatestEngine:
    ### 생성자 ###
    def __init__(self):
        self.conn=""
        
        ## DB 연결 ##
        try: 
            self.conn=pymysql.connect(host="127.0.0.1", user="root", password="", db="testcapstone", charset="utf8")
            print("### [Success][parsing_latest_chatgpt.py][__init__] DB: testcapstone ###")
        except:
            print("### [Failed][parsing_latest_chatgpt.py][__init__] DB: testcapstone ###]")
            exit(0)
        
         ## DB Table Create : home_news_articles (index 최신뉴스) ##
        try:
            with self.conn.cursor() as cur:
                cur.execute("DROP TABLE IF EXISTS home_news_articles")
                sql="""
                CREATE TABLE IF NOT EXISTS home_news_articles (
                    code VARCHAR(20),
                    date DATETIME,
                    title VARCHAR(255),
                    score int,
                    summary TEXT,
                    keyword1 TEXT,
                    keyword2 TEXT,
                    keyword3 TEXT,
                    keyword4 TEXT,
                    keyword5 TEXT,
                    image TEXT,
                    url TEXT,
                    content TEXT,
                    PRIMARY KEY (code)
                )
                """
                cur.execute(sql)
            self.conn.commit()
            print("### [Success][parsing_latest_chatgpt.py][__init__] Drop & Create table > home_news_articles ###")
        except:
            print("### [Failed][parsing_latest_chatgpt.py][__init__] Error Drop & Create table > home_news_articles ###")
            exit(0)
    
    ### 시가총액 기준, 상위 28개 종목코드 및 종목명 리스트 리턴 ###
    def get_codes_names_excel(self):
        krx_list=pd.read_html("E:\학교\학교개인프로젝트모음\chatgpt\data\상장법인목록.xls")
        krx_list[0].종목코드=krx_list[0].종목코드.map("{:06d}".format)
        #print(len(krx_list))
        
        df=pd.concat([krx_list[0].회사명, krx_list[0].종목코드], axis=1)
        
        selected_companies = [
            '삼성전자', 'SK하이닉스', 'LG에너지솔루션', '삼성바이오로직스',
            '현대자동차', '기아', '셀트리온', 'SK이노베이션',
            'POSCO홀딩스', 'NAVER', '삼성SDI', 'LG화학', 
            '삼성물산', 'KB금융', '현대모비스', '신한지주',
            '카카오', '포스코퓨처엠', '삼성생명', '하나금융지주',
            '메리츠금융지주', 'LG전자', '하이브', '한국전력공사',
            '한미반도체', 'SK', 'LG', '카카오뱅크'
        ]
        selected_df = df[df['회사명'].isin(selected_companies)]
        #print(selected_df)

        stock_codes=[code for code in selected_df.종목코드]
        stock_names=[name for name in selected_df.회사명]
        
        #print(len(stock_codes))
        #print(stock_names)
        return stock_codes, stock_names
        
    ### 전체 뉴스 데이터 가져와서, 상위 28개 종목들의 최신 뉴스 행들만 리턴 ###
    def get_news_data_selected(self):
        df="" # 전체 뉴스 데이터 저장 변수(리턴x)
        codes,names=self.get_codes_names_excel() # 상위 28개 종목코드, 종목명 리스트 가져오기
        
        sql_codes=[f"code='{code}'" for code in codes] # sql 명령어의 where절에 쓰일 문자열 작업
        #print(sql_codes)
        
        with self.conn.cursor() as curs:
            sql="SELECT * FROM news_articles WHERE "
            # WHERE 절 뒤에 조건 문자열 추가
            for idx in range(len(sql_codes)):
                if idx==len(sql_codes)-1:
                    sql+=sql_codes[idx]
                else:
                    sql+=sql_codes[idx]+" or "
            curs.execute(sql)
            result=curs.fetchall()
            df=pd.DataFrame(result)
        
        # 데이터프레임 컬럼명 변경
        df.columns=['code','date','title','content','image','url']
        #print(df)
        
        ## 필터링 ##
        result_df=pd.DataFrame() # 빈 데이터프레임 생성.(리턴대상)
        
        for code in codes:
            tmp_df=df[df['code']==code].sort_values(by='date') # 날짜 오름차순 정렬
            result_df=pd.concat([result_df,tmp_df.tail(1)]) # 가장 마지막행만 추가(해당 종목코드 최신 뉴스)
            #print(result_df)
            #break
        #print(result_df)
        return result_df
        
    ### chatgpt 요청 : 각 뉴스 기사 감성점수 ###
    # 초기 비용: 0.76~0.77 / 실행 후 비용: 0.77#
    def request_chatgpt_home_news_emotion(self):
        print()
        print("################# request_chatgpt_home_news_emotion #####################")
        
        home_news_articles_df = self.get_news_data_selected()
        result_list=[]
        
        idx=1;print()
        for _,row in home_news_articles_df.iterrows():
            # Prompt
            messages = []
            messages.append({"role": "system", "content": "You are a helpful assistant."})
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
            
            # 결과 필터링
            count_list=[result.count("긍정"),result.count("중립"),result.count("부정")]
            select_list=[1,0,-1]
            result_filter=select_list[count_list.index(max(count_list))]
            
            # 결과 저장 리스트에 추가.
            result_list.append([row['code'], row['date'], row['title'], row['content'], row['image'], row['url'], result_filter])
            
            # 성공 결과 출력
            print(f"[Success #{idx}][parsing_latest_chatgpt.py][request_chatgpt_home_news_emotion] {row['code']} / {result} / {result_filter}")
            print()
            idx+=1
            time.sleep(1)
        
        print("######################################################################")
        print()
        return result_list
            
    
    ### chatgpt 요청 : 각 뉴스 기사 주요키워드 ###
    # 초기 비용: 0.77 / 실행 후 비용: #
    def request_chatgpt_home_news_keywords(self):
        print()
        print("################# request_chatgpt_home_news_keywords #####################")
        
        home_news_articles_df = self.get_news_data_selected()
        result_list=[]
        
        idx=1;print()
        for _,row in home_news_articles_df.iterrows():
            # Prompt
            messages = []
            messages.append({"role": "system", "content": "You are a helpful assistant."})
            messages.append({"role":"user", "content":
                "해당 뉴스 기사의 주가와 사업성과 관련된 주요 단어 5개 선정하여, '결과: 주요단어1, 주요단어2, 주요단어3, 주요단어4, 주요단어5' 형식으로만 출력되도록 요청드립니다.\n"+
                f"종목코드: {row['code']}\n"+
                f"제목: {row['title']}\n" +
                f"내용: {row['content']}\n"})
            
            # Setting ChatGPT
            openai = OpenAI(api_key="")
            
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            
            # 결과받기
            result=response.choices[0].message.content
            #print(result)
            #break
            # 결과 필터링
            result_filter=[row['code']]
            for item in result.replace(' ','')[3:].split(','):
                result_filter.append(item[6:]) if "주요단어" in item else result_filter.append(item)
            #print(result_filter)
            result_list.append(result_filter)
            
            # 성공 결과 출력
            print(f"[Success #{idx}][parsing_latest_chatgpt.py][request_chatgpt_home_news_keywords] {row['code']} / {result_filter}")
            print()
            idx+=1
            time.sleep(1)
        
        print("######################################################################")
        print()
        return result_list
    
    
    ### chatgpt 요청 : 각 뉴스 기사 뉴스요약 ###
    # 초기 비용:  / 실행 후 비용: #
    def request_chatgpt_home_news_summary(self):
        print()
        print("################# request_chatgpt_home_news_summary #####################")
        
        home_news_articles_df = self.get_news_data_selected()
        result_list=[]
        
        idx=1;print()
        for _,row in home_news_articles_df.iterrows():
            # Prompt
            messages = []
            messages.append({"role": "system", "content": "You are a helpful assistant."})
            messages.append({"role":"user", "content":
                "해당 종목코드에 대한 뉴스 기사의 자세한 요약을 요청드립니다.\n"+
                f"종목코드: {row['code']}\n"+
                f"제목: {row['title']}\n" +
                f"내용: {row['content']}\n"})
            
            # Setting ChatGPT
            openai = OpenAI(api_key="")
            
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            
            # 결과받기
            result=response.choices[0].message.content
            #print(result)
            #break
            
            # 결과 필터링
            result_filter=result.replace('\n',' ')
            result_list.append([row['code'], result_filter])

            # 성공 결과 출력
            print(f"[Success #{idx}][parsing_latest_chatgpt.py][request_chatgpt_home_news_summary] {row['code']} / {result_filter}")
            print()
            idx+=1
            time.sleep(1)
        
        print("######################################################################")
        print()
        return result_list
    
    
    ### run 함수: chatgpt 3가지 작업 실행 & 정제 & home_news_articles 저장 ###
    def run(self):
        ## ChatGPT 3가지 작업 응답 받기 ##
        emotions=self.request_chatgpt_home_news_emotion() # 감성점수 반환 리스트 / 형식: [code, date, title, content, image, url, result_filter]
        keywords=self.request_chatgpt_home_news_keywords() # 키워드 반환 리스트 / 형식: [word1, word2, word3, word4, word5]
        summarys=self.request_chatgpt_home_news_summary() # 요약 반환 리스트 / 형식: [code, result_filter]
    
        ## DB에 삽입하기 위한 삽입대상리스트 정제 ##
        # 테이블 형식: code, date, title, score, summary, keyword1, keyword2, keyword3, keyword4, keyword5, image, url, content#
        insert_list=[[e[0],e[1],e[2],e[6],s[1],k[1],k[2],k[3],k[4],k[5],e[4],e[5],e[3]] for e,k,s in zip(emotions,keywords,summarys)]
        
        ## home_news_articles에 삽입##
        with self.conn.cursor() as curs:
            for item in insert_list:
                sql=f"""
                INSERT INTO home_news_articles VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                curs.execute(sql,item)
        self.conn.commit()
        
        ## 성공 여부 출력 ##
        print("### [Success][parsing_latest_chatgpt.py][run] Insert to home_news_articles ###")
        print()
                
        
if __name__=="__main__":
    engine=LatestEngine()
    ### TEST ###
    #a,b=engine.get_codes_names_excel() # 종목코드, 종목명 리스트
    #print(engine.get_news_data_selected()) # news_articles 테이블 상위28개종목만 가져오기
    #print(engine.request_chatgpt_home_news_emotion()) # chatgpt 요청 : 감성점수
    #print(*engine.request_chatgpt_home_news_keywords(), end="\n") # chatgpt 요청 : 주요키워드
    #print("\n".join(map(str,engine.request_chatgpt_home_news_summary()))) # chatgpt 요청 : 요약
    
    ### RUN ###
    engine.run() # 초기비용: 0.78~0.79달러 / 2번실행비용: 0.83달러(오차+=1)
                 # 초기비용: 0.83달러 / 1번실행비용:중단 / 2번실행비용: 0.87