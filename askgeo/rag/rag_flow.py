import askgeo.database.geodb.postgres as geodb
import askgeo.database.vecdb.chroma as vecdb
from askgeo.util.util import log


def setup():
    pass  # 필요한 셋업 수행


# 여기서는 사용자 쿼리를 받아서 각 db에 질의를 보내고, 그 결과를 활용해서 사용자에게 대답하는 것을 구현함
# 사용자 쿼리를 sql로 변환하는 것은 각 db의 retreiver의 역할임
# prompt: 자연어를 입력해서 결과를 받을 때
# query: sql을 입력해서 결과를 받을 때
def prompt(user_prompt):
    log('rag', 'user_prompt', user_prompt)
    table_names = vecdb.retrieve_table_names(user_prompt)
    log('rag', 'metadata', table_names)

    geodb_sql = geodb.generate_sql(user_prompt, {'table_name': table_names})
    geodb_result = geodb.execute_sql(geodb_sql)

    log('rag', 'final_result', geodb_result)
    if geodb_result:
        return geodb_result
    else:
        print("No WKT Point found in the database.")
