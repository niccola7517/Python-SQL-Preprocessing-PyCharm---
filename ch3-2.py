# ch3-2.py
import pandas as pd
import numpy as np
import cx_Oracle      # Oracle DB 연동을 위한 cx_Oracle 패키지 임포트

# 데이터로드 (ch3-2.csv : 데이터 원본 파일)
# encoding : 윈도우즈 환경에서의 한글 처리
# engine : python 3.6에서 한글이 포함된 파일이름 사용
rawData_org = pd.read_csv('chap3/ch3-2(유망중소기업현황).csv', encoding='CP949', engine='python')

# 원본 데이터파일에서 '시군'과 '지정구분' 속성만 추출
rawData = rawData_org.loc[:,'시군':'지정구분']

# Oracle DB 연결
# 접속정보(connection string) : ID/PASS@CONNECTION_ALIAS
# CONNECTION_ALIAS : Oracle TNSNAMES.ORA 파일에 있는 접속정보 별칭(ALIAS)
conn_ora = cx_Oracle.connect("prep1/prep1@XE")

# DB 커서(Cursor) 선언
cur = conn_ora.cursor()

# 사용할 Oracle 소스 테이블명 지정
src_table = "d_base3_2"

# 데이터프레임(rawData)에 저장된 데이터를 Oracle 테이블(d_base3_2)에 입력하기 위한 로직
# d_base3_2 테이블 존재하는지 체크하는 함수
def table_exists(name=None, con=None):
    sql = "select table_name from user_tables where table_name='MYTABLE'".replace('MYTABLE', name.upper())
    df = pd.read_sql(sql, con)

    # 테이블이 존재하면 True, 그렇지 않으면 False 반환
    exists = True if len(df) > 0 else False
    return exists

# 테이블(d_base3_2) 생성 (테이블이 이미 존재한다면 TRUNCATE TABLE)
if table_exists(src_table, conn_ora):
    cur.execute("TRUNCATE TABLE " + src_table)
else:
    cur.execute("create table " + src_table + " ( \
               시군 varchar2(10), \
               지정구분 varchar2(20))")

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
cols = [k for k in rawData.dtypes.index]
colnames = ','.join(cols)
colpos = ', '.join([':' + str(i + 1) for i, f in enumerate(cols)])
insert_sql = 'INSERT INTO %s (%s) VALUES (%s)' % (src_table, colnames, colpos)

# INSERT INTO ... VALUES (:1, :2, ...)의 바인드 변수 값을 저장하는 Dictionary 구조 생성
data = [convertSequenceToDict(rec) for rec in rawData.values]

# 바인드 변수와 Dictionary 데이터구조를 활용하여 Bulk Insertion 구현
cur.executemany(insert_sql, data)
conn_ora.commit()

# 관측도수/기대도수 분할표 생성 (1차원 배열 형식)
count_df = pd.read_sql(" \
         select a.시군 \
              , a.지정구분 \
              , nvl(b.관측도수,0) 관측도수 /*관측되지않은 (시군+지정구분)은 0으로 처리*/ \
              , a.기대도수_시군 * a.기대도수_지정구분 / a.기대도수_전체 기대도수 \
         from ( select x.시군, y.지정구분 \
                     , x.기대도수_시군 \
                     , y.기대도수_지정구분 \
                     , x.기대도수_전체 \
                from ( select 시군 \
                            , count(*) 기대도수_시군 /* 시군 속성의 cardinality */ \
                            , sum(count(*)) over () 기대도수_전체 /* 전체 행 개수 */ \
                       from " + src_table + " \
                       group by 시군 ) x, \
                     ( select 지정구분 \
                            , count(*) 기대도수_지정구분 /* 지정구분 속성의 cardinality */ \
                       from " + src_table + " \
                      group by 지정구분 ) y ) a, \
              ( select 시군 \
                      , 지정구분 \
                      , count(*) 관측도수 /* 시군, 지정구분 별 실제 행 개수 */ \
                from " + src_table + " \
                group by 시군, 지정구분 ) b \
         where a.시군 = b.시군(+) /* 특정 (시군+지정구분) 값은 존재하지 않을 수 있어서 외부조인으로 처리 */ \
           and a.지정구분 = b.지정구분(+)", con=conn_ora)

# 관측도수/기대도수 분할표 출력
print(count_df)

# 2개 속성에 대한 자유도(degree of freedom) 갭 구하기
# A 속성에 대한 cardinality = a, B 속성에 대한 cardinality = b라 가정
# cardinality : 서로 다른 속성값의 개수
# 분할표 전체 행 갯수(a*b) 구하기
tot_rows = count_df.shape[0]

# A 속성의 cardianlity(a)와 B 속성의 cardinality(b) 구하기
count_df2 = pd.read_sql("select count(distinct 시군) 도수_시군 \
                           , count(distinct 지정구분) 도수_지정구분\
                      from " + src_table , con=conn_ora)

# cardinality 갭 [(a*b-1) - (a-1)*(b-1)] 구하기
v_ddof = (tot_rows - 1) - (count_df2['도수_시군']-1)*(count_df2['도수_지정구분']-1)

obs_array = count_df['관측도수'] # obs_array : 관측도수를 저장하는 1차원 배열
exp_array = count_df['기대도수'] # exp_array : 기대도수를 저장하는 1차원 배열

# 카이제곱검정을 위한 scipy 패키지 중 stats 모듈 임포트
from scipy import stats

# stats.chisquare() : 카이제곱검정 함수
chis = stats.chisquare(obs_array, exp_array, ddof=v_ddof)

# stats.chisquare() 수행 후의 카이제곱 통계량과 p-value
print("statistic = %.3f, p-value = %.5f" % (chis))

cur.close()   # 커서(cursor) 종료
conn_ora.close()  # Oracle connection 종료