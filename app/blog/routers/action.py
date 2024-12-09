from typing import List
from fastapi import APIRouter
from .. import database, schemas, models
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status
from ..repository import address, city, action

router = APIRouter(
    prefix="/action",
    tags=['Action']
)

get_db = database.get_db

@router.get("/permissions/{user_id}")
def get_user_permissions(user_id: int, db: Session = Depends(get_db)):
    results = action.get_user_permissions(user_id=user_id, db=db)
    return results
@router.get("/")
def get_all_action(db: Session = Depends(get_db)):
    actions = action.get_all_action(db=db)
    return actions

@router.get("/user/{user_id}")
def get_action_of_userID(user_id: int, db: Session = Depends(get_db)):
    userAction = action.get_action_of_userID(user_id=user_id, db=db)
    return userAction

@router.post("/{action_id}/user/{user_id}")
def add_permission_to_user(user_id: int, action_id: int,  db: Session = Depends(get_db)):
    userAction = action.add_permission_to_user(action_id=action_id, user_id=user_id, db=db)
    return userAction

@router.post("/{user_action_id}")
def change_status_by_UserActionID(user_action_id: int,  db: Session = Depends(get_db)):
    return action.change_status_by_UserActionID(user_action_id=user_action_id, db=db)

