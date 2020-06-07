# ch4-1.py
import pandas as pd
import numpy as np
import cx_Oracle      # Oracle DB 연동을 위한 cx_Oracle 패키지 임포트

# 데이터로드 (ch4-1.csv : 데이터 원본 파일)
# encoding : 윈도우즈 환경에서의 한글 처리
# engine : python 3.6에서 한글이 포함된 파일이름 사용
rawData = pd.read_csv('chap4/ch4-1(국내대학현황).csv', encoding='CP949', engine='python')

# Oracle DB 연결
# 접속정보(connection string) : ID/PASS@CONNECTION_ALIAS
# CONNECTION_ALIAS : Oracle TNSNAMES.ORA 파일에 있는 접속정보 별칭(ALIAS)
conn_ora = cx_Oracle.connect("prep1/prep1@XE")

# DB 커서(Cursor) 선언
cur = conn_ora.cursor()

# 사용할 Oracle 소스 테이블명 지정
src_table = "d_base4_1"

# 데이터프레임(rawData)에 저장된 데이터를 Oracle 테이블(d_base4_1)에 입력하기 위한 로직
# d_base4_1 테이블 존재하는지 체크하는 함수
def table_exists(name=None, con=None):
    sql = "select table_name from user_tables where table_name='MYTABLE'".replace('MYTABLE', name.upper())
    df = pd.read_sql(sql, con)

    # 테이블이 존재하면 True, 그렇지 않으면 False 반환
    exists = True if len(df) > 0 else False
    return exists

# 테이블(d_base4_1) 생성 (테이블이 이미 존재한다면 TRUNCATE TABLE)
if table_exists(src_table, conn_ora):
    cur.execute("TRUNCATE TABLE " + src_table)
else:
    cur.execute("create table " + src_table + " ( \
               학제 varchar2(40), \
               학교명 varchar2(100), \
               지역 varchar2(10), \
               설립 varchar2(20), \
               재적학생수 number(8), \
               재학생수 number(8), \
               휴학생수 number(8), \
               총장및전임교원수 number(8))")

# Sequence 구조를 Dictionary 구조((element, value))로 변환하는 함수
# 예: ("Matt", 1) -> {'1':'Matt', '2':1}
# INSERT INTO ... VALUES (:1, :2, ...) 에서 바인드 변수값을 주기위해 Dictionary item 구조 사용
def convertSequenceToDict(list):
    dict = {}
    argList = range(1, len(list) + 1)
    for k, v in zip(argList, list):
        if pd.isnull(v):
            dict[str(k)] = -1 # list 요소 값이 NULL이면 -1로 assign
        else:
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

# 컬럼값이 -1이면, NULL값으로 업데이트
cur.execute("update " + src_table +
           " set 재적학생수 = decode(재적학생수,-1,NULL,재적학생수) \
             , 재학생수 = decode(재학생수,-1,NULL,재학생수) \
             , 휴학생수 = decode(휴학생수,-1,NULL,휴학생수) \
             , 총장및전임교원수 = decode(총장및전임교원수,-1,NULL,총장및전임교원수) \
           where 재적학생수 = -1 OR 재학생수 = -1 OR 휴학생수 = -1 OR 총장및전임교원수 = -1")

# csv 파일 데이터의 Oracle 테이블 입력 완료
conn_ora.commit()

# cube(), grouping() 함수를 이용한 데이터큐브 뷰(view) 생성
cur.execute("create or replace view v_base4_1 \
           as \
           select decode(grouping(지역), 1, '총계', 지역) 지역 \
                , decode(grouping(학제), 1, '총계', 학제) 학제 \
                , decode(grouping(설립), 1, '총계', 설립) 설립 \
                , sum(재학생수) 재학생수 \
           from " + src_table +
           " group by cube(지역, 학제, 설립)")

# (1) 지역/학제/설립 별 재학생수
result_df = pd.read_sql("select 지역, 학제, 설립, 재학생수 \
                     from v_base4_1 \
                     where 지역 <> '총계' and 학제 <> '총계' and 설립 <> '총계'", con=conn_ora)
print("(1) 지역/학제/설립 별 재학생수")
print(result_df)

# (2) 지역/학제 별 재학생수(설립 집계 레벨)
result_df = pd.read_sql("select 지역, 학제, 재학생수 \
                     from v_base4_1 \
                     where 지역 <> '총계' and 학제 <> '총계' and 설립 = '총계'", con=conn_ora)
print("(2) 지역/학제 별 재학생수(설립 집계 레벨)")
print(result_df)

# (3) 학제/설립 별 재학생수(지역 집계 레벨)
result_df = pd.read_sql("select 학제, 설립, 재학생수 \
                     from v_base4_1 \
                     where 지역 = '총계' and 학제 <> '총계' and 설립 <> '총계'", con=conn_ora)
print("(3) 학제/설립 별 재학생수(지역 집계 레벨)")
print(result_df)

# (4) 지역/설립 별 재학생수(학제 집계 레벨)
result_df = pd.read_sql("select 지역, 설립, 재학생수 \
                     from v_base4_1 \
                     where 지역 <> '총계' and 학제 = '총계' and 설립 <> '총계'", con=conn_ora)
print("(4) 지역/설립 별 재학생수(학제 집계 레벨)")
print(result_df)

# (5) 지역 별 재학생수(학제/설립 집계 레벨)
result_df = pd.read_sql("select 지역, 재학생수 \
                     from v_base4_1 \
                     where 지역 <> '총계' and 학제 = '총계' and 설립 = '총계'", con=conn_ora)
print("(5) 지역 별 재학생수(학제/설립 집계 레벨)")
print(result_df)

# (6) 학제 별 재학생수(지역/설립 집계 레벨)
result_df = pd.read_sql("select 학제, 재학생수 \
                     from v_base4_1 \
                     where 지역 = '총계' and 학제 <> '총계' and 설립 = '총계'", con=conn_ora)
print("(6) 학제 별 재학생수(지역/설립 집계 레벨)")
print(result_df)

# (7) 설립 별 재학생수(지역/학제 집계 레벨)
result_df = pd.read_sql("select 설립, 재학생수 \
                     from v_base4_1 \
                     where 지역 = '총계' and 학제 = '총계' and 설립 <> '총계'", con=conn_ora)
print("(7) 설립 별 재학생수(지역/학제 집계 레벨)")
print(result_df)

# (8) 총 재학생수 (지역/학제/설립 집계 레벨)
result_df = pd.read_sql("select 재학생수 \
                     from v_base4_1 \
                     where 지역 = '총계' and 학제 = '총계' and 설립 = '총계'", con=conn_ora)
print("(8) 총 재학생수 (지역/학제/설립 집계 레벨)")
print(result_df)

cur.close()   # 커서(cursor) 종료
conn_ora.close()  # Oracle connection 종료