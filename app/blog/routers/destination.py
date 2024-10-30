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

@router.get("/hotel/{hotel_id}")
def get_hotel_info_by_id(hotel_id: int, db: Session = Depends(get_db)):
    return destination.get_hotel_info( hotel_id=hotel_id, db=db)

@router.get("/hotels/")
def get_all_hotels( db: Session = Depends(get_db)):
    return destination.get_all_hotel(db=db)

@router.get("/popular/{city_id}")
def get_popular_destination_by_cityID(city_id: int, db: Session = Depends(get_db)):
    return destination.get_popular_destinations_by_city_ID(city_id=city_id, db=db)

@router.get("/")
def get_destination(
    id: int = None,
    city_id: int = None,
    sort_by_reviews: bool = False,
    get_rating: bool = False,
    db: Session = Depends(get_db)
):
    results = []

    # Nếu có id, lấy destination theo ID
    if id:
        dest = destination.get_by_id(id, db)
        if not dest:
            return {"error": "Destination not found"}
        results.append(dest)

    # Nếu có city_id, lấy destinations theo city_id
    elif city_id:
        results = destination.get_by_city_id(city_id, db)

    # Nếu không có id hay city_id, lấy tất cả destinations
    else:
        results = destination.get_all(db)

    # Nếu cần sắp xếp theo đánh giá
    if sort_by_reviews:
        results = destination.sorting_by_ratings_and_quantity_of_reviews(destinations=results, db=db)

    # Chuyển đổi các kết quả sang định dạng mong muốn
    final_results = []
    for dest in results:
        result = schemas.ShowDestination.from_orm(dest).dict()
        if get_rating:
            rating_info = destination.get_ratings_and_reviews_number_of_destinationID(dest.id, db)
            result.update({
                "rating": rating_info["ratings"],
                "numOfReviews": rating_info["numberOfReviews"]
            })
        final_results.append(result)

    return final_results