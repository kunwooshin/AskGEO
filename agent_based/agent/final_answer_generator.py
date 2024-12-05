import folium
from shapely.wkt import loads as load_wkt
from pyproj import Transformer

import os

from dotenv import load_dotenv
from openai import OpenAI

# Initialize OpenAI
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm = OpenAI(api_key=OPENAI_API_KEY)

INSTRUCTION = """
You are a knowledgeable assistant tasked with generating a final answer based on a series of questions and their corresponding responses. Use the provided information to create a clear, coherent, and comprehensive answer.

Here is the data you have:

You must also include the key execution result from databased you've referenced to generate the final answer.
"""

# Function to refine the GPT query
def generate_response(prompt):
    response = llm.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {"role": "user", "content": prompt},
        ],
        temperature=0
    )

    return response.choices[0].message.content.strip()


# Main function
def inquire(history):
    # Example user question
    iteration = 0

    # Create initial prompt
    prompt = INSTRUCTION

    for line in history:
        prompt += line + "\n"

    response = generate_response(prompt)
    visualize(response)
    
    return response, prompt


def parse_response_to_json(response):
    prompt = f"""
Extract name and geometry data(e.g, POLYGON, POINT, LINESTRING, etc) from the text given.

Text:
{response}

Please respond with a JSON object structured as follows (if the sql query is correct, return the query as it is):
[
    {{
        "name": "관정도서관",
        "geometry": "POLYGON((...))"
    }},
    {{
        "name": "파리바게뜨",
        "geometry": "POINT(...)"
    }},

    ...
]
"""

    res = llm.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {"role": "user", "content": prompt},
        ],
        temperature=0
    )

    json_res = res.choices[0].message.content

    json_res = json_res.replace("```json", "")
    json_res = json_res.replace("```", "")
    json_res = json_res.replace('\\', '').replace('\n', '').replace('\r', '')
    print(json_res)
    return eval(json_res)


def visualize(response):
    print
    # GPT를 통해 JSON 데이터 추출
    try:
        locations = parse_response_to_json(response)
        # print(locations)
    except Exception as e:
        print("Error parsing response:", e)
        return None
    
    if not locations:
        return None
    
    # Folium 맵 초기화
    initial_point = (37.459882, 126.951905)  # Default 서울대학교 좌표
    m = folium.Map(location=initial_point, zoom_start=16)
    # 좌표 변환기 생성 (EPSG:3857 → EPSG:4326)
    transformer = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)
    
    def transform_coordinates(coords):
        return [transformer.transform(x, y) for x, y in coords]
    
    for loc in locations:
        geom = load_wkt(loc["geometry"])
        if geom.geom_type == 'Point':
            # Transform Point coordinates
            transformed_coords = transformer.transform(geom.x, geom.y)
            folium.Marker(
                location=(transformed_coords[1], transformed_coords[0]),
                popup=folium.Popup(loc["name"])
            ).add_to(m)
        
        elif geom.geom_type == 'Polygon':
            # Transform Polygon coordinates
            transformed_coords = transform_coordinates(geom.exterior.coords)
            folium.Polygon(
                locations=[(lat, lon) for lon, lat in transformed_coords],
                color='blue',
                fill=True,
                fill_opacity=0.4,
                popup=folium.Popup(loc["name"])
            ).add_to(m)
            
        elif geom.geom_type == 'LineString':
            # Transform LineString coordinates
            transformed_coords = transform_coordinates(geom.coords)
            folium.PolyLine(
                locations=[(lat, lon) for lon, lat in transformed_coords],
                color='green',
                weight=4,
                popup=folium.Popup(loc["name"])
            ).add_to(m)

    # 저장 디렉토리 확인 및 생성
    output_dir = "./map"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # HTML 파일로 저장
    map_path = os.path.join(output_dir, "map.html")
    m.save(map_path)
    
    return map_path

if __name__ == "__main__":
    question = "공대위치와 도서관위치를 알려줘."
    result, full_prompt = inquire(question)
    print(result)
