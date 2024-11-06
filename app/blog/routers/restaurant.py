
from datetime import date, time
from typing import List, Optional
from fastapi import APIRouter, Body, HTTPException, Path, Query, UploadFile
from .. import database, schemas, models
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status
from ..repository import restaurant

router = APIRouter(
    prefix="/restaurant",
    tags=['Restaurant']
)

get_db = database.get_db



@router.post("/restaurant/{destination_id}", 
             response_model=schemas.ShowRestaurant, 
             summary="Tạo nhà hàng mới",
             description="Tạo một nhà hàng mới cho một điểm đến cụ thể dựa trên destination_id.",
             response_description="Thông tin về nhà hàng vừa được tạo.")
def create_destination_by_cityID(
    request: schemas.Restaurant = Body(..., description="Thông tin nhà hàng cần tạo."),
    destination_id: int = Path(..., description="ID của điểm đến mà nhà hàng sẽ được gán vào."),
    db: Session = Depends(get_db)
):
    return restaurant.create_restaurant_info_by_destinationID(request=request, destination_id=destination_id, db=db)


@router.put("/restaurant/{restaurant_id}", response_model=schemas.ShowRestaurant)
def update_restaurant_info_by_id(request: schemas.Restaurant, restaurant_id: int, db: Session = Depends(get_db)):
    return restaurant.update_restaurant_info_by_id(request=request, id=restaurant_id, db=db)
@router.get("/restaurants/")
def get_all_restaurants( 
    db: Session = Depends(get_db),
    cuisines: list[str] = Query(default=[], alias='cuisines'),
):
    return restaurant.filter_restaurant(db, cuisines=cuisines) 

@router.get("/restaurant/{restaurant_id}")
def get_restaurant_info_by_id(restaurant_id: int, db: Session = Depends(get_db)):
    return restaurant.get_destination_info( restaurant_id=restaurant_id, db=db)

