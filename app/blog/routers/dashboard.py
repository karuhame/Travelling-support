from datetime import date, time
from typing import List, Optional
from fastapi import APIRouter, Body, HTTPException, Path, Query, UploadFile
from .. import database, schemas, models
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status
from ..repository import destination, city

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