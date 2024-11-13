
from sqlalchemy.orm import Session
from blog import models, schemas
from fastapi import HTTPException, UploadFile, status
from blog.hashing import Hash
from blog.repository.image_handler import ImageHandler
from blog.repository import image

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
            detail=f"Failed to add default avatar: {str(e.detail)}"
        )
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
        print(f"Error: {str(e.detail)}")  # In ra lỗi để kiểm tra
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve user info")

def get_userInfo_by_id(db:Session, id: int):
    try:
        user_info =  db.query(models.UserInfo).filter(models.UserInfo.id == id).first()  # Chờ truy vấn
        if not user_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"UserInfo with the id {id} is not available")
        return user_info

    except HTTPException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve user info:{e.detail}")
    except Exception as e:
            # Bắt mọi lỗi khác có thể xảy ra
            print(f"Unexpected Error: {str(e.detail)}")  # In ra lỗi bất ngờ
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve user info")

def get_all(db: Session):
    try:
        user_infoes = db.query(models.UserInfo).all()  # Chờ truy vấn
        return user_infoes
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error retrieving userinfo: {str(e.detail)}")

def update_user_info(info: schemas.UserInfoBase, address: schemas.Address, id: int, db: Session):
    
    try:
        # Tìm UserInfo theo ID
        user_info = db.query(models.UserInfo).filter(models.UserInfo.id == id).first()
        if not user_info:
            print("no")
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
        print(f"Exception type: {type(e).__name__}, message: {str(e.detail)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update user info:{str(e.detail)}")
    
async def delete_user_info(id: int, db: Session):
    try:
        user_info = db.query(models.UserInfo).filter(models.UserInfo.id == id).first()  # Chờ truy vấn
        await image.delete_image(db=db,id=user_info.image.id)
        if not user_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"UserInfo with the id {id} is not available")
        db.delete(user_info)
        db.commit()
        return {"message": "UserInfo deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete user info")

