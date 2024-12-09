from typing import List
from sqlalchemy import func
from sqlalchemy.orm import Session
from blog import models, schemas
from fastapi import HTTPException, status


ACTION_LIST = [
    "CREATE_DESTINATION",
    "DELETE_DESTINATION",
    "SHOW_DESTINATION"
]

def get_all_action(db:Session):
    return db.query(models.Action).all()


def get_action_of_userID(user_id: int, db:Session):
    try:
        return (
            db.query(models.UserAction, models.Action.action_name)
            .join(models.Action, models.UserAction.action_id == models.Action.id)
            .filter(models.UserAction.user_id == user_id)
            .all()
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get action of user with id: {user_id}")

    
def add_permission_to_user(user_id: int, action_id: int, db:Session):
    try:
        
        userAction = models.UserAction(
            user_id = user_id,
            action_id = action_id,
            is_allowed = True,
        )
        db.add(userAction)  
        db.commit()
        db.refresh(userAction)
        return userAction
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add permission")
        
    
def change_status_by_UserActionID(user_action_id: int, db:Session):
    try:

        userAction = db.query(models.UserAction).filter(models.UserAction.id == user_action_id).first()
        userAction.is_allowed = not userAction.is_allowed
        db.commit()
        db.refresh(userAction)
        return userAction
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed change permission_status")
def get_user_permissions(user_id: int, db: Session):
    # Lấy tất cả hành động
    actions = db.query(models.Action).all()
    
    result = []
    
    for action in actions:
        # Kiểm tra permission của user cho action này
        user_action = db.query(models.UserAction).filter_by(user_id=user_id, action_id=action.id).first()
        
        if user_action is None:
            # Nếu không có permission, thêm mới vào bảng UserAction
            new_user_action = models.UserAction(user_id=user_id, action_id=action.id, is_allowed=False)
            db.add(new_user_action)
            result.append(new_user_action)  # Thêm vào result trước khi commit
        else:
            result.append(user_action)

    db.commit()  # Commit tất cả các thay đổi ở cuối
    # Refresh tất cả các đối tượng mới trong result để đảm bảo chúng có ID
    for action in result:
        db.refresh(action)

    return result