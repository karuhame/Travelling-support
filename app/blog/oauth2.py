from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from requests import Session
from blog import token, schemas, models, database

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(data: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # Xác thực token và lấy dữ liệu
    token_data = token.verify_token(data, credentials_exception)
    
    # Sử dụng phiên làm việc db để truy vấn
    user = db.query(models.User).filter(models.User.email == token_data.email).first()
    
    if user is None:
        raise credentials_exception
    if user.status != "enable":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is banned",
        )
    token_data.user_id = user.id
    print(token_data.user_id)
    return token_data  # Trả về đối tượng user thay vì token_data

def authorize_action(action_name: str):
    def decorator(current_user: schemas.User = Depends(get_current_user),  db: Session = Depends(database.get_db)):
        # Tìm action_id dựa trên action_name
        action = db.query(models.Action).filter(models.Action.action_name == action_name).first()
        print(action.action_name)
        print(action.id)
        if not action:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Action not found"
            )
        
        # Kiểm tra quyền hạn của người dùng
        permission = db.query(models.UserAction).filter(
            (models.UserAction.user_id == current_user.user_id),
            (models.UserAction.action_id == action.id)
        ).first()
        if not permission or not permission.is_allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action"
            )
        return current_user
    return decorator