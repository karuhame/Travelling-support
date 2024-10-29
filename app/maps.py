import requests
import json

AZURE_MAPS_KEY = '7HO4fnAGwLJuEC0BsVDFixUnJS4IRNsNT6IlGyMsJqeNZws9D7HRJQQJ99AJACYeBjFZvPJUAAAgAZMP1h2w'

def geocode_address(address):
    url = f"https://atlas.microsoft.com/search/address/json?subscription-key={AZURE_MAPS_KEY}&api-version=1.0&query={address}&limit=1"
    response = requests.get(url)
    return response.json()

def find_nearby_hotels(latitude, longitude, radius=3000, limit=10, countrySet = "Viet Nam"):
    url = f"https://atlas.microsoft.com/search/nearby/json?subscription-key={AZURE_MAPS_KEY}&api-version=1.0&countrySet={countrySet}&lat={latitude}&lon={longitude}&radius={radius}&limit={limit}&poiCategory=bar"
    response = requests.get(url)
    return response.json()

# Địa chỉ cần tìm
address = "3 Núi thành, Đà Nẵng"

# Bước 1: Geocode địa chỉ
geocode_result = geocode_address(address)
if geocode_result and 'results' in geocode_result and geocode_result['results']:
    location = geocode_result['results'][0]['position']
    latitude = location['lat']
    longitude = location['lon']
    
    # Bước 2: Tìm kiếm các khách sạn gần đó
    hotels = find_nearby_hotels(latitude, longitude)

    # Lấy thông tin mô tả và hình ảnh từ kết quả
    if hotels and 'results' in hotels:
        for hotel in hotels['results']:
            poi = hotel.get('poi', {})
            name = poi.get('name', 'Không có tên')
            description = poi.get('description', 'Không có mô tả')
            images = poi.get('images', [])
            
            print(f"Tên: {name}")
            print(f"Mô tả: {description}")

            # Lấy URL hình ảnh nếu có
            if images:
                for image in images:
                    print(f"Hình ảnh URL: {image['url']}")
            else:
                print("Không có hình ảnh.")
            print("-----")
    else:
        print("Không tìm thấy khách sạn.")
else:
    print("Không tìm thấy địa chỉ.")