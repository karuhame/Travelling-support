from sqlalchemy.orm import Session
from blog import models, schemas
from fastapi import HTTPException, status



def create_tag(request: schemas.Tag, db: Session):
    try:
        new_tag = models.Tag(name=request.name)
        db.add(new_tag)
        db.commit()
        db.refresh(new_tag)
        return new_tag
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error creating tag: {str(e.detail)}")

def get_all_tags(db: Session):
    try:
        return db.query(models.Tag).all()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error retrieving tags: {str(e.detail)}")

def get_tag_by_id(id: int, db: Session):
    try:
        tag = db.query(models.Tag).filter(models.Tag.id == id).first()
        if not tag:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Tag with id {id} not found")
        return tag
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error retrieving tag: {str(e.detail)}")

def update_tag(id: int, request: schemas.Tag, db: Session):
    try:
        tag = db.query(models.Tag).filter(models.Tag.id == id).first()
        if not tag:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Tag with id {id} not found")
        
        tag.name = request.name
        db.commit()
        db.refresh(tag)
        return tag
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error updating tag: {str(e.detail)}")

def delete_tag(id: int, db: Session):
    try:
        tag = db.query(models.Tag).filter(models.Tag.id == id).first()
        if not tag:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Tag with id {id} not found")
        
        db.delete(tag)
        db.commit()
        return {"detail": "Tag deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error deleting tag: {str(e.detail)}")
        
def add_tag_to_destination(tag_id: int, dest_id: int, db: Session):
    try:
        # Tạo một đối tượng mới cho mối quan hệ giữa Destination và Tag
        destination_tag = models.DestinationTag(destination_id=dest_id, tag_id=tag_id)
        
        # Thêm vào cơ sở dữ liệu
        db.add(destination_tag)
        db.commit()  # Lưu thay đổi
        db.refresh(destination_tag)
        print(destination_tag.id)
        return destination_tag
    except Exception as e:
        db.rollback()  # Hoàn tác nếu có lỗi khác
        raise ValueError(str(e.detail))