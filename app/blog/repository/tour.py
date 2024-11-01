from typing import List
from sqlalchemy import func
from sqlalchemy.orm import Session
from blog import models, schemas
from fastapi import HTTPException, status
from blog.hashing import Hash

def create(db: Session,
           request: schemas.Tour,
           ):
    try:
        new_tour = models.Tour(
            name=request.name,
            description=request.description,
            user_id=request.user_id,
            city_id = request.city_id,
            duration = 0
        )

        # Liên kết các destination_id với tour
        for destination_id in request.destination_ids:
            destination = db.query(models.Destination).filter(models.Destination.id == destination_id).first()
            if destination:
                new_tour.duration += destination.duration
                new_tour.destinations.append(destination)  # Thêm destination vào tour
        
        db.add(new_tour)
        db.commit()
        db.refresh(new_tour)  # Làm mới đối tượng để lấy ID vừa tạo

        return new_tour
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error creating destination: {str(e)}")

def get_tour_by_id(tour_id: int, db: Session):
    # Truy vấn để lấy tour theo id
    tour = db.query(models.Tour).filter(models.Tour.id == tour_id).first()
    
    if not tour:
        return {"error": "Tour not found"}

    # Tạo từ điển với thông tin tour
    tour_info = {
        "id": tour.id,
        "name": tour.name,
        "description": tour.description,
        "user_id": tour.user_id,
        "destinations": [destination.id for destination in tour.destinations],  # Lấy danh sách ID của các destination
        "images": [destination.images[0].url if destination.images else None for destination in tour.destinations],

    }

    return tour_info



def get_ratings_and_reviews_number_of_tourID(tour_id: int, db: Session):
    reviews = db.query(models.Review).filter(models.Review.tour_id == tour_id).all()
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
        

def get_all_tour(db: Session):
    # Truy vấn để lấy tất cả các tour
    tours = db.query(models.Tour).all()

    tour_list = []
    for tour in tours:
        tour_info = {
            "id": tour.id,
            "name": tour.name,
            "description": tour.description,
            "user_id": tour.user_id,
            "destinations": [destination.id for destination in tour.destinations],  # Lấy danh sách ID của các destination
            "images": [destination.images[0].url if destination.images else None for destination in tour.destinations],
        }
        tour_list.append(tour_info)

    return tour_list
