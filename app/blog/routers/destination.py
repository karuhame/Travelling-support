from datetime import date, time
from typing import List, Optional
from fastapi import APIRouter, Body, File, HTTPException, Path, Query, UploadFile
from .. import database, schemas, models
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status
from ..repository import destination, image

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
    
    is_popular: bool = False,
    get_rating: bool = False,
    db: Session = Depends(get_db)
):
    results = []
    if city_id:
        results = destination.get_by_city_id(city_id, db)

    # Nếu không có id hay city_id, lấy tất cả destinations
    else:
        results = destination.get_all(db)

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


@router.delete("/{id}")
async def delete_destination_by_id(id: int, db: Session = Depends(get_db)):
    return await destination.delete_by_id(id, db)

# @router.post("/uploadfiles/")
# async def upload_files(files: List[UploadFile] = None):
#     if not files:
#         return {"message": "No files uploaded."}
    
#     file_names = [file.filename for file in files]
#     return {"file_names": file_names}