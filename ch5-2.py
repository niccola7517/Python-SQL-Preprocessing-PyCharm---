# ch5-2.py
import pandas as pd
import numpy as np

# 데이터로드 (ch5-2(국내대학현황).csv : 데이터 원본 파일)
# encoding : 윈도우즈 환경에서의 한글 처리
# engine : python 3.6에서 한글이 포함된 파일이름 사용
rawData = pd.read_csv('chap5/ch5-2(국내대학현황).csv', encoding='CP949', engine='python')

# 재적학생수 속성을 벡터(리스트)로 저장
v_재적학생수 = list(rawData.loc[:, '재적학생수'])

# 오름차순 정렬
v_재적학생수.sort()

# 엔트로피(entropy)-기반 재적학생수 이산화
# l_bound: 최소점, u_bound: 최대점, s_point: 분할점
# v_s_points: 구간경계점을 저정하는 벡터
l_bound = 0
u_bound = len(v_재적학생수) - 1
v_s_points = []  # 벡터(리스트) 초기화

# 엔트로피 계산을 위한 scipy.stats 모듈 임포트
from scipy.stats import entropy

# 기대정보요구량을 구하는 함수 정의
# 해당 구간에서 최소기대정보요구량을 나타내는 지점을 찾고 그 점을 경계로 재귀적으로 호출하는 구조
def info_gain(l_bound, u_bound) :
    i = l_bound + 1

    # 최소기대정보요구량의 위치 찾기
    while (i < u_bound) :
        # 기대정보요구량 계산
        v_info_gain = entropy(v_재적학생수[l_bound:(i + 1)])*(i - l_bound + 1) \
                      / (u_bound - l_bound + 1) \
                      + entropy(v_재적학생수[(i + 1):(u_bound + 1)]) * (u_bound - i) \
                      / (u_bound - l_bound + 1)

        # 최소값 찾기
        if (i == l_bound + 1) :
            min_info_gain = v_info_gain
            min_idx = i
        else :
            if (v_info_gain < min_info_gain) :
                min_info_gain = v_info_gain
                min_idx = i

        i = i + 1

    # 최소지점 위치를 v_s_points 벡터에 추가
    v_s_points.extend([min_idx])

    # 구간 수 20개 내외로 분할하기 위해 임계값을 5.2로 설정(trial and error 방식으로 찾음)
    if (min_info_gain < 5.2) :
        return 1

    # 경계점을 중심으로 한 재귀적 함수 호출
    info_gain(l_bound, min_idx)
    info_gain(min_idx, u_bound)

# 함수 호출
info_gain(l_bound, u_bound)

# 경계점 벡터 정렬(오름차순)
v_s_points.sort()

# 리스트 변수에 엔트로피 이산화 결과값(재적학생수, 대학수)을 행 단위로 저장
list_of_disc = []
for i in range(0, len(v_s_points)) :
    idx = v_s_points[i]
    list_of_disc.append([v_재적학생수[idx], idx])

# 데이터프레임 생성
rawData_disc = pd.DataFrame(list_of_disc, columns=['재적학생수', '대학수'])

print(rawData_disc)

# 카이제곱-결합 이산화
# 재적학생수와 지역 간의 카이제곱 검정에 의한 재적학생수 이산화

# 원본 데이터파일에서 '시군'과 '지정구분' 속성만 추출
rawData_kai = rawData.loc[:, ('지역','재적학생수')]

import cx_Oracle      # Oracle DB 연동을 위한 cx_Oracle 패키지 임포트
from scipy import stats  # 카이제곱검정을 위한 scipy 패키지 중 stats 모듈 임포트

# Oracle DB 연결
# 접속정보(connection string) : ID/PASS@CONNECTION_ALIAS
# CONNECTION_ALIAS : Oracle TNSNAMES.ORA 파일에 있는 접속정보 별칭(ALIAS)
conn_ora = cx_Oracle.connect("prep1/prep1@XE")

# DB 커서(Cursor) 선언
cur = conn_ora.cursor()

src_table = "d_base5_2"  # 사용할 Oracle 소스 테이블명 지정
ord_table = "d_base_ord"  # 소스테이블에서 재적학생수 기준으로 정렬하여 순번을 매긴 테이블명 지정
cont_table = "d_base_cont"  # 사용할 분할표(contingency table)을 저장할 Oracle 소스 테이블명 지정

# 데이터프레임(rawData)에 저장된 데이터를 Oracle 테이블(d_base5_2)에 입력하기 위한 로직
# d_base5_2 테이블 존재하는지 체크하는 함수
def table_exists(name=None, con=None):
    sql = "select table_name from user_tables where table_name='MYTABLE'".replace('MYTABLE', name.upper())
    df = pd.read_sql(sql, con)

    # 테이블이 존재하면 True, 그렇지 않으면 False 반환
    exists = True if len(df) > 0 else False
    return exists

# 테이블(d_base5_2) 생성 (테이블이 이미 존재한다면 TRUNCATE TABLE)
if table_exists(src_table, conn_ora):
    cur.execute("TRUNCATE TABLE " + src_table)
else:
    cur.execute("create table " + src_table + " ( \
               지역 varchar2(10), \
               재적학생수 number(6))")

# Sequence 구조를 Dictionary 구조((element, value))로 변환하는 함수
# 예: ("Matt", 1) -> {'1':'Matt', '2':1}
# INSERT INTO ... VALUES (:1, :2, ...) 에서 바인드 변수값을 주기위해 Dictionary item 구조 사용
def convertSequenceToDict(list):
    dict = {}
    argList = range(1, len(list) + 1)
    for k, v in zip(argList, list):
        dict[str(k)] = v
    return dict

# 데이터프레임에 저장된 데이터를 Oracle 테이블로 입력(insert)
cols = [k for k in rawData_kai.dtypes.index]
colnames = ','.join(cols)
colpos = ', '.join([':' + str(i + 1) for i, f in enumerate(cols)])
insert_sql = 'INSERT INTO %s (%s) VALUES (%s)' % (src_table, colnames, colpos)

# INSERT INTO ... VALUES (:1, :2, ...)의 바인드 변수 값을 저장하는 Dictionary 구조 생성
data = [convertSequenceToDict(rec) for rec in rawData_kai.values]

# 바인드 변수와 Dictionary 데이터구조를 활용하여 Bulk Insertion 구현
cur.executemany(insert_sql, data)
conn_ora.commit()

# 재적학생수 기준으로 오름차순 정렬
# 순번 테이블(d_base_ord) 생성 (테이블이 이미 존재한다면 TRUNCATE TABLE)
if table_exists(ord_table, conn_ora):
    cur.execute("TRUNCATE TABLE " + ord_table)
else:
    cur.execute("CREATE TABLE " + ord_table + " ( \
               지역 varchar2(10), \
               재적학생수 number(6), \
               순번 number(4))")

cur.execute("INSERT INTO " + ord_table +
            " select 지역, 재적학생수, \
            row_number() over (order by 재적학생수) - 1 순번 from " + src_table)

conn_ora.commit()

# df_재적학생수 : 재적학생수의 오름차순으로 정렬된 재적학생수 데이터프레임
df_재적학생수 = pd.read_sql("select 재적학생수 from " + ord_table + " order by 재적학생수", con=conn_ora)

# 분할표 테이블(d_base_cont) 생성 (테이블이 이미 존재한다면 TRUNCATE TABLE)
if table_exists(cont_table, conn_ora):
    cur.execute("TRUNCATE TABLE " + cont_table)
else:
    cur.execute("CREATE TABLE " + cont_table + " ( \
               지역 varchar2(10), \
               구간 varchar2(7))")

# 카이제곱 검정을 통해 구간병합을 할지 말지를 결정하는 함수
def chi_process(l_bound1, u_bound1, l_bound2, u_bound2) :

    # 이전 구간의 분할표 데이터 삭제
    cur.execute("TRUNCATE TABLE " + cont_table)

    # 관측도수 분할표 생성
    cur.execute("INSERT INTO " + cont_table +
                " select 지역 \
                , case when 순번 between " + str(l_bound1) + " and " + str(u_bound1) +
                " then '구간1' else '구간2' end 구간 \
                from " + ord_table +
                " where 순번 between " + str(l_bound1) + " and " + str(u_bound2))

    conn_ora.commit()

    # 관측도수/기대도수 분할표 생성 (1차원 배열 형식)
    count_df = pd.read_sql(" \
             select a.지역 \
                  , a.구간 \
                  , nvl(b.관측도수,0) 관측도수 /*관측되지 않은 (지역+구간)은 0으로 처리*/ \
                  , a.기대도수_지역 * a.기대도수_구간 / a.기대도수_전체 기대도수 \
             from ( select x.지역, y.구간 \
                         , x.기대도수_지역 \
                         , y.기대도수_구간 \
                         , x.기대도수_전체 \
                    from ( select 지역 \
                                , count(*) 기대도수_지역 /* 지역 속성의 cardinality */ \
                                , sum(count(*)) over () 기대도수_전체 /*전체 행 개수*/ \
                           from " + cont_table + " \
                           group by 지역 ) x, \
                         ( select 구간 \
                                , count(*) 기대도수_구간 /* 구간 속성의 cardinality */ \
                           from " + cont_table + " \
                           group by 구간 ) y ) a, \
                  ( select 지역 \
                         , 구간 \
                         , count(*) 관측도수 /* 지역, 구간 별 실제 행 개수 */ \
                    from " + cont_table + " \
                    group by 지역, 구간 ) b \
             where a.지역 = b.지역(+) /* 특정 (지역+구간) 값은 존재하지 않을 수 있어서 외부조인으로 처리 */ \
                  and a.구간 = b.구간(+)", con=conn_ora)

    # 2개 속성에 대한 자유도(degree of freedom) 갭 구하기
    # A 속성에 대한 cardinality = a, B 속성에 대한 cardinality = b라 가정
    # cardinality : 서로 다른 속성값의 개수
    # 분할표 전체 행 갯수(a*b) 구하기
    tot_rows = count_df.shape[0]

    # A 속성의 cardianlity(a)와 B 속성의 cardinality(b) 구하기
    count_df2 = pd.read_sql("select count(distinct 지역) 도수_지역 \
                               , count(distinct 구간) 도수_구간 \
                          from " + cont_table, con=conn_ora)

    # cardinality 갭 [(a*b-1) - (a-1)*(b-1)] 구하기
    v_ddof = (tot_rows - 1) - (count_df2['도수_지역'] - 1) * (count_df2['도수_구간'] - 1)

    obs_array = count_df['관측도수']  # obs_array : 관측도수를 저장하는 1차원 배열
    exp_array = count_df['기대도수']  # exp_array : 기대도수를 저장하는 1차원 배열

    # stats.chisquare() : 카이제곱검정 함수
    chis = stats.chisquare(obs_array, exp_array, ddof=v_ddof)

    # pvalue 임계치(0.35)는 구간수 20개 내외를 맞추기 위해 시행착오(trial & error) 방식으로 찾음
    if (chis.pvalue[0] > 0.35) :
        return(True)    # 구간들이 클래스와 독립적이므로 구간병합
    else :
        return(False)   # 구간들이 클래스와 독립적이라 볼 수 없으므로 병합하지 않음

# gugan_len : 초기 구간 단위를 30으로 일정하게 잡음
# boundary_idx : 구간 경계점의 위치를 저장하는 벡터
gugan_len = 30
i = 0
boundary_idx = []

# 구간 경계점의 위치를 지정 (30단위로)
while (i*gugan_len <= len(df_재적학생수)) :
    boundary_idx.extend([i*gugan_len])
    i = i + 1

# 마지막 구간 경계점 지점 (반드시 30단위로 된다고 볼 수 없으므로 별도 지정)
boundary_idx.extend([len(df_재적학생수)-1])

# 인접 구간과의 카이제곱 검정을 통해 p-value가 특정 임계치 이상인 경우(병합이 필요한 경우)는
# 해당 경계점의 boundary_idx 값을 -1로 세팅
# boundary_idx를 차례로 순환하면서 병합지점을 찾고,
# 순환 동안 병합이 한번도 발생하지 않을 시에 while루프 탈출
while (1) :
    merge_cnt = 0
    i = 0
    ind = 1

    # l_bound1: 인접 두 구간 중 첫번째 구간의 왼쪽 경계점
    # u_bound1: 인접 두 구간 중 첫번째 구간의 오른쪽 경계점
    # l_bound2: 인접 두 구간 중 두번째 구간의 왼쪽 경계점
    # u_bound2: 인접 두 구간 중 두번째 구간의 오른쪽 경계점
    while (i < len(boundary_idx)-1) :
        if (boundary_idx[i] == -1) :
            i = i + 1
        elif (ind == 1) :
            l_bound1 = boundary_idx[i]
            i = i + 1
            ind = ind + 1
        elif (ind == 2) :
            u_bound1 = boundary_idx[i] - 1
            l_bound2 = boundary_idx[i]
            merge_idx = i
            i = i + 1
            ind = ind + 1
        elif (ind == 3) :
            u_bound2 = boundary_idx[i] - 1

            # 인접 구간의 경계점을 패러미터로 주고 카이제곱 검정 사용자정의 함수 호출
            if (chi_process(l_bound1, u_bound1, l_bound2, u_bound2)) :
                # 병합이 필요한 경우에는 두 구간 경계점의 boundary_idx 값을 -1로 세팅
                boundary_idx[merge_idx] = -1
                merge_cnt = merge_cnt + 1  # 병합 카운트 1증가
            ind = 1

    # 병합 카운트가 0일 때(순환주기 동안 병합이 한번도 일어나지 않을 때), 루프 탈출
    if (merge_cnt == 0) :
        break

cur.close()  # 커서(cursor) 종료
conn_ora.close()  # Oracle connection 종료

# 결과보기
i = 1
v_s_points = []   # 구간 분할 경계점을 저장하는 벡터 초기화

# boundary_idx가 -1일 경우는 구간 병합을 의미하므로 분할 경계점에서 제외
while (i < len(boundary_idx)-1) :
    if (boundary_idx[i] != -1) :
        v_s_points.extend([boundary_idx[i] - 1])
    i = i + 1

# 리스트 변수에 엔트로피 이산화 결과값(재적학생수, 대학수)을 행 단위로 저장
list_of_disc = []
for i in range(0, len(v_s_points)) :
    idx = v_s_points[i]
    list_of_disc.append([df_재적학생수.loc[idx,'재적학생수'], idx])

# 데이터프레임 생성
rawData_disc = pd.DataFrame(list_of_disc, columns=['재적학생수', '구간경계점(대학수)'])

print(rawData_disc)

# 직관적 분할에 의한 재적학생수 이산화
# v_s_points : 재적학생수 구간 경계점을 저장하는 벡터(리스트)
v_s_points = []  # 초기화

# 3-4-5 규칙을 재귀적으로 적용하는 함수
# l_bound : 구간 최소값
# u_bound : 구간 최대값
# v_depth : 함수 호출 depth
def intuitive_split(l_bound, u_bound, v_depth) :

    # 문자형 변환
    l_bound_str = str(l_bound)
    u_bound_str = str(u_bound)

    # 문자길이 반환
    ms_pos = len(u_bound_str)

    # 서로 다른 가장 큰 유효숫자(Most Significant Bit, MSB) 의 갯수 구하기
    i = l_bound
    ms_v = ""

    # 구간 내 숫자별 MSB를 구하여 ms_v에 저장
    while (i <= u_bound) :
        ele_str = str(i)
        ms_v = ms_v + ele_str[0]
        i = i+1

    # 중복 배제
    ms_v_unique = set(ms_v)

    # ms_card : 서로 다른 MSB의 갯수 저장
    ms_card = len(ms_v_unique)

    # ms_card의 수에 따라 분할 구간 수를 다르게 함 (3-4-5 규칙에 따라)
    if (ms_card == 3 or ms_card == 6 or ms_card == 9) :

        # gugan_len : 단위 구간 길이
        gugan_len = round((u_bound - l_bound) / 3, 0)

        # 2번째 중첩 호출(v_depth: 2)에서 구간 분할을 끝냄
        if (v_depth == 2) :
            # 구간 경계점 벡터 v_s_points에 요소 추가
            v_s_points.extend([l_bound])
            v_s_points.extend([l_bound + gugan_len])
            v_s_points.extend([l_bound + gugan_len * 2])
            v_s_points.extend([u_bound])
            return (True)
        else :
            # 1번째 함수 호출에서는 구간 범위를 달리하여 재귀적 함수 호출
            intuitive_split(l_bound, l_bound + gugan_len, v_depth + 1)
            intuitive_split(l_bound + gugan_len, l_bound + gugan_len * 2, v_depth + 1)
            intuitive_split(l_bound + gugan_len * 2, u_bound, v_depth + 1)
    elif (ms_card == 7) :
        gugan_len = round((u_bound - l_bound) / 7, 0)
        if (v_depth == 2) :
            v_s_points.extend([l_bound])
            v_s_points.extend([l_bound + gugan_len * 2])
            v_s_points.extend([l_bound + gugan_len * 5])
            v_s_points.extend([u_bound])
            return (True)
        else :
            intuitive_split(l_bound, l_bound + gugan_len * 2, v_depth + 1)
            intuitive_split(l_bound + gugan_len * 2, l_bound + gugan_len * 5, v_depth + 1)
            intuitive_split(l_bound + gugan_len * 5, u_bound, v_depth + 1)
    elif (ms_card == 2 or ms_card == 4 or ms_card == 8) :
        gugan_len = round((u_bound - l_bound) / 4, 0)
        if (v_depth == 2) :
            v_s_points.extend([l_bound])
            v_s_points.extend([l_bound + gugan_len])
            v_s_points.extend([l_bound + gugan_len * 2])
            v_s_points.extend([l_bound + gugan_len * 3])
            v_s_points.extend([u_bound])
            return (True)
        else :
            intuitive_split(l_bound, l_bound + gugan_len, v_depth + 1)
            intuitive_split(l_bound + gugan_len, l_bound + gugan_len * 2, v_depth + 1)
            intuitive_split(l_bound + gugan_len * 2, l_bound + gugan_len * 3, v_depth + 1)
            intuitive_split(l_bound + gugan_len * 3, u_bound, v_depth + 1)
    elif (ms_card == 1 or ms_card == 5 or ms_card == 10) :
        gugan_len = round((u_bound - l_bound) / 5, 0)
        if (v_depth == 2) :
            v_s_points.extend([l_bound])
            v_s_points.extend([l_bound + gugan_len])
            v_s_points.extend([l_bound + gugan_len * 2])
            v_s_points.extend([l_bound + gugan_len * 3])
            v_s_points.extend([l_bound + gugan_len * 4])
            v_s_points.extend([u_bound])
            return (True)
        else :
            intuitive_split(l_bound, l_bound + gugan_len, v_depth + 1)
            intuitive_split(l_bound + gugan_len, l_bound + gugan_len * 2, v_depth + 1)
            intuitive_split(l_bound + gugan_len * 2, l_bound + gugan_len * 3, v_depth + 1)
            intuitive_split(l_bound + gugan_len * 3, l_bound + gugan_len * 4, v_depth + 1)
            intuitive_split(l_bound + gugan_len * 4, u_bound, v_depth + 1)

# 함수 호출
v_재적학생수.sort()
intuitive_split(v_재적학생수[0], v_재적학생수[len(v_재적학생수)-1], 1)

# 중복값 제거 및 오름차순 정렬
list_of_disc = list(set(v_s_points))
list_of_disc.sort()

# 데이터프레임 생성
rawData_disc = pd.DataFrame(list_of_disc, columns=['재적학생수'])

print(rawData_disc)