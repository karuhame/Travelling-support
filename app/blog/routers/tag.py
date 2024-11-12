from datetime import date, time
from typing import List, Optional
from fastapi import APIRouter, Body, HTTPException, Path, Query, UploadFile
from .. import database, schemas, models
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status
from ..repository import tag

router = APIRouter(
    prefix="/tag",
    tags=['Tag']
)

get_db = database.get_db


@router.post("/add_to_destination")
def add_tag_to_destination(tag_id: int, dest_id: int,  db: Session = Depends(get_db)):
    return tag.add_tag_to_destination(db=db, tag_id=tag_id, dest_id=dest_id)
    

@router.post("/", response_model=schemas.ShowTag)
def create_tag(request: schemas.Tag, db: Session = Depends(get_db)):
    return tag.create_tag(request, db)

@router.get("/", response_model=List[schemas.ShowTag])
def get_all_tags(db: Session = Depends(get_db)):
    return tag.get_all_tags(db)

@router.get("/{id}", response_model=schemas.ShowTag)
def get_tag(id: int, db: Session = Depends(get_db)):
    return tag.get_tag_by_id(id, db)

@router.put("/{id}", response_model=schemas.ShowTag)
def update_tag(id: int, request: schemas.Tag, db: Session = Depends(get_db)):
    return tag.update_tag(id, request, db)

@router.delete("/{id}")
def delete_tag(id: int, db: Session = Depends(get_db)):
    return tag.delete_tag(id, db)

