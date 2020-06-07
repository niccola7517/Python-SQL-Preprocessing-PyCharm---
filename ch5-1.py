# ch5-1.py
import pandas as pd
import numpy as np

# 데이터로드 (ch5-1(선박입출항).csv : 데이터 원본 파일)
# encoding : 윈도우즈 환경에서의 한글 처리
# engine : python 3.6에서 한글이 포함된 파일이름 사용
rawData = pd.read_csv('chap5/ch5-1(선박입출항).csv', encoding='CP949', engine='python')

# 최소-최대 정규화
# 최소값 : 0, 최대값 : 1로 가정
from sklearn.preprocessing import MinMaxScaler  # sklearn.preprocessing의 MinMaxScaler 모듈 임포트

# MinMaxScaler() : 최대-최소 정규화 함수 (기본최소값 : 0, 기본최대값 : 1)
mmscaler = MinMaxScaler()

# 최소-최대 정규화 수행 및 데이터프레임 생성
df1 = pd.DataFrame(rawData.loc[:,'항만'], columns = ['항만'])
df2 = pd.DataFrame(mmscaler.fit_transform(rawData.loc[:, '입항선박수' : '출항선박톤수']), columns=['입항선박수', '입항선박톤수', '출항선박수', '출항선박톤수'])
rawData_scaling = pd.concat([df1, df2], axis=1)  # 두 개의 데이터프레임(df1, df2) 결합

print(rawData_scaling)

# Z-score 정규화
# sklearn.preprocessing의 StandardScaler 모듈 임포트
from sklearn.preprocessing import StandardScaler

# StandardScaler() : Z-score 정규화 함수
stdscaler = StandardScaler()

# Z-score 정규화 수행 및 데이터프레임 생성
df1 = pd.DataFrame(rawData.loc[:,'항만'], columns = ['항만'])
df2 = pd.DataFrame(stdscaler.fit_transform(rawData.loc[:, '입항선박수' : '출항선박톤수']), columns=['입항선박수', '입항선박톤수', '출항선박수', '출항선박톤수'])
rawData_std = pd.concat([df1, df2], axis=1)  # 두 개의 데이터프레임(df1, df2) 결합

print(rawData_std)

# 소수 척도화
# 각 항목에서 최대값 구하기
max_입항선박수 = max(rawData.loc[:,'입항선박수'])
max_입항선박톤수 = max(rawData.loc[:,'입항선박톤수'])
max_출항선박수 = max(rawData.loc[:,'입항선박수'])
max_출항선박톤수 = max(rawData.loc[:,'출항선박톤수'])

# 소수 척도화 수행
list_of_decs = []  # 소수 척도화 결과값을 저장할 리스트 변수 초기화

# 리스트 변수에 소수 척도화 결과값을 행 단위로 저장
for i in range(0, len(rawData)) :
    list_of_decs.append([rawData.loc[i,'항만'],
                        rawData.loc[i, '입항선박수'] / pow(10, len(str(max_입항선박수))),
                        rawData.loc[i, '입항선박톤수'] / pow(10, len(str(max_입항선박톤수))),
                        rawData.loc[i, '출항선박수'] / pow(10, len(str(max_출항선박톤수))),
                        rawData.loc[i, '출항선박수'] / pow(10, len(str(max_출항선박톤수)))])

# 데이터프레임 생성
rawData_dec = pd.DataFrame(list_of_decs, columns=['항만', '입항선박수', '입항선박톤수', '출항선박수', '출항선박톤수'])

print(rawData_dec)