from typing import Optional
from fastapi import APIRouter, File, UploadFile
from .. import database, schemas, models, oauth2
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status
from ..repository import userInfo

router = APIRouter(
    prefix="/userInfo",
    tags=['Users Info']
)

get_db = database.get_db


@router.post("/")
async def create_user_info_by_userid(
    user_id: int,
    description: str,
    phone_number: str,
    district: str,
    street: str,
    ward: str,
    city_id: int,
    image: Optional[UploadFile] = File(None),  
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

    # Thêm hình ảnh vào thông tin người dùng
    await userInfo.add_image_to_userInfo(db, image, user_info.id)

    return schemas.ShowUserInfo.from_orm(user_info)

@router.get("/{id}")
def get_user_info(id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    user_info = userInfo.get_userInfo_by_id(db=db, id=id)  # Gọi hàm với await
    return schemas.ShowUserInfo.from_orm(user_info)  # Trả về thông tin người dùng

@router.put("/{id}")
async def update_user_info(
    id: int,
    user_id: int,
    description: str,
    phone_number: str,
    district: str,
    street: str,
    ward: str,
    city_id: int,
    image: Optional[UploadFile] = File(None),  
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
    
    user_info = userInfo.update_user_info(address=address, info=info, id=id, db=db)

    await userInfo.update_image(db,image=image, userInfo_id=user_info.id)
    return schemas.ShowUserInfo.from_orm(user_info)
@router.delete("/{id}")
def delete_user_info(id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    return userInfo.delete_user_info(id, db)

@router.get("/")
def get_all(db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    user_infoes = userInfo.get_all(db=db)
    return [schemas.ShowUserInfo.from_orm(user_info) for user_info in user_infoes]