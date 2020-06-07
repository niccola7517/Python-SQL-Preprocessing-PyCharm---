# ch4-4.py
import pandas as pd
import numpy as np

# 데이터로드 (ch4-4(국내증권사재무제표).csv : 데이터 원본 파일)
# encoding : 윈도우즈 환경에서의 한글 처리
# engine : python 3.6에서 한글이 포함된 파일이름 사용
rawData = pd.read_csv('chap4/ch4-4(국내증권사재무제표).csv', encoding='CP949', engine='python')

# PCA 대상 속성 추출
pca_src = rawData[['총자본순이익률','자기자본순이익률','자기자본비율','부채비율','자기자본회전율']]

# 데이터 표준화를 위한 sklearn.preprocessing 중 StandardScaler 모듈 임포트
from sklearn.preprocessing import StandardScaler

# StandardScaler() : 데이터를 표준화시키기 위한 함수
pca_std = StandardScaler().fit_transform(pca_src)

# PCA 분석을 위한 sklearn.decomposition 중 PCA 모듈 임포트
from sklearn.decomposition import PCA

# i : 몇 차원으로 축소할 것인지에 대한 정보를 담기위한 변수
# cum_prop : n 차원까지의 누적기여율(cumulative proportion)을 담기위한 변수
i = 1
cum_prop = 0

# 몇 차원으로 축소할 것인지를 결정하는 루틴
# 여기서는 누적기여율이 0.95 이상이 되는 차원수까지 진행함
# pca.explained_variance_ratio_ : 분석된 주성분(principal components)의 기여율(percentage of variance)
while True :
    pca = PCA(n_components=i)
    principalComponents = pca.fit_transform(pca_std)
    cum_prop += pca.explained_variance_ratio_[i-1]
    print("\n차원수 : " + str(i))
    print("기여율(Proportion of Variance) : " + str(pca.explained_variance_ratio_[i-1]))
    print("누적기여율(Cumulative Proportion) : " + str(cum_prop))

    # 누적기여율이 0.95 이상이면 루프 탈출
    if (cum_prop >= 0.95) :
        break
    i += 1

# 주성분으로 구성되는 데이터프레임의 컬럼이름을 저장하는 리스트 변수
str_param = []

# 주성분 컬럼이름 리스트 구성
for j in range(1, i+1) :
    str_param.append("PC" + str(j))  # PC : 주성분(Principal Component)

# 주성분 데이터프레임 구성
principalDf = pd.DataFrame(data=principalComponents
                               , columns=str_param)

# 주성분 데이터프레임 출력
print("\n* 주성분 데이터프레임 : ")
print(principalDf)

# components_ : 원 속성(총자본수익률, 자기자본수익률, 자기자본비율, 부채비율, 자기자본회전율)에
# 대한 주성분의 영향력(variance) 정도로서, 절대값이 클수록 영향력이 높음
print("\n* 원 속성에 대한 주성분 영향도(행: 주성분, 열: 원속성) : ")
print(pca.components_)

# 주성분의 (차원)수가 3차원이라는 가정 하에 시각화
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # 3차원 그래프 생성을 위한 모듈 임포트

fig = plt.figure(figsize = (8,8))
ax = fig.add_subplot(111, projection='3d')
ax.set_xlabel('PC1', fontsize = 15)
ax.set_ylabel('PC2', fontsize = 15)
ax.set_zlabel('PC3', fontsize = 15)
ax.set_title('3 component PCA', fontsize = 20)

ax.scatter(principalDf.loc[:, 'PC1'], principalDf.loc[:, 'PC2'], principalDf.loc[:, 'PC3'])
ax.view_init(20, -60)
plt.show()  # 3차원 그래프 보여주기