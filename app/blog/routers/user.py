from fastapi import APIRouter, HTTPException
from blog import database, schemas, models, oauth2
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status
from blog.repository import user
from typing import List

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

@router.delete('/{id}')
def delete_user(id: int, db: Session = Depends(get_db)):
    return user.delete(id=id, db=db)