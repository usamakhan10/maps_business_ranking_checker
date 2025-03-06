from get_grid import get_bounding_box,get_grid
from math import radians, cos, sin, sqrt, atan2
import os
from dotenv import load_dotenv
import urllib.parse
from evomi import make_request
import json

# Search parameters - these could be set from command line arguments
QUERY = "chinese restaurant virginia beach"  # Default search query
RADIUS_KM = 5
GRID_SIZE = 3
load_dotenv(".env")
GEO_CODING_API_KEY = os.getenv('geocoding_api')



def haversine(lat1, lng1, lat2, lng2):
    """Calculate the great-circle distance between two points on Earth."""
    R = 6371  # Earth's radius in km
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c  # Distance in km

def create_grid(center_lat, center_lng, radius_km, grid_size):
    grid_points = []
    step_size = (1.5 * radius_km) / (grid_size)

    # Prevent division by zero at poles
    lng_factor = cos(radians(center_lat)) if abs(center_lat) < 90 else 1e-6
    
    lat_step = step_size / 111  # Approx. km per degree latitude
    lng_step = step_size / (111 * lng_factor)  # Approx. km per degree longitude

    lat_min = center_lat - radius_km / 111
    lng_min = center_lng - radius_km / (111 * lng_factor)

    for i in range(grid_size):
        lat = lat_min + i * lat_step
        for j in range(grid_size):
            lng = lng_min + j * lng_step
            if haversine(center_lat, center_lng, lat, lng) <= radius_km +1:
                grid_points.append((lat, lng))
    return grid_points






def prepare(input):
    # Remove the first 5 characters and newlines
    prepared_for_parsing = input[4:].replace('\n', '')
    json_data = json.loads(prepared_for_parsing)
    results = []
    del json_data[0][1][0]
    for item in json_data[0][1]:
        try:
            results.append(item[14])
        except Exception as e:
            print(f"Error: {e}")
    return results

def prepare_lookup(data):
    # This function returns a lookup function for retrieving data using a list of indexes
    def lookup(*indexes):
        try:
            result = data
            for index in indexes:
                result = result[index]
            return result
        except (IndexError, TypeError):
            return None
    return lookup

def build_results(prepared_data):
    results = []
    for place in prepared_data:
        lookup = prepare_lookup(place)

        # Use the indexes below to extract certain pieces of data
        # or as a starting point of exploring the data response.
        result = {
            'address': {
                'street_address': lookup(183, 1, 2),
                'city': lookup(183, 1, 3),
                'zip': lookup(183, 1, 4),
                'state': lookup(183, 1, 5),
                'country_code': lookup(183, 1, 6),
            },
            'name': lookup(11),
            'tags': lookup(13),
            'notes': lookup(25, 15, 0, 2),
            'placeId': lookup(78),
            'phone': lookup(178, 0, 0),
            'coordinates': {
                'long': lookup(208, 0, 2),
                'lat': lookup(208, 0, 3)
            }
        }
        results.append(result)
    
    return results



def main():
    business_name = input("Enter your business name: ").strip()
    query = input("\nEnter your search query or keyword: ")
    coordinates = input("\nEnter your coordinates in lat,long format. Press enter if you want to search by place name: ")
    if coordinates=="":
        place = input("\nEnter the place name you want to search for: ")
        if place == "":
            print("You must enter a place name to proceed")
            return
        bounding_box = get_bounding_box(place,GEO_CODING_API_KEY)
        grid = get_grid(bounding_box,GRID_SIZE)
    else:
        lat = coordinates.split(",")[0].strip()
        long = coordinates.split(",")[1].strip()
        grid = create_grid(float(lat),float(long),RADIUS_KM,GRID_SIZE)
    

    final_results=[]
    unique_results = 0
    
    # we're going to look at the first 20 results for every coordinate, so start is 0 and count is 20
    start = 0 
    count = 20
    encoded_keyword = urllib.parse.quote(query)
    zoom_levels = [15000,45000,80000] # Zoom level
    
    for  lat_long in grid:
        lat = lat_long[0]
        long = lat_long[1]
        for zoom in zoom_levels:
            url = f"https://www.google.com/search?tbm=map&authuser=0&hl=en&pb=!4m12!1m3!1d{zoom}!2d{long}!3d{lat}!2m3!1f0!2f0!3f0!3m2!1i1517!2i674!4f13.1!7i{count}!8i{start}!10b1!12m20!1m2!18b1!30b1!2m3!5m1!6e2!20e3!10b1!12b1!13b1!16b1!17m1!3e1!20m3!5e2!6b1!14b1!46m1!1b0!94b1!19m4!2m3!1i360!2i120!4i8!20m57!2m2!1i203!2i100!3m2!2i4!5b1!6m6!1m2!1i86!2i86!1m2!1i408!2i240!7m42!1m3!1e1!2b0!3e3!1m3!1e2!2b1!3e2!1m3!1e2!2b0!3e3!1m3!1e8!2b0!3e3!1m3!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e9!2b1!3e2!1m3!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e10!2b0!3e4!2b1!4b1!9b0!22m5!1swIHQZpHzL4mC7M8P9JSx6Ao%3A79!2s1i%3A0%2Ct%3A150715%2Cp%3AwIHQZpHzL4mC7M8P9JSx6Ao%3A79!7e81!12e3!17swIHQZpHzL4mC7M8P9JSx6Ao%3A84!24m104!1m31!13m9!2b1!3b1!4b1!6i1!8b1!9b1!14b1!20b1!25b1!18m20!3b1!4b1!5b1!6b1!9b1!12b1!13b1!14b1!17b1!20b1!21b1!22b1!25b1!27m1!1b0!28b0!31b0!32b0!33m1!1b1!10m1!8e3!11m1!3e1!14m1!3b0!17b1!20m2!1e3!1e6!24b1!25b1!26b1!29b1!30m1!2b1!36b1!39m3!2m2!2i1!3i1!43b1!52b1!54m1!1b1!55b1!56m1!1b1!65m5!3m4!1m3!1m2!1i224!2i298!71b1!72m19!1m5!1b1!2b1!3b1!5b1!7b1!4b1!8m10!1m6!4m1!1e1!4m1!1e3!4m1!1e4!3sother_user_reviews!6m1!1e1!9b1!89b1!98m3!1b1!2b1!3b1!103b1!113b1!114m3!1b1!2m1!1b1!117b1!122m1!1b1!125b0!126b1!127b1!26m4!2m3!1i80!2i92!4i8!30m28!1m6!1m2!1i0!2i0!2m2!1i530!2i674!1m6!1m2!1i1467!2i0!2m2!1i1517!2i674!1m6!1m2!1i0!2i0!2m2!1i1517!2i20!1m6!1m2!1i0!2i654!2m2!1i1517!2i674!34m18!2b1!3b1!4b1!6b1!8m6!1b1!3b1!4b1!5b1!6b1!7b1!9b1!12b1!14b1!20b1!23b1!25b1!26b1!37m1!1e81!42b1!47m0!49m9!3b1!6m2!1b1!2b1!7m2!1e3!2b1!8b1!9b1!50m4!2e2!3m2!1b1!3b1!67m3!7b1!10b1!14b1!69i704&q={encoded_keyword}&nfpr=1&tch=1&ech=1&psi=wIHQZpHzL4mC7M8P9JSx6Ao.1724940746483.1"
            response = make_request(url)
            raw_input = response.text.replace('/*""*/',"")
            try:
                raw_input = json.loads(raw_input)["d"]
            except Exception as e:
                print(f'unable to load raw input: {e}')

            prepared_data = prepare(raw_input)
            list_results = build_results(prepared_data)
            for ranking, result in enumerate(list_results,start=1):
                is_new_result = True
                for final_result in final_results:
                    if result['name'] == final_result['name']:
                        final_result['score'] += ranking
                        final_result['occurence'] += 1
                        is_new_result = False
                        break
                if is_new_result:
                    unique_results += 1
                    final_results.append(
                        {'name': result['name'], 'score': ranking, 'occurence': 1}
                    )
                
    
    filtered_results = []  # New list to store valid results
    target_business_found = False
    print("\n\n\n===== FILTERING RESULTS =====")
    for result in final_results[:]:  
        result['score'] = round(result['score'] / result['occurence'], 2)  

        # Normalize names for comparison
        result_name_clean = result['name'].replace(" ", "").lower()
        business_name_clean = business_name.replace(" ", "").lower()
        if result['occurence'] < 5 and result_name_clean != business_name_clean:
            print(f"Discarding {result['name']} due to low occurrence")
        else:
            if result_name_clean == business_name_clean:
                result['name'] += " [target business]"
                target_business_found = True
            filtered_results.append(result)  # Add to new list

    # Update final_results after filtering
    final_results[:] = filtered_results

    target_business_id = -1
    for idx, result in enumerate(final_results):
        if "[target business]" in result['name']:
            target_business_id = idx
    
    
    final_results.sort(key=lambda x: x['score'])
    print("\n\n\n===== RANKING SUMMARY =====")
    print(f"#average_ranking --- name_of_business --- number_of_occurences")
    for result in final_results:
        print(f"#{round(result['score']):2d} --- {result['name']} --- {result['occurence']} occurences")
        

    print(f"\n\n\n===== RANKING SUMMARY FOR {business_name} =====")
    
    if not target_business_found:
        print(f"Target business {business_name} not found in the results")
    else :
        print(f'Found target business "{business_name}" in the results')
        print(f"Target business was found at {final_results[target_business_id]['occurence']} out of {len(grid)*len(zoom_levels)} searches")

    avg_rank = sum(result['score'] for result in final_results) / len(final_results)
    
    print(f"Best ranking: #{final_results[0]['score']} {final_results[0]['name']}")
    print(f"Worst ranking: #{final_results[-1]['score']} {final_results[-1]['name']}")
    print(f"Average ranking: #{avg_rank:.1f}")

    
    print("\n\n\n===== ALL BUSINESSES FOUND IN SEARCH RESULTS =====")
    print(f"Found {unique_results} unique results")
    print(f"Discarded {unique_results - len(final_results)} results")
            
    
if __name__ == "__main__":
    results = main()
    