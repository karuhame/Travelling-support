from fastapi import APIRouter
from .. import database, schemas, models
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status
from ..repository import userInfo

router = APIRouter(
    prefix="/userInfo",
    tags=['Users Info']
)

get_db = database.get_db


@router.post("/{user_id}", response_model=schemas.ShowUserInfo)
def create_user_info_by_userid(request: schemas.UserInfoBase, user_id: int, db: Session = Depends(get_db)):
    return userInfo.create_user_info_by_userid(request, user_id, db)

@router.get("/{user_id}", response_model=schemas.ShowUserInfo)
def get_user_info_by_userid(user_id: int, db: Session = Depends(get_db)):
    return userInfo.get_user_info_by_userid(user_id, db)

@router.put("/{user_id}", response_model=schemas.ShowUserInfo)
def update_user_info_by_userid(user_id: int, request: schemas.UserInfoBase, db: Session = Depends(get_db)):
    return userInfo.update_user_info_by_userid(user_id, request, db)

@router.delete("/{user_id}")
def delete_user_info_by_userid(user_id: int, db: Session = Depends(get_db)):
    return userInfo.delete_user_info_by_userid(user_id, db)
