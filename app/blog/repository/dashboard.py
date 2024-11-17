from typing import List
from sqlalchemy import func
from sqlalchemy.orm import Session
from blog import models, schemas

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

def get_user_counts_by_month(db: Session, year: int):
    results = (
        db.query(
            func.month(models.User.created_at).label('month'),
            func.count(models.User.id).label('user_count')
        )
        .filter(func.year(models.User.created_at) == year)
        .group_by('month')
        .order_by('month')  # Sắp xếp theo tháng
        .all()
    )
    return [schemas.UserCountByMonth(month=row.month, user_count=row.user_count) for row in results]
def get_user_counts_by_day(db: Session, year: int, month: int):
    results = (
        db.query(
            func.day(models.User.created_at).label('day'),
            func.count(models.User.id).label('user_count')
        )
        .filter(func.year(models.User.created_at) == year, func.month(models.User.created_at) == month)
        .group_by('day')
        .order_by('day')  # Sắp xếp theo ngày
        .all()
    )
    return [schemas.UserCountDetail(day=row.day, user_count=row.user_count) for row in results]