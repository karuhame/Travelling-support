from sqlalchemy.orm import Session
from blog import models, schemas
from fastapi import HTTPException, status
from blog.hashing import Hash
from typing import Optional
from collections import Counter
from blog.repository.destination import get_tags_by_id
from sqlalchemy import func


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
        return True
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error deleting user: {str(e)}")
    return False
    
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






def has_liked(user_id: int, destination_id: int, db: Session) -> bool:
    like = db.query(models.UserDestinationLike).filter_by(user_id=user_id, destination_id=destination_id).first()
    return like is not None

def like_destination(user_id: int, destination_id: int, db: Session):
    if has_liked(user_id, destination_id, db):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User has already liked this destination.")
    
    new_like = models.UserDestinationLike(user_id=user_id, destination_id=destination_id)
    db.add(new_like)
    db.commit()
    db.refresh(new_like)
    return new_like

def unlike_destination(user_id: int, destination_id: int, db: Session):
    like = db.query(models.UserDestinationLike).filter_by(user_id=user_id, destination_id=destination_id).first()
    if not like:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User has not liked this destination.")
    
    db.delete(like)
    db.commit()
    return {"detail": "Like removed successfully."}

def get_liked_destinations(user_id: int, db: Session):
    likes = db.query(models.UserDestinationLike).filter_by(user_id=user_id).all()
    return [like.destination_id for like in likes]


def count_tags_for_user(user_id: int, db: Session):
    try:
        # Get destinations liked by the user
        liked_destinations = get_liked_destinations(user_id, db)
        
        # Initialize a counter for tags
        tag_counter = Counter()

        for destination_id in liked_destinations:
            tags = get_tags_by_id(destination_id, db)
            if tags and "tags" in tags:
                tag_counter.update(tag.id for tag in tags["tags"])
        
        return dict(tag_counter)
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error counting tags: {str(e)}")
    
def get_user_counts(
    period: str,
    db: Session):
    if period == "day_of_week":
        results = (
            db.query(
                func.dayofweek(models.User.created_at).label('day_of_week'),  # MySQL function
                func.count(models.User.id).label('user_count')
            )
            .group_by('day_of_week')
            .all()
        )
        return [schemas.UserCount(month=row.day_of_week, user_count=row.user_count) for row in results]

    elif period == "week_of_month":
        results = (
            db.query(
                func.week(models.User.created_at, 1).label('week'),  # MySQL function with mode 1 for week starts on Monday
                func.count(models.User.id).label('user_count')
            )
            .group_by('week')
            .all()
        )
        return [schemas.UserCount(month=row.week, user_count=row.user_count) for row in results]

    elif period == "month":
        results = (
            db.query(
                func.month(models.User.created_at).label('month'),  # MySQL function
                func.count(models.User.id).label('user_count')
            )
            .group_by('month')
            .all()
        )
        return [schemas.UserCount(month=row.month, user_count=row.user_count) for row in results]
