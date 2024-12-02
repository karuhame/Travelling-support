from fastapi import APIRouter, HTTPException
from blog import database, schemas, models, oauth2
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status
from blog.repository import user
from typing import List, Dict

router = APIRouter(
    prefix="/user",
    tags=['Users']
)

get_db = database.get_db


@router.post('/', response_model=schemas.ShowUser)
def create_user(request: schemas.SignUp, db: Session = Depends(get_db)):
    return user.create(request, db)


@router.get('/{id}', response_model=schemas.ShowUser)
def get_user(id: int, db: Session = Depends(get_db)):
    return user.get_by_id(id, db)

@router.get('/', response_model=List[schemas.ShowUser])
def admin_all(db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role == "admin":
        return user.get_all(db)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource."
        )
@router.post('/status_change/{user_id}')
def change_status(user_id: int, db:Session = Depends(get_db)):
    return user.change_status(db=db, user_id = user_id)




@router.get('/{user_id}/has_liked/{destination_id}', response_model=bool)
def check_like(user_id: int, destination_id: int, db: Session = Depends(get_db)):
    return user.has_liked(user_id, destination_id, db)

@router.post('/{user_id}/like/{destination_id}')
def add_like(user_id: int, destination_id: int, db: Session = Depends(get_db)):
    return user.like_destination(user_id, destination_id, db)

@router.delete('/{user_id}/unlike/{destination_id}')
def remove_like(user_id: int, destination_id: int, db: Session = Depends(get_db)):
    return user.unlike_destination(user_id, destination_id, db)

@router.get('/{user_id}/likes', response_model=List[int])
def get_user_likes(user_id: int, db: Session = Depends(get_db)):
    return user.get_liked_destinations(user_id, db)

@router.get('/{user_id}/tags_stastic', response_model=Dict[int, int])
def get_user_likes(user_id: int, db: Session = Depends(get_db)):
    return user.count_tags_for_user(user_id, db)

@router.delete('/{id}')
def delete_user(id: int, db: Session = Depends(get_db)):
    return user.delete(id=id, db=db)
