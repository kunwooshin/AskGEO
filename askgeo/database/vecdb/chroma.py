import os

import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

collection = None


def get_collection():
    global collection
    if collection is None:
        collection = connect_vectorDB('table_names')
    return collection


def connect_vectorDB(metadata_type):
    global collection
    client = chromadb.PersistentClient(path='./data/metadata/')
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=OPENAI_API_KEY,
        model_name="text-embedding-3-small"
    )
    collection_name = metadata_type

    collection = client.get_collection(
        name=collection_name,
        embedding_function=openai_ef,
    )

    return collection


def retrieve_table_names(user_prompt):
    results = get_collection().query(query_texts=user_prompt, n_results=1)  # 일단 single query 일 때만
    table_name = results['metadatas'][0][0]['table_name']
    return table_name
