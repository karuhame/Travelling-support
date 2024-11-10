from datetime import date, time
from typing import List, Optional
from fastapi import APIRouter, Body, HTTPException, Path, Query, UploadFile
from .. import database, schemas, models
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status
from ..repository import hotel, destination

router = APIRouter(
    prefix="/hotel",
    tags=['Hotel']
)

get_db = database.get_db



@router.post("/hotel/{destination_id}", response_model=schemas.ShowHotel)
def create_destination_by_cityID(request: schemas.Hotel, destination_id: int, db: Session = Depends(get_db)):
    return hotel.create_by_destinationID(request=request, destination_id=destination_id, db=db)


@router.put("/hotel/{id}", response_model=schemas.ShowHotel)
def update_hotel_info_by_id(request: schemas.Hotel, id: int, db: Session = Depends(get_db)):
    return hotel.update_hotel_info_by_id(request=request, id=id, db=db)

@router.delete("/hotel/{id}")
def update_hotel_info_by_id(id: int, db: Session = Depends(get_db)):
    return hotel.delete_by_id(id=id, db=db)



@router.get("/hotel/{id}")
def get_hotel_info_by_id(id: int, db: Session = Depends(get_db)):
    return hotel.get_hotel_info( id=id, db=db)


@router.get("/hotels/")
def get_all_hotels( 
    city_id: int = None,
    is_popular: bool = None,
    
    db: Session = Depends(get_db),
    price_range: list[str] = Query(default=[], alias='price_range'
                                   , description="Danh sách các khoảng giá (ví dụ: 'low', 'middle', 'high')"),
    amenities: list[str] = Query(default=[], alias='amenities'),
    hotel_star: list[int] = Query(default=[], alias='hotel_star')
):
    
    hotels = hotel.get_all_hotel(db, city_id)
    
    if any([price_range, amenities, hotel_star]):
        hotels = hotel.filter_hotel(hotels = hotels, db=db, price_range=price_range, amenities=amenities, hotel_star=hotel_star) 
    
    if is_popular == True:
        hotels = destination.sorting_by_ratings_and_quantity_of_reviews(db=db, destinations=hotels)
    
    results = []
    for hotel_dest in hotels:
        hotel_info = hotel.get_hotel_info(db=db, id = hotel_dest.id)
        results.append(hotel_info)
    
    return results
    
    