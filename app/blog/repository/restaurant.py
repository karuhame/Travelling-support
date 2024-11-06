

from typing import List
from sqlalchemy import func
from sqlalchemy.orm import Session
from blog import models, schemas
from fastapi import HTTPException, UploadFile, status
from blog.hashing import Hash
from blog.repository.image import ImageHandler



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
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error deleting destination: {str(e)}")

def create_restaurant_of_destination(destination: models.Destination, request:schemas.Restaurant, db: Session):
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
                            detail=f"Error updating destination: {str(e)}")
        
