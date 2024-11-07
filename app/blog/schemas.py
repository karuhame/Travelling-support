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
    name : str
    price_bottom : int  
    price_top : int  
    date_create : date 
    age : int  
    opentime : time
    duration : int 
    description: Optional[str] = None
    
    class Config():
        orm_mode = True
class Destination_Address(Address, Destination):
    pass

class Restaurant(BaseModel):
    cuisine: Optional[str] = None
    special_diet: Optional[str] = None

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
class ShowDestination(Destination):
    id: int
    hotel_id: Optional[int] = None
    restaurant_id: Optional[int] = None
    hotel: Optional[ShowHotel] = None
    restaurant: Optional[ShowRestaurant] = None
    images: List[ShowImage]
    address : Optional[ShowAddress]= None
    
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
