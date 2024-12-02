from datetime import date
import random
from fastapi import HTTPException
from sqlalchemy import create_engine, select, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import pymysql
from datetime import date  # Đảm bảo bạn import date
from fastapi import HTTPException

from blog import repository
from blog import models
from . import schemas  # Import schemas nếu cần
from blog.repository.image import ImageHandler
# from blog.repository import destination

# DATABASE_URL=mysql+pymysql://travel_user:password@localhost:3306/db_connect
# cnx = mysql.connector.connect(user="travel_user", password="{your_password}", host="travel-sql.mysql.database.azure.com", port=3306, database="{your_database}", ssl_ca="{ca-cert filename}", ssl_disabled=False)


# Tải các biến môi trường từ tệp .env
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
SSL_CA_PATH = os.getenv('SSL_CA_PATH')

print('dasd', os.path.exists(SSL_CA_PATH))

# Kiểm tra xem SSL_CA_PATH có tồn tại không
if not SSL_CA_PATH or not os.path.exists(SSL_CA_PATH):
    raise ValueError("SSL_CA_PATH không hợp lệ hoặc không tồn tại")

# Cấu hình kết nối SSL
ssl_args = {
    "ssl": {
        "ssl_ca": SSL_CA_PATH
    }
}

# Tạo engine với cấu hình SSL
try:
    engine = create_engine(DATABASE_URL, connect_args=ssl_args)
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Không thể kết nối đến database: {str(e)}")


# high-level abstract (ORM) -> manage database through Object in code. Unlike Engine -> manage db through SQL command
SessionLocal = sessionmaker(autocommit=False, autoflush = False, bind = engine)
# Create base class for all models (code -> DB)
Base = declarative_base()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def delete_all(engine):
    pass

def create_sample_data():

    # Lấy phiên làm việc với cơ sở dữ liệu
    db = next(get_db())
    
    try:
        # Kiểm tra xem có người dùng nào trong cơ sở dữ liệu không
        existing_users = db.execute(select(models.User)).scalars().all()
        if not existing_users:  # Nếu không có người dùng nào
            # Tạo dữ liệu mẫu cho người dùng
            user1_data = schemas.User(username='user1', email='user1@gmail.com', password='123', role="guest", status="enable")
            admin1_data = schemas.User(username='admin1', email='admin1@gmail.com', password='123', role="admin", status="enable")

            # Gọi hàm create cho mỗi người dùng
            user1 = repository.user.create_business_admin(user1_data, db)
            admin1 = repository.user.create_business_admin(admin1_data, db)

            # Tạo thông tin người dùng liên quan đến user1 và user2
            user1_info = models.UserInfo(description='Tour operator', phone_number='123456789', user=user1)
            admin1_info = models.UserInfo(phone_number='987654321', user=admin1)
            
            db.add_all([user1_info, admin1_info])
            db.commit()
            
            # Tạo 61 người dùng với phân quyền là business
            cities = [
                "Hà Nội", "TP Hồ Chí Minh", "Đà Nẵng", "Hải Phòng", "Nha Trang", 
                "Cần Thơ", "Huế", "Quảng Ninh", "Vĩnh Phúc", "Đồng Nai",
                "Bà Rịa - Vũng Tàu", "Bắc Ninh", "Thái Nguyên", "Nam Định", "Ninh Bình",
                "Hà Nam", "Hưng Yên", "Điện Biên", "Hà Tĩnh", "Quảng Bình",
                "Quảng Trị", "Thừa Thiên Huế", "Bình Định", "Phú Yên", "Khánh Hòa",
                "Gia Lai", "Kon Tum", "Đắk Lắk", "Đắk Nông", "Lâm Đồng",
                "Tây Ninh", "Long An", "Tiền Giang", "Bến Tre", "Trà Vinh",
                "Vĩnh Long", "Hậu Giang", "Sóc Trăng", "Đồng Tháp", "An Giang",
                "Kiên Giang", "Cà Mau", "Bạc Liêu", "Hà Giang", "Lào Cai",
                "Yên Bái", "Tuyên Quang", "Hòa Bình", "Ninh Thuận", "Bình Thuận",
                "Cao Bằng", "Thái Bình", "Bắc Kạn", "Lạng Sơn", "Đắk Lắk",
                "Lâm Đồng", "Bến Tre", "Bình Dương", "Bình Phước", "Hưng Yên", "Vĩnh Phúc"
            ]

            for i in range(61):
                username = f'business{i+1}'
                email = f'business{i+1}@gmail.com'
                password = '123'

                # Tạo người dùng
                user_data = schemas.User(username=username, email=email, password=password, role="business", status="enable")
                user = repository.user.create_business_admin(user_data, db)

                # Tạo thông tin người dùng
                user_info = models.UserInfo(description='Business Owner', phone_number='0123456789', user=user)
                db.add(user_info)

                # Tạo thành phố
                city = models.City(
                    name=cities[i],
                    description=f"{cities[i]} - một tỉnh thành tuyệt đẹp",
                    user_id=user.id  # Liên kết với user vừa tạo
                )
                db.add(city)
                db.commit()
                db.refresh(city)
                
                # crawl data cho city
                # ImageHandler.crawl_image(db=db, city= city)
                # image.crawl_image(db=db, city=city )
                
                # Thêm 1 điểm đến cho mỗi user
                for j in range(2):
                    
                    address = models.Address(
                        district = f"district of {cities[i]}",
                        street = f"street of {cities[i]}",
                        ward = f"ward of {cities[i]}",
                        city = city
                    )
                    db.add(address)
                    db.commit()
                    destination = models.Destination(
                        description = "description",
                        name=f"Destination {j+1} tại {cities[i]}",
                        # address=f"Địa chỉ {j+1}, {cities[i]}",
                        address = address,
                        price_bottom=0,
                        price_top=0,
                        date_create=date.today(),
                        age=0,
                        opentime="00:00:00",
                        duration=24,
                        user_id=user.id,
                    )
                    db.add(destination)
                    db.commit()
                    db.refresh(destination)
                    
                    imageHandler = ImageHandler()
                    # imageHandler.fake_db_destination(db, destination=destination)
                    
                    hotel = models.Hotel(
                        property_amenities='Free WiFi, Pool, Gym',
                        room_features='AC, TV, Minibar',
                        room_types='Suite, Deluxe',
                        hotel_class=random.randint(3, 5),  # Hotel class từ 3-5 sao
                        hotel_styles='Luxury, Modern',
                        Languages='English, Vietnamese',
                    )
                    
                    # restaurant = models.Restaurant(
                    #     cuisine='Vietnamese, International',
                    #     special_diet='Vegetarian, Vegan',
                    # )
                    # destination.restaurant = restaurant
                    destination.hotel = hotel
                    db.add_all([hotel,  destination,address ])
                    db.commit()
                    
                    
                    # Tạo 3-5 reviews cho mỗi destination
                    num_reviews = random.randint(0, 7)
                    for k in range(num_reviews):
                        review = models.Review(
                            title=f"Review {k + 1} for Destination {j + 1}",
                            content=f"This is review {k + 1} for Destination {j + 1}.",
                            rating= float(random.randint(1, 10)/2),  # Rating từ 1.0 đến 5.0
                            date_create=date.today(),
                            user_id=user.id,  # Gán user_id của user đã tạo
                            destination_id=destination.id  # Gán destination_id của destination đã tạo
                        )
                        db.add(review)
                        db.commit()
                        db.refresh(review)
                        # imageHandler.fake_db_review(db, review=review)
                        
    
            db.commit()
            # destination.update_all_destination_ratings(db)

            # for user_id in range(1, 5):
            #     for destination_id in range(1, 11):
            #         if random.randint(0, 1) == 1:
            #             like = models.UserDestinationLike(
            #                 user_id=user_id,
            #                 destination_id=destination_id
            #             )
            #             db.add(like)
            
            # # Tạo sample data cho DestinationTag
            # for destination_id in range(1, 11):
            #     for tag_id in range(1, 6):
            #         if random.randint(0, 1) == 1:
            #             destination_tag = models.DestinationTag(
            #                 destination_id=destination_id,
            #                 tag_id=tag_id
            #             )
            #             db.add(destination_tag)
            
            # db.commit()
            

            # 
            print("Sample data created.")
        else:
            print("Sample data already exists.")

    except Exception as e:
        # Xử lý lỗi
        raise HTTPException(status_code=500, detail=f"Error creating sample data: {str(e)}")

    finally:
        # Đóng phiên làm việc
        db.close()