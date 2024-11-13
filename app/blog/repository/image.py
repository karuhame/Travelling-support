from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from blog import models, schemas
from blog.repository.image_handler import ImageHandler  # Giả sử bạn đã định nghĩa ImageHandler như trước

image_handler = ImageHandler()
async def create_image(db: Session, request: schemas.Image, image: UploadFile):
    # Kiểm tra ít nhất một ID được cung cấp
    if not (request.city_id or request.destination_id or request.review_id or request.userInfo_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="At least one of city_id, destination_id, or review_id must be provided.")

    try:
        db_image = models.Image()
        blob_name_prefix = ""
        if request.city_id:
            db_image.city_id = request.city_id
            blob_name_prefix += "cities"
        elif request.destination_id: 
            db_image.destination_id = request.destination_id
            blob_name_prefix += "destinations"
        elif request.review_id: 
            db_image.review_id = request.review_id
            blob_name_prefix += "reviews"
        elif request.userInfo_id: 
            db_image.userInfo_id = request.userInfo_id
            blob_name_prefix += "userInfoes"
            
            
        db.add(db_image)
        db.commit()
        db.refresh(db_image)

        # Tải ảnh lên Azure Blob Storage
        img_file_name = ImageHandler.save_image(image=image, file_location=f"travel-image/download.png")
        db_image.blob_name = blob_name_prefix + f"/{db_image.id}.png"
        
        await image_handler.upload_to_azure(img_file_name, blob_name_prefix=db_image.blob_name)  # Tải lên từ URL
        # Lấy URL của ảnh từ Azure Blob Storage
        url = image_handler.get_image_url(blob_name_prefix, img_file_name=f"{db_image.id}.png")
        db_image.url = url  # Cập nhật URL cho đối tượng ảnh

        db.add(db_image)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error creating image: {str(e.detail)}")

    return db_image


async def delete_image(db: Session, id: int):
    db_image = db.query(models.Image).filter(models.Image.id == id).first()
    if db_image:
        # Xóa ảnh khỏi Azure Blob Storage
        await image_handler.delete_image_azure(db_image.blob_name)

        db.delete(db_image)
        db.commit()
        return True
    return False

async def update_image(db: Session, id: int, image_inp : UploadFile):
    try:
        print(image_inp)
        db_image = db.query(models.Image).filter(models.Image.id == id).first()

        # Tải ảnh lên Azure Blob Storage
        img_file_name = ImageHandler.save_image(image=image_inp, file_location=f"travel-image/download.png")
        
        await image_handler.upload_to_azure(img_file_name, blob_name_prefix=db_image.blob_name)  # Tải lên từ URL
        db.add(db_image)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error creating image: {str(e)}")

    return db_image
