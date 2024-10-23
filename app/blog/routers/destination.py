from typing import List
from fastapi import APIRouter, HTTPException
from .. import database, schemas, models
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status
from ..repository import destination

router = APIRouter(
    prefix="/destination",
    tags=['Destination']
)

get_db = database.get_db


@router.delete("/{id}")
def delete_destination_by_id(id: int, db: Session = Depends(get_db)):
    return destination.delete_by_id(id, db)

@router.post("/", response_model=schemas.ShowDestination)
def create_destination(request: schemas.Destination_Address, db: Session = Depends(get_db)):
    return destination.create(request, db)

@router.post("/hotel/{destination_id}", response_model=schemas.ShowHotel)
def create_destination_by_cityID(request: schemas.Hotel, destination_id: int, db: Session = Depends(get_db)):
    return destination.create_hotel_info_by_destinationID(request=request, destination_id=destination_id, db=db)

@router.post("/restaurant/{destination_id}", response_model=schemas.ShowRestaurant)
def create_destination_by_cityID(request: schemas.Restaurant, destination_id: int, db: Session = Depends(get_db)):
    return destination.create_restaurant_info_by_destinationID(request=request, destination_id=destination_id, db=db)

@router.put("/{id}", response_model=schemas.ShowDestination)
def update_destination_by_id(id: int, request: schemas.Destination, db: Session = Depends(get_db)):
    return destination.update_by_id(id, request, db)

@router.put("/restaurant/{restaurant_id}", response_model=schemas.ShowRestaurant)
def update_restaurant_info_by_id(request: schemas.Restaurant, restaurant_id: int, db: Session = Depends(get_db)):
    return destination.update_restaurant_info_by_id(request=request, id=restaurant_id, db=db)

@router.put("/hotel/{hotel_id}", response_model=schemas.ShowHotel)
def update_hotel_info_by_id(request: schemas.Hotel, hotel_id: int, db: Session = Depends(get_db)):
    return destination.update_hotel_info_by_id(request=request, id=hotel_id, db=db)

@router.get("/")
def get_destination(
    id: int = None,
    city_id: int = None,
    sort_by_reviews: bool = False,
    get_rating: bool = False,
    db: Session = Depends(get_db)
):
    if id:
        # Lấy destination theo ID
        dest = destination.get_by_id(id, db)
        
        if get_rating:
            rating_info = destination.get_ratings_and_reviews_number_of_destinationID(dest.id, db)
            result = schemas.ShowDestination.from_orm(dest).dict()
            result.update({
                "rating": rating_info["ratings"],
                "numOfReviews": rating_info["numberOfReviews"]
            })
            return result
        
        return schemas.ShowDestination.from_orm(dest)
    
    if city_id:
        destinations = destination.get_by_city_id(city_id, db)
        results = [schemas.ShowDestination.from_orm(dest).dict() for dest in destinations]
        
        # Nếu get_rating=True, thêm thông tin rating và số lượng reviews
        if get_rating:
            for result in results:
                rating_info = destination.get_ratings_and_reviews_number_of_destinationID(result["id"], db)
                result.update({
                    "rating": rating_info["ratings"],
                    "numOfReviews": rating_info["numberOfReviews"]
                })
        return results
    
    if sort_by_reviews:
        destinations = destination.sorting_by_ratings_and_quantity_of_reviews(destinations=destinations, db=db)
        results = [schemas.ShowDestination.from_orm(dest).dict() for dest in destinations]
        
        # Nếu get_rating=True, thêm thông tin rating và số lượng reviews
        if get_rating:
            for result in results:
                rating_info = destination.get_ratings_and_reviews_number_of_destinationID(result["id"], db)
                result.update({
                    "rating": rating_info["ratings"],
                    "numOfReviews": rating_info["numberOfReviews"]
                })
        return results
    
    # Nếu không có tham số nào, trả về tất cả các destination
    destinations = destination.get_all(db)
    results = [schemas.ShowDestination.from_orm(dest).dict() for dest in destinations]
    
    # Nếu get_rating=True, thêm thông tin rating và số lượng reviews
    if get_rating:
        for result in results:
            rating_info = destination.get_ratings_and_reviews_number_of_destinationID(result["id"], db)
            result.update({
                "rating": rating_info["ratings"],
                "numOfReviews": rating_info["numberOfReviews"]
            })
    return results
