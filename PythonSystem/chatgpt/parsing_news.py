import requests
import pymysql
import time
import pandas as pd
from datetime import datetime

class NewsEngine:
    ### 생성자 ###
    def __init__(self):
        self.conn="" # mysql 연결자
        self.articles=[] # 뉴스 기사 리스트(형식: [종목코드, 등록일, 제목, 내용, 이미지, URL])
        self.continue_articles=[]
        
        ## DB 연결 ##
        try: 
            self.conn=pymysql.connect(host="127.0.0.1", user="root", password="", db="testcapstone", charset="utf8")
            print("### [Success][parsing_news.py] DB: testcapstone ###")
        except:
            print("### [Failed][parsing_news.py] DB: testcapstone ###]")
            exit(0)
            
        ## news_articles Table 생성 ##
        try:
            with self.conn.cursor() as cur:
                cur.execute("DROP TABLE IF EXISTS news_articles")
                sql="""
                CREATE TABLE IF NOT EXISTS news_articles (
                    code VARCHAR(20),
                    date DATETIME,
                    title VARCHAR(255),
                    content TEXT,
                    image TEXT,
                    url TEXT,
                    PRIMARY KEY (code,date,title)
                )
                """
                cur.execute(sql)
            self.conn.commit()
            print("### [Success][parsing_news.py][__init__] created table news_articles ###")
        except:
            print("### [Failed][parsing_news.py][__init__] Error created table news_articles ###")
            exit(0)
    
    
    ### 소멸자 ###
    def __del__(self):
        self.conn.close()
    
    
    ### 종목코드들 가져오기 ###
    def get_stock_codes(self):
        codes=[]
        
        try:
            with self.conn.cursor() as curs:
                curs.execute("SELECT DISTINCT code FROM daily_chart")
                result=curs.fetchall()
                df=pd.DataFrame(result)
                
                df.columns=["code"]
                
                for item in df.itertuples():
                    codes.append(item[1])
                
                print(f"### [Success][parsing_news.py][get_stock_codes] Count : {len(codes)} ###")
        except:
            print("### [Failed][parsing_news.py][get_stock_codes] Error get stock_codes in DB-daily_chart table ###")
            exit(0)
        
        #print(len(codes))
        #print(codes)
        return codes;
    
    
    ### 네이버 API를 통해 뉴스 가져오기 ###
    def get_news_data(self):
        ## daily_chart에 있는 종목코드들 가져오기 ##
        codes=self.get_stock_codes()
        
        ## 네이버 뉴스 API 요청을 위한 URL ##
        url = "https://openapi.naver.com/v1/search/news.json"

        ## API 요청 헤더 설정 ##
        headers = {
            'X-Naver-Client-Id': '',
            'X-Naver-Client-Secret': ''
        }

        ## 종목코드만큼 뉴스 가져오기 ##
        idx=1
        for code in codes:
            #if idx==10:
            #    break
            # 네이버 뉴스 API 호출
            response = requests.get(url, headers=headers, params={'query': f'{code}', 'display': 50})

            # API 응답 확인
            if response.status_code == 200:
                news_data = response.json()
                item=[code]
                # 기사 정보 파싱
                articles = news_data['items']
                for article in articles:
                    image_url = ''  # 기사 이미지 URL
                    title = article.get('title', '')      # 기사 제목
                    description = article.get('description', '')  # 기사 내용
                    pub_date = article.get('pubDate', '') # 기사 등록일 (str 반환)
                    article_url = article.get('link', '') # 기사 URL (네이버)
                    
                    pub_date_date = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
                    date = pub_date_date.strftime('%Y-%m-%d %H:%M:%S')
                    
                    item.append(date)
                    item.append(title)
                    item.append(description)
                    item.append(image_url)
                    item.append(article_url)
                
                    # self.articles에 해당 종목코드 기사 레코드 넣기
                    self.articles.append(item)
                    print(f"[Success #{idx}][parsing_news.py][get_news_data] {code} / {item[1]} / {item[2]}")
                    item=[code]
            else:
                print(f"[Continue #{idx}][parsing_news.py][get_news_data][API 호출 실패:{response.status_code}] {code}")
                self.continue_articles.append(code)
            idx+=1
            time.sleep(1)
        
        ## 결과 ##
        print()
        print(f"Count to self.articles : {len(self.articles)}")
        print(f"Count to self.cotinue_articles : {len(self.continue_articles)}")
        print()
        print(self.articles[0])
        
        
    ### 가져온 뉴스 news_articles 테이블에 삽입 ###
    def insert_news_data(self):
        with self.conn.cursor() as curs:
            idx=1
            for item in self.articles:
                if item[0] in self.continue_articles:
                    idx+=1
                    print(f"[Contine #{idx}][parsing_news.py][insert_news_data] insert {item[0]}")
                    continue
                sql = """
                INSERT INTO news_articles (code, date, title, content, image, url) 
                VALUES (%s, %s, %s, %s, %s, %s) 
                ON DUPLICATE KEY UPDATE 
                date = VALUES(date),
                title = VALUES(title),
                content = VALUES(content),
                image = VALUES(image),
                url = VALUES(url)
                """
                curs.execute(sql,item)
                print(f"[Success #{idx}][parsing_news.py][insert_news_data] insert {item[0]}")
                idx+=1
        self.conn.commit()
        print()
        print("### [Success][parsing_news.py][insert_news_data] inserted records ###")


if __name__=="__main__":
    engine=NewsEngine()
    #t=engine.get_stock_codes()
    engine.get_news_data()
    engine.insert_news_data()