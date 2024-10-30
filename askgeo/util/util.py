import folium
from shapely import wkt

do_log = True


def log(module, title, content):
    if not do_log:
        return
    # Print the header with module and title
    print(f"{'=' * 5} [{module}] {title} {'=' * 8}")

    print(content)

    # Print the footer with "{title} end"
    print(f"{'=' * 5} [{module}] {title} end {'=' * 5}")
    print()
    print()


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
