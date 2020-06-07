# ch4-5.py
import pandas as pd
import numpy as np
import random as rd  # 샘플링을 위한 random 패키지 임포트

# 데이터로드 (ch4-5(유동인구수).csv : 데이터 원본 파일)
# encoding : 윈도우즈 환경에서의 한글 처리
# engine : python 3.6에서 한글이 포함된 파일이름 사용
rawData = pd.read_csv('chap4/ch4-5(유동인구수).csv', encoding='CP949', engine='python')

# 소스 데이터를 읽은 데이터프레임의 인덱스 값 중 2,000개를 샘플링
# len() : 데이터프레임의 크기를 구하는 함수
sample_idx = rd.sample(range(0, len(rawData)-1), 2000)

# 인덱스 값 정렬(오름차순)
sample_idx.sort()

# 샘플링 된 인덱스로 구성된 샘플 데이터프레임 생성
rawData_sample = rawData.loc[sample_idx]

# 첫 10개의 행만 출력
print(rawData_sample.head(10))

# 2) 히스토그램을 통한 수량 축소
# 소스 데이터프레임에 총계 컬럼 추가 : sampling 빈도를 구하는데 활용
rawData['총계'] = rawData['남자10대']+rawData['남자20대']+rawData['남자30대']\
                +rawData['남자40대']+rawData['남자50대']+rawData['여자10대']+rawData['여자20대']\
                +rawData['여자30대']+rawData['여자40대']+rawData['여자50대']

# rawData_grp : 총계 컬럼값을 100으로 나눈 몫을 기준으로 그룹핑하여 그룹별 그룹값과 빈도수(count)를 구함
# groupby() 함수의 패러미터로 as_index=False를 주지 않았기 때문에 index 값은 rawData['총계']//100 값이 그대로 쓰임
# rawData_hist : 그룹별 기준값과 빈도값을 저장하는 데이터프레임
rawData_grp = rawData.groupby(rawData['총계']//100)['총계'].count()
rawData_hist = pd.DataFrame(data={'기준' : rawData_grp.index.values, '빈도' : rawData_grp.values})

# sum_tot : 빈도 컬럼의 총합
sum_tot = rawData_hist['빈도'].sum()

# 데이터프레임 rawData_hist에 대한 히스토그램 시각화
import matplotlib.pyplot as plt

n_bins = len(rawData_hist)
fig, ax = plt.subplots(1, 1, figsize = (15,15))
ax.hist(rawData_hist['빈도'], bins=n_bins, color="green")

# 최종 sampling된 인덱스 리스트를 저장
sample_idx = []

# rawData_hist를 하나씩 읽어가면서 해당 기준값 범위에 있는 총계값을 가진 rawData 행 인덱스를 대상으로 빈도수에 비례하여 sampling 수행
for j in range(0, len(rawData_hist)) :
    sample_gugan_idx = rd.sample(list(rawData.loc[rawData['총계'].isin(range(rawData_hist.loc[j]['기준']*100,(rawData_hist.loc[j]['기준']+1)*100-1))].index.values),
                                 rawData_hist.loc[j]['빈도'] * 2000 // sum_tot)
    sample_idx += sample_gugan_idx

sample_idx.sort()

# 샘플링 된 인덱스로 구성된 샘플 데이터프레임 생성
rawData_sample = rawData.loc[sample_idx]

# 샘플링된 총 로우의 갯수
print("* 샘플링된 총 로우의 개수 : " + str(len(rawData_sample)))

# 첫 10개의 행만 출력
print(rawData_sample.head(10))

# 3) 클러스터링을 통한 수량 축소
# K-Means 클러스터링 관련 함수를 가지고 있는 모듈 임포트
from sklearn.cluster import KMeans

n = 10  # 클러스터 개수

# K-Means 클러스터링 알고리듬 수행
kmeans = KMeans(n_clusters=n).fit(rawData.loc[:, '남자10대' : '여자50대'])

# kmeans.labels_ : 소스데이터의 각 행들의 클러스터 레이블을 저장하고 있는 속성 리스트
# labelDF : 행별로 클러스터링 결과 레이블을 저장하는 데이터프레임
labelDF = pd.DataFrame(kmeans.labels_, columns={'cluster_label'})

# labelDF 데이터프레임을 대상으로 cluster_label 별 빈도수 구함
cluster_cnt = labelDF.groupby('cluster_label')['cluster_label'].count()

# 최종 sampling된 인덱스 리스트를 저장
sample_idx = []

# 0부터 n까지의 cluster label을 하나씩 읽어가면서 해당 label 값을 가진 rawData 행 인덱스를 대상으로 빈도수에 비례하여 sampling 수행
for i in range(0, n) :
    sample_gugan_idx = rd.sample(list(labelDF['cluster_label'].isin([i]).index.values), cluster_cnt[i] * 2000 // len(labelDF))
    sample_idx += sample_gugan_idx

sample_idx.sort()  # 오름차순 정렬

# 샘플링 된 인덱스로 구성된 샘플 데이터프레임 생성
rawData_sample = rawData.loc[sample_idx]

# 샘플링된 총 로우의 갯수
print("* 샘플링된 총 로우의 개수 : " + str(len(rawData_sample)))

# 첫 10개의 행만 출력
print(rawData_sample.head(10))