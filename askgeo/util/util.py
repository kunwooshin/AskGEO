from sqlalchemy import create_engine, text
from shapely import wkt
import folium
from . import loader, const
from shapely import wkt
import folium
from tabulate import tabulate
import json

DATABASE_URI = loader.DATABASE_URI


def text_to_sql(user_query):
    # 1. 메타데이터 검색
    # 1-1. 필요한 테이블명
    # 1-2. Text-to-SQL 프롬프트 지시문 (e.g., 좌표는 ST_AsText(ST_MakePoint()) 사용)
    collection = loader.connect_vectorDB('table_names')
    results = collection.query(query_texts=user_query, n_results=1)  # 일단 single query 일 때만
    table_name = results['metadatas'][0][0]['table_name']
    instruction = 'single coordinate (latitude, longitude) should be wrapped with ST_AsText(ST_MakePoint())' # query를 조금 정제해서 이 instruction이 뽑혀나오도록 해야함. instruction용 메타데이터 db도 따로 생성하기
    
    # 2. DB에서 테이블 스키마 검색
    query = const.schema_retrieval_query.format(table_name = table_name)
    engine = create_engine(DATABASE_URI)

    with engine.connect() as conn:
        result = conn.execute(text(query), {"table_name": table_name})
        rows = result.fetchall()
        headers = result.keys()
    
    table_schema = 'TABLE: ' + table_name +'\n' + tabulate(rows, headers, tablefmt="grid")
    
    # 3. user_query + table_schema + 필요시 few-shot 등을 통해 sql 생성
    prompt = const.text_to_sql_prompt.format(table_schema = table_schema, instruction = instruction, user_query = user_query, few_shot_examples = None)

    res = loader.llm_call(prompt)
    
    json_res = res.replace("```json", "")
    json_res = json_res.replace("```", "")
    json_res = json_res.replace('\\', '').replace('\n', '').replace('\r', '')

    try:
        json_res = json.loads(json_res)
        geospatial_query = json_res['full_sql_query']
    except json.decoder.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}")
        print(res.choices[0].message.content)
        
    return geospatial_query

def retrieve_point(point_retrieval_query):
    engine = create_engine(DATABASE_URI)
    
    with engine.connect() as conn:
        result = conn.execute(text(point_retrieval_query))
        rows = result.fetchall()
        
    wkt_point = rows[0][0] if rows else None # 출력 결과가 안나오면 사용자에게 다시 묻기
    return wkt_point

# Function to generate a map using WKT point
def generate_map(name, wkt_point):
    if wkt_point:
        point = wkt.loads(wkt_point)
        coordinates = [point.y, point.x]  # POINT(경도, 위도)
        
        mymap = folium.Map(location=coordinates, zoom_start=15)
        folium.Marker(location=coordinates, popup=f'{name}').add_to(mymap)

        # Save map to file
        map_output_path = "./data/citibike_wkt_map.html"
        mymap.save(map_output_path)
        
        return map_output_path
    else:
        return "No WKT Point Found."
