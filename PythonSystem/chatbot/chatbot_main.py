
#
"""
1. 직접적인 투자 행동에 관한 질문인가?
=> true라면, 답변불가 메시지 저장.
=> false라면, 2번으로 넘어감

2. about_website.csv에 들어있는 질문 내용인가? (2차 방어를 위해 매수/매도를 직접 질문 포함)
=> true라면, 알아서 출력.
=> false라면, 3번으로 넘어감.

3. 어떤 유형의 질문인가?
=> 분석성, 정보성, 예측성 등
=> 이를 바탕으로 동적 데이터 준비 프로세스로 넘어가야함.
"""

import pandas as pd
from openai import OpenAI
import pymysql, time
import traceback
from datetime import datetime
from chatbot_learner import LearnerEngine
from chatbot_data_manager import DataManager

### 메인 로직 클래스 ###
class ChatEngine:
    def __init__(self):
        self.learner_engine = LearnerEngine() # 웹사이트 관련 질문 처리에 대한 클래스.
        self.data_engine = DataManager() # prompt에 맞춘 동적 데이터 삽입을 위한 준비 클래스.
        self.conn = pymysql.connect(host="127.0.0.1", user="root", password="비밀번호", db="testcapstone", charset="utf8")
    
    def __del__(self):
        self.conn.close()
    
    def insert_new_record(self, username, text):
        with self.conn.cursor() as curs:
            sql="INSERT INTO chatbot_history (username, date, req_msg, res_msg) VALUES (%s, NOW(), %s, NULL);"
            curs.execute(sql, (username, text))
        self.conn.commit()
        print(f"\t[레코드삽입] 정상 완료")
    
    def update_record_res_msg(self):
        with self.conn.cursor() as curs:
            sql="UPDATE chatbot_history SET res_msg = '서버 오류로 인해 답변을 하지 못하게 되었습니다. 관리자에게 문의해주세요.' ORDER BY id DESC LIMIT 1";
            curs.execute(sql)
        self.conn.commit()
        
    ## 사용자가 입력한 질문이 어떤 유형인지 파악하는 함수 ##
    def chatgpt_query_flag(self, query):
        messages=[{"role": "system", "content": "You are a helpful assistant."}]
        messages.append({"role":"user", "content": 
            f"다음의 질문이 예측성, 정보성, 판단성, 개인정보성 중에서 어떤 유형인지 파악해줘.\n" + 
            f"이때, 만약 정보성 유형이고, 내가 데이터를 prompt로 너에게 안주고도 답변이 가능하다면, 절차성 유형으로 구분해줘. 질문은 다음과 같아.\n\n" +
            f"'{query}'\n\n" + 
            f"너가 답변할 때, 나에게 보여줄 출력 형식은 다음과 같아. 예시를 들어줄게.\n" + 
            f"Q) '삼성전자의 주가는 최근에 어떻게 움직였는가?'\n" + 
            f"A) 해당 질문은 예측성 질문입니다.\n\n" +
            f"Q) '주식 거래를 위해 어떤 계좌가 필요한가요?'\n" +
            f"A) 해당 질문은 정보성 질문입니다."})
        
        openai = OpenAI(api_key="api키")
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        result=response.choices[0].message.content
        #if 'A' in result:
        #    result=result[result.index('A')+2:]
        #print(result)
        if ('예측성' in result) or ('정보성' in result) or ('판단성' in result):
            return 1
        elif '개인정보성' in result:
            return 0
        else:
            return -1
    
    ## 사용자 입력 질문이 직접적인 투자 행동과 관련된건지 체크하는 함수 ##
    def chatgpt_flag_invest_action(self, query):
        messages=[{"role": "system", "content": "You are a helpful assistant."}]
        messages.append({"role":"user", "content": 
            f"다음의 질문이 직접적인 투자 행동인 매수와 매도에 관한 질문인지 파악해줘.\n\n" +
            f"'{query}'\n\n" + 
            f"너가 답변할 때, 나에게 보여줄 출력 형식은 다음과 같아. 예시를 들어줄게.\n" + 
            f"Q) '삼성전자의 주가는 최근에 어떻게 움직였는가?'\n" + 
            f"A) false\n\n" +
            f"Q) '주식 거래를 위해 어떤 계좌가 필요한가요?'\n" +
            f"A) false\n\n" + 
            f"Q) '삼성전자 주식을 지금 사거나 파는게 좋을까?'\n" + 
            f"A) true\n\n" + 
            f"Q) '삼성전자 주식을 다음 달에 팔면 좋을 것으로 예상해?'\n" + 
            f"A) true"})
        
        openai = OpenAI(api_key="api키")
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        result=response.choices[0].message.content
        #print(result)
        if 'true' in result or 'True' in result:
            return False # 직접적인 투자 질문인 경우
        else:
            return True # 아닐 경우

    ### 사용자 입력 질문들이 저장되있는 chatbot_history 전체 레코드 가져오기 ###
    def get_all_records(self):
        df=pd.DataFrame()
        
        with self.conn.cursor() as curs:
            curs.execute("SELECT * FROM chatbot_history")
            result=curs.fetchall()
            df=pd.DataFrame(result)
        
        df.columns=['id', 'username', 'date', 'req_msg', 'res_msg']
        return df # 전체 레코드 데이터프레임
    
    ## prompt 최적화 함수 (self-prompt) ##
    def optimizing_prompt(self, query):
        """ 여러번 self-prompt 요청 테스트 해보지 않았기에, 1번의 요청을 통한 결과를 바로 이용. """
        
        messages=[{"role": "system", "content": "You are a helpful assistant."}]
        messages.append({"role":"user", "content": 
            f"너는 훌륭한 최적화 prompt를 생성하는 전문가야.\n" +
            f"다음의 질문에 대해 너가 질문의 의도에 맞게 정확한 답변을 할 가능성이 가장 높은 질문을 1개 생성해줘 한 문장으로 알려줘.\n\n" + 
            f"'{query}'\n\n" +
            f"나에게 보여줄 답변의 형식은 다음과 같아. 예시를 통해 설명할게.\n" +
            f"답변) 이 회사의 최근 재무 보고서에 따르면 현재 채무 상황이 어떤가요? 이에 따라 주식을 보유해야 할 만한 가치가 있는지 판단해야 할까요?"})
        
        openai = OpenAI(api_key="api키")
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        result=response.choices[0].message.content
        #print(result)
        return result
    
    ## 동적인 prompt에 따른 동적 데이터 처리 함수(예측성/정보성/판단성 질문) ##
    def dynamic_setting_process_data(self, query):
        chart_datas, news_datas, financial_datas = self.data_engine.get_datas(query,1) # (사용자 원본 질문 사용)
        # 타겟기업명 못찾았을 경우 예외처리
        if chart_datas=="" and news_datas=="" and financial_datas=="":
            return []
        
        conditions_count=[chart_datas.count("")<len(chart_datas), news_datas.count("")<len(news_datas), 
                            financial_datas.count("")<len(financial_datas)] # 각 데이터 리스트의 내용이 존재하는지 조건
                    
        text=[] # '이어 말하기' 기법을 활용하기 위해, 리스트로 변경
        text.append(f"""
                    너는 훌륭한 금융 애널리스트 역할을 맡게 되었어.
                    다음은 너에게 질문하고 싶은 내용이야.
                                
                    '{query}'
                    """) # 초기 텍스트 세팅 (사용자 질문 원본 사용)
                    
        if conditions_count[0]: # 차트데이터: 여러 종목중 하나라도 차트데이터가 존재한다면
            text[0]+=f"\n\n다음 대화에 이어서, 너에게 해당 질문에 대한 답변을 도와주기 위해 주가(차트) 데이터를 입력할거야. 아직 답변하지 말아줘."
            for data in chart_datas:
                if data!="":
                    text.append(data+"다음 대화에 이어서, 데이터를 계속 입력할거야. 아직 답변하지 말아줘.")
                    
        if conditions_count[1]: # 뉴스데이터: 여러 종목중 하나라도 뉴스데이터가 존재한다면
            if not conditions_count[0]:
                text[0]+=f"\n\n다음 대화에 이어서, 너에게 해당 질문에 대한 답변을 도와주기 위해 뉴스 데이터를 입력할거야. 아직 답변하지 말아줘."
            for data in news_datas:
                if data!="":
                    text.append(data+"다음 대화에 이어서, 데이터를 계속 입력할거야. 아직 답변하지 말아줘.")
                    
        if conditions_count[2]: # 재무제표: 여러 종목중 하나라도 재무제표 데이터가 존재한다면
            if not conditions_count[0] and not conditions_count[1]:
                text[0]+=f"\n\n다음 대화에 이어서, 너에게 해당 질문에 대한 답변을 도와주기 위해 재무제표 데이터를 입력할거야. 아직 답변하지 말아줘."
            for data in financial_datas:
                if data!="":
                    text.append(data+"다음 대화에 이어서, 데이터를 계속 입력할거야. 아직 답변하지 말아줘.")
                    
        if conditions_count[0] or conditions_count[1] or conditions_count[2]: # 차트,뉴스,재무제표 중 하나라도 데이터 존재하는경우
            text.append(f"""
                        모든 데이터 입력을 완료했어. 질문했던 내용에 대해 너가 분석할 때, 다음의 사항을 참고하면 되.
                        1. 주가데이터가 입력되었다면, 이를 활용한다.
                        2. 뉴스데이터가 입력되었다면, 이를 활용한다.
                        3. 제무재표가 입력되었다면, 이를 활용한다.
                        4. 주가데이터, 뉴스데이터, 차트데이터 중 존재하는 데이터들은 모두 활용한다.
                        
                        이제 질문했던 내용에 대해 답변해줘.
                        질문했던 내용은 다음과 같아.
                        
                        '{query}'
                        
                        만약, 너가 분석하는데 시간이 걸린다면, 모든 분석이 완료된 후에 최종 답변 내용을 나에게 알려줘.
                        """)
        
        return text
    
    ## Chatgpt에게 prompt 요청 및 응답 수신 함수 ##
    def request_chatgpt(self, msg_list, query):
        tmp_result_list=[]
        
        for msg_item in msg_list:
            messages=[{"role": "system", "content": "You are a helpful assistant."}]
            messages.append({"role":"user", "content": msg_item})
            
            openai = OpenAI(api_key="api키")
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            tmp_result_list.append(response.choices[0].message.content)
        
        # 최종 답변 얻기(분석 시간이 오래 걸려, 기다리라는 답변이 왔을 경우)
        if '기다' in tmp_result_list[-1] or '잠시' in tmp_result_list[-1]:
            wait_flag=True
            while wait_flag:
                messages=[{"role": "system", "content": "You are a helpful assistant."}]
                messages.append({"role":"user", "content": 
                    f"'{query}' 질문에 대한 분석을 다 마쳤으면, 해당 질문에 대한 최종 답변을 제공하시기 바랍니다."})
                    
                openai = OpenAI(api_key="api키")
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages
                )
                
                result=response.choices[0].message.content
                if '기다' in result or '잠시' in result:
                    print(f"\t\t[Chatgpt 요청 진행중] ... ")
                    time.sleep(2)
                else:
                    tmp_result_list.append(response.choices[0].message.content)
                    break
        
        return tmp_result_list[-1]
    
    
    ## Python Chatbot Main Logic ##
    def chatbot_process(self):
        try:
            ## 필요 변수 정리 ##
            chatbot_history_records_df = pd.DataFrame() # chatbot_history 데이터프레임
            
            ## Main Logic ##
            #print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] prev:{prev_count}개 / Server Processing ... ")
                
            ## 1. chatbot_history 전체 레코드 가져오기 ##
            chatbot_history_records_df=self.get_all_records()
            chatbot_history_records_df = chatbot_history_records_df.sort_values(by='date')
            #print(chatbot_history_records_df.tail(4))
            print(f"\t\t[DB연결] chatbot_history 전체 레코드 데이터프레임 생성 완료")
                
            ## 2. 사용자 질문 파악 : 직접적인 투자와 관련된 질문인가? ##
            new_record_query = chatbot_history_records_df['req_msg'].iloc[-1] # 질문 내용
            record_id = chatbot_history_records_df['id'].iloc[-1] # 구별키
            print(f"\t\trecord_id: {record_id}")
            flag = self.chatgpt_flag_invest_action(new_record_query)
                
            if not flag:
                print(f"\t\t[사용자 질문 파악 #1][직접투자인가] 직접 투자 내용이므로 답변 불가로 처리.")
                with self.conn.cursor() as curs:
                    sql=f"""
                        UPDATE chatbot_history
                        SET res_msg='해당 질문은 직접적인 투자 행동과 관련된 질문으로 답변드릴 수 없습니다.'
                        WHERE id='{record_id}'
                        """
                    curs.execute(sql)
                self.conn.commit()
                return True
            else:
                print(f"\t\t[사용자 질문 파악 #1][직접투자인가] 다음 '웹사이트 관련 질문 파악' 프로세스 진행.")
                
            ## 3. 사용자 질문 파악 : 웹사이트와 관련된 질문인가? ##
            msg=self.learner_engine.learn_run(new_record_query)
                
            if msg!="false" and msg!="":
                print(f"\t\t[사용자 질문 파악 #2][웹사이트관련] 개발자 지정 답변 리턴 처리.")
                with self.conn.cursor() as curs:
                    sql=f"""
                        UPDATE chatbot_history
                        SET res_msg='{msg}'
                        WHERE id='{record_id}'
                        """
                    curs.execute(sql)
                self.conn.commit()
                return True
            else:
                print(f"\t\t[사용자 질문 파악 #2][웹사이트관련] 다음 '질문 유형 파악' 프로세스 진행.")
                    
            ## 4. 사용자 질문 파악 : 어떤 질문 유형인가? ##
            flag=self.chatgpt_query_flag(new_record_query)
            print(f"\t\t[사용자 질문 파악 #3][질문유형] 질문유형 파악 완료. 'prompt 최적화' 프로세스 진행.")
                
            ## 5. 사용자 질문 최적화 작업 (prompt 최적화) ##
            optimize_query=self.optimizing_prompt(new_record_query)
            use_flag_optimize_query=False # chatgpt가 반환한 최적화 질문 내용을 사용할 것인가
                                          # chatgpt 반환 최적화 질문이 질문 형식으로 안나오는 경우가 있음. 이를 위해 사용 여부 결정
            
            optimize_query = optimize_query.replace("'", "").replace('"', "")
            if optimize_query[-1]=="?": # 최적화 prompt가 질문형식이면
                use_flag_optimize_query=True
                with self.conn.cursor() as curs:
                    sql = """INSERT INTO optimize_prompt (prev_req_msg, result_msg) VALUES (%s, %s)"""
                    curs.execute(sql, (new_record_query, optimize_query))
                self.conn.commit()
            # else: # 문장형식이면.
            #     with self.conn.cursor() as curs:
            #         sql="INSERT INTO optimize_prompt (prev_req_msg, result_msg) VALUES (%s, %s)"
            #         curs.execute(sql, (new_record_query, new_record_query))
            #     self.conn.commit()
            
            print(f"\t\t[prompt 최적화][TB:optimize_prompt] 최적화 및 DB 저장 완료. '데이터 동적 처리' 프로세스 진행.")
            print(f"\t\t\t use query: '{optimize_query if use_flag_optimize_query else new_record_query}'")
                
            ## 6. 동적인 prompt에 따른 필요 데이터 동적처리: 질문 유형별로 필요한 데이터를 요청메시지에 담기 ##
            # new_record_query(사용자 질문 원본) / optimize_query(chatgpt가 최적화한 질문)
            # 둘 중 성능이 조금 더 좋은 것을 사용. (성능=정확도/유사도/질문형식)
            text="" # chatgpt에 보낼 메시지 내용
            if flag==1: # 예측성,정보성,판단성 (데이터 필요)
                #print(f"\t\ttext1: {new_record_query}")
                if use_flag_optimize_query==True:
                    text=self.dynamic_setting_process_data(optimize_query) # 최적화 질문 활용
                else:
                    text=self.dynamic_setting_process_data(new_record_query) # 원본 질문 활용
            elif flag==0: # 개인정보성 (데이터 필요없음)
                #print(f"\t\ttext2: {new_record_query}")
                text=[optimize_query] if use_flag_optimize_query else [new_record_query]
            else: # 절차성 (데이터 필요없음)
                #print(f"\t\ttext3: {new_record_query}")
                text=[optimize_query] if use_flag_optimize_query else [new_record_query]
            # 타겟 기업명 못찾아, 메시지 준비를 못하는 경우
            if text==[]:
                with self.conn.cursor() as curs:
                    sql=f"""
                    UPDATE chatbot_history
                    SET res_msg='타겟 기업들을 찾지 못했습니다. 다시 한번 질문을 저에게 요청해주세요.'
                    WHERE id='{record_id}'
                    """
                    curs.execute(sql)
                self.conn.commit()
                print(f"\t\t[데이터 동적 처리] 타겟 기업 리스트 부재 예외 처리 완료")
                return True
            # 타겟 기업명 찾아, 메시지 준비된 경우
            print(f"\t\t[데이터 동적 처리] 사용자 prompt에 따른 동적 처리 완료(flag={flag}) / chatgpt요청개수예상: {len(text)}개")
                
            ## 7. Chatgpt에게 요청하고, 이에 따른 답변 받기##
            if use_flag_optimize_query:
                result=self.request_chatgpt(text, optimize_query)
            else:
                result=self.request_chatgpt(text, new_record_query)
            print(f"\t\t[Chatgpt 요청] 정상적으로 응답 메시지 받기 완료.")
                
            ## 8. 최종 답변, DB 레코드에 덮어쓰기(갱신) ##
            with self.conn.cursor() as curs:
                sql=f"""
                    UPDATE chatbot_history
                    SET res_msg='{result}'
                    WHERE id='{record_id}'
                    """
                curs.execute(sql)
            self.conn.commit()
            print(f"\t\t[답변 처리][TB:chatbot_history] 답변 Table에 업데이트 완료")
            
            ## 9. Flask에게 정상 처리 완료되었다고 리턴##
            return True
        
        except Exception as ex:
            print(f"\t\t[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Python chatbot server-error occured!!")
            print()
            print(traceback.format_exc())
            return False
    
    
# if __name__=="__main__":
#     engine=ChatEngine()
#     ### TEST ###
#     #print(engine.chatgpt_query_flag("향후 6개월 동안 특정 주식의 변동성은 어떻게 될 것으로 예상되는가?")) # (예상/출력)=(1/1)
#     #print(engine.chatgpt_query_flag("주식 투자를 위해 어떤 정보를 참고해야 하나요?")) # (-1/-1)
#     #print(engine.chatgpt_query_flag("이 주식이 시장의 특정 추세에 따라 어떻게 움직일 것으로 보나요?")) #(1/1)
#     #print(engine.chatgpt_query_flag("개발자들은 어디 소속인가요?")) #(0/-1)
#     #print(engine.chatgpt_flag_invest_action("현재 내가 대우건설 주식을 가지고 있어. 현재 주가 동향을 바탕으로 언제쯤 파는게 좋을까?")) # (False / False)
#     #engine.check_new_record(True)
#     #engine.optimizing_prompt("현재 내가 대우건설 주식을 가지고 있어. 현재 주가 동향을 바탕으로 언제쯤 파는게 좋을까?")
#     f=engine.chatbot_process()
    """
    "반도체 산업간 경쟁이 치열해질 경우 삼성전자의 시장 점유율은 어떻게 변할 것으로 예상되는가?"
    '반도체 산업의 현재 트렌드 및 전망은 어떻게 되는가?'
    '다음 분기에 특정 기업의 수익은 어떻게 될 것으로 예상되는가?'
    '삼성전자의 특정 사업이 재무에 어떤 영향을 미쳤는지 분석해줘'
    '삼성전자의 주식을 언제쯤 사는게 좋을까?'
    '이 사이트는 어떤 서비스를 제공해?'
    '삼성전자의 현재 동향을 바탕으로, 주가 흐름에 어떤 영향을 미칠지 분석해줘.'
    'SK하이닉스의 뉴스 소식과 주가의 상관관계 분석을 통해, 동향 분석을 진행해서 결과를 알려줘.'
    
    
    INSERT INTO chatbot_history (username, date, req_msg, res_msg)
    VALUES ('admin001', NOW(), 'SK하이닉스의 뉴스 소식과 주가의 상관관계 분석을 통해, 동향 분석을 알려줘.', NULL);
    
    DELETE FROM chatbot_history WHERE id = 1;
    """
    