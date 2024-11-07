from datetime import date, time
from typing import List, Optional
from fastapi import APIRouter, Body, HTTPException, Path, Query, UploadFile
from .. import database, schemas, models
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status
from ..repository import destination

router = APIRouter(
    prefix="/destination",
    tags=['Destination']
)

get_db = database.get_db

@router.post("/",
             )
async def create_destination(
    images: List[UploadFile],
    
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
    await destination.add_images_to_destination(db, images=images, destination_id=new_dest.id)
    
    return schemas.ShowDestination.from_orm(new_dest)

@router.put("/{id}", response_model=schemas.ShowDestination)
async def update_destination_by_id(
    id: int,
    images: List[UploadFile],
    
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
    await destination.add_images_to_destination(db, images=images, destination_id=new_dest.id)
    
    return schemas.ShowDestination.from_orm(new_dest)


@router.get("/popular/{city_id}")
def get_popular_destination_by_cityID(city_id: int, db: Session = Depends(get_db)):
    return destination.get_popular_destinations_by_city_ID(city_id=city_id, db=db)

@router.get("/")
def get_destination(
    id: int = None,
    city_id: int = None,
    
    sort_by_reviews: bool = False,
    get_rating: bool = False,
    db: Session = Depends(get_db)
):
    results = []

    # Nếu có id, lấy destination theo ID
    if id:
        dest = destination.get_by_id(id, db)
        if not dest:
            return {"error": "Destination not found"}
        results.append(dest)

    # Nếu có city_id, lấy destinations theo city_id
    elif city_id:
        results = destination.get_by_city_id(city_id, db)

    # Nếu không có id hay city_id, lấy tất cả destinations
    else:
        results = destination.get_all(db)

    # Nếu cần sắp xếp theo đánh giá
    if sort_by_reviews:
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
def delete_destination_by_id(id: int, db: Session = Depends(get_db)):
    return destination.delete_by_id(id, db)
    