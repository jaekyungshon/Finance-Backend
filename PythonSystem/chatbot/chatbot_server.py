"""
해당 flask 서버와 spring boot 서버 간 통신을 하게 된다.
각 함수를 컨트롤러의 함수라고 생각하면 된다.
"""

# http://127.0.0.1:5000

from flask import Flask, request, jsonify
from chatbot_main import ChatEngine
from datetime import datetime

app = Flask(__name__)

# springboot에서 chatbot 대화 처리 요청 시, 처리 및 응답 메시지 리턴 함수(post 방식)
@app.route('/chatbot-message', methods=['POST'])
def chatbot_request_process():
    print(f"\t[Client][Spring-Boot][Request][{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Received Checked!")
    data = request.json # REST API 방식으로, JSON 형식을 사용.
    username = data.get('username') # springboot가 username을 보냈는지 확인(username == 로그인ID)
    text = data.get('text')

    print(f"\t[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 요청자:spring-boot / 대화고객명:{username}")
    
    # chatbot_main 불러오기
    engine=ChatEngine()
    
    # 사용자 입력에 맞춰 새로운 레코드 chatbot_history에 삽입
    engine.insert_new_record(username, text)
    
    # 사용자 입력에 대한 답변 처리
    flag=engine.chatbot_process()
    
    # 처리완료 알림을 spring-boot에 응답.
    if flag:
        print(f"\t[Server][Flask][Response][{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Response-status: 200\n")
        return jsonify({'state': 'true'}), 200 # 메시지(JSON형식), 상태코드
    else:
        print(f"\t[Server][Flask][Response][{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Response-status: 400\n")
        return jsonify({'state': 'false'}), 400
    
if __name__ == '__main__':
    app.run(debug=True) # 개발서버
    #app.run(debug=False) # 운영서버