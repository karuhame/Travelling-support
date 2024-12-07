import math
from typing import List, Optional
from sqlalchemy import func,desc
from sqlalchemy.orm import Session
from blog import models, schemas
from fastapi import HTTPException, UploadFile, status
from blog.hashing import Hash
import blog.repository.user as user
from datetime import datetime
from typing import List
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

# def create(request, db: Session):
#     try:
#         # Tạo điểm đến mới
#         new_destination = models.Destination(
#             name=request.name,
#             price_bottom=request.price_bottom,
#             price_top=request.price_top,
#             date_create=request.date_create,
#             age=request.age,
#             opentime=request.opentime,
#             duration=request.duration,
#             description=request.description

#         )
        
#         # Thêm điểm đến vào cơ sở dữ liệu
#         db.add(new_destination)
#         db.commit()  # Commit để lưu điểm đến
#         db.refresh(new_destination)  # Làm mới đối tượng mới

#         return new_destination
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                             detail=f"Error creating destination: {str(e)}")

def create(request, db: Session):
    try:
        new_destination = models.Destination(
            user_id = request.user_id,
            name=request.name,
            price_bottom=request.price_bottom,
            price_top=request.price_top,
            date_create=request.date_create,
            age=request.age,
            opentime=request.opentime,
            duration=request.duration,
            description=request.description,
            average_rating=0.0,
            review_count=0,
            popularity_score=0.0
        )
        
        db.add(new_destination)
        db.commit()
        db.refresh(new_destination)
        return new_destination
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail=f"Error creating destination: {str(e)}")
    
def get_by_userID(user_id: int, db: Session):
    try:
        destination = db.query(models.Destination).filter(models.Destination.user_id == user_id).all()
        return destination
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error retrieving destination: {str(e)}")    
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
    
def get_tags_by_id(id: int, db: Session):
    try:
        destination = db.query(models.Destination).filter(models.Destination.id == id).first()  
        if not destination:
            return None
        return {"tags": destination.tags}
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

        destination.user_id=request.user_id,
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



def get_like_count(destination_id: int, db: Session) -> int:
    return db.query(models.UserDestinationLike).filter_by(destination_id=destination_id).count()




def calculate_popularity_score(avg_rating: float, review_count: int) -> float:
    if review_count == 0:
        return 0
    return avg_rating * math.log(1 + review_count)


def update_destination_rating(destination_id: int, db: Session):
    try:
        rating_stats = db.query(
            func.avg(models.Review.rating).label('avg_rating'),
            func.count(models.Review.id).label('review_count')
        ).filter(
            models.Review.destination_id == destination_id
        ).first()

        destination = db.query(models.Destination).filter(
            models.Destination.id == destination_id
        ).first()

        if not destination:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Destination not found"
            )

        destination.average_rating = rating_stats.avg_rating or 0
        destination.review_count = rating_stats.review_count or 0
        destination.popularity_score = calculate_popularity_score(
            destination.average_rating,
            destination.review_count
        )

        db.commit()
        return destination

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating destination rating: {str(e)}"
        )
    
def update_all_destination_ratings(db: Session):
    try:
        # Get all destination IDs
        destinations = db.query(models.Destination.id).all()
        
        # Update ratings for each destination
        for dest_id in destinations:
            update_destination_rating(dest_id[0], db)
            
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating all destination ratings: {str(e)}"
        )

def get_top_destinations(db: Session, limit: int = 10, min_reviews: int = 3):
    try:
        return db.query(models.Destination).filter(
            models.Destination.review_count >= min_reviews
        ).order_by(
            desc(models.Destination.popularity_score)
        ).limit(limit).all()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching top destinations: {str(e)}"
        )
    

def get_destinations_by_rating_range(
    db: Session, 
    min_rating: float = 0, 
    max_rating: float = 5,
    min_reviews: int = 2
):
    try:
        return db.query(models.Destination).filter(
            models.Destination.average_rating >= min_rating,
            models.Destination.average_rating <= max_rating,
            models.Destination.review_count >= min_reviews
        ).order_by(
            desc(models.Destination.popularity_score)
        ).all()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching destinations by rating: {str(e)}"
        )
    
def get_destination_stats(db: Session, destination_id: int):
    """Lấy thống kê chi tiết về rating của một destination"""
    try:
        destination = db.query(models.Destination)\
                       .filter(models.Destination.id == destination_id)\
                       .first()
        if not destination:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Destination {destination_id} not found"
            )
            
        return {
            "destination_id": destination_id,
            "name": destination.name,
            "average_rating": destination.average_rating,
            "review_count": destination.review_count,
            "popularity_score": destination.popularity_score
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching destination stats: {str(e)}"
        )
def get_top_destinations_by_tag(
    db: Session, 
    tag_id: int, 
    limit: int, 
    city_id: Optional[int] = None
) -> List[models.Destination]:
    try:
        # Base query
        query = (
            db.query(models.Destination)
            .join(models.DestinationTag)
            .join(models.Address)  # Join với Address
            .filter(models.DestinationTag.tag_id == tag_id)
        )

        # Thêm filter city_id nếu được chỉ định
        if city_id is not None:
            query = query.filter(models.Address.city_id == city_id)

        # Thực hiện query
        top_destinations = (
            query
            .order_by(desc(models.Destination.popularity_score))
            .limit(limit)
            .all()
        )

        if not top_destinations:
            print(f"No destinations found with tag_id {tag_id}" + 
                  f" and city_id {city_id}" if city_id else "")
            return []  # Trả về list rỗng thay vì raise exception

        return top_destinations

    except Exception as e:
        print(f"Error in get_top_destinations_by_tag: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving top destinations: {str(e)}"
        )


def get_top_destination_ids_by_tag(
    db: Session, 
    tag_id: int, 
    limit: int, 
    city_id: Optional[int] = None
) -> List[int]:
    try:
        # Base query
        query = (
            db.query(models.Destination.id)
            .join(models.DestinationTag)
            .join(models.Address)  # Join với Address
            .filter(models.DestinationTag.tag_id == tag_id)
        )

        # Thêm filter city_id nếu được chỉ định
        if city_id is not None:
            query = query.filter(models.Address.city_id == city_id)

        # Thực hiện query
        top_destination_ids = (
            query
            .order_by(desc(models.Destination.popularity_score))
            .limit(limit)
            .all()
        )

        # Convert kết quả từ list of tuples thành list of integers
        return [dest.id for dest in top_destination_ids]

    except Exception as e:
        print(f"Error in get_top_destination_ids_by_tag: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving top destination ids: {str(e)}"
        )

def get_recommended_destinations(user_id: int, db: Session, city_id: Optional[int] = None, limit: int = 20):
    try:
        # 1. Lấy số lượng mỗi tag từ các destination user đã like
        tag_counts = user.count_tags_for_user(user_id, db)
        print(f"\n1. Tag counts from user's liked destinations: {tag_counts}")
        
        if not tag_counts:
            popular_destinations = get_popular_destinations_by_city_ID(city_id, db) if city_id else get_popular_destinations_by_city_ID(None, db)
            result = [dest["id"] for dest in popular_destinations[:limit]]
            print(f"\nNo tags found - Returning popular destinations: {result}")
            return result
            
        # 2. Tính toán tỷ lệ cho mỗi tag
        total_tags = sum(tag_counts.values())
        tag_proportions = {
            tag_id: int((count/total_tags) * limit)
            for tag_id, count in tag_counts.items()
        }
        print(f"\n2. Distribution of recommendations per tag: {tag_proportions}")
        print(f"Total recommendations planned: {sum(tag_proportions.values())}")

        # 3. Lấy danh sách destination_ids đã được like
        liked_destinations = set(user.get_liked_destinations(user_id, db))
        print(f"\n3. User's liked destinations: {liked_destinations}")
        
        # 4. Xây dựng recommendations cho từng tag
        recommended_destinations = set()
        remaining_slots = limit
        
        # Sắp xếp tags theo tần suất giảm dần
        sorted_tags = sorted(tag_proportions.items(), key=lambda x: x[1], reverse=True)
        print(f"\n4. Tags sorted by frequency: {sorted_tags}")
        
        for tag_id, proportion in sorted_tags:
            if remaining_slots <= 0:
                break
                
            print(f"\nProcessing tag_id: {tag_id}, target proportion: {proportion}")
            
            # Lấy top destinations cho tag hiện tại
            top_destinations = set(get_top_destinations_by_tag(db, tag_id, proportion))
            print(f"Top destinations found for tag {tag_id}: {top_destinations}")
            
            # Lọc bỏ các destinations đã recommend hoặc đã like
            new_recommendations = top_destinations - recommended_destinations - liked_destinations
            print(f"New unique recommendations: {new_recommendations}")
            
            # Thêm recommendations mới theo số lượng được phân bổ
            recommendations_to_add = list(new_recommendations)[:proportion]
            recommended_destinations.update(recommendations_to_add)
            
            remaining_slots -= len(recommendations_to_add)
            print(f"Added {len(recommendations_to_add)} destinations, remaining slots: {remaining_slots}")

        # 5. Điền các slots còn trống bằng popular destinations
        if remaining_slots > 0:
            print(f"\n5. Filling remaining {remaining_slots} slots with popular destinations")
            popular_destinations = get_popular_destinations_by_city_ID(city_id, db) if city_id else get_popular_destinations_by_city_ID(None, db)
            popular_ids = set(dest["id"] for dest in popular_destinations)
            additional_recommendations = popular_ids - recommended_destinations - liked_destinations
            final_additions = list(additional_recommendations)[:remaining_slots]
            recommended_destinations.update(final_additions)
            print(f"Added popular destinations: {final_additions}")

        final_result = list(recommended_destinations)
        print(f"\nFinal recommendations: {final_result}")
        print(f"Total recommendations: {len(final_result)}")
        
        return final_result

    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting recommendations: {str(e)}"
        )
    
def get_rating_distribution(destination_id: int, db: Session):
    try:
        # Dictionary để lưu số lượng đánh giá cho mỗi rating
        rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        # Query để đếm số lượng review cho mỗi rating
        reviews = db.query(
            func.floor(models.Review.rating).label('rating'),
            func.count().label('count')
        ).filter(
            models.Review.destination_id == destination_id,
            models.Review.rating.isnot(None)  # Loại bỏ các review không có rating
        ).group_by(
            func.floor(models.Review.rating)
        ).all()
        
        # Cập nhật số lượng vào dictionary
        for review in reviews:
            rating = int(review.rating)
            if 1 <= rating <= 5:  # Đảm bảo rating nằm trong khoảng hợp lệ
                rating_counts[rating] = review.count
                
        return rating_counts
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting rating distribution: {str(e)}"
        )