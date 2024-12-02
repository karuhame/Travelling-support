
from datetime import date, time
from typing import List, Optional
from fastapi import APIRouter, Body, HTTPException, Path, Query, UploadFile
from .. import database, schemas, models
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status
from ..repository import restaurant, destination

router = APIRouter(
    prefix="/restaurant",
    tags=['Restaurant']
)

get_db = database.get_db



@router.post("/{destination_id}", response_model=schemas.ShowRestaurant)
def create_by_destinationID(request: schemas.Restaurant, destination_id: int, db: Session = Depends(get_db)):
    return restaurant.create_by_destinationID(request=request, destination_id=destination_id, db=db)


@router.put("/{id}", response_model=schemas.ShowRestaurant)
def update_restaurant_info_by_id(request: schemas.Restaurant, id: int, db: Session = Depends(get_db)):
    return restaurant.update_restaurant_info_by_id(request=request, id=id, db=db)

@router.delete("/{id}")
def update_restaurant_info_by_id(id: int, db: Session = Depends(get_db)):
    return restaurant.delete_by_id(id=id, db=db)

@router.get("/{id}")
def get_restaurant_info_by_id(id: int, db: Session = Depends(get_db)):
    return restaurant.get_restaurant_info( id=id, db=db)


@router.get("/")
def get_all_restaurants( 
    city_id: int = None,
    is_popular: bool = None,
    
    db: Session = Depends(get_db),
    special_diets: list[str] = Query(default=[], alias='special_diets'
                                   , description="Danh sách các khoảng giá (ví dụ: 'vege')"),
    cuisines: list[str] = Query(default=[], alias='cuisines'
                                , description="Danh sách các khoảng giá (ví dụ: 'Vietnam', 'ThaiLand', 'Indo')"),
    features: list[str] = Query(default=[], alias='features'
                                , description="Danh sách các khoảng giá (ví dụ: 'outdoor sitting, private dining, buffet')"),
    meals: list[str] = Query(default=[], alias='meals'
                                , description="Danh sách các khoảng giá (ví dụ: 'breakfast, dinner')"),

):
    restaurants = restaurant.get_all_restaurant(db, city_id)
    
    if any([special_diets, cuisines, features, meals]):
        restaurants = restaurant.filter_restaurant(restaurants = restaurants, db=db, cuisines=cuisines, special_diets=special_diets, features=features, meals=meals) 
    
    if is_popular == True:
        restaurants = destination.sorting_by_ratings_and_quantity_of_reviews(db=db, destinations=restaurants)
    
    results = []                                                     
    for restaurant_dest in restaurants:
        restaurant_info = restaurant.get_restaurant_info(db=db, id = restaurant_dest.restaurant.id)
        results.append(restaurant_info)
    
    return results
    
    