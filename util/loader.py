from sqlalchemy import create_engine, text
from . import const
import json
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
import os
from dotenv import load_dotenv
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

from geopy.geocoders import Nominatim
import geopandas as gpd
from sqlalchemy import create_engine, text
from shapely.geometry import Point, Polygon

from tqdm import tqdm
from sentence_transformers import SentenceTransformer

import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Load environment variables
load_dotenv()

# Database and API configurations from .env file
HOST = os.getenv('DB_HOST')
PORT = os.getenv('DB_PORT')
USER = os.getenv('DB_USER')
PASSWORD = os.getenv('DB_PASSWORD')
DATABASE = os.getenv('DB_NAME')
DATABASE_URI = f'postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}'

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI
llm = OpenAI(api_key=OPENAI_API_KEY)

# Initialize Nominatim
geolocator = Nominatim(user_agent="Askgeo")


# Function to get response from OpenAI LLM
def llm_call(prompt):
    response = llm.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {"role": "user", "content": prompt},
        ],
        temperature=0
    )
    return response.choices[0].message.content


def load_embeddings_for_search_help():
    snu_lst = pd.read_csv('./data/snu.csv', header=None)[0].tolist()[1:]
    # Step 2: Load a sentence transformer model
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    # Step 3: Generate embeddings for the building names
    entity_embeddings = model.encode(snu_lst)
    return entity_embeddings


def load_sample_data():
    snu_lst = pd.read_csv('./data/snu.csv', header=None)[0].tolist()

    loc_data = []
    for building in tqdm(snu_lst, desc="Processing"):
        location = geolocator.geocode(f"{building}, 관악구", geometry='geojson')
        try:
            if location and 'geojson' in location.raw:
                loc_data.append({
                    "name": building,
                    "address": location.raw['display_name'],
                    "center": Point(location.latitude, location.longitude),
                    "class": location.raw['class'],  # 'building'이 amenity로 잘못 설정된 경우 존재
                    "geometry": Polygon(location.raw['geojson']['coordinates'][0]),
                })
            else:
                print(f"{building}: No search results found")
        except Exception as e:
            # 에러 발생 시 메시지 출력
            print(f"Error processing '{building}': {e}")

    gdf = gpd.GeoDataFrame(
        loc_data,
        crs="EPSG:4326"  # 좌표계 정의 (WGS84)
    )

    engine = create_engine(DATABASE_URI)
    gdf.to_postgis('snu', engine, if_exists='replace')

# def load_sample_data():
#     json_file_path = './data/citibike_stations_sample.json'
#     with open(json_file_path, 'r') as file:
#         data = json.load(file)

#     # SQLAlchemy 엔진 생성
#     engine = create_engine(DATABASE_URI)

#     with engine.connect() as conn:
#         conn.execute(text(const.sample_data['create_table_query']))
#         conn.execute(text(const.sample_data['insert_query']), data)


# def connect_vectorDB(metadata_type):
#     client = chromadb.PersistentClient(path='./data/metadata/')
#     openai_ef = embedding_functions.OpenAIEmbeddingFunction(
#         api_key=OPENAI_API_KEY,
#         model_name="text-embedding-3-small"
#     )
#     collection_name = metadata_type

#     collection = client.get_collection(
#         name=collection_name,
#         embedding_function=openai_ef,
#     )

#     return collection

# def create_metadata_collection(metadata_type):
#     openai_ef = embedding_functions.OpenAIEmbeddingFunction(
#         api_key=OPENAI_API_KEY,
#         model_name="text-embedding-3-small"
#     )

#     db_path = './data/metadata/'
#     client = chromadb.PersistentClient(path=db_path)

#     if metadata_type == 'table_names':
#         json_file_path = db_path + 'spatialdb_desc.json'
#         with open(json_file_path, 'r') as file:
#             data = json.load(file)

#         collection = client.get_or_create_collection(
#             name=metadata_type,
#             embedding_function=openai_ef,
#             metadata={"hnsw:space": "cosine"}
#         )

#         # Add documents and embeddings to ChromaDB collection
#         if collection.count() == 0:
#             print("CREATING TABLE-NAMES-COLLECTION...")
#             collection.add(
#                 ids=[f"table_{i}" for i in range(len(data))],
#                 documents=[table['table_description'] for table in data],
#                 metadatas=[{"table_name": data[i]['table_name']} for i in range(len(data))]
#             )
#             print("TABLE-NAMES-COLLECTION CREATED!")
