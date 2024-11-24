from datetime import date
from fastapi import APIRouter, Body, HTTPException, UploadFile
from .. import database, schemas, models
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status
from ..repository import review, image
from typing import List, Optional


router = APIRouter(
    prefix="/review",
    tags=['Review']
)

get_db = database.get_db

@router.post("/")
async def create_by_userId_destinationId(
    title :str,
    content :str, 
    rating : float, 
    user_id: int,
    destination_id: int, 
    language: str,
    companion: str, 
    date_create: date = date.today(),
    
    images: list[UploadFile] = [],
    db: Session = Depends(get_db)):
    
    sh_review= schemas.Review(
        title = title,
        content = content,
        rating = rating,
        date_create = date_create,
        language = language,
        companion=companion,
        )
    new_review = review.create_by_userId_destinationId(user_id, destination_id, sh_review, db)    
    for img in images:
        sc_image = schemas.Image(
            review_id = new_review.id
        )
        await image.create_image(db, request=sc_image, image=img)
    
    return schemas.ShowReview.from_orm(new_review)

@router.put("/{id}", response_model=schemas.ShowReview)
async def update_review_by_id(
    id: int,
    new_images: Optional[List[UploadFile]] = [],  # Ảnh mới
    image_ids_to_remove: Optional[List[int]] = Body([]),  # Danh sách ID ảnh cần xóa

    title :str = None,
    content :str = None,
    rating : float = None,
    language: str = None,
    companion: str = None,

    date_create : date = date.today(),
    db: Session = Depends(get_db)):
    
    sh_review= schemas.Review(
        title = title,
        content = content,
        rating = rating,
        date_create = date_create,
        language = language,
        companion=companion,

        )
    
    new_review = review.update_by_id(id=id, request = sh_review, db = db)
    #delete images_to_remove
    for img_id in image_ids_to_remove:
        await image.delete_image(db=db,id=img_id )
        
    #add new images
    for img in new_images:
        sc_image = schemas.Image(
            review_id = id
        )
        await image.create_image(db, request=sc_image, image=img)
        
    return new_review

@router.delete("/{id}")
async def delete_review_by_id(id: int, db: Session = Depends(get_db)):
    return await review.delete_by_id(id, db)


@router.get("/{id}")
def get_by_id(
    review_id: int = None,
    db: Session = Depends(get_db)
):
    rv = review.get_by_id(review_id, db)
    return schemas.ShowReview.from_orm(rv)

@router.get("/", 
            description= "Fill destination_id : get all review about 1 destination; Fill both user_id and destination_id: get all review of 1 user about 1 destination")
def get_reviews(
    destination_id: int = None,
    user_id: int = None,
    language: str = None,
    companion: str = None,
    db: Session = Depends(get_db)
):

    if destination_id:
        if user_id:
            reviews = review.get_reviews_of_user_in_1_destination_by_userId_and_destinationID(destination_id, user_id, db)
        else:
            reviews = review.get_reviews_of_destination_by_destinationId(destination_id, db)
        
        results = []
        for item in reviews:
            if (language is None or item.language == language) and (companion is None or item.companion == companion):
                results.append(item)

        return [schemas.ShowReview.from_orm(rv).dict() for rv in results]
                

    raise HTTPException(status_code=400, detail="You must provide destination_id, or both user_id and destination_id.")

