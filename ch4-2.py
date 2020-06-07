# ch4-2.py
import pandas as pd
import numpy as np

# Scikit-Learn 패키지 : 머신 러닝 교육 및 실무를 위한 패키지로 샘플 데이터셋,
# 다양한 기계학습 기법에 대한 함수 등을 포함하고 있음
from sklearn import tree  # 의사결정트리 기법에 관련된 모듈
from sklearn.model_selection import train_test_split  # 분석모형 선택에 관련된 모듈
from sklearn.preprocessing import StandardScaler  # 데이터전처리에 관련된 모듈
import numpy as np

# 데이터로드 (ch4-2(붓꽃데이터).csv : 데이터 원본 파일)
# encoding : 윈도우즈 환경에서의 한글 처리
# engine : python 3.6에서 한글이 포함된 파일이름 사용
rawData = pd.read_csv('chap4/ch4-2(붓꽃데이터).csv', encoding='CP949', engine='python')

# 소스 데이터프레임에서 분류(classification)을 위한 속성 집합
X = rawData.loc[:, 'sepal_length' : 'petal_width']
y = rawData.loc[:, 'class']  # 분류 클래스(class)

# 자동으로 데이터셋을 트레이닝셋과 테스트셋으로 분리해주는 함수로
# 트레이닝셋과 데이터셋의 비율을 7:3으로 세팅함
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)

# 데이터 표준화 작업
# StandardScaler() : 표준 스케일링을 위한 클래스를 생성하는 함수 (sklearn.preprocessing 모듈 소속)
# fit() : 표준화를 위한 변환계수를 추정하는 함수
sc = StandardScaler()
sc.fit(X_train)

# 표준화된 데이터셋
# transform() : 변환계수에 의해 실제로 데이터를 변환하는 함수
X_train_std = sc.transform(X_train)
X_test_std = sc.transform(X_test)

# DecisionTreeClassifier() : 의사결정트리를 생성하는 함수
# fit() : 트레이닝 데이터셋을 대상으로 의사결정트리 학습 진행
iris_tree = tree.DecisionTreeClassifier(criterion='entropy', max_depth=3, random_state=0)
iris_tree.fit(X_train, y_train)


from sklearn.metrics import accuracy_score  # 분류 정확도(classification accuracy)를 계산하는 모듈

# tree.predict() 함수를 활용하여 의사결정트리를 대상으로 테스트셋을 예측
y_pred_tr = iris_tree.predict(X_test)

# accuracy_score() 함수를 활용하여 테스트셋의 실제 클래스와 예측된 클래스 간 정확도 측정
print('Accuracy: %.2f' % accuracy_score(y_test, y_pred_tr))

# 의사결정트리 시각화를 위한 작업
# 트리 시각화를 위한 export_graphviz 모듈 임포트 (이를 위해 graphviz 별도 설치 필요)
from sklearn.tree import export_graphviz
import pydotplus  # graphviz의 dot language 와의 인터페이스를 제공하는 패키지 임포트
from IPython.display import Image  # IPython의 display와 관련된 Public API

x_list = list(X.columns)
y_list = list(y.drop_duplicates(inplace=False))

# export_graphviz() : 의사결정트리에 대한 graphviz dot data를 생성하는 함수
dot_data = export_graphviz(iris_tree, out_file=None, feature_names=x_list,
                          class_names=y_list, filled=True, rounded=True, special_characters=True)

graph = pydotplus.graph_from_dot_data(dot_data)  # graphviz의 dot data로부터 트리 그래프 생성

# 트리 그래프를 위한 png 이미지 생성 및 출력 (jupyter notebook 환경에서 구동함)
Image(graph.create_png())
