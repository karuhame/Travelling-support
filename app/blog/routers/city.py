from typing import List, Optional
from fastapi import APIRouter, Body, UploadFile
from .. import database, schemas, models
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status
from ..repository import city, image

router = APIRouter(
    prefix="/city",
    tags=['City']
)

get_db = database.get_db


@router.post("/", response_model=schemas.ShowCity)
async def create_city(
    name: str,
    description: str,
    images: Optional[List[UploadFile]] = [],
    db: Session = Depends(get_db)
):
    
    request = schemas.City(
        name=  name,
        description=  description
    )
    
    new_city = city.create_city(request, db)
    for img in images:
        sc_image = schemas.Image(
            city_id = new_city.id
        )
        await image.create_image(db, request=sc_image, image=img)
    return new_city
    

@router.get("/{id}")
def get_city_by_id(id: int, db: Session = Depends(get_db)):
    result = city.get_city_by_id(id, db)
    return schemas.ShowCity.from_orm(result)
@router.get("/", response_model=List[schemas.ShowCity])
def get_all_city(db: Session = Depends(get_db)):
    cities = city.get_all_city(db)
    return [schemas.ShowCity.from_orm(city) for city in cities]


@router.put("/{id}", response_model=schemas.ShowCity)
async def update_city_by_id(
    id: int,
    name: str,
    description: str,

    new_images: Optional[List[UploadFile]] = [],  # Ảnh mới
    image_ids_to_remove: Optional[List[int]] = Body([]),  # Danh sách ID ảnh cần xóa
    
    db: Session = Depends(get_db)):
    
    request = schemas.City(
        name=  name,
        description=  description
    )
    new_city =  city.update_city_by_id(id=id, request=request, db=db)

    #delete images_to_remove
    for img_id in image_ids_to_remove:
        await image.delete_image(db=db,id=img_id )
        
    #add new images
    for img in new_images:
        sc_image = schemas.Image(
            city_id = new_city.id
        )
        await image.create_image(db, request=sc_image, image=img)
    
    return new_city

@router.delete("/{id}")
async def delete_city_by_id(id: int, db: Session = Depends(get_db)):
    return await city.delete_city_by_id(id, db)
