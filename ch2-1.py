# ch2-1.py

import pandas as pd  # 데이터프레임 활용을 위한 pandas 패키지 임포트

# 데이터로드 (ch2-1.csv : 데이터 원본 파일)
# encoding : 윈도우즈 환경에서의 한글 처리
# engine : python 3.6에서 한글이 포함된 파일이름 사용
rawData = pd.read_csv('chap2/ch2-1(약수터수질현황).csv', encoding='CP949', engine='python')

# 결측값(NULL값)을 포함하고 있는 투플 제거(row-wise deletion)
rawData_missing_exclusion = rawData.dropna()

print(rawData_missing_exclusion)    # 결과보기

# 결측값(NULL값)을 전역상수(0)로 대체
rawData_missing_fill_constant = rawData.fillna(0)

# 결과보기 (결측값은 채운 연번이 4, 17, 20인 투플만 출력)
print(rawData_missing_fill_constant.query('연번 in (4, 17, 20)'))

# 결측값(NULL값)을 해당 속성의 평균값으로 대체
rawData_missing_fill_mean = rawData.fillna(rawData.mean())

# 결과보기 (결측값은 채운 연번이 4, 17, 20인 투플만 출력)
print(rawData_missing_fill_mean.query('연번 in (4, 17, 20)'))

# 결측값을 같은 클래스(분류)의 속성 평균값으로 대체
# 클래스(분류) 기준 속성 : 적합
# 데이터프레임 복사 : rawData -> rawData_missing_fill_mean_groupby
# copy=True 이면 별도의 공간에 데이터프레임 생성
rawData_missing_fill_mean_groupby = pd.DataFrame(rawData, copy=True)
rawData_missing_fill_mean_groupby['일반세균'].fillna(rawData_missing_fill_mean_groupby.groupby('적합')['일반세균'].transform('mean'), inplace=True)
rawData_missing_fill_mean_groupby['질산성질소'].fillna(rawData_missing_fill_mean_groupby.groupby('적합')['질산성질소'].transform('mean'), inplace=True)

# 결과보기 (결측값은 채운 연번이 4, 17, 20인 투플만 출력)
print(rawData_missing_fill_mean_groupby.query('연번 in (4, 17, 20)'))

# 회귀분석을 활용한 결측치 예측 (일반세균과 질산성질소 간 회귀분석)
from scipy import stats  # 선형회귀분석을 위한 scipy 패키지 중 stats 모듈 임포트
import numpy as np  # 수학 및 과학 연산을 위한 패키지

# 회귀분석을 활용한 결측치 예측 (일반세균과 질산성질소 간 회귀분석)
# stats.linregress(x, y) : y = slope * x + intercept 형식의 선형함수를 찾아주는 stats 모듈 함수로 다섯 개의 값을 반환
# 데이터프레임 복사 : rawData -> rawData_missing_fill_regression
rawData_missing_fill_regression = pd.DataFrame(rawData, copy=True)

# NaN(NULL)값을 제외하고 선형회귀분석 수행
mask = ~np.isnan(rawData_missing_fill_regression['일반세균']) & ~np.isnan(rawData_missing_fill_regression['질산성질소'])
slope, intercept, r_value, p_value, std_err = stats.linregress(rawData_missing_fill_regression['일반세균'][mask], rawData_missing_fill_regression['질산성질소'][mask])

# 일반세균값에 의한 질산성질소값 산출 (연번 4번 투플에 적용)
rawData_missing_fill_regression.loc[3, '질산성질소'] = rawData_missing_fill_regression['일반세균'][3]*slope + intercept

# NaN(NULL)값을 제외하고 선형회귀분석 수행
slope, intercept, r_value, p_value, std_err = stats.linregress(rawData_missing_fill_regression['질산성질소'][mask], rawData_missing_fill_regression['일반세균'][mask])

# 질산성질소 값에 의한 일반세균값 산출 (연번 20번 투플에 적용)
rawData_missing_fill_regression.loc[19, '일반세균'] = rawData_missing_fill_regression['질산성질소'][19]*slope + intercept

# 결과보기 (결측값은 채운 연번이 4, 20인 투플만 출력)
print(rawData_missing_fill_regression.query('연번 in (4, 20)'))

