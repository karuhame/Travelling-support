from sqlalchemy.orm import Session
from blog import models, schemas
from fastapi import HTTPException, status
from blog.hashing import Hash
from typing import Optional

def create(request: schemas.User, db: Session):
    try:
        new_user = models.User(
            username=request.username,
            email=request.email,
            password=Hash.hash_password(request.password)
        )
        db.add(new_user)
        db.commit()  # Chờ hoàn tất việc commit
        db.refresh(new_user)  # Chờ làm mới đối tượng mới
        return new_user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error creating user: {str(e)}")

def create_business_admin(request: schemas.User, db: Session):
    try:
        new_user = models.User(
            username=request.username,
            email=request.email,
            password=Hash.hash_password(request.password),
            role=request.role
        )
        db.add(new_user)
        db.commit()  # Chờ hoàn tất việc commit
        db.refresh(new_user)  # Chờ làm mới đối tượng mới
        return new_user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error creating business admin: {str(e)}")

def get_by_id(id: int, db: Session):
    try:
        user = db.query(models.User).filter(models.User.id == id).first()  # Chờ truy vấn
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"User with the id {id} is not available")
        return user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error retrieving user: {str(e)}")

def get_all(db: Session):
    try:
        users = db.query(models.User).all()  # Chờ truy vấn
        return users
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error retrieving users: {str(e)}")

def get_by_email(email: str, db: Session):
    try:
        user = db.query(models.User).filter(models.User.email == email).first()  # Chờ truy vấn
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"User with the email {email} is not available")
        return user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error retrieving user by email: {str(e)}")

def update(id: int, request: schemas.User, db: Session):
    try:
        user = db.query(models.User).filter(models.User.id == id).first()  # Chờ truy vấn
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"User with the id {id} is not available")

        user.username = request.username
        user.email = request.email
        if request.password:  # Chỉ cập nhật password nếu có
            user.password = Hash.hash_password(request.password)
        
        db.commit()  # Chờ hoàn tất việc commit
        db.refresh(user)  # Chờ làm mới đối tượng mới
        return user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error updating user: {str(e)}")

def delete(id: int, db: Session):
    try:
        user = db.query(models.User).filter(models.User.id == id).first()  # Chờ truy vấn
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"User with the id {id} is not available")

        db.delete(user)  # Chờ xóa đối tượng
        db.commit()  # Chờ hoàn tất việc commit
        return {"detail": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error deleting user: {str(e)}")
def change_status(db: Session, user_id:int ):
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()  # Chờ truy vấn
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"User with the id {id} is not available")

        if user.status != "enable":
            user.status = "enable"
        else:
            user.status = "disable"
            
        db.commit()      
        return {"detail": "Change successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error deleting user: {str(e)}")
    


# Hàm này trả về None nếu không tìm thấy user
# Không raise exception vì đây là business logic bình thường
# Sử dụng Optional type hint để chỉ rõ hàm có thể trả về None
def get_user_by_email(email: str, db: Session) -> Optional[models.User]:
    """
    Lấy thông tin user theo email.
    Trả về None nếu không tìm thấy user, không raise exception.
    """
    return db.query(models.User).filter(models.User.email == email).first()
