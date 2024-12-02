from typing import List, Optional
from fastapi import UploadFile
from pydantic import BaseModel, Field
from datetime import date, time

class BlogBase(BaseModel):
    title: str
    body: str

class Blog(BlogBase):
    id: int
    class Config():
        orm_mode = True

class UserInfoBase(BaseModel):
    description: str# Thông tin mô tả doanh nghiệp
    phone_number: str
    
    
class Tour(BaseModel):
    name: str
    description: str
    user_id: int
    city_id: int
    
    destination_ids: List[int]
    
class User(BaseModel):
    username:str
    email:str
    password:str    
    role: str
    status: str

    class Config:
        orm_mode = True


class Login(BaseModel):
    email: str
    password:str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None
    
class SignUp(BaseModel):
    email: str
    password:str
    username: str

     
class Image(BaseModel):
    id: int
    city_id: Optional[int] = None
    destination_id: Optional[int] = None
    url: str
    
    class Config():
        orm_mode = True
    
class ShowImage(BaseModel):
    id: int
    url: Optional[str]
    
    class Config():
        orm_mode = True

class City(BaseModel):
    name: str
    description: str

class ShowCity(City):
    id: int
    images: List[ShowImage]
    
    class Config():
        orm_mode = True

class Address(BaseModel):
    district: str
    street: str
    ward: str
    city_id: int


class ShowAddress(Address):
    id: int
    
    class Config():
        orm_mode = True

class Destination(BaseModel):
    id: Optional[int]  # Thêm id để đồng bộ với ORM
    name: Optional[str]
    price_bottom: Optional[int]
    price_top: Optional[int]
    date_create: Optional[date]
    age: Optional[int]
    opentime: Optional[time]
    duration: Optional[int]
    description: Optional[str] = None
    average_rating: Optional[float] = 0.0  # Thêm trường
    review_count: Optional[int] = 0         # Thêm trường
    popularity_score: Optional[float] = 0.0 # Thêm trường

    class Config:
        orm_mode = True

class Destination_Address(Address, Destination):
    pass

class Restaurant(BaseModel):
    cuisine: Optional[str] = Field(
        default=None,
        examples="Italian, Japanese, Vietnamese"
    )
    special_diet: Optional[str] = Field(
        default=None,
        description="Special dietary options that the restaurant can accommodate (e.g., vegan, gluten-free, etc.)"
    )

class Hotel(BaseModel):
    property_amenities: Optional[str]
    room_features: Optional[str]
    room_types: Optional[str]
    hotel_class: int
    hotel_styles: Optional[str]
    Languages: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    website: Optional[str]
    



class ShowRestaurant(Restaurant):
    id: int
    class Config():
        orm_mode = True
class ShowHotel(Hotel):
    id: int
    class Config():
        orm_mode = True

        
class Review(BaseModel):
    title :str 
    content :str 
    rating : float
    date_create :date
    

    
class ShowReview(Review):
    id: int
    # Foreign Key
    user_id : int
    destination_id :int
    images: List[ShowImage]
    class Config():
        orm_mode = True
   
class ShowUserInfo(BaseModel):
    id: int
    description: Optional[str]  # Thông tin mô tả doanh nghiệp
    phone_number: Optional[str]  
    image: Optional[ShowImage]
    address : Optional[ShowAddress]

    
    class Config():
        orm_mode = True


class ShowUser(BaseModel):
    id: int
    username:str
    email:str
    role: str
    status: str
    
    user_info: Optional[ShowUserInfo]
    class Config():
        orm_mode = True

class ShowBlog(BaseModel):
    id: int
    title: str
    body:str
    creator: ShowUser

    class Config():
        orm_mode = True

class ShowDestinationOfTour(Destination):
    id: int
    hotel_id: Optional[int] = None
    restaurant_id: Optional[int] = None
    images: Optional[List[ShowImage]]
    address : Optional[ShowAddress]= None
    
    class Config():
        orm_mode = True
        
        
class ShowTour(BaseModel):
    id: int
    name: str
    description: str
    duration: int
    user_id: int
    city_id: int
    
    destinations: Optional[List[ShowDestinationOfTour]]
    
    class Config():
        orm_mode = True

class Tag(BaseModel):
    name: Optional[str]
    
class ShowTag(Tag):
    id: Optional[int]
    
    class Config():
        orm_mode = True
        
class ShowDestination(Destination):
    id: int
    tags: Optional[List[ShowTag]] = None
    address : Optional[ShowAddress]= None
    images: Optional[List[ShowImage]]
    hotel_id: Optional[int] = None
    hotel: Optional[ShowHotel] = None
    restaurant_id: Optional[int] = None
    restaurant: Optional[ShowRestaurant] = None
    
    
    class Config():
        orm_mode = True

class ShowDestinationTag(Destination):
    id: int
    tags: Optional[List[ShowTag]] = None    
    
    class Config():
        orm_mode = True


class UserDestinationLikeBase(BaseModel):
    user_id: int
    destination_id: int

class UserDestinationLikeCreate(UserDestinationLikeBase):
    pass

class UserDestinationLikeResponse(UserDestinationLikeBase):
    class Config:
        orm_mode = True

class DestinationStats(BaseModel):
    destination_id: int
    name: str
    average_rating: float
    review_count: int
    popularity_score: float
    
    class Config:
        orm_mode = True

class DestinationBase(BaseModel):
    name: str
    average_rating: float
    review_count: int
    popularity_score: float