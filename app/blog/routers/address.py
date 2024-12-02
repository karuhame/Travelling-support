from typing import List
from fastapi import APIRouter
from .. import database, schemas, models
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status
from ..repository import address, city

router = APIRouter(
    prefix="/address",
    tags=['Address']
)

get_db = database.get_db

@router.get("/cities")
def read_distinct_cities(db: Session = Depends(get_db)):
    cities = address.get_distinct_cities(db)
    return cities

@router.get("/districts/{city_id}", response_model=list[str])
def read_distinct_districts(city_id: int, db: Session = Depends(get_db)):
    districts = address.get_distinct_districts(db=db, city_id=city_id)
    return [district[0] for district in districts]  # Chuyển đổi tuple thành danh sách

@router.get("/wards/{district_name}", response_model=list[str])
def read_distinct_wards(district_name: str, db: Session = Depends(get_db)):
    wards = address.get_distinct_wards(db=db, district=district_name)
    return [ward[0] for ward in wards]  # Chuyển đổi tuple thành danh sách