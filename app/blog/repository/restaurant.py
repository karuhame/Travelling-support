

from typing import List
from sqlalchemy import func
from sqlalchemy.orm import Session
from blog import models, schemas
from fastapi import HTTPException, UploadFile, status
from blog.hashing import Hash
from blog.repository.image import ImageHandler

from blog.repository import destination

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException





def create_by_destinationID(destination_id: int, request:schemas.Restaurant, db: Session):
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
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error create destination: {str(e)}")

def create_hotel_of_destination(destination: models.Destination, request:schemas.Restaurant, db: Session):
    try:
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
        db.rollback()
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
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error updating destination: {str(e.detail)}")

def delete_by_id(id: int, db: Session):
    try:
        restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == id).first()  # Chờ truy vấn
        if not restaurant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"restaurant with the id {id} is not available")

        db.delete(restaurant)  # Chờ xóa đối tượng
        db.commit()  # Chờ hoàn tất việc commit
        return {"detail": "restaurant deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error deleting restaurant: {str(e.detail)}")

    
def filter_restaurant(restaurants: list[models.Destination], db: Session,  cuisines = [str], special_diets = [str]):
    
    # Lọc khách sạn theo các tiêu chí
    filtered_restaurants = []

    for dest in restaurants:
        restaurant = dest.restaurant
        # Kiểm tra điều kiện cho amenities
        if cuisines:
            cuisines_list = [cuisin.strip().lower() for cuisin in restaurant.cuisine.split(',')]
            if not all(cuisin.lower() in cuisines_list for cuisin in cuisines):
                continue 
        if special_diets:
            diets_list = [diet.strip().lower() for diet in restaurant.special_diet.split(',')]
            if not all(diet.lower() in diets_list for diet in special_diets):
                continue 
        
        filtered_restaurants.append(dest)
    return filtered_restaurants




   
def get_restaurant_info(id: int, db: Session):
    print(id)
    dest = db.query(models.Destination).filter(models.Destination.restaurant_id == id).first()
    if not dest:
        return {"error": "Destination not found"}
    result = schemas.ShowDestination.from_orm(dest).dict()
    rating_info = destination.get_ratings_and_reviews_number_of_destinationID(dest.id, db)
    result.update({
        "rating": rating_info["ratings"],
        "numOfReviews": rating_info["numberOfReviews"]
    })
    return result



def get_all_restaurant(db: Session, city_id: int = None):
    dest_restaurants = []
    try:
        if city_id is not None:
            # Lấy danh sách khách sạn theo city_id
            dest_restaurants = db.query(models.Destination).join(models.Address).filter(
                models.Destination.restaurant_id.isnot(None),
                models.Address.city_id == city_id
            ).all()

        else:
            # Lấy tất cả khách sạn không có giá trị Null
            dest_restaurants = db.query(models.Destination).filter(
                models.Destination.restaurant_id.isnot(None)
            ).all()

        return dest_restaurants
        
       

    except SQLAlchemyError as e:
        # Ghi log lỗi hoặc xử lý lỗi tùy ý
        print(f"Database error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    except Exception as e:
        # Bắt các lỗi khác
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# property_amenities = Column(String(255), default='Free Parking, Pool, Free breakfast')
