# API key  : 

import pandas as pd
from openai import OpenAI
"""
chatgpt의 유사성 판단과 출력 형식이 자기 마음대로 이기에, 성능 정확도에 대해 어느정도 고민 필요
"""
# Chatgpt가 개발자들이 정해놓은 답변을 출력하도록 하는 필터링 클래스
# Chatgpt가 개발자가 정해놓은 답변을 학습하였다고 가정하는 것이다. (실제 chatgpt는 이전 대화를 기억하지 않음)
class LearnerEngine:
    def __init__(self):
        self.website_df = self.read_csv()
        
    ### 엑셀 파일 불러오기 ###
    def read_csv(self):
        website_df = pd.read_csv("E:\\학교\\학교개인프로젝트모음\\chatbot\\learner_data\\about_website.csv", encoding="CP949")
        #print(website_df)
        return website_df
    
    ### chatgpt 학습 ###
    def learn_run(self, query):
        df1 = self.website_df
    
        # 아래의 prompt를 주면, chatgpt는 이를 활용하지 못함을 확인.
        # 실제 질문이 들어오면, 해당 질문이 답변리스트에 있는지 확인을 통해 답변 유도하는 것으로 변경
        """
        messages.append({"role":"user", "content": 
                    f"앞으로, '{reqMsg}'라는 질문이 들어오게 되면, 다음과 같은 답변을 출력하도록 해줘.\n\n" + 
                    f"'{resMsg}'\n\n" +
                    f"다른 질문들도 '{reqMsg}'라는 질문과 유사하다고 너가 판단되면, 위의 답변을 출력하도록 해줘."})
        """
        
        # Prompt
        messages=[{"role": "system", "content": "You are a helpful assistant."}]
        
        # Prompt Content 준비1 : 정해높은 질문들 합치기
        idx=1; texts_query="" # 정해놓은 질문 리스트
        for _,row in df1.iterrows():
            texts_query+=f"{idx}. {row.iloc[0]}\n"
            idx+=1
        
        # Prompt Content 준비2 : 정해놓은 답변들 합치기
        idx=1; texts_answer="" # 정해놓은 답변 리스트
        for _,row in df1.iterrows():
            texts_answer+=f"{idx}. {row.iloc[1]}\n"
            idx+=1
        
        # Prompt Content 설정
        messages.append({"role":"user", "content": 
            f"다음의 질문 리스트가 있어.\n\n" + 
            f"{texts_query}\n" + 
            f"그리고 다음은 각 번호에 맞는 답변 리스트야.\n\n" + 
            f"{texts_answer}\n" + 
            f"'{query}'라는 질문에 대해 질문 리스트에서 유사하거나 같은 정도가 0.5이상인(최대:1) 질문이 있다고 판단되면, 너가 최종적으로 가장 유사하다고 생각하는 질문에 대한 답변을 질문 리스트 가장 유사한 질문 번호와 매핑되는 답변리스트의 번호의 내용을 그대로 출력해줘.\n" +
            f"또한, 해당 질문에서 특정 기업명이 들어가있다면, 특정 기업명 단어의 포함 여부는 제외하고 유사성 판단을 진행해줘.\n" +
            f"너가 나에게 알려줄 답변내용(출력내용)의 형식을 다음과 같은 예시로 알려줄게.\n" +
            f"Q) '이 사이트의 목적은 뭐야?'\n" +
            f"A) '저희 사이트는 투자의 보조 정보를 사용자들에게 제공함으로써, 사용자들의 투자 결정에 도움을 주기 위해 개발되었습니다.'\n" + 
            f"이때, 유사성 기준은 다음과 같아.\n" +
            f"1. 사이트와 관련된 질문인가?\n" +
            f"2. 매수 또는 매도와 관련된 질문인가?\n" +
            f"3. 특정 종목명(기업명) 주식의 추천을 요청하는 것과 관련된 질문인가?\n\n" +
            f"또한, 여러 개의 유사한 질문들이 존재한다면, 유사성 우선순위는 다음과 같아.\n" +
            f"1순위: 같은 단어가 많이 포함되어있느냐\n" +
            f"2순위: 질문들의 내용이 얼마나 유사한가\n\n" + 
            f"또한, 유사한 정도를 판단할 때 주의해야할 점은 다음과 같아.\n" +
            f"1. '재무', '지표', '제표', '이벤트', '뉴스' 단어가 들어간 질문의 경우, 유사하지 않다고 판단한다. 이때, 답변 형식에는 'false'를 무조건 포함시킨다.\n" +
            f"2. 분석을 요청하는 질문의 경우, 유사하지 않다고 판단한다. 이때, 답변 형식에는 'false'를 무조건 포함시킨다.\n\n" +
            f"위의 모든 사항들을 적용해서 유사한 질문이 없다고 판단되면, 'false'를 그대로 출력해줘."})
        #print(messages[1]['content'])
        #return ""
        
        # Setting ChatGPT
        openai = OpenAI(api_key="api키")
            
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
            
        # 결과받기
        result=response.choices[0].message.content
        #print(result)
        #print("=======================")
        #return ""
        
        # 조건부 리턴
        # false가 출력? => return "false"
        # 정상 내용 출력? => return 해당답변
        if "false" in result or "False" in result:
            return "false"
        else:
            for _,row in df1.iterrows():
                if row.iloc[1] in result:
                    return row.iloc[1]
            return ""
        
### TEST ###
# if __name__=="__main__":
#     engine=LearnerEngine()
#     #engine.read_csv()
#     #print(engine.learn_run("이 사이트는 어떤 목적으로 개발되었어?")) # OK(정확도: 3/5)
#     #print(engine.learn_run("이 사이트에서 우리는 무엇을 얻을 수 있어?")) # OK(정확도: 3/3)
#     #print(engine.learn_run("LG전자는 앞으로 주식이 오를까?")) # OK(정확도: 3/4)
#     #print(engine.learn_run("삼성전자는 어떤 사업성을 현재 가지고 있어?")) # Processing