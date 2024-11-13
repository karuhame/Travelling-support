from typing import List
from sqlalchemy import func
from sqlalchemy.orm import Session
from blog import models, schemas
from fastapi import HTTPException, UploadFile, status
from blog.hashing import Hash
from blog.repository.image_handler import ImageHandler
from blog.repository import image

def create_address_of_destination(db: Session, destination: models.Destination, address):
    try:
        if not destination.address: 
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
            destination.address_id = new_address.id
        else:
            destination.address.district = address.district
            destination.address.street = address.street
            destination.address.ward = address.ward
            destination.address.city_id = address.city_id
        # Tạo điểm đến mới
        
        # Thêm điểm đến vào cơ sở dữ liệu
        db.add(destination)
        db.commit()  # Commit để lưu điểm đến
        db.refresh(destination)  # Làm mới đối tượng mới

        return destination
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error creating address: {str(e)}")

def create(request, db: Session):
    try:
        # Tạo điểm đến mới
        new_destination = models.Destination(
            name=request.name,
            price_bottom=request.price_bottom,
            price_top=request.price_top,
            date_create=request.date_create,
            age=request.age,
            opentime=request.opentime,
            duration=request.duration,
            description=request.description

        )
        
        # Thêm điểm đến vào cơ sở dữ liệu
        db.add(new_destination)
        db.commit()  # Commit để lưu điểm đến
        db.refresh(new_destination)  # Làm mới đối tượng mới

        return new_destination
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error creating destination: {str(e)}")
def get_by_id(id: int, db: Session):
    try:
        destination = db.query(models.Destination).filter(models.Destination.id == id).first()
        # if not destination:
        #     return {"detail": "Không tìm thấy điểm đến."}

        # # Chuyển đổi hình ảnh thành ShowImage
        # images = [schemas.ShowImage.from_orm(img) for img in destination.images] if destination.images else None

        # # Tạo từ điển cho dữ liệu điểm đến
        # destination_data = {
        #     "id": destination.id,
        #     "name": destination.name,
        #     "address": destination.address,
        #     "price_bottom": destination.price_bottom,
        #     "price_top": destination.price_top,
        #     "date_create": destination.date_create,
        #     "age": destination.age,
        #     "opentime": destination.opentime,
        #     "duration": destination.duration,
        #     "images": images
        # }

        # # Trả về ShowDestination đã được xác thực
        # return schemas.ShowDestination(**destination_data)
        return destination
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error retrieving destination: {str(e)}")

def get_by_city_id(city_id: int, db: Session):
    try:
        destinations = db.query(models.Destination).join(models.Address).filter(models.Address.city_id == city_id).all()
        
        if not destinations:
            return {"detail": "No destinations found for the specified city ID."}

        results = []
        
        for dest in destinations:
            # Chuyển đổi danh sách các đối tượng Image thành ImageSchema, xử lý trường hợp không có ảnh
            dest = get_by_id(dest.id, db)
            
            results.append(dest)

        return results
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error retrieving destinations: {str(e)}")

def get_all(db: Session):
    try:
        destinations = db.query(models.Destination).all()  # Chờ truy vấn
        return destinations
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error retrieving destinations: {str(e)}")
def sorting_by_ratings_and_quantity_of_reviews(destinations: List[models.Destination], db: Session):
    try:
        # Tạo danh sách để lưu trữ thông tin điểm đến cùng với điểm số và số lượng đánh giá
        destination_scores = []

        for destination in destinations:
            # Sử dụng hàm get_ratings_and_reviews_of_destination để tính điểm số
            review_data = get_ratings_and_reviews_number_of_destinationID(destination.id, db)

            # Sử dụng điểm số tính toán từ hàm get_ratings_and_reviews_of_destination
            point = review_data["numberOfReviews"] * (review_data["ratings"] ** 2)

            destination_scores.append({
                "destination": destination,
                "total_point": point
            })

        # Sắp xếp danh sách theo total_point từ cao xuống thấp
        destination_scores.sort(key=lambda x: x['total_point'], reverse=True)

        # Trả về danh sách các đối tượng Destination đã sắp xếp
        sorted_destinations = [item["destination"] for item in destination_scores]
        return sorted_destinations

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error sorting destinations: {str(e)}")
        
def update_by_id(id: int, request: schemas.Destination, db: Session):
    try:
        destination = db.query(models.Destination).filter(models.Destination.id == id).first()  # Chờ truy vấn
        if not destination:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"destination with the id {id} is not available")

        destination.name =request.name
        destination.price_bottom =request.price_bottom
        destination.price_top =request.price_top
        destination.date_create =request.date_create
        destination.age =request.age
        destination.opentime =request.opentime
        destination.duration =request.duration
        destination.description=request.description

        
        # Thêm điểm đến vào cơ sở dữ liệu
        db.commit()  # Commit để lưu điểm đến
        db.refresh(destination)  # Làm mới đối tượng mới

        return destination 
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error updating destination: {str(e)}")

async def delete_by_id(id: int, db: Session):
    try:
        destination = db.query(models.Destination).filter(models.Destination.id == id).first()  # Chờ truy vấn
        for img in destination.images:
            await image.delete_image(db=db, id=img.id)
        if not destination:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"destination with the id {id} is not available")

        db.delete(destination)  # Chờ xóa đối tượng
        db.commit()  # Chờ hoàn tất việc commit
        return {"detail": "destination deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error deleting destination: {str(e)}")

def get_ratings_and_reviews_number_of_destinationID(destination_id: int, db: Session):
    # Lấy ra tất cả các rating cho destination_id cụ thể
    ratings = db.query(models.Review.rating).filter(models.Review.destination_id == destination_id).all()
    
    if ratings:
        # Chuyển đổi từ danh sách tuple thành danh sách rating
        ratings_list = [rating[0] for rating in ratings]

        # Tính tổng số điểm và số lượng đánh giá
        total_ratings = sum(ratings_list)
        quantity_of_reviews = len(ratings_list)
        average_rating = total_ratings / quantity_of_reviews

        # Tính điểm theo công thức
        point = (average_rating * 10)

        return {
            "ratings": average_rating,
            "numberOfReviews": quantity_of_reviews
        }
    else:
        return {
            "ratings": 0,
            "numberOfReviews": 0
        }

def get_popular_destinations_by_city_ID(city_id: int, db: Session):
    # Truy vấn để lấy danh sách các điểm đến phổ biến
    popular_destinations = (
        db.query(models.Destination)
        .outerjoin(models.Review, models.Destination.id == models.Review.destination_id)  # Kết hợp với bảng Review
        .filter(models.Destination.address.has(city_id=city_id))  # Lọc theo city_id
        .group_by(models.Destination.id)  # Nhóm theo id của Destination
        .having(func.avg(models.Review.rating) >= 4.5)  # Điều kiện xếp hạng
        .having(func.count(models.Review.id) >= 1000)  # Điều kiện số lượng đánh giá
        .all()
    )

    # Tạo danh sách chứa thông tin các điểm đến
    destination_list = []
    for destination in popular_destinations:
        # Lấy thông tin địa chỉ
        address = destination.address
        location = f"{address.street}, {address.district}, {address.city.name}, Vietnam" if address else "Unknown Location"

        # Lấy tất cả hình ảnh liên quan đến điểm đến
        images = db.query(models.Image).filter(models.Image.destination_id == destination.id).limit(5).all()  # Lấy tối đa 5 hình ảnh
        image_urls = [image.url for image in images]

        # Tính tổng số lượng đánh giá
        num_of_reviews = len(destination.reviews)

        # Tạo từ điển với thông tin điểm đến
        destination_info = {
            "id": destination.id,
            "name": destination.name,
            "category": "popular",
            "image": image_urls,
            "location": location,
            "review": num_of_reviews,
            "price": destination.price_bottom,  

            "description": destination.description,  
            "rate": func.avg(models.Review.rating)  
        }

        destination_list.append(destination_info)

    return destination_list

def search_by_name(db: Session,text : str):
    try:
        dest = db.query(models.Destination).filter(models.Destination.name.ilike(f"%{text}%")).all()
        return dest
    except Exception as e:
        db.rollback()
        print(f"Error detail: {e}")
        
        

def get_by_tags(db:Session, tag_ids = list[int]):
    try: 
        dests = db.query(models.Destination).join(models.DestinationTag).filter(models.DestinationTag.tag_id.in_(tag_ids)).all()
        return dests
    except Exception as e:
        # Bắt các lỗi khác
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
