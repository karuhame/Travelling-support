from typing import List
from fastapi import APIRouter
from .. import database, schemas, models
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status
from ..repository import city

router = APIRouter(
    prefix="/city",
    tags=['City']
)

get_db = database.get_db


@router.post("/", response_model=schemas.ShowCity)
def create_city(request: schemas.City, db: Session = Depends(get_db)):
    return city.create_city(request, db)

@router.get("/{id}")
def get_city_by_id(id: int, db: Session = Depends(get_db)):
    result = city.get_city_by_id(id, db)
    return schemas.ShowCity.from_orm(result)
@router.get("/", response_model=List[schemas.ShowCity])
def get_all_city(db: Session = Depends(get_db)):
    return city.get_all_city(db)


@router.put("/{id}", response_model=schemas.ShowCity)
def update_city_by_id(id: int, request: schemas.City, db: Session = Depends(get_db)):
    return city.update_city_by_id(id, request, db)

@router.delete("/{id}")
def delete_city_by_id(id: int, db: Session = Depends(get_db)):
    return city.delete_city_by_id(id, db)
