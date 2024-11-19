from typing import Optional
from fastapi import APIRouter, File, HTTPException, UploadFile
from .. import database, schemas, models, oauth2
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status
from ..repository import userInfo, image

router = APIRouter(
    prefix="/userInfo",
    tags=['Users Info']
)

get_db = database.get_db


@router.post("/")
async def create_user_info_by_userid(
    user_id: int,
    description: str = None,
    phone_number: str = None,
    district: str = None,
    street: str = None,
    ward: str = None,
    city_id: int = None,
    image_inp: Optional[UploadFile] = File(None),  
    
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.get_current_user)
):
    
    # Tạo đối tượng request từ schema UserInfoBase
    info = schemas.UserInfoBase(
        description=description,
        phone_number=phone_number,
    )

    # Tạo đối tượng address từ schema Address
    address = schemas.Address(
        district=district,
        street=street,
        ward=ward,
        city_id=city_id,
    )
    
    # Tạo thông tin người dùng bằng user_id
    user_info = userInfo.create_user_info_by_userid(address=address, info=info, user_id=user_id, db=db)
    sc_image = schemas.Image(
        userInfo_id= user_info.id
    )

    # Thêm hình ảnh vào thông tin người dùng
    await image.create_image(db, request=sc_image, image=image_inp)
    
    return schemas.ShowUserInfo.from_orm(user_info)

@router.get("/{id}")
def get_user_info(id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    user_info = userInfo.get_userInfo_by_id(db=db, id=id)  # Gọi hàm với await
    return schemas.ShowUserInfo.from_orm(user_info)  # Trả về thông tin người dùng

@router.put("/{id}")
async def update_user_info(
    id: int,
    description: str = None,
    phone_number: str = None,
    district: str = None,
    street: str = None,
    ward: str = None,
    city_id: int = None,
    image_inp: Optional[UploadFile] = File(None),  
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.get_current_user)
):
    # Tạo đối tượng request từ schema UserInfoBase
    info = schemas.UserInfoBase(
        description=description,
        phone_number=phone_number,
    )

    # Tạo đối tượng address từ schema Address
    address = schemas.Address(
        district=district,
        street=street,
        ward=ward,
        city_id=city_id,
    )
    
    sc_image = schemas.Image(
        userInfo_id= id
    )
    
    user_info = userInfo.update_user_info(address=address, info=info, id=id, db=db)
    if user_info.image.blob_name:
        await image.update_image(db,image_inp=image_inp, id=user_info.image.id)
    else:
        await image.create_image(db, sc_image, image=image_inp)
    return schemas.ShowUserInfo.from_orm(user_info)
@router.delete("/{id}")
async def delete_user_info(id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    return  await userInfo.delete_user_info(id, db)

@router.get("/")
def get_all(db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    user_infoes = userInfo.get_all(db=db)
    return [schemas.ShowUserInfo.from_orm(user_info) for user_info in user_infoes]