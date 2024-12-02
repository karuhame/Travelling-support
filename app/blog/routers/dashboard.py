from datetime import date, time
from typing import List, Optional
from fastapi import APIRouter, Body, HTTPException, Path, Query, UploadFile
from .. import database, schemas, models
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status
from ..repository import destination, city,dashboard

router = APIRouter(
    prefix="/dashboard",
    tags=['Dashboard']
)

get_db = database.get_db

@router.get("/search", description="Search city and destination by name, the result contains 2 list: cities and destinations")
def search_by_name_of_destination_and_city(
    text: str = None,    
    db: Session = Depends(get_db)
):
    city_list = city.search_by_name(db=db, text=text)
    destination_list = destination.search_by_name(db=db, text=text)
    
    results = {
        "cities": [{"id": city.id, "name": city.name} for city in city_list],
        "destinations": [{"id": destination.id, "name": destination.name} for destination in destination_list]
    }

    return results

@router.get("/usercounts/month/{year}", response_model=List[schemas.UserCountByMonth])
def read_user_counts_by_month(
    year: int,
    is_business: bool,
    db: Session = Depends(get_db)
):
    return dashboard.get_account_counts_by_month(db=db, year=year, is_business= is_business)

@router.get("/usercounts/{year}/{month}/days", response_model=List[schemas.UserCountDetail])
def read_user_counts_by_day(
    year: int,
    month: int,
    is_business: bool,
    db: Session = Depends(get_db)):
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Invalid month. Month must be between 1 and 12.")
    return dashboard.get_account_counts_by_day(db=db, year=year, is_business= is_business,month= month)


