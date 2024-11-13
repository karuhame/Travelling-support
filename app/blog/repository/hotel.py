from typing import List
from sqlalchemy import func
from sqlalchemy.orm import Session
from blog import models, schemas
from fastapi import HTTPException, UploadFile, status
from blog.hashing import Hash
from blog.repository.image_handler import ImageHandler
from blog.repository import destination

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException




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
                            detail=f"Error create destination: {str(e)}")
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
                            detail=f"Error updating destination: {str(e.detail)}")

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
                            detail=f"Error deleting hotel: {str(e.detail)}")


 
def filter_hotel(hotels: list[models.Destination], db: Session, price_range = [str], amenities = [str], hotel_star = [int]):
        
    # Lọc khách sạn theo các tiêu chí
    filtered_hotels = []

    for dest in hotels:
        hotel = dest.hotel
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
            price_top = dest.price_top  # Giả sử bạn có thuộc tính này trong mô hình
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
        filtered_hotels.append(dest)

    return filtered_hotels


   
def get_hotel_info(id: int, db: Session):
    
    dest = db.query(models.Destination).filter(models.Destination.hotel_id == id).first()
    if not dest:
        return {"error": "Destination not found"}
    result = schemas.ShowDestination.from_orm(dest).dict()
    rating_info = destination.get_ratings_and_reviews_number_of_destinationID(dest.id, db)
    result.update({
        "rating": rating_info["ratings"],
        "numOfReviews": rating_info["numberOfReviews"]
    })
    return result



def get_all_hotel(db: Session, city_id: int = None):
    dest_hotels = []
    
    try:
        if city_id is not None:
            # Lấy danh sách khách sạn theo city_id
            dest_hotels = db.query(models.Destination).join(models.Address).filter(
                models.Destination.hotel_id.isnot(None),
                models.Address.city_id == city_id
            ).all()

        else:
            # Lấy tất cả khách sạn không có giá trị Null
            dest_hotels = db.query(models.Destination).filter(
                models.Destination.hotel_id.isnot(None)
            ).all()

        return dest_hotels
        
        results = []
        for hotel in dest_hotels:
            # Lấy thông tin điểm đến liên quan
            hotel_info = get_hotel_info(db=db, id=hotel.id)
            results.append(hotel_info)

        return results

    except SQLAlchemyError as e:
        # Ghi log lỗi hoặc xử lý lỗi tùy ý
        print(f"Database error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    except Exception as e:
        # Bắt các lỗi khác
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# property_amenities = Column(String(255), default='Free Parking, Pool, Free breakfast')
