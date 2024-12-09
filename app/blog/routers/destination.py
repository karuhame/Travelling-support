from datetime import date, time
from typing import List, Optional
from fastapi import APIRouter, Body, File, HTTPException, Path, Query, UploadFile
from .. import database, schemas, models
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status
from ..repository import destination, user,image
from ..oauth2 import authorize_action
router = APIRouter(
    prefix="/destination",
    tags=['Destination']
)

get_db = database.get_db

@router.get("/by_tags")
def get_by_tag_lists(
    tag_ids: list[int] = Query([], description="List of tag IDs"),
    db: Session = Depends(get_db)
):
    dests = destination.get_by_tags(db=db, tag_ids = tag_ids)
    
    final_results = []
    for dest in dests:
        result = schemas.ShowDestination.from_orm(dest).dict()
        rating_info = destination.get_ratings_and_reviews_number_of_destinationID(dest.id, db)
        result.update({
            "rating": rating_info["ratings"],
            "numOfReviews": rating_info["numberOfReviews"]
        })
        final_results.append(result)

    return final_results


@router.post("/",
             )
async def create_destination(
    images: Optional[List[UploadFile]] = [],
    
    user_id: int = None,
    name: str = None,
    price_bottom: int = None,
    price_top: int = None,
    age: int = None,
    opentime: time = None,
    duration: int = None,
    description: Optional[str] = None,
    date_create: date = date.today(),
    
    #address
    district: str = None,
    street: str = None,
    ward: str = None,
    city_id: int = None,
    db: Session = Depends(get_db),
    _ = Depends(authorize_action(action_name='CREAT_DESTINATION')),
    
    
):
    address = schemas.Address(
        district=district,
        street=street,
        ward=ward,
        city_id=city_id,
    )
    
    sh_destination = schemas.Destination(
        user_id=user_id,
        name=name,
        price_bottom=price_bottom,
        price_top=price_top,
        date_create=date_create,
        age=age,
        opentime=opentime,
        duration=duration,
        description=description
    )
    
    new_dest = destination.create(sh_destination, db)
    new_dest = destination.create_address_of_destination(db=db, destination=new_dest, address=address)
    print(new_dest.user_id)
    for img in images:
        sc_image = schemas.Image(
            destination_id = new_dest.id
        )
        await image.create_image(db, request=sc_image, image=img)
    
    
    return schemas.ShowDestination.from_orm(new_dest)

@router.put("/{id}", response_model=schemas.ShowDestination)
async def update_destination_by_id(
    id: int,
    new_images: Optional[List[UploadFile]] = [],  # Ảnh mới
    image_ids_to_remove: Optional[List[int]] = Body([]),  # Danh sách ID ảnh cần xóa
    
    user_id: int = None,
    name: str = None,
    price_bottom: int = None,
    price_top: int = None,
    age: int = None,
    opentime: time = None,
    duration: int = None,
    description: Optional[str] = None,
    date_create: date = date.today(),
    
    #address
    district: str = None,
    street: str = None,
    ward: str = None,
    city_id: int = None,
    db: Session = Depends(get_db),
    
):
    address = schemas.Address(
        district=district,
        street=street,
        ward=ward,
        city_id=city_id,
    )
    
    sh_destination = schemas.Destination(
        user_id=user_id,
        name=name,
        price_bottom=price_bottom,
        price_top=price_top,
        date_create=date_create,
        age=age,
        opentime=opentime,
        duration=duration,
        description=description
    )

    new_dest = destination.update_by_id(id, sh_destination, db)
    new_dest = destination.create_address_of_destination(db=db, destination=new_dest, address=address)
    
    #delete images_to_remove
    for img_id in image_ids_to_remove:
        await image.delete_image(db=db,id=img_id )
        
    #add new images
    for img in new_images:
        sc_image = schemas.Image(
            destination_id = new_dest.id
        )
        await image.create_image(db, request=sc_image, image=img)
    
    
    return schemas.ShowDestination.from_orm(new_dest)

@router.get("/{id}")
def get_destination_by_id(
    id: int = None,    
    db: Session = Depends(get_db)
):
    dest = destination.get_by_id(id, db)
    if not dest:
        return {"error": "Destination not found"}
    result = schemas.ShowDestination.from_orm(dest).dict()
    rating_info = destination.get_ratings_and_reviews_number_of_destinationID(dest.id, db)
    result.update({
        "rating": rating_info["ratings"],
        "numOfReviews": rating_info["numberOfReviews"]
    })
    return result


@router.get("/")
def get_destination(
    city_id: int = None,
    user_id: int = None,
    is_popular: bool = False,
    get_rating: bool = False,
    db: Session = Depends(get_db),
    # _ = Depends(authorize_action(action_name='SHOW_DESTINATION')),
):
    results = []

    if user_id: 
        results = destination.get_by_userID(user_id=user_id, db=db)

    else:
        results = destination.get_all(db)
    
    if city_id:
        results = destination.get_by_city_id(city_id, db)

    # Nếu không có id hay city_id, lấy tất cả destinations

    # Nếu cần sắp xếp theo đánh giá
    if is_popular:
        results = destination.sorting_by_ratings_and_quantity_of_reviews(destinations=results, db=db)

    # Chuyển đổi các kết quả sang định dạng mong muốn
    final_results = []
    for dest in results:
        result = schemas.ShowDestination.from_orm(dest).dict()
        if get_rating:
            rating_info = destination.get_ratings_and_reviews_number_of_destinationID(dest.id, db)
            result.update({
                "rating": rating_info["ratings"],
                "numOfReviews": rating_info["numberOfReviews"]
            })
        final_results.append(result)

    return final_results




@router.get('/{destination_id}/like_count', response_model=int)
def get_destination_like_count(destination_id: int, db: Session = Depends(get_db)):
    return destination.get_like_count(destination_id, db)


@router.get("/{id}/get_tags_byid")
def get_destination_by_id(
    id: int = None,    
    db: Session = Depends(get_db)
):
    dest = destination.get_tags_by_id(id, db)
    if not dest:
        return {"error": "Destination not found"}
    return dest



@router.get("/top", response_model=List[schemas.Destination])
def get_top_destinations(
    limit: int = 10, 
    min_reviews: int = 3,
    db: Session = Depends(get_db)
):
    """Get top destinations sorted by popularity score"""
    return destination.get_top_destinations(db, limit, min_reviews)

@router.get("/by-rating", response_model=List[schemas.Destination])
def get_destinations_by_rating(
    min_rating: float = 0,
    max_rating: float = 5,
    min_reviews: int = 2,
    db: Session = Depends(get_db)
):
    """Get destinations filtered by rating range"""
    return destination.get_destinations_by_rating_range(
        db, 
        min_rating, 
        max_rating, 
        min_reviews
    )

@router.get("/{destination_id}/stats", response_model=schemas.DestinationStats)
def get_destination_statistics(
    destination_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed statistics for a specific destination"""
    return destination.get_destination_stats(db, destination_id)


@router.get("/top-destinations/{tag_id}")
def get_top_destinations(
    tag_id: int,
    limit: int = Query(default=5, ge=1, le=100),  # Mặc định lấy 5 destinations, giới hạn từ 1-100
    db: Session = Depends(get_db)
):
    return destination.get_top_destinations_by_tag(db, tag_id, limit)


@router.get("/top-destination-ids/{tag_id}")
def get_top_destination_ids(
    tag_id: int,
    limit: int = Query(default=5, ge=1, le=100),  # Số lượng kết quả (mặc định là 5)
    db: Session = Depends(get_db)
):
    return destination.get_top_destination_ids_by_tag(db, tag_id, limit)


@router.get('/recommendations_bylikes/{user_id}')
def get_recommendations(
    user_id: int, 
    city_id: Optional[int] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    return destination.get_recommended_destinations(user_id, db, city_id, limit)

async def delete_destination_by_id(id: int, db: Session = Depends(get_db)):
    return await destination.delete_by_id(id, db)

# @router.post("/uploadfiles/")
# async def upload_files(files: List[UploadFile] = None):
#     if not files:
#         return {"message": "No files uploaded."}
    
#     file_names = [file.filename for file in files]
#     return {"file_names": file_names}
