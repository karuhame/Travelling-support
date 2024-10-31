from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from blog import schemas, database, models, token, oauth2
from blog.hashing import Hash
from sqlalchemy.orm import Session

router = APIRouter(tags=['Authentication'])


@router.post('/login')
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(
        models.User.email == request.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Invalid Credentials")
    if not Hash.verify(user.password, request.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Incorrect password")

    access_token = token.create_access_token(data={"email": user.email, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get('/current-user')
def read_users_me(
    current_user: Annotated[schemas.User, Depends(oauth2.get_current_user)], db: Session = Depends(database.get_db),
):
    user = db.query(models.User).filter(
        models.User.email == current_user.email).first()
    return schemas.ShowUser.from_orm(user).dict()