from typing import List
from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from .. import database, schemas, models
from sqlalchemy.orm import Session
from ..repository import tour, image_handler
from fastapi import APIRouter, Depends, status

router = APIRouter(
    prefix="/tour",
    tags=['Tour']
)

get_db = database.get_db

@router.post("/")
def create_tour(
    tour_data: schemas.Tour,
    db: Session = Depends(get_db)):
        
    return tour.create(request=tour_data, db=db)


@router.put("/{id}")
def update_tour(
    id: int, 
    tour_data: schemas.Tour,
    db: Session = Depends(get_db)):
        
    return tour.update_tour(id=id, request=tour_data, db=db)


@router.delete("/{id}")
def delete_tour(
    id: int, 
    db: Session = Depends(get_db)):

    return tour.delete_tour(id=id, db=db)

@router.get("/{id}")
def get_tour_by_id_endpoint(id: int, db: Session = Depends(get_db)):
    tour_info =  schemas.ShowTour.from_orm(tour.get_tour_by_id(tour_id=id, db=db)).dict()
    rating_info = tour.get_ratings_and_reviews_number_of_tourID(tour_info["id"], db)
    tour_info.update({
        "rating": rating_info["ratings"],
        "numOfReviews": rating_info["numberOfReviews"]
    })
    return tour_info

@router.get("/",
    description=(
        "### Get tour\n\n"
        "This endpoint allows you to retrieve tour based on the following criteria:\n\n"
        "- **Fill `user_id`**: Get all tour of 1 user;\n"
        "- **Fill `city_id`**: Get all tour in 1 city;\n"
        "- **Fill both `user_id` and `city_id`**: Get all tour of 1 user in 1 city;\n"
))
def get_all_tour_endpoint(
    city_id: int = None,
    user_id: int = None,
    
    is_popular: bool = False,
    db: Session = Depends(get_db)
):
    
    results = tour.get_all_tour(db=db, city_id=city_id, user_id=user_id)

    # Nếu cần sắp xếp theo đánh giá
    if is_popular:
        results = tour.sorting_by_ratings_and_quantity_of_reviews(tours=results, db=db)

    # Chuyển đổi các kết quả sang định dạng mong muốn
    final_results = []
    for tour_item in results:
        result = schemas.ShowTour.from_orm(tour_item).dict()
       
        rating_info = tour.get_ratings_and_reviews_number_of_tourID(tour_item.id, db)
        result.update({
            "rating": rating_info["ratings"],
            "numOfReviews": rating_info["numberOfReviews"]
        })
        final_results.append(result)

    return final_results