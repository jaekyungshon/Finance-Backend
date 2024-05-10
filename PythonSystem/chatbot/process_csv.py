import pandas as pd

# => 재무제표 엑셀 출처 : https://opendart.fss.or.kr/disclosureinfo/fnltt/dwld/main.do

### 재무제표 엑셀 불러오기 ###
#############################################
# 1분기
df_1=pd.read_csv("E:\\학교\\학교개인프로젝트모음\\chatbot\\learner_data\\financial\\2023_1분기_재무제표.csv", encoding="CP949")
df_1['종목코드']=df_1['종목코드'].apply(lambda x: x[1:-1]) # [000020] -> 000020
df_1 = df_1[~df_1['항목명'].str.contains('\[abstract\]')] # '자산 [abstract]' 형식 값을 갖는 행 제거
df_1.rename(columns={'당기 1분기말': '당기_1분기말'}, inplace=True) # 열이름 변경

# 2분기
df_2=pd.read_csv("E:\\학교\\학교개인프로젝트모음\\chatbot\\learner_data\\financial\\2023_2분기_재무제표.csv", encoding="CP949")
df_2['종목코드']=df_2['종목코드'].apply(lambda x: x[1:-1])
df_2 = df_2[~df_2['항목명'].str.contains('\[abstract\]')]
df_2.rename(columns={'당기 반기말': '당기_반기말'}, inplace=True)

# 3분기
df_3=pd.read_csv("E:\\학교\\학교개인프로젝트모음\\chatbot\\learner_data\\financial\\2023_3분기_재무제표.csv", encoding="CP949")
df_3['종목코드']=df_3['종목코드'].apply(lambda x: x[1:-1])
df_3 = df_3[~df_3['항목명'].str.contains('\[abstract\]')]
df_3.rename(columns={'당기 3분기말': '당기_3분기말'}, inplace=True)

# 4분기
df_4=pd.read_csv("E:\\학교\\학교개인프로젝트모음\\chatbot\\learner_data\\financial\\2023_4분기_재무제표.csv", encoding="CP949")
df_4['종목코드']=df_4['종목코드'].apply(lambda x: x[1:-1])
df_4 = df_4[~df_4['항목명'].str.contains('\[abstract\]')]
df_4.rename(columns={'당기 4분기말':'당기_4분기말', '전기 4분기말':'전기_4분기말'}, inplace=True)

# 고유 종목코드 개수 확인하기
# print(len(pd.unique(df_1['종목코드'])))
# print(len(pd.unique(df_2['종목코드'])))
# print(len(pd.unique(df_3['종목코드'])))
# print(len(pd.unique(df_4['종목코드'])))

# 고유 종목코드 4분기까지 다 있는 행 찾기.
uni_code_1Q = pd.unique(df_1['종목코드'])
uni_code_2Q = pd.unique(df_2['종목코드'])
uni_code_3Q = pd.unique(df_3['종목코드'])
uni_code_4Q = pd.unique(df_4['종목코드'])

uni_code_result = list(set(uni_code_1Q) & set(uni_code_2Q) & set(uni_code_3Q) & set(uni_code_4Q))
print(len(uni_code_result))

#############################################


### 정제해서 새로운 데이터프레임에 담기 ###
#############################################
df=pd.concat([df_1, df_2, df_3, df_4], axis=0)

df.drop(columns=['전전기말', '재무제표종류', '시장구분', '업종', '통화', '항목코드'], inplace=True)
print(df.columns)
df=df.sort_values(by='결산기준일')
df=df.sort_values(by='종목코드')

#print(df[df['종목코드']=='null'])
df=df[df['종목코드']!='null'] # 비상장종목 등, 종목코드가 'null'인 행 제거.

print(df.head(5))
#print(*pd.unique(df['종목코드']))

#############################################

# tmp_df=df[['회사명','항목명','당기_4분기말','전기_4분기말']]
# tmp_tmp_df=tmp_df.dropna(axis=0)
# print(tmp_tmp_df[tmp_tmp_df['회사명']=='삼성전자'])
#print(pd.unique(df['종목코드']))

#print(tmp_tmp_df['회사명'].iloc[-1])

### 새로운 데이터프레임 엑셀로 저장하기 ###
#############################################
df['종목코드'] = df['종목코드'].apply(lambda x: f"{x:06}")  # 종목코드 6자리 형식 유지한채로 엑셀에 저장하기 위한 필터링
df.to_csv("E:\\학교\\학교개인프로젝트모음\\chatbot\\learner_data\\financial\\2023_종합_재무제표.csv", index=False)
print("Success!")
#############################################
