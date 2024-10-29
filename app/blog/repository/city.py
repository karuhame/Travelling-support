
from sqlalchemy.orm import Session
from blog import models, schemas
from fastapi import HTTPException, status
from blog.hashing import Hash

def create_city(request: schemas.City, db: Session):
    try:
        new_city = models.City(
            name=request.name,
            description=request.description,
        )
        db.add(new_city)
        db.commit()
        db.refresh(new_city)
        return new_city
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create city info")


def get_city_by_id(id: int, db: Session):
    try:
        
        city = db.query(models.City).filter(models.City.id == id).first()  # Chờ truy vấn
        print(city)
        
        if not city:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"City with the id {id} is not available")
        return city
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve city info")

def get_all_city(db: Session):
    try:
        cities = db.query(models.City).all()  # Chờ truy vấn
        return cities
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve city info")

def update_city_by_id(id: int, request: schemas.City, db: Session):
    try:
        city = db.query(models.City).filter(models.City.id == id).first()  # Chờ truy vấn
        if not city:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"City with the id {id} is not available")
        city.description = request.description
        city.name = request.name
        db.commit()
        db.refresh(city)
        return city
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update city info")


def delete_city_by_id(id: int, db: Session):
    try:
        city = db.query(models.City).filter(models.City.id == id).first()  # Chờ truy vấn
        if not city:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"City with the id {id} is not available")
        db.delete(city)
        db.commit()
        return {"message": "City deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete city info")
