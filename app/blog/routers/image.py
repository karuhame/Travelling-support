from datetime import date, time
from typing import List, Optional
from fastapi import APIRouter, Body, File, HTTPException, Path, Query, UploadFile
from .. import database, schemas, models
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status
from ..repository import image

router = APIRouter(
    prefix="/image",
    tags=['Image']
)

get_db = database.get_db


@router.post("/")
async def create_user_info_by_userid(
    city_id:int = None, 
    destination_id:int = None, 
    review_id:int = None, 
    userInfo_id:int = None, 

    image_inp: Optional[UploadFile] = File(None),  
    db: Session = Depends(get_db),
):
    sc_image = schemas.Image(
        city_id= city_id,
        destination_id= destination_id,
        review_id= review_id,
        userInfo_id= userInfo_id
    )
    # Thêm hình ảnh vào thông tin người dùng
    img = await image.create_image(db, sc_image, image=image_inp)
    print(img.id)
    return img


@router.delete("/{id}")
async def create_user_info_by_userid(
    id: int,
    db: Session = Depends(get_db),
):
    return await image.delete_image(db=db, id=id)
    