from sqlalchemy import create_engine, text
import folium
from . import loader, const
from shapely import wkt, wkb
import folium
from tabulate import tabulate
import json
import pandas as pd
from datetime import datetime
from sentence_transformers import SentenceTransformer

import faiss
import numpy as np

DATABASE_URI = loader.DATABASE_URI
# FIXME 나중에 main 시작할 함께 호출되도록 refactoring
entity_embeddings = loader.load_embeddings_for_search_help()


def handle_action(response):
    """
    Parses the response JSON and calls the appropriate function based on the action.
    """
    json_res = response.replace("```json", "")
    json_res = json_res.replace("```", "")
    json_res = json_res.replace('\\', '').replace('\n', '').replace('\r', '')

    try:
        json_res = json.loads(json_res)
        action = json_res.get("action")
        parameters = json_res.get("parameters", {})

        building_lst = pd.read_csv('./data/snu.csv', header=None)[0].tolist()[1:]

        # Action에 따라 함수 연결
        if action == "find_nearby_buildings":
            if parameters.get("building_name") in building_lst:
                building = parameters.get("building_name")
            else:
                building = search_help(parameters.get("building_name"))
                if building.lower() == 'no':
                    print(f'No data related to {parameters.get("building_name")} exists')
                    return 'no data', 'no data'

            answer, map_result = find_nearby_buildings(building, parameters.get("distance"))
            return answer, map_result

        elif action == "find_coordinates":
            if parameters.get("building_name") in building_lst:
                building = parameters.get("building_name")
            else:
                building = search_help(parameters.get("building_name"))
                if building.lower() == 'no':
                    print(f'No data related to {parameters.get("building_name")} exists')
                    return 'no data', 'no data'

            answer, map_result = find_coordinates(building)
            return answer, map_result

        elif action == "ambiguous_query":
            print('Please provide more specific details or a valid geospatial operation.')

            return 'more details'

        else:
            print(f"Unknown action")
            return 'unknown action', 'unknown action'

    except json.decoder.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}")
        print(response)
        return 'error', 'error'


def find_coordinates(building_name):
    try:
        engine = create_engine(DATABASE_URI)
        exact_query = text(const.exact_query)

        with engine.connect() as conn:
            exact_result = conn.execute(exact_query, {"building_name": building_name}).fetchall()

        res = pd.DataFrame(exact_result, columns=["name", "address", "location", "type", "polygon"])
        map_html = visualize(res, mode='find_coordinates')

        answer = tabulate(res[["name", "location", "address"]], headers="keys", tablefmt="grid")

        return answer, map_html

    except Exception as e:
        return f"Error querying database: {e}"


def find_nearby_buildings(building_name, distance):
    try:
        engine = create_engine(DATABASE_URI)
        nearby_query = text(const.nearby_query)

        with engine.connect() as conn:
            nearby_result = conn.execute(nearby_query,
                                         {"building_name": building_name, "distance": distance}).fetchall()

        if not nearby_result:
            print("No buildings found within the specified distance.")
            return 'additional chat', 'no map'
        # FIXME 가까운 빌딩 없을 때 로직 문제 해결

        res = pd.DataFrame(nearby_result, columns=["name", "address", "location", "type", "polygon", "distance"])

        map_html = visualize(res, mode='find_nearby_buildings')

        answer = tabulate(res.loc[1:, ["name", "distance"]], headers="keys", tablefmt="grid")

        return answer, map_html

    except Exception as e:
        return f"Error querying database: {e}"


def search_help(target_building):
    # FIXME 빌딩명 또 잘못 입력한 경우 해결
    # Step 1: Prepare the building list
    building_lst = pd.read_csv('./data/snu.csv', header=None)[0].tolist()[1:]
    # Step 2: Load a sentence transformer model
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

    # Step 4: Create a FAISS index
    dimension = entity_embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(entity_embeddings))

    # Step 5: Function to search for the closest matches
    def find_closest_buildings(target_building, k=3):
        query_embedding = model.encode([target_building])
        distances, indices = index.search(query_embedding, k)
        results = [(building_lst[i], distances[0][j]) for j, i in enumerate(indices[0])]
        return results

    results = find_closest_buildings(target_building)

    for building, distance in results:
        print(f"Suggested: {building}")

    revised_name = input('Select one from the suggestions or type "no" to reject them: ')

    return revised_name


def visualize(res, mode):
    # 지도 생성 (첫 번째 데이터의 위치 사용)
    first_location = res.iloc[0]["location"]
    latitude, longitude = map(float, first_location.replace("POINT (", "").replace(")", "").split())
    m = folium.Map(location=[latitude, longitude], zoom_start=16)

    if mode == 'find_nearby_buildings':
        for index, row in res.iterrows():
            # 마커 추가
            loc = row["location"]
            lat, lon = map(float, loc.replace("POINT (", "").replace(")", "").split())

            if index == 0:
                icon = folium.Icon(color="red")
            else:
                icon = folium.Icon(color="blue")

            folium.Marker(
                location=[lat, lon],
                popup=f"{row['name']} (Distance: {row['distance']} m)",
                tooltip=row["name"],
                icon=icon
            ).add_to(m)

    elif mode == "find_coordinates":
        for index, row in res.iterrows():
            loc = row["location"]
            lat, lon = map(float, loc.replace("POINT (", "").replace(")", "").split())

            shape = wkb.loads(row["polygon"])
            coords = list(shape.exterior.coords)

            folium.Marker(
                location=[lat, lon],
                popup=f"{row['name']} (Coordinate: latitude: {lat}, longitude: {lon})",
                tooltip=row["name"],
            ).add_to(m)

            folium.Polygon(
                locations=[[y, x] for x, y in coords],
                color="blue",
                weight=2,
                fill=True,
                fill_opacity=0.4
            ).add_to(m)

    # 고유한 파일 이름 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    m.save(f"./map/map_{timestamp}.html")
    print(f"map saved: 'map_{timestamp}.html'")

    return m
