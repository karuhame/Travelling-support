from typing import List
from sqlalchemy import func
from sqlalchemy.orm import Session
from blog import models, schemas
from fastapi import HTTPException, status
from blog.hashing import Hash


def create(db: Session, request: schemas.Tour):
    try:
        new_tour = models.Tour(
            name=request.name,
            description=request.description,
            user_id=request.user_id,
            city_id=request.city_id,
            duration=0
        )

        # Link destination_ids with the tour
        for destination_id in request.destination_ids:
            destination = db.query(models.Destination).filter(models.Destination.id == destination_id).first()
            if destination:
                new_tour.duration += destination.duration
                new_tour.destinations.append(destination)  # Add destination to tour
        
        db.add(new_tour)
        db.commit()
        db.refresh(new_tour)  # Refresh the object to get the created ID

        return new_tour
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error creating tour: {str(e.detail)}")


def get_ratings_and_reviews_number_of_tourID(id: int, db: Session):
    try:
        reviews = db.query(models.Review).filter(models.Review.tour_id == id).all()
        if reviews:
            # Calculate total ratings and number of reviews
            total_ratings = sum(review.rating for review in reviews)
            quantity_of_reviews = len(reviews)
            average_rating = total_ratings / quantity_of_reviews

            # Calculate points based on the formula
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
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error fetching ratings and reviews: {str(e.detail)}")

def get_tour_by_id(tour_id: int, db: Session):
    try:
    # Truy vấn để lấy tour theo id
        tour = db.query(models.Tour).filter(models.Tour.id == tour_id).first()
        
        if not tour:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Tour not found")
        return tour
    except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Error fetching ratings and reviews: {str(e.detail)}")



def get_all_tour(db: Session, city_id: int):
    try:
        # Query to get all tours
        if city_id:        
            tours = db.query(models.Tour).filter(models.Tour.city_id == city_id).all()
        else: 
            tours = db.query(models.Tour).all()
        return tours
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error fetching tours: {str(e.detail)}")


def update_tour(db: Session, id: int, request: schemas.Tour):
    try:
        tour = db.query(models.Tour).filter(models.Tour.id == id).first()
        if not tour:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Tour not found")

        # Update tour details
        tour.name = request.name
        tour.description = request.description
        tour.city_id = request.city_id
        tour.user_id = request.user_id
        tour.duration = 0  # Reset duration to recalculate

        # Update destinations
        tour.destinations.clear()  # Clear existing destinations
        for destination_id in request.destination_ids:
            destination = db.query(models.Destination).filter(models.Destination.id == destination_id).first()
            if destination:
                tour.duration += destination.duration
                tour.destinations.append(destination)

        db.commit()
        db.refresh(tour)  # Refresh the object to get updated details

        return tour
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error updating tour: {str(e.detail)}")


def delete_tour(db: Session, id: int):
    try:
        tour = db.query(models.Tour).filter(models.Tour.id == id).first()
        if not tour:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Tour not found")

        db.delete(tour)
        db.commit()
        return {"detail": "Tour deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error deleting tour: {str(e.detail)}")
def sorting_by_ratings_and_quantity_of_reviews(tours: List[models.Tour], db: Session):
    try:
        # Tạo danh sách để lưu trữ thông tin điểm đến cùng với điểm số và số lượng đánh giá
        tour_scores = []

        for tour in tours:
            # Sử dụng hàm get_ratings_and_reviews_of_tour để tính điểm số
            review_data = get_ratings_and_reviews_number_of_tourID(tour.id, db)

            # Sử dụng điểm số tính toán từ hàm get_ratings_and_reviews_of_tour
            point = review_data["numberOfReviews"] * (review_data["ratings"] ** 2)

            tour_scores.append({
                "tour": tour,
                "total_point": point
            })

        # Sắp xếp danh sách theo total_point từ cao xuống thấp
        tour_scores.sort(key=lambda x: x['total_point'], reverse=True)

        # Trả về danh sách các đối tượng tour đã sắp xếp
        sorted_tours = [item["tour"] for item in tour_scores]
        return sorted_tours

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error sorting tours: {str(e.detail)}")
        