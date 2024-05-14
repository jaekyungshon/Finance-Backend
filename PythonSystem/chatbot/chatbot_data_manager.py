import pandas as pd
from datetime import datetime
import pymysql
from openai import OpenAI

# 최종 확정 알고리즘.
"""
예측성/정보성/판단성 질문에 대한 데이터를 어떤 방법으로 동적 처리를 해야하는가?
=> 핵심 기준: '비교가 필요한 질문인가?'


### 데이터 관리 클래스 ###
class DataManager:
    def __init__(self):
        self.conn=pymysql.connect(host="127.0.0.1", user="root", password="비밀번호", db="testcapstone", charset="utf8")
        self.df_company="" # 기업정보(종목코드,종목명)
        self.df_chart="" # 차트 데이터
        self.df_news="" # 뉴스 데이터
        self.df_nq="" # 재무제표 데이터
        
        self.init_method()
        
    def __del__(self):
        self.conn.close()
    
    ### 생성자 호출시: 각종 데이터 미리 준비하는 함수###
    def init_method(self):
        ## 차트데이터, 뉴스 데이터, 기업정보데이터 ##
        df_list=[]
        
        for table_name in ['daily_chart', 'news_articles', 'company_info']:
            with self.conn.cursor() as curs:
                curs.execute(f"SELECT * FROM {table_name}")
                result=curs.fetchall()
                df_list.append(pd.DataFrame(result))
        
        self.df_chart=df_list[0]; self.df_news=df_list[1]; self.df_company=df_list[2]
        self.df_chart.columns=['code','date','time','open','high','low','close','volume']
        self.df_news.columns=['code', 'date', 'title', 'content', 'image', 'url']
        self.df_company.columns=['code','company']
        
        ## 재무제표 데이터 ##
        df=pd.read_csv("E:\\학교\\학교개인프로젝트모음\\chatbot\\learner_data\\financial\\2023_종합_재무제표.csv")
        df['종목코드'] = df['종목코드'].apply(lambda x: f"{x:06}")
        self.df_nq=df
        #print(self.df_nq.head(5))

    ### 사용자 입력 질문(문자열) 필터링 및 타겟 기업명 찾기 ###
    def query_filter(self, query):
        # 텍스트 준비 #
        text=f"""
        다음의 내용이 있어.
            
        '{query}'
            
        너는 해당 텍스트를 분석하는 임무를 맡게 되었어. 
        만약, 해당 텍스트가 산업(업종)간 비교가 필요한 텍스트라고 판단된다면, 해당 산업(업종)에서 유명한 상장 기업 5개만 너가 임의로 선정해줘.
        이때, 아래에서 내가 지정한 답변 형식으로 출력해줘.
        반대로, 산업(업종)간 비교가 필요하지 않은 텍스트라고 판단된다면 아래에서 내가 지정한 답변 형식으로 출력해줘.

        나에게 답변할 출력 형식은 다음과 같아.

        먼저, 산업(업종)간 비교가 필요하다고 판단된 경우의 출력 형식이야.
        '
        판단여부: True
        기업명: 회사1명(종목코드 6자리), ... , 회사N명(종목코드 6자리)
        '

        다음으로, 산업(업종)간 비교가 필요하지 않다고 판단된 경우의 출력 형식이야.
        '
        판단여부: False
        '
        """
        
        # prompt 설정 #
        messages=[{"role": "system", "content": "You are a helpful assistant."}]
        messages.append({"role":"user", "content": text})
        
        # 필요 변수 설정 #
        bool_contain_flag=False # query에 원하는 내용 포함 여부 체크 변수
        request_chatgpt_count=1 # chatgpt 요청 카운팅
        target_companys=[] # 타겟 회사명들. (형식1: ['삼성전자(005930)',...] / 형식2: ['삼성전자'])
        
        # Chatgpt에게 대화 요청#
        while not bool_contain_flag: # 원하는 답변 형식이 아니면, 계속 요청 보냄.(최대 5번까지.)
            request_chatgpt_count+=1 # 요청 카운팅 갱신
            # 요청
            openai = OpenAI(api_key="api키")
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            result=response.choices[0].message.content
            
            # 원하는 출력 형식이고, 비교질문인 경우
            if ("True" in result) or ("true" in result):
                # 0. 이상한 답변 예외 처리(다시 요청 보낸다.)
                except_list=['기업1', '기업2', '기업3', '기업4', '기업5', '기업0', '종목코드', '6자리',
                            '회사1', '회사2', '회사3', '회사4', '회사5', '회사0']
                except_check_list=[1 for word in except_list if word in result]
                if len(except_check_list)>0:
                    continue
                # 1. 문자열 줄바꿈문자를 기준으로, 나누기
                result_tmp=result.split("\n")  
                result_filter, result_filter_flag="",False
                # 2-1. '기업명:'이 들어가있는 항목만 추출
                for sentiment in result_tmp:
                    if '기업명:' in sentiment:
                        result_filter=sentiment
                        result_filter_flag=True
                        break
                # 2-2. 없으면, '기업명:'이 result에 나올때까지 다시 요청.
                if not result_filter_flag:
                    continue
                # 3-1. '기업명:' 이후의 문자열 추출.
                # 3-2. ','를 기준으로 나눈 각 문자열을 list에 저장.
                # 3-3. list의 각 항목의 공백/줄바꿈을 제거.
                target_companys = [item.strip() for item in result_filter[result_filter.find('기업명:') + len('기업명:'):].split(',')]
                # 4. 문자열 필터링 완료했으므로, 반복문 탈출
                bool_contain_flag=True
            
            # 원하는 답변형식이고, 비교질문이 아닌 경우
            if ("False" in result) or ("False" in result):
                with self.conn.cursor() as curs:
                    curs.execute("SELECT * FROM company_info")
                    result=curs.fetchall()
                    df_company=pd.DataFrame(result) # DB에서 상장기업정보 가져오기
                    df_company.columns=['code','company']
                    # 사용자 입력 질문에 기업명들어간 것 찾아 리턴할 리스트에 저장하기
                    target_companys=[company for company in df_company['company'] if company in query]
                    bool_contain_flag=True
            
            # 요청 반복 횟수 5번 초과인 경우, 반복문 STOP
            if request_chatgpt_count>=5:
                break
        
        # 만약 필요하면 여기에 작성: (내용) 회사명과 종목코드 리스트로 각각 나누는 작업 #
        # 리턴 변수가 달라져야함.
        
        # 요청해도 원하는 결과를 얻지 못한 경우 -> 예외처리로 이어짐 #
        if not bool_contain_flag:
            return False, []
        # 정상 필터링 완료한 경우 #
        else:
            return True, target_companys
        
    ### query에 맞는 데이터 정제 및 리턴 함수 ###
    def get_datas(self, query, query_type):
        # 예측성/정보성/판단성 질문인 경우 #
        if query_type==1:
            # 프로세스 1) 비교가 필요한 질문인가? - 문자열 필터링
            filter_flag,target_company_names=self.query_filter(query=query)
            if not filter_flag: # 원하는 답변을 못받을 경우
                return "","",""
            
            #has_flag_chart=True if ('주가' in query or '가격' in query) else False # 차트데이터가 필요한가
            chart_datas=[] # 존재 차트데이터를 text형식으로 삽입하는 리스트. (target_companys 개수 맞춰서)
            news_datas=[] # 존재 뉴스데이터를 text 형식으로 삽입하는 리스트.
            finacial_datas=[] # 존재 제무재표를 text 형식으로 삽입하는 리스트.
            for name in target_company_names:
                tmp_text=""
                code=name[name.index('(')+1:-1] if '(' in name else self.df_company.loc[self.df_company['company']==name, 'code'].values[0]
                # 프로세스 2) '주가', '가격' 단어가 질문에 포함되어 있는가?
                if ('주가' in query) or ('가격' in query):
                    if code in pd.unique(self.df_chart['code']):
                        tmp_df=self.df_chart[self.df_chart['code']==code]
                        tmp_df=tmp_df[['date','close','volume']].tail(30) # 최근 30일치 차트데이터
                        tmp_text+=f"다음은 {name}의 차트 데이터이다.\n date close volume\n"
                        for _,row in tmp_df.iterrows():
                            tmp_text+=f"{row.iloc[0]} {row.iloc[1]} {row.iloc[2]}\n"
                        tmp_text+="\n"
                chart_datas.append(tmp_text)
                
                # 프로세스 3-1) 뉴스 데이터가 존재하는가?
                tmp_text=""
                if code in pd.unique(self.df_news['code']):
                    tmp_df=self.df_news[self.df_news['code']==code]
                    tmp_df=tmp_df[['date','content']].tail(30) # 최근 기사 30개
                    tmp_text+=f"다음은 {name}의 뉴스 데이터이다.\n date content\n"
                    for _,row in tmp_df.iterrows():
                        tmp_text+=f"{row.iloc[0]} {row.iloc[1]}\n"
                    tmp_text+="\n"
                news_datas.append(tmp_text)
                
                # 프로세스 3-2) 재무제표 데이터가 존재하는가?
                tmp_text=""
                if code in pd.unique(self.df_nq['종목코드']):
                    tmp_df=self.df_nq[self.df_nq['종목코드']==code]
                    tmp_df=tmp_df[['항목명','당기_4분기말','전기_4분기말']]
                    tmp_df=tmp_df.dropna(axis=0)
                    if tmp_df.shape[0] > 0:
                        tmp_text+=f"다음은 {name}의 재무제표 데이터이다.\n 항목명 당기_4분기말 전기_4분기말\n"
                        for _,row in tmp_df.iterrows():
                            tmp_text+=f"{row.iloc[0]} {row.iloc[1]} {row.iloc[2]}\n"
                        tmp_text+="\n"
                finacial_datas.append(tmp_text)
            
            # 프로세스 4) 데이터 넘겨주기
            return chart_datas, news_datas, finacial_datas   
                
        # 개인정보성 질문인 경우 #
        elif query_type==0:
            return [],[],[]
        # 절차성 질문인 경우(삭제) #
        else:
            return [],[],[]


# if __name__=="__main__":
#     engine=DataManager()
#     #print(engine.df_chart.tail(10))
#     #print(engine.df_nq.head(5))
#     #print(pd.unique(engine.df_nq['종목코드'])) # good