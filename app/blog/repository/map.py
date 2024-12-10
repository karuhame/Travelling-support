import os
from dotenv import load_dotenv
import requests

# Tải các biến môi trường từ tệp .env
load_dotenv()
AZURE_CONNECTION_STRING = os.getenv('AZURE_CONNECTION_STRING')

GOONG_API_URL = os.getenv('GOONG_API_URL')
GOONG_MAP_URL = os.getenv('GOONG_MAP_URL')
GOONG_API_KEY = os.getenv('GOONG_API_KEY')
GOONG_MAP_KEY = os.getenv('GOONG_MAP_KEY')


def get_coordinate(location: str):
    """Lấy tọa độ (latitude, longitude) từ tên địa điểm."""
    api_link = f"{GOONG_API_URL}/Geocode?address={location}&api_key={GOONG_API_KEY}"
    response = requests.get(api_link)
    
    if response.status_code == 200:
        data = response.json()
        if data['results'] and len(data['results']) > 0:
            location_data = data['results'][0]['geometry']['location']
            return (location_data['lat'], location_data['lng'])
        else:
            raise ValueError("Không tìm thấy tọa độ cho địa điểm này.")
    else:
        raise Exception(f"Error fetching coordinates: {response.status_code} - {response.text}")

def get_distance_of_2_locations(latlong1, latlong2):
    """Lấy khoảng cách giữa hai tọa độ (latitude, longitude) sử dụng Goong API."""
    api_link = f"{GOONG_API_URL}/DistanceMatrix?origins={latlong1[0]},{latlong1[1]}&destinations={latlong2[0]},{latlong2[1]}&api_key={GOONG_API_KEY}"
    response = requests.get(api_link)
    
    if response.status_code == 200:
        data = response.json()
        if data['rows'] and len(data['rows']) > 0 and data['rows'][0]['elements'] and len(data['rows'][0]['elements']) > 0:
            distance = data['rows'][0]['elements'][0]['distance']['value']  # Giá trị khoảng cách tính bằng mét
            return distance / 1000  # Chuyển đổi sang km
        else:
            raise ValueError("Không tìm thấy khoảng cách giữa các địa điểm.")
    else:
        raise Exception(f"Error fetching distance: {response.status_code} - {response.text}")
def get_distances_between_all_locations(locations):
    """Lấy ra khoảng cách giữa tất cả các đường với nhau dưới dạng ma trận đối xứng."""
    n = len(locations)
    distances = [[0] * n for _ in range(n)]  # Khởi tạo ma trận n x n

    for i in range(n):
        for j in range(i + 1, n):  # Chỉ tính khoảng cách một lần cho mỗi cặp
            distance = get_distance_of_2_locations(locations[i], locations[j])
            distances[i][j] = distance
            distances[j][i] = distance  # Ma trận đối xứng

    return distances


# Ví dụ sử dụng
if __name__ == "__main__":
    location_a = "Hà Nội"
    location_b = "TP Hồ Chí Minh"
    location_c = "Đà Nẵng"

    coords_a = get_coordinate(location_a)
    coords_b = get_coordinate(location_b)
    coords_c = get_coordinate(location_c)

    print(f"Tọa độ A: {coords_a}")
    print(f"Tọa độ B: {coords_b}")
    print(f"Tọa độ C: {coords_c}")

    locations = [coords_a, coords_b, coords_c]
    distance_matrix = get_distances_between_all_locations(locations)

    print("Ma trận khoảng cách:")
    # for i, row in enumerate(distance_matrix):
    #     for j, distance in enumerate(row):
    #         if i == j:
    #             print(f"Khoảng cách từ {['A', 'B', 'C'][i]} đến {['A', 'B', 'C'][j]}: 0 km")
    #         else:
    #             print(f"Khoảng cách từ {['A', 'B', 'C'][i]} đến {['A', 'B', 'C'][j]}: {distance:.2f} km")
    
    for i in distance_matrix:
        print(i)