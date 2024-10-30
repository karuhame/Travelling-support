from fastapi import APIRouter, HTTPException
from .. import database, schemas, models
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status
from ..repository import review
from typing import List


router = APIRouter(
    prefix="/review",
    tags=['Review']
)

get_db = database.get_db


@router.post("/", response_model=schemas.ShowReview)
def create_by_userId_destinationId(request: schemas.Review, user_id: int, destination_id: int, db: Session = Depends(get_db)):
    return review.create_by_cityID(user_id, destination_id, request, db)

# @router.get("/{id}", response_model=schemas.ShowReview)
# def get_review_by_id(id: int, db: Session = Depends(get_db)):
#     return review.get_by_id(id, db)

# @router.get("/reviews_of_destination/", response_model=List[schemas.ShowReview])
# def get_reviews_of_destination_by_destinationId(destination_id: int, db: Session = Depends(get_db)):
#     return review.get_reviews_of_destination_by_destinationId(destination_id, db)

# @router.get("/reviews_of_user_in_destination/", response_model=List[schemas.ShowReview])
# def get_reviews_of_user_in_1_destination_by_userId_and_destinationID(destination_id: int, user_id:int,  db: Session = Depends(get_db)):
#     return review.get_reviews_of_user_in_1_destination_by_userId_and_destinationID(destination_id, user_id, db)


@router.put("/{id}", response_model=schemas.ShowReview)
def update_review_by_id(id: int, request: schemas.Review, db: Session = Depends(get_db)):
    return review.update_by_id(id, request, db)

@router.delete("/{id}")
def delete_review_by_id(id: int, db: Session = Depends(get_db)):
    return review.delete_by_id(id, db)

@router.get("/")
def get_reviews(
    review_id: int = None,
    destination_id: int = None,
    user_id: int = None,
    db: Session = Depends(get_db)
):
    if review_id:
        rv = review.get_by_id(review_id, db)
        return schemas.ShowReview.from_orm(rv)

    if destination_id:
        if user_id:
            reviews = review.get_reviews_of_user_in_1_destination_by_userId_and_destinationID(destination_id, user_id, db)
        else:
            reviews = review.get_reviews_of_destination_by_destinationId(destination_id, db)
        
        return [schemas.ShowReview.from_orm(rv).dict() for rv in reviews]

    raise HTTPException(status_code=400, detail="You must provide either review_id, destination_id, or both user_id and destination_id.")