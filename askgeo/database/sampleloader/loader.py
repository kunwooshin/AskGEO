import json
import os

import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from dotenv import load_dotenv
from openai import OpenAI
from sqlalchemy import create_engine, text

from askgeo.database.sampleloader import const

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


def load_sample_data():
    json_file_path = './data/citibike_stations_sample.json'
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    # SQLAlchemy 엔진 생성
    engine = create_engine(DATABASE_URI)

    with engine.connect() as conn:
        conn.execute(text(const.sample_data['create_table_query']))
        conn.execute(text(const.sample_data['insert_query']), data)


def create_metadata_collection(metadata_type):
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=OPENAI_API_KEY,
        model_name="text-embedding-3-small"
    )

    db_path = './data/metadata/'
    client = chromadb.PersistentClient(path=db_path)

    if metadata_type == 'table_names':
        json_file_path = db_path + 'spatialdb_desc.json'
        with open(json_file_path, 'r') as file:
            data = json.load(file)

        collection = client.get_or_create_collection(
            name=metadata_type,
            embedding_function=openai_ef,
            metadata={"hnsw:space": "cosine"}
        )

        # Add documents and embeddings to ChromaDB collection
        if collection.count() == 0:
            print("CREATING TABLE-NAMES-COLLECTION...")
            collection.add(
                ids=[f"table_{i}" for i in range(len(data))],
                documents=[table['table_description'] for table in data],
                metadatas=[{"table_name": data[i]['table_name']} for i in range(len(data))]
            )
            print("TABLE-NAMES-COLLECTION CREATED!")


def load_data():
    load_sample_data()
    create_metadata_collection('table_names')
