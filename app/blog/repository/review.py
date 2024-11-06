from sqlalchemy.orm import Session
from blog import models, schemas
from fastapi import HTTPException, UploadFile, status
from blog.hashing import Hash
from blog.repository.image import ImageHandler
def create_by_userId_destinationId(user_id: int, destination_id: int,  request: schemas.Review, db: Session):
    try:
        new_review = models.Review(
            title = request.title,
            content = request.content,
            rating = request.rating,
            date_create = request.date_create,
            user_id = user_id,
            destination_id = destination_id
        )
        db.add(new_review)
        db.commit()  # Chờ hoàn tất việc commit
        db.refresh(new_review)  # Chờ làm mới đối tượng mới
        return new_review
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error creating review: {str(e)}")

def get_by_id(id: int, db: Session):
    try:
        review = db.query(models.Review).filter(models.Review.id == id).first()  # Chờ truy vấn
        if not review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"review with the id {id} is not available")
        return review
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error retrieving review: {str(e)}")

def get_reviews_of_destination_by_destinationId(destination_id: int, db: Session):
    try:
        print(destination_id)
        reviews = db.query(models.Review).filter(models.Review.destination_id == destination_id).all()  # Chờ truy vấn
        return reviews
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error retrieving reviews: {str(e)}")
def get_reviews_of_user_in_1_destination_by_userId_and_destinationID(destination_id: int, user_id: int, db: Session):
    try:
        # Truy vấn chỉ các review có destination_id và user_id tương ứng
        reviews = db.query(models.Review).filter(
            models.Review.destination_id == destination_id,
            models.Review.user_id == user_id
        ).all()  # Lấy tất cả các review
        return reviews
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error retrieving reviews: {str(e)}")
def update_by_id(id: int, request: schemas.Review, db: Session):
    try:
        review = db.query(models.Review).filter(models.Review.id == id).first()  # Chờ truy vấn
        if not review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"review with the id {id} is not available")

        review.title = request.title
        review.content = request.content
        review.rating = request.rating
        review.date_create = request.date_create
    
        db.commit()  # Chờ hoàn tất việc commit
        db.refresh(review)  # Chờ làm mới đối tượng mới
        return review
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error updating review: {str(e)}")

def delete_by_id(id: int, db: Session):
    try:
        review = db.query(models.Review).filter(models.Review.id == id).first()  # Chờ truy vấn
        if not review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"review with the id {id} is not available")

        db.delete(review)  # Chờ xóa đối tượng
        db.commit()  # Chờ hoàn tất việc commit
        return {"detail": "review deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error deleting review: {str(e)}")

async def add_images_to_review(db: Session, images: list[UploadFile], review_id: int):
    local_filenames = []
    imageHandler = ImageHandler()

    for image in images:

        img_file_name = ImageHandler.save_image(image=image, file_location=f"travel-image/reviews/{review_id}.png")
        print(img_file_name)
        try:
            # Tạo đối tượng Image mới
            img = models.Image(
                review_id=review_id
            )
            db.add(img)  # Thêm vào session
            db.commit()  # Lưu lại để lấy id của image                        
            db.refresh(img)  # Làm mới đối tượng để lấy id

            # Tải lên hình ảnh lên Azure
            blob_name = f"reviews/{review_id}/{img.id}.png"  # Tên blob
            await imageHandler.upload_to_azure(img_file_name, blob_name)  # Tải lên Azure

            # Lấy URL hình ảnh từ Azure
            url = imageHandler.get_image_url(blob_name_prefix=f"reviews/{review_id}", img_file_name=f"{img.id}.png")
            
            # Gán URL cho đối tượng hình ảnh
            img.url = url
            db.add(img)  # Thêm lại vào session
            db.commit()  # Lưu lại
            db.refresh(img)  # Làm mới đối tượng
                
        except Exception as e:
            print(f"Could not process image {img_file_name}: {e}")
    
    return {"status": "success", "review_id": review_id}