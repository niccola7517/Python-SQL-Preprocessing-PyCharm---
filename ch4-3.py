# ch4-3.py
import pandas as pd
import numpy as np
import pywt  # Discrete Wavelete Transform을 위한 패키지

# 데이터로드 (ch4-3(대기오염측정).csv : 데이터 원본 파일)
# encoding : 윈도우즈 환경에서의 한글 처리
# engine : python 3.6에서 한글이 포함된 파일이름 사용
rawData = pd.read_csv('chap4/ch4-3(대기오염도측정).csv', encoding='CP949', engine='python')

# 대기오염 측정치(SO2, NO2, CO, O3, PM10)를 대상으로 multi-level 웨이블릿변환함수 dwt2() 적용

# rawData를 1차원 배열(array)로 변환
wavelete_src = []
wavelete_src.extend(rawData.loc[:,'SO2'])
wavelete_src.extend(rawData.loc[:,'NO2'])
wavelete_src.extend(rawData.loc[:,'CO'])
wavelete_src.extend(rawData.loc[:,'O3'])
wavelete_src.extend(rawData.loc[:,'PM10'])

# pywt.wavedec() : Multi-level 1D Discrete Wavelet Transform을 위한 함수
# mode : 'zero', 'constant', 'symmetric', 'periodic', 'smooth', 'periodization' 중 periodic 적용
# level : decomposition level을 지정하는 패러미터로서 여기서는 12를 지정
coeffs = pywt.wavedec(wavelete_src, 'db1', mode='periodic', level=12)

# coeffs_a = pywt.downcoef('a',wavelete_src, 'db1', mode='periodic')
# coeffs_d = pywt.downcoef('d',wavelete_src, 'db1', mode='periodic')

# coeffs 리스트의 크기 구하기
coeffs_len = len(coeffs)

# Approximation coefficient 출력 (level=12)
print("Approximation coefficient : ")
print(coeffs[0])

# Detail coefficient 출력 (level 12부터 1까지)
for i in range(1, coeffs_len):
    print("Detail coefficient (level = " + str(coeffs_len-i) + ")")
    print(coeffs[i])

# coefficient 시각화
import matplotlib.pyplot as plt

# 원 소스 그래프
print("Source data graph : ")
plt.plot(wavelete_src)
plt.show()  # 차트 보여주기

# Approximation coefficient 시각화 (level=12)
print("Approximation coefficient graph : ")
plt.plot(coeffs[0])
plt.show()

# Detail coefficient 출력 (level 12부터 1까지)
for i in range(1, coeffs_len):
    print("Detail coefficient graph(level = " + str(coeffs_len-i) + ")")
    plt.plot(coeffs[i])
    plt.show()