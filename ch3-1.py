# ch3-1.py
import pandas as pd
import numpy as np

# matplotlib : 자료를 차트(chart)나 플롯(plot)으로 시각화(visulaization)하는 패키지
# pyplot : matlab이라는 수치해석 소프트웨어의 시각화 명령을 거의 그대로 사용할 수 있도록 Matplotlib 의 하위 API를 포장(wrapping)한 명령어 집합을 제공
import matplotlib.pyplot as plt

# 데이터로드 (ch3-1.csv : 데이터 원본 파일)
# encoding : 윈도우즈 환경에서의 한글 처리
# engine : python 3.6에서 한글이 포함된 파일이름 사용
rawData = pd.read_csv('chap3/ch3-1(유동인구수).csv', encoding='CP949', engine='python')

# 상관계수 분석 (남자20대 vs. 여자20대)
corr = np.corrcoef(rawData['남자20대'], rawData['여자20대'])
print("-- 상관계수(남자20대 vs. 여자20대) --")
print(corr)

plt.figure(figsize  = (8,6))  # 차트 사이즈 설정 (inch 단위)

# scatter() : 산점도(scatter plot)를 그려주는 함수
plt.scatter(rawData['남자20대'], rawData['여자20대'])

plt.show()  # 차트 보여주기

# 상관계수 분석 (남자10대 vs. 여자50대)
corr = np.corrcoef(rawData['남자10대'], rawData['여자50대'])
print("-- 상관계수(남자10대 vs. 여자50대) --")
print(corr)

plt.figure(figsize  = (8,6))
plt.scatter(rawData['남자10대'], rawData['여자50대'])
plt.show()