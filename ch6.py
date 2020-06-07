# ch6.py
import pandas as pd
import numpy as np

# 데이터로드 (ch6(전문대학정보공시데이터).csv : 데이터 원본 파일)
# encoding : 윈도우즈 환경에서의 한글 처리
# engine : python 3.6에서 한글이 포함된 파일이름 사용
rawData = pd.read_csv('chap6/ch6(전문대학정보공시데이터).csv', encoding='CP949', engine='python')

# 결측치(NULL값) 제거 : 결측치를 해당 속성의 평균값으로 채우는 방법 채택
rawData_missing_fill_mean = rawData.fillna(rawData.mean())

# Z-score 정규화
# sklearn.preprocessing의 StandardScaler 모듈 임포트
from sklearn.preprocessing import StandardScaler

# StandardScaler() : Z-score 정규화 함수
stdscaler = StandardScaler()

# Z-score 정규화 수행 및 데이터프레임 생성
rawData_std = pd.DataFrame(stdscaler.fit_transform(rawData_missing_fill_mean.loc[:, 'sc1' : 'tc']),
                           columns=['sc1_n', 'sc2_n', 'sc3_n', 'sc4_n', 'sc5_n', 'sc6_n', 'sc7_n', 'sc8_n', 'sc9_n',
                                    'sc10_n', 'sc11_n', 'sc12_n', 'tc_n'])

print(rawData_std)

# 상관계수 분석 ( 정보공시지표 vs. 취업률 )
# col_names : 정보공시지표명을 저장하는 리스트
col_names = ["학생충원율", "중도탈락학생비율", "1인당장학금", "장학금수혜율",
             "학자금대출 이용학생비율", "학생1인당 교육비", "전임교원1인당 학생수",
             "전임교원강의담당비율", "업체당 실습학생수평균",
             "현장실습이수율", "캡스톤디자인이수비율", "캡스톤디자인학생당지원금액", "취업률"]
print("-- 상관계수(정보공시지표 vs. 취업률) --")

# 정보공시지표 각각에 대하여 취업률과의 상관분석 수행 (지표값은 정규화된 값을 사용)
# rawData_std : 정규화된 정보공시지표값을 저장하고 있는 데이터프레임 (이전 예제에서 생성함)
# NUM_OF_VAR : 변수(지표)의 총 개수(종속변수 취업률 포함)를 저장 (파이썬 변수이나 상수처럼 사용할 것)
NUM_OF_VAR = 13
for i in range(0, NUM_OF_VAR-1) :
    corr = np.corrcoef(rawData_std.iloc[:, i], rawData_std.iloc[:, NUM_OF_VAR-1])  # 12는 13번째 컬럼으로 취업률을 의미
    print("(" + col_names[i] + " vs. " + col_names[NUM_OF_VAR-1] + ") : %.3f" % (corr[0][1]))

# 후보변수로 채택된 정보공시지표 추출
# 0 : 학생충원율(sc1), 4 : 학자금대출 이용학생비율(sc5), 5 : 학생1인당 교육비(sc6),
# 7 : 전임교원강의담당비율(sc8), 9 : 현장실습이수율(sc10), 12 : 취업률(tc)
# rawData_std : 정규화된 정보공시지표값을 저장하고 있는 데이터프레임 (이전 예제에서 생성함)
rawData_candi = rawData_std.iloc[:, [0, 4, 5, 7, 9, 11, 12]]

# NUM_OF_VAR_CANDI : 후보 독립변수(지표)와 종속변수(취업률)의 총 변수 개수를 저장 (파이썬 변수이나 상수처럼 사용할 것)
NUM_OF_VAR_CANDI = 7

# col_names : 정보공시지표명을 저장하고 있는 문자열 리스트 (이전 예제에서 생성함)
col_names_candi = []
col_names_candi.append(col_names[0])  # 후보 독립변수 : 학생충원율
col_names_candi.append(col_names[4])  # 후보 독립변수 : 학자금대출 이용학생비율
col_names_candi.append(col_names[5])  # 후보 독립변수 : 학생1인당 교육비
col_names_candi.append(col_names[7])  # 후보 독립변수 : 전임교원강의담당비율
col_names_candi.append(col_names[9])  # 후보 독립변수 : 현장실습이수율
col_names_candi.append(col_names[11]) # 후보 독립변수 : 캡스톤디자인학생당지원금액
col_names_candi.append(col_names[12]) # 종속 독립변수 : 취업률

# 후보변수와 취업률 간 선형회귀분석
from scipy import stats  # 선형회귀분석을 위한 scipy 패키지 중 stats 모듈 임포트
import matplotlib.pyplot as plt # 선형회귀 분석결과 시각화를 위한 패키지 임포트

for i in range(0, NUM_OF_VAR_CANDI-1) : # len(rawData_candi)-1
    # stats.linregress(x, y) : y = slope * x + intercept 형식의 선형함수를 찾아주는 stats 모듈 함수로 다섯 개의 값을 반환
    slope, intercept, r_value, p_value, std_err = stats.linregress(rawData_candi.iloc[:, i],
                                                     rawData_candi.iloc[:, NUM_OF_VAR_CANDI-1])

    # 회귀분석결과 시각화 (그래프 생성)
    plt.plot(rawData_candi.iloc[:, i], rawData_candi.iloc[:, NUM_OF_VAR_CANDI-1], '.')  # 산점도 그래프
    plt.plot(rawData_candi.iloc[:, i], np.array(rawData_candi.iloc[:, i]) * slope + intercept)  # 선형 그래프
    plt.show()