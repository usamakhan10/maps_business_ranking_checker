import requests
from urllib.parse import quote

def get_bounding_box(place,api_key):
    address = quote(place)
    url = f"https://geocode.maps.co/search?q={address}&api_key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()[0]['boundingbox']
    else:
        print(f"AN error occured while  fetching the bounding box for {place}. Status Code: {response.status_code}")


def get_grid(boundary_box,grid_length):
    grid=[]
    lat_1 =  float(boundary_box[0])
    lat_2 =  float(boundary_box[1])
    long_1 = float(boundary_box[2])
    long_2 = float(boundary_box[3])
    lat_step_difference = (lat_2 - lat_1)/grid_length
    long_step_difference = (long_2 - long_1)/grid_length
    current_lat_position = lat_1
    current_long_position = long_1
    for _ in range(grid_length):
        for _ in range(grid_length):
            new_position = [current_lat_position,current_long_position]
            grid.append(new_position)
            current_long_position+= long_step_difference
        current_lat_position += lat_step_difference
    return grid

