import requests
import pymysql
from datetime import datetime
import time
import pandas as pd

class ImageEngine:
    def __init__(self):
        self.conn=""
        self.images=[]
        self.primary_keys=[]
    
        ## DB 연결 ##
        try: 
            self.conn=pymysql.connect(host="127.0.0.1", user="root", password="", db="testcapstone", charset="utf8")
            print("### [Success][parsing_news.py] DB: testcapstone ###")
        except:
            print("### [Failed][parsing_news.py] DB: testcapstone ###]")
            exit(0)
    
    ### 소멸자 ###
    def __del__(self):
        self.conn.close()
    
    def get_news_articles_title(self):
        titles=[]
        
        with self.conn.cursor() as curs:
            curs.execute("""
                         SELECT code,date,title FROM news_articles""")
            result=curs.fetchall()
            for item in result:
                titles.append([item[0],item[1],item[2]])
        
        #print(titles[0])
        return titles
    
    
    def request_naver_image(self):
        titles=self.get_news_articles_title() # news_articles 전체 레코드
        unique_codes=[] # 고유 종목코드 리스트
        
        for item in titles:
            if item[0] not in unique_codes:
                unique_codes.append(item[0])
            self.primary_keys.append([item[0],item[1],item[2]])
                
        #print(len(unique_codes))
        #print(len(self.primary_keys))
        #print(unique_codes)
        #return
        
        ## 네이버 뉴스 API 요청을 위한 URL ##
        url = "https://openapi.naver.com/v1/search/image"

        ## API 요청 헤더 설정 ##
        ## API 요청 헤더 설정 ##
        headers = {
            'X-Naver-Client-Id': '',
            'X-Naver-Client-Secret': ''
        }
        
        idx=1
        for code in unique_codes:
            # 제목 검색이 안되서, code로 대체
            response = requests.get(url, headers=headers, params={'query': code, 'display': 50}) # 'sort':'date'
            
             # API 응답 확인
            if response.status_code == 200:
                data=response.json()
                articles = data['items']
                #print(articles)
                
                num=0
                for article in articles:
                    image_url = article.get('link', '')  # 기사 이미지 URL
                    self.images.append(image_url)
                    num+=1
                print(f"[Success #{idx}][parsing_news_image.py][request_naver_image] {code} / Count articles: {num}")
            else:
                print(f"[Continue #{idx}][parsing_news_image.py][request_naver_image][API 호출 실패:{response.status_code}] {code}")
            idx+=1
            #if idx>2:
            #    break
        
        print()
        #print(len(self.images))
        #print()

        for i in range(len(self.primary_keys)):
            self.primary_keys[i].append(self.images[i])
            item=self.primary_keys[i]
            print(f"[Success 정제 #{i}] {item[0]} / {item[1]} / {item[2]} / {item[3]}")
            #if i==99:
            #    break
        
        """
        for i in range(len(self.primary_keys)):
            item=self.primary_keys[i]
            print(f"[# {i}] {item[0]} / {item[1]} / {item[2]} / {item[3]}")
            if i==99:
                break
        """
        print()
        print(f"Count self.primary_keys: {len(self.primary_keys)}")
        print(f"last self.primary_keys : {self.primary_keys[-1]}")
    
    
    def alter_records(self):
        print()
        with self.conn.cursor() as curs:
            idx=1
            print("news_table ALTER SQL 진행중...")
            for code,date,title,image in self.primary_keys:
                sql=f"""
                UPDATE news_articles
                SET image='{image}'
                WHERE code='{code}' and date='{date}' and title="{title}"
                """
                curs.execute(sql)
                #print(f"[Success #{idx}][parsing_news_image.py][alter_records] {code} / {date}")
                idx+=1
        self.conn.commit()
        print()
        print("All Success!!")
            

if __name__=="__main__":
    engine=ImageEngine()
    #print(len(engine.get_news_articles_title()))
    engine.request_naver_image()
    engine.alter_records()