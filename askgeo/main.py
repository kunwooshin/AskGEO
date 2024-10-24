import psycopg2
import pandas as pd
from sqlalchemy import create_engine, text
from util import util, loader
import json


def main():
    loader.load_sample_data()
    loader.create_metadata_collection('table_names')
    # user_query = input("Enter your question for the Askgeo: ")
    user_query = 'Leonard Gordon Park 자전거 정류장 좌표알려줘' # 정확한 명칭 입력했다고 가정
    sql = util.text_to_sql(user_query)
    wkt_point = util.retrieve_point(sql)
    
    if wkt_point:
        # 사용자 질의에서 name도 추출할 수 있도록 질의 정제 필요
        name = 'Leonard Gordon Park Station'
        util.generate_map(name , wkt_point)

        # llm이 wkt_point와 name을 활용해서 대답할 수 있도록 수정해야함
        print("LLM Response:", wkt_point)
    else:
        print("No WKT Point found in the database.")

# Entry point
if __name__ == "__main__":
    main()