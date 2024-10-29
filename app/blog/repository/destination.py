from typing import List
from sqlalchemy import func
from sqlalchemy.orm import Session
from blog import models, schemas
from fastapi import HTTPException, status
from blog.hashing import Hash

def create(request: schemas.Destination_Address, db: Session):
    try:
        # Tạo địa chỉ mới
        new_address = models.Address(
            district=request.district,
            street=request.street,
            ward=request.ward,
            city_id=request.city_id  # Sử dụng city_id làm khóa ngoại
        )
        
        # Thêm địa chỉ vào cơ sở dữ liệu
        db.add(new_address)
        db.commit()  # Commit để lưu địa chỉ
        db.refresh(new_address)  # Làm mới địa chỉ để lấy ID

        # Tạo điểm đến mới
        new_destination = models.Destination(
            name=request.name,
            price_bottom=request.price_bottom,
            price_top=request.price_top,
            date_create=request.date_create,
            age=request.age,
            opentime=request.opentime,
            duration=request.duration,
            address=new_address  # Liên kết đến địa chỉ vừa tạo
        )
        
        # Thêm điểm đến vào cơ sở dữ liệu
        db.add(new_destination)
        db.commit()  # Commit để lưu điểm đến
        db.refresh(new_destination)  # Làm mới đối tượng mới

        return new_destination
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error creating destination: {str(e)}")
def get_by_id(id: int, db: Session):
    try:
        destination = db.query(models.Destination).filter(models.Destination.id == id).first()
        if not destination:
            return {"detail": "Không tìm thấy điểm đến."}

        # Chuyển đổi hình ảnh thành ShowImage
        images = [schemas.ShowImage.from_orm(img) for img in destination.images] if destination.images else None

        # Tạo từ điển cho dữ liệu điểm đến
        destination_data = {
            "id": destination.id,
            "name": destination.name,
            "address": destination.address,
            "price_bottom": destination.price_bottom,
            "price_top": destination.price_top,
            "date_create": destination.date_create,
            "age": destination.age,
            "opentime": destination.opentime,
            "duration": destination.duration,
            "images": images
        }

        # Trả về ShowDestination đã được xác thực
        return schemas.ShowDestination(**destination_data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error retrieving destination: {str(e)}")

def get_by_city_id(city_id: int, db: Session):
    try:
        destinations = db.query(models.Destination).join(models.Address).filter(models.Address.city_id == city_id).all()
        
        if not destinations:
            return {"detail": "No destinations found for the specified city ID."}

        results = []
        
        for dest in destinations:
            # Chuyển đổi danh sách các đối tượng Image thành ImageSchema, xử lý trường hợp không có ảnh
            dest = get_by_id(dest.id, db)
            
            results.append(dest)

        return results
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error retrieving destinations: {str(e)}")

def get_all(db: Session):
    try:
        destinations = db.query(models.Destination).all()  # Chờ truy vấn
        return destinations
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error retrieving destinations: {str(e)}")
def sorting_by_ratings_and_quantity_of_reviews(destinations: List[models.Destination], db: Session):
    try:
        # Tạo danh sách để lưu trữ thông tin điểm đến cùng với điểm số và số lượng đánh giá
        destination_scores = []

        for destination in destinations:
            # Sử dụng hàm get_ratings_and_reviews_of_destination để tính điểm số
            review_data = get_ratings_and_reviews_number_of_destinationID(destination.id, db)

            # Sử dụng điểm số tính toán từ hàm get_ratings_and_reviews_of_destination
            point = review_data["numberOfReviews"] * (review_data["ratings"] ** 2)

            destination_scores.append({
                "destination": destination,
                "total_point": point
            })

        # Sắp xếp danh sách theo total_point từ cao xuống thấp
        destination_scores.sort(key=lambda x: x['total_point'], reverse=True)

        # Trả về danh sách các đối tượng Destination đã sắp xếp
        sorted_destinations = [item["destination"] for item in destination_scores]
        return sorted_destinations

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error sorting destinations: {str(e)}")
        
def update_by_id(id: int, request: schemas.Destination, db: Session):
    try:
        destination = db.query(models.Destination).filter(models.Destination.id == id).first()  # Chờ truy vấn
        if not destination:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"destination with the id {id} is not available")

        destination.name = request.name
        destination.email = request.email
        db.commit()  # Chờ hoàn tất việc commit
        db.refresh(destination)  # Chờ làm mới đối tượng mới
        return destination
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error updating destination: {str(e)}")

def delete_by_id(id: int, db: Session):
    try:
        destination = db.query(models.Destination).filter(models.Destination.id == id).first()  # Chờ truy vấn
        if not destination:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"destination with the id {id} is not available")

        db.delete(destination)  # Chờ xóa đối tượng
        db.commit()  # Chờ hoàn tất việc commit
        return {"detail": "destination deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error deleting destination: {str(e)}")

def create_restaurant_info_by_destinationID(destination_id: int, request:schemas.Restaurant, db: Session):
    try:
        destination = db.query(models.Destination).filter(models.Destination.id == destination_id).first()  # Chờ truy vấn
        new_restaurant = models.Restaurant(
            cuisine = request.cuisine,
            special_diet = request.special_diet
        )
        db.add(new_restaurant)
        db.commit()  # Chờ hoàn tất việc commit
        db.refresh(new_restaurant)  # Chờ làm mới đối tượng mới
        
        destination.restaurant_id = new_restaurant.id
        db.commit()
        db.refresh(destination)
        return new_restaurant
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error deleting destination: {str(e)}")

def update_restaurant_info_by_id(id:int, request: schemas.Restaurant, db: Session):
    try:
        restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == id).first()  # Chờ truy vấn
        if not restaurant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"restaurant with the id {id} is not available")

        restaurant.cuisine = request.cuisine
        restaurant.special_diet = request.special_diet
        db.commit()  # Chờ hoàn tất việc commit
        db.refresh(restaurant)  # Chờ làm mới đối tượng mới
        return restaurant
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error updating destination: {str(e)}")
        


def create_hotel_info_by_destinationID(destination_id: int, request:schemas.Hotel, db: Session):
    try:
        destination = db.query(models.Destination).filter(models.Destination.id == destination_id).first()  # Chờ truy vấn
        new_hotel = models.Hotel(
            property_amenities = request.property_amenities,
            room_features = request.room_features,
            room_types = request.room_types,
            hotel_class = request.hotel_class,
            hotel_styles = request.hotel_styles,
            Languages = request.Languages
        )
        db.add(new_hotel)
        db.commit()  # Chờ hoàn tất việc commit
        db.refresh(new_hotel)  # Chờ làm mới đối tượng mới
        
        destination.hotel_id = new_hotel.id
        db.commit()
        db.refresh(destination)
        return new_hotel
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error deleting destination: {str(e)}")

def update_hotel_info_by_id(id:int, request: schemas.Hotel, db: Session):
    try:
        hotel = db.query(models.Hotel).filter(models.Hotel.id == id).first()  # Chờ truy vấn
        if not hotel:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"hotel with the id {id} is not available")

        hotel.property_amenities = request.property_amenities,
        hotel.room_features = request.room_features,
        hotel.room_types = request.room_types,
        hotel.hotel_class = request.hotel_class,
        hotel.hotel_styles = request.hotel_styles,
        hotel.Languages = request.Languages

        db.commit()  # Chờ hoàn tất việc commit
        db.refresh(hotel)  # Chờ làm mới đối tượng mới
        return hotel
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error updating destination: {str(e)}")
        

def get_ratings_and_reviews_number_of_destinationID(destination_id: int, db: Session):
    reviews = db.query(models.Review).filter(models.Review.destination_id == destination_id).all()
    if reviews:
        # Tính tổng số điểm và số lượng đánh giá
        total_ratings = sum(review.rating for review in reviews)
        quantity_of_reviews = len(reviews)
        average_rating = total_ratings / quantity_of_reviews

        # Tính điểm theo công thức
        point = (average_rating * 10)

        return {
            "ratings": average_rating,
            "numberOfReviews": quantity_of_reviews
        }
    else:
        return {
            "ratings": 0,
            "numberOfReviews": 0
        }
def get_hotel_info(hotel_id: int, db: Session):
    # Truy vấn để lấy thông tin khách sạn
    hotel = db.query(models.Hotel).filter(models.Hotel.id == hotel_id).first()
    
    if hotel is None:
        return {"error": "Hotel not found"}

    # Lấy thông tin điểm đến liên quan
    destination = db.query(models.Destination).filter(models.Destination.hotel_id == hotel_id).first()
    
    # Lấy thông tin địa chỉ
    address = db.query(models.Address).filter(models.Address.id == destination.address_id).first() if destination else None

    # Lấy thông tin đánh giá liên quan
    reviews = db.query(models.Review).filter(models.Review.destination_id == destination.id).all()

    # Tính toán số lượng đánh giá và tổng điểm
    num_of_reviews = len(reviews)
    total_rating = sum(review.rating for review in reviews) if num_of_reviews > 0 else 0
    average_rating = total_rating // num_of_reviews if num_of_reviews > 0 else 0

    # Gom các trường trong bảng Address thành một chuỗi
    address_string = f"{address.ward}, {address.district}, {address.street}" if address else "No address available"

    # Lấy tất cả URL hình ảnh liên quan đến khách sạn
    images = db.query(models.Image).filter(models.Image.destination_id == destination.id).all() if destination else []
    img_urls = [image.url for image in images]

    # Tạo từ điển với thông tin khách sạn
    hotel_info = {
        "id": hotel.id,
        "name": destination.name ,
        "address": address_string,
        "price": destination.price_bottom if destination else 0,
        "phone": hotel.phone,
        "email": hotel.email,
        "website": hotel.website,
        "features": hotel.room_features.split(",") if hotel.room_features else [],
        "amenities": hotel.property_amenities.split(",") if hotel.property_amenities else [],
        "description": destination.description, 
        "rating": average_rating,
        "numOfReviews": num_of_reviews,
        "imgURL": img_urls
    }

    return hotel_info

def get_all_hotel(db: Session):
    # Truy vấn để lấy tất cả khách sạn
    hotels = db.query(models.Hotel).all()
    
    hotel_list = []

    for hotel in hotels:
        # Lấy thông tin điểm đến liên quan
        destination = db.query(models.Destination).filter(models.Destination.hotel_id == hotel.id).first()
        
        # Lấy thông tin đánh giá liên quan
        reviews = db.query(models.Review).filter(models.Review.destination_id == destination.id).all()

        # Tính toán số lượng đánh giá và tổng điểm
        num_of_reviews = len(reviews)
        total_rating = sum(review.rating for review in reviews) if num_of_reviews > 0 else 0
        average_rating = total_rating // num_of_reviews if num_of_reviews > 0 else 0
        
        # Lấy thông tin địa chỉ từ điểm đến
        address_string = (
            f"{destination.address.district}, {destination.address.street}, {destination.address.ward}"
            if destination and destination.address else "No address available"
        )

        # Lấy tất cả URL hình ảnh liên quan đến khách sạn
        images = db.query(models.Image).filter(models.Image.destination_id == destination.id).all() if destination else []
        img_urls = [image.url for image in images]

        # Tạo từ điển với thông tin khách sạn
        hotel_info = {
            "id": hotel.id,
            "name": destination.name if destination else "Unnamed Destination",
            "address": address_string,
            "rating": average_rating,
            "numOfReviews": num_of_reviews,
            "features": hotel.room_features.split(",") if hotel.room_features else [],
            "imgURL": img_urls[0] if img_urls else None  # Lấy URL đầu tiên nếu có
        }

        hotel_list.append(hotel_info)

    return hotel_list

def get_popular_destinations_by_city_ID(city_id: int, db: Session):
    # Truy vấn để lấy danh sách các điểm đến phổ biến
    popular_destinations = (
        db.query(models.Destination)
        .outerjoin(models.Review, models.Destination.id == models.Review.destination_id)  # Kết hợp với bảng Review
        .filter(models.Destination.address.has(city_id=city_id))  # Lọc theo city_id
        .group_by(models.Destination.id)  # Nhóm theo id của Destination
        .having(func.avg(models.Review.rating) >= 4.5)  # Điều kiện xếp hạng
        .having(func.count(models.Review.id) >= 1000)  # Điều kiện số lượng đánh giá
        .all()
    )

    # Tạo danh sách chứa thông tin các điểm đến
    destination_list = []
    for destination in popular_destinations:
        # Lấy thông tin địa chỉ
        address = destination.address
        location = f"{address.street}, {address.district}, {address.city.name}, Vietnam" if address else "Unknown Location"

        # Lấy tất cả hình ảnh liên quan đến điểm đến
        images = db.query(models.Image).filter(models.Image.destination_id == destination.id).limit(5).all()  # Lấy tối đa 5 hình ảnh
        image_urls = [image.url for image in images]

        # Tính tổng số lượng đánh giá
        num_of_reviews = len(destination.reviews)

        # Tạo từ điển với thông tin điểm đến
        destination_info = {
            "id": destination.id,
            "name": destination.name,
            "category": "popular",
            "image": image_urls,
            "location": location,
            "review": num_of_reviews,
            "price": destination.price_bottom,  

            "description": destination.description,  
            "rate": func.avg(models.Review.rating)  
        }

        destination_list.append(destination_info)

    return destination_list