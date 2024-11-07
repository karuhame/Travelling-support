
from sqlalchemy.orm import Session
from blog import models, schemas
from fastapi import HTTPException, UploadFile, status
from blog.hashing import Hash
from blog.repository.image import ImageHandler

async def add_default_avatar(db: Session, userInfo_id: int):
    imageHandler = ImageHandler()
    default_avatar_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSSlKZSwwbFBoiLx-hWWmEfVIZ1jADecLCEhQ&s"
    
    try:
        # Tạo đối tượng Image mới
        img = models.Image(
            userInfo_id=userInfo_id,
            url=default_avatar_url  # Sử dụng URL mặc định
        )
        db.add(img)
        db.commit()
        db.refresh(img)
        
        return img
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add default avatar: {str(e)}"
        )

async def add_image_to_userInfo(db: Session, image: UploadFile, userInfo_id: int):
    imageHandler = ImageHandler()


    img_file_name = ImageHandler.save_image(image=image, file_location=f"travel-image/userInfoes/{userInfo_id}.png")
    try:
        # Tạo đối tượng Image mới
        img = models.Image(
            userInfo_id = userInfo_id
        )
        db.add(img)  # Thêm vào session
        db.commit()  # Lưu lại để lấy id của image                        
        db.refresh(img)  # Làm mới đối tượng để lấy id

        # Tải lên hình ảnh lên Azure
        blob_name = f"userInfoes/{userInfo_id}/{img.id}.png"  # Tên blob
        await imageHandler.upload_to_azure(img_file_name, blob_name)  # Tải lên Azure

        # Lấy URL hình ảnh từ Azure
        url = imageHandler.get_image_url(blob_name_prefix=f"userInfoes/{userInfo_id}", img_file_name=f"{img.id}.png")
        
        # Gán URL cho đối tượng hình ảnh
        img.url = url
        db.add(img)  # Thêm lại vào session
        db.commit()  # Lưu lại
        db.refresh(img)  # Làm mới đối tượng
            
    except Exception as e:
        print(f"Could not process image {img_file_name}: {e}")
    
    return {"status": "success", "userInfo_id": userInfo_id}

async def update_image(db: Session, image: UploadFile, userInfo_id: int):
    imageHandler = ImageHandler()

    # Lưu hình ảnh tạm thời
    img_file_name = ImageHandler.save_image(image=image, file_location=f"travel-image/userInfoes/{userInfo_id}.png")
    try:
        # Tìm user_info theo userInfo_id
        user_info = db.query(models.UserInfo).filter(models.UserInfo.id == userInfo_id).first()
        if user_info is None:
            raise HTTPException(status_code=404, detail="UserInfo not found")

        # Kiểm tra xem user_info đã có image hay chưa
        if user_info.image is None:
            # Tạo đối tượng Image mới
            user_info.image = models.Image(
                userInfo_id=userInfo_id
            )
            db.add(user_info.image)  # Thêm vào session
            db.commit()  # Lưu lại để lấy id của image                        
            db.refresh(user_info.image)  # Làm mới đối tượng để lấy id

        # Tải lên hình ảnh lên Azure
        blob_name = f"userInfoes/{userInfo_id}/{user_info.image.id}.png"  # Tên blob
        await imageHandler.upload_to_azure(img_file_name, blob_name)  # Tải lên Azure

        # Lấy URL hình ảnh từ Azure
        url = imageHandler.get_image_url(blob_name_prefix=f"userInfoes/{userInfo_id}", img_file_name=f"{user_info.image.id}.png")
        
        print("url:" + url)
        # Gán URL cho đối tượng hình ảnh
        user_info.image.url = url
        
        # Cập nhật đối tượng image trong cơ sở dữ liệu
        db.commit()  # Lưu lại thay đổi
        db.refresh(user_info.image)  # Làm mới đối tượng
            
    except Exception as e:
        print(f"Could not process image {img_file_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Could not process image: {str(e)}")  # Trả về lỗi nếu có

    return {"status": "success", "userInfo_id": userInfo_id}
async def delete_image(db: Session, userInfo_id: int):
    imageHandler = ImageHandler()
    
    try:
        # Tìm hình ảnh liên quan đến userInfo_id
        img = db.query(models.Image).filter(models.Image.userInfo_id == userInfo_id).first()
        if not img:
            return
        # Xóa hình ảnh khỏi Azure Blob Storage
        blob_name_prefix = f"userInfoes/{userInfo_id}/{img.id}.png"
        await imageHandler.delete_image_azure(blob_name_prefix)

        # Xóa hình ảnh khỏi cơ sở dữ liệu
        db.delete(img)
        db.commit()  # Lưu lại thay đổi

    except Exception as e:
        db.rollback()  # Hoàn tác nếu có lỗi
        print(f"Could not delete image: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete image")

    return {"status": "success", "userInfo_id": userInfo_id}

def create_user_info_by_userid(info: schemas.UserInfoBase, address: schemas.Address ,user_id: int, db: Session):
    try:
        
        # Tạo địa chỉ mới
        new_address = models.Address(
            district=address.district,
            street=address.street,
            ward=address.ward,
            city_id=address.city_id  # Sử dụng city_id làm khóa ngoại
        )
        
        # Thêm địa chỉ vào cơ sở dữ liệu
        db.add(new_address)
        db.commit()  # Commit để lưu địa chỉ
        db.refresh(new_address)  # Làm mới địa chỉ để lấy ID

        new_user_info = models.UserInfo(
            description=info.description,
            phone_number=info.phone_number,
            user_id=user_id,
            address = new_address,
        )
        db.add(new_user_info)
        db.commit()
        db.refresh(new_user_info)
        return new_user_info
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user info")


def get_user_info_by_userid(user_id: int, db: Session):
    try:
        user_info = db.query(models.UserInfo).filter(models.UserInfo.user_id == user_id).first()  # Chờ truy vấn
        print(user_info.description)
        if not user_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"UserInfo with the user_id {user_id} is not available")
        return user_info
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve user info")
def get_userInfo_by_id(db:Session, id: int):
    try:
        user_info =  db.query(models.UserInfo).filter(models.UserInfo.id == id).first()  # Chờ truy vấn
        if not user_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"UserInfo with the id {id} is not available")
        return user_info
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve user info")

def get_all(db: Session):
    try:
        user_infoes = db.query(models.UserInfo).all()  # Chờ truy vấn
        return user_infoes
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error retrieving userinfo: {str(e)}")

def update_user_info(info: schemas.UserInfoBase, address: schemas.Address, id: int, db: Session):
    
    try:
        # Tìm UserInfo theo ID
        user_info = db.query(models.UserInfo).filter(models.UserInfo.id == id).first()
        if not user_info:
            raise HTTPException(status_code=404, detail="UserInfo not found")

        # Cập nhật thông tin UserInfo
        user_info.description = info.description
        user_info.phone_number = info.phone_number

        # Cập nhật địa chỉ trực tiếp thông qua user_info
        if user_info.address:
            user_info.address.district = address.district
            user_info.address.street = address.street
            user_info.address.ward = address.ward
            user_info.address.city_id = address.city_id
        else:
            # Nếu không có địa chỉ, tạo địa chỉ mới và liên kết
            new_address = models.Address(
                district=address.district,
                street=address.street,
                ward=address.ward,
                city_id=address.city_id
            )
            db.add(new_address)
            db.commit()  # Commit để lưu địa chỉ
            db.refresh(new_address)  # Làm mới địa chỉ để lấy ID
            user_info.address = new_address  # Gán địa chỉ mới cho user_info

        # Lưu lại thay đổi
        db.commit()
        db.refresh(user_info)  # Làm mới đối tượng để lấy dữ liệu mới

        return user_info
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update user info")
    
def delete_user_info(id: int, db: Session):
    try:
        delete_image(db=db,userInfo_id=id)
        user_info = db.query(models.UserInfo).filter(models.UserInfo.id == id).first()  # Chờ truy vấn
        if not user_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"UserInfo with the id {id} is not available")
        db.delete(user_info)
        db.commit()
        return {"message": "UserInfo deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete user info")
