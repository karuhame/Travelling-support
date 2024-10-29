from typing import List
from fastapi import APIRouter, HTTPException
from .. import database, schemas, models
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status
from ..repository import tour

router = APIRouter(
    prefix="/tour",
    tags=['Tour']
)

get_db = database.get_db

@router.post("/tours")
def create_tour(tour_data: schemas.Tour, db: Session = Depends(get_db)):
    return tour.create(request=tour_data, db=db)

@router.get("/tours/{tour_id}")
def get_tour_by_id_endpoint(tour_id: int, db: Session = Depends(get_db)):
    return tour.get_tour_by_id(tour_id=tour_id, db=db)

@router.get("/tours")
def get_all_tour_endpoint(db: Session = Depends(get_db)):
    return tour.get_all_tour(db = db)