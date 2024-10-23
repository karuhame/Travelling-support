from typing import List
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
        destination = db.query(models.Destination).filter(models.Destination.id == id).first()  # Chờ truy vấn
        
        if not destination:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"destination with the id {id} is not available")
        return destination
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error retrieving destination: {str(e)}")
def get_by_city_id(city_id: int, db: Session):
    try:
        destinations = db.query(models.Destination).join(models.Address).filter(models.Address.city_id == city_id).all()        
        if not destinations:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"destinations with the city_id {city_id} is not available")
        return destinations
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