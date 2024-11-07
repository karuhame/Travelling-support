from typing import List
from sqlalchemy import func
from sqlalchemy.orm import Session
from blog import models, schemas
from fastapi import HTTPException, UploadFile, status
from blog.hashing import Hash
from blog.repository.image import ImageHandler
from blog.repository import destination






def create_by_destinationID(destination_id: int, request:schemas.Hotel, db: Session):
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
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error deleting destination: {str(e)}")
def create_hotel_of_destination(destination: models.Destination, request:schemas.Hotel, db: Session):
    try:
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
        db.rollback()
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
        hotel.phone = request.phone
        hotel.email = request.email
        hotel.website = request.website

        db.commit()  # Chờ hoàn tất việc commit
        db.refresh(hotel)  # Chờ làm mới đối tượng mới
        return hotel
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error updating destination: {str(e)}")
        

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

# property_amenities = Column(String(255), default='Free Parking, Pool, Free breakfast')

def filter_hotel(city_id: int, db: Session, price_range = [str], amenities = [str], hotel_star = [int]):
    hotels = db.query(models.Hotel).all()
    # Chuyển đổi hotel_star thành danh sách số nguyên nếu cần
    hotel_star = [int(star) for star in hotel_star]
    # Lọc khách sạn theo các tiêu chí
    filtered_hotels = []
    
    dest = None
    if city_id:
        dests = destination.get_by_city_id(db=db, city_id=city_id)

        

    for hotel in hotels:
        # Kiểm tra điều kiện cho amenities
        if amenities:
            amenities_list = [amenity.strip().lower() for amenity in hotel.property_amenities.split(',')]
            if not all(amenity.lower() in amenities_list for amenity in amenities):
                continue  # Nếu không có tất cả amenities yêu cầu, bỏ qua khách sạn này

        # Kiểm tra điều kiện cho hotel_class
        if hotel_star and hotel.hotel_class  not in hotel_star:
            continue  # Nếu lớp khách sạn không nằm trong danh sách yêu cầu, bỏ qua
        
        # Kiểm tra điều kiện cho price_range
        if price_range:
            price_top = hotel.destination.price_top  # Giả sử bạn có thuộc tính này trong mô hình
            price_category = ""

            if price_top > 3000000:
                price_category = "high"
            elif price_top > 1000000:
                price_category = "middle"
            else:
                price_category = "low"

            if price_category not in price_range:
                continue  # Nếu không nằm trong danh sách price_range, bỏ qua khách sạn

        # Thêm khách sạn vào danh sách đã lọc
        filtered_hotels.append(hotel)

    return filtered_hotels


   
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


def delete_by_id(id: int, db: Session):
    try:
        hotel = db.query(models.Hotel).filter(models.Hotel.id == id).first()  # Chờ truy vấn
        if not hotel:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"hotel with the id {id} is not available")

        db.delete(hotel)  # Chờ xóa đối tượng
        db.commit()  # Chờ hoàn tất việc commit
        return {"detail": "hotel deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error deleting hotel: {str(e)}")
