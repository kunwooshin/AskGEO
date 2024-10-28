import json
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from tabulate import tabulate

import askgeo.llm.gpt as llm
from askgeo.database.geodb import const
from askgeo.util.util import log

# Load environment variables
load_dotenv()

# Database and API configurations from .env file
HOST = os.getenv('DB_HOST')
PORT = os.getenv('DB_PORT')
USER = os.getenv('DB_USER')
PASSWORD = os.getenv('DB_PASSWORD')
DATABASE = os.getenv('DB_NAME')
DATABASE_URI = f'postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}'

engine = None


def get_engine():
    global engine
    if engine is None:
        engine = create_engine(DATABASE_URI)
    return engine


def generate_sql(user_query, metadata):
    instruction = 'single coordinate (latitude, longitude) should be wrapped with ST_AsText(ST_MakePoint())'  # query를 조금 정제해서 이 instruction이 뽑혀나오도록 해야함. instruction용 메타데이터 db도 따로 생성하기

    # 2. DB에서 테이블 스키마 검색
    table_name = metadata.get('table_name')
    query = const.schema_retrieval_query.format(table_name=table_name)

    with get_engine().connect() as conn:
        result = conn.execute(text(query), {"table_name": table_name})
        rows = result.fetchall()
        headers = result.keys()

    table_schema = 'TABLE: ' + table_name + '\n' + tabulate(rows, headers, tablefmt="grid")

    # 3. user_query + table_schema + 필요시 few-shot 등을 통해 sql 생성
    prompt = const.text_to_sql_prompt.format(table_schema=table_schema, instruction=instruction, user_query=user_query,
                                             few_shot_examples=None)

    res = llm.inquire_prompt(prompt)

    json_res = res.replace("```json", "")
    json_res = json_res.replace("```", "")
    json_res = json_res.replace('\\', '').replace('\n', '').replace('\r', '')

    geospatial_query = None
    try:
        json_res = json.loads(json_res)
        geospatial_query = json_res['full_sql_query']
    except json.decoder.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}")
        print(res.choices[0].message.content)

    log('geodb','generate_sql',geospatial_query)
    return geospatial_query


def execute_sql(sql):
    with get_engine().connect() as conn:
        result = conn.execute(text(sql))
        rows = result.fetchall()

    return rows
