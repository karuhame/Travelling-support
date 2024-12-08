from typing import List
from sqlalchemy import func
from sqlalchemy.orm import Session
from blog import models, schemas
from fastapi import HTTPException


def get_all_action(db:Session):
    return db.query(models.Action).all()


def get_action_of_userID(user_id: int, db:Session):
    return db.query(models.UserAction).filter(models.UserAction.user_id == user_id).all()
