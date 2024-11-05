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
    
    print(user.status)
    return token_data  # Trả về đối tượng user thay vì token_data
