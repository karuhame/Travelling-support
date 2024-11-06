from datetime import date, time
from typing import List, Optional
from fastapi import APIRouter, Body, HTTPException, Path, Query, UploadFile
from .. import database, schemas, models
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status
from ..repository import destination

router = APIRouter(
    prefix="/hotel",
    tags=['Hotel']
)

get_db = database.get_db



@router.post("/hotel/{destination_id}", response_model=schemas.ShowHotel)
def create_destination_by_cityID(request: schemas.Hotel, destination_id: int, db: Session = Depends(get_db)):
    return destination.create_hotel_info_by_destinationID(request=request, destination_id=destination_id, db=db)


@router.put("/hotel/{hotel_id}", response_model=schemas.ShowHotel)
def update_hotel_info_by_id(request: schemas.Hotel, hotel_id: int, db: Session = Depends(get_db)):
    return destination.update_hotel_info_by_id(request=request, id=hotel_id, db=db)

@router.get("/hotel/{hotel_id}")
def get_hotel_info_by_id(hotel_id: int, db: Session = Depends(get_db)):
    return destination.get_hotel_info( hotel_id=hotel_id, db=db)


@router.get("/hotels/")
def get_all_hotels( 
    city_id: int = None,
    popular: bool = None,
    db: Session = Depends(get_db),
    price_range: list[int] = Query(default=[], alias='price_range'),
    amenities: list[str] = Query(default=[], alias='amenities'),
    hotel_star: list[int] = Query(default=[], alias='hotel_star')
):
    return destination.filter_hotel(city_id=city_id, popular= popular,db=db, price_range=price_range, amenities=amenities, hotel_star=hotel_star) 
