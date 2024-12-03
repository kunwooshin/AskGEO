import psycopg2
import pandas as pd
from sqlalchemy import create_engine, text
from util import util, loader, const
import json
import geopandas as gpd
from shapely.geometry import Point, Polygon


class AskGeo:
    def __init__(self, database_uri):
        self.DATABASE_URI = loader.DATABASE_URI


def main():
    # loader.load_sample_data()
    print("Welcome to Askgeo!")
    print("Askgeo is a geospatial question answering chat bot.")
    print("You can ask questions about geospatial data in the database.")
    print("If you want to exit, type 'exit'.")
    print("ex1) Show me the buildings within 300 meters of the Cultural Center")
    print("ex2) Tell me the coordinate of KWANJEONG Library")

    initial_query = False
    while True:
        if initial_query:
            user_query = 'Show me the buildings within 300 meters of the Culture Center'
            # user_query = 'Tell me the coordinate of KWANJEONG Library'
            initial_query = False
        else:
            user_query = input('Question: ')
            if user_query.lower() == "exit":
                print("Goodbye!")
                break

        # FIXME: 사용자에게 additional information 요구하는 추가 질문하는 대화 추가.
        prompt = const.input_prompt.format(user_query=user_query)
        response = loader.llm_call(prompt)
        print(response)

        answer, map_result = util.handle_action(response)

        if answer == 'unknown action':
            print('Out of my knowledge')
            continue
        elif answer == 'no data':
            continue

        print(answer)
        print(map_result)

    # Entry point


if __name__ == "__main__":
    main()
