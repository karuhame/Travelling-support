from typing import List
from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from .. import database, schemas, models
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status
from ..repository import tour, image

router = APIRouter(
    prefix="/tour",
    tags=['Tour']
)

get_db = database.get_db

@router.post("/")
def create_tour(
    tour_data: schemas.Tour,
    # images: list[UploadFile] = File(...),  # Nhận danh sách các tệp ản
    db: Session = Depends(get_db)):
    
    
    return tour.create(request=tour_data, db=db)

@router.post("/img")
def create_tour(
    name: str,
    description: str,
    user_id: int,
    city_id: int,
    destination_ids: list[int] = Query(default=[], alias='destination_ids'),
    images: List[UploadFile] = File(...),  # Nhận danh sách các tệp ảnh
    db: Session = Depends(get_db)
):
    image_handler = image.ImageHandler()
    urls = [image_handler.save_image(image, f"travel-image/tours/1.png") for image in images]
    print(urls)
    # # Tạo tour với thông tin và ảnh đã xử lý
    # return tour.create(
    #     request={
    #         "name": name,
    #         "description": description,
    #         "user_id": user_id,
    #         "city_id": city_id,
    #         "destination_ids": destination_ids
    #     },
    #     images=image_urls,
    #     db=db
    # )

@router.get("//{tour_id}")
def get_tour_by_id_endpoint(tour_id: int, db: Session = Depends(get_db)):
    return tour.get_tour_by_id(tour_id=tour_id, db=db)

@router.get("/")
def get_all_tour_endpoint(db: Session = Depends(get_db)):
    return tour.get_all_tour(db = db)


@router.get("/")
def get_all_tour_endpoint(
    id: int = None,
    city_id: int = None,
    sort_by_reviews: bool = False,
    db: Session = Depends(get_db)
):
    results = []

    # Nếu có id, lấy tour theo ID
    if id:
        tour = tour.get_by_id(id, db)
        if not tour:
            return {"error": "tour not found"}
        results.append(tour)

    # Nếu có city_id, lấy tours theo city_id
    elif city_id:
        results = tour.get_by_city_id(city_id, db)

    # Nếu không có id hay city_id, lấy tất cả tours
    else:
        results = tour.get_all(db)

    # Nếu cần sắp xếp theo đánh giá
    if sort_by_reviews:
        results = tour.sorting_by_ratings_and_quantity_of_reviews(tours=results, db=db)

    # Chuyển đổi các kết quả sang định dạng mong muốn
    final_results = []
    for tour in results:
        result = schemas.Showtour.from_orm(tour).dict()
       
        rating_info = tour.get_ratings_and_reviews_number_of_tourID(tour.id, db)
        result.update({
            "rating": rating_info["ratings"],
            "numOfReviews": rating_info["numberOfReviews"]
        })
        final_results.append(result)

    return final_results