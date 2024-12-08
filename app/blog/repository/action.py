from typing import List
from sqlalchemy import func
from sqlalchemy.orm import Session
from blog import models, schemas
from fastapi import HTTPException, status


def get_all_action(db:Session):
    return db.query(models.Action).all()


def get_action_of_userID(user_id: int, db:Session):
    return (
        db.query(models.UserAction, models.Action.action_name)
        .join(models.Action, models.UserAction.action_id == models.Action.id)
        .filter(models.UserAction.user_id == user_id)
        .all()
    )
    
def change_status_by_UserActionID(user_action_id: int, db:Session):
    try:

        userAction = db.query(models.UserAction).filter(models.UserAction.id == user_action_id).first()
        userAction.is_allowed = not userAction.is_allowed
        db.commit()
        db.refresh(userAction)
        return userAction
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update city info")
