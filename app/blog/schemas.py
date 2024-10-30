from typing import List, Optional
from pydantic import BaseModel
from datetime import date, time
class BlogBase(BaseModel):
    title: str
    body: str

class Blog(BlogBase):
    id: int
    class Config():
        from_attributes = True
class UserInfoBase(BaseModel):
    business_description: str# Thông tin mô tả doanh nghiệp
    phone_number: str
    
    
class Tour(BaseModel):
    id: int
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

class ShowUserInfo(BaseModel):
    business_description: Optional[str]  # Thông tin mô tả doanh nghiệp
    phone_number: Optional[str]  
    class Config:
        from_attributes = True
class ShowUser(BaseModel):
    id: int
    username:str
    email:str
    role: str
    class Config():
        from_attributes = True

class ShowBlog(BaseModel):
    id: int
    title: str
    body:str
    creator: ShowUser

    class Config():
        from_attributes = True


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
        from_attributes = True
    
class ShowImage(BaseModel):
    id: int
    url: str
    
    class Config():
            from_attributes = True


class City(BaseModel):
    name: str
    description: str

class ShowCity(City):
    id: int
    images: List[ShowImage]
    
    class Config():
        from_attributes = True

class Address(BaseModel):
    district: str
    street: str
    ward: str
    city_id: int


class ShowAddress(Address):
    id: int
    
    class Config():
        from_attributes = True
class Destination(BaseModel):
    name : str
    address : Optional[ShowAddress]= None
    price_bottom : int  
    price_top : int  
    date_create : date 
    age : int  
    opentime : time
    duration : int 
    
    class Config():
        from_attributes = True
class Destination_Address(Address, Destination):
    pass

class Restaurant(BaseModel):
    cuisine: Optional[str] = None
    special_diet: Optional[str] = None

class ShowRestaurant(Restaurant):
    id: int
    class Config():
        from_attributes = True
class Hotel(BaseModel):
    property_amenities: str
    room_features: str
    room_types: str
    hotel_class: int
    hotel_styles: str
    Languages: str
class ShowHotel(Hotel):
    id: int
    class Config():
        from_attributes = True



class ShowDestination(Destination):
    id: int
    hotel_id: Optional[int] = None
    restaurant_id: Optional[int] = None
    hotel: Optional[ShowHotel] = None
    restaurant: Optional[ShowRestaurant] = None
    images: List[ShowImage]
    
    class Config():
        from_attributes = True
        
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
        from_attributes = True
   