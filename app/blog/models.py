from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Date, Time, DateTime
from blog.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime


class User(Base):
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, default='Guest')
    password = Column(String(255), default='password123')  
    email = Column(String(50), unique=True)
    role = Column(String(10), default="guest") #guest/business/admin
    status = Column(String(10), default="enable")
    created_at = Column(DateTime, default=datetime.utcnow)  # New field
    
    # Relationship
    business_type = relationship("BusinessType", back_populates="user")
    user_info = relationship("UserInfo", back_populates="user", uselist=False)  
    reviews = relationship("Review", back_populates="user")
    journeys=  relationship("Journey", back_populates="user")
    destinations = relationship("Destination", back_populates="user")
    forum_comments = relationship("ForumComment", back_populates="user")
    city = relationship("City", back_populates="user")
    tours = relationship("Tour", back_populates="user")
    likes = relationship("UserDestinationLike", back_populates="user")

    
class UserInfo(Base):
    __tablename__ = 'userInfo'

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String(200), default='No Description')
    phone_number = Column(String(12), default='N/A')
    
    # Foreign Key
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    address_id = Column(Integer, ForeignKey('address.id', ondelete='CASCADE'))
    
    # Relationship
    user = relationship("User", back_populates="user_info")
    address = relationship("Address", back_populates="user_info")
    image = relationship("Image", back_populates="user_info",uselist=False)

class BusinessType(Base):
    __tablename__ = 'businessType'
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), default='General')  

    # Foreign Key
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))

    # Relationship
    user = relationship("User", back_populates="business_type")

class Destination(Base):
    __tablename__ = 'destination'
    
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String(200), default='Description')
    name = Column(String(50), default='Unnamed Destination')
    price_bottom = Column(Integer, nullable=True, default=0)  
    price_top = Column(Integer, nullable=True, default=0)  
    date_create = Column(Date, nullable=True, default=None)  
    age = Column(Integer, nullable=True, default=0)  
    opentime = Column(Time, nullable=True, default=None)  
    duration = Column(Integer, nullable=True, default=3)  

    average_rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    popularity_score = Column(Float, default=0.0)

    # Foreign Key
    user_id = Column(Integer, ForeignKey('user.id', name="fk_destination_user", ondelete='CASCADE'))
    address_id = Column(Integer, ForeignKey('address.id', name="fk_destination_address", ondelete='CASCADE'), nullable=True)
    hotel_id = Column(Integer, ForeignKey('hotel.id', name="fk_destination_hotel", ondelete='CASCADE'), nullable=True)
    restaurant_id = Column(Integer, ForeignKey('restaurant.id', name="fk_destination_restaurant", ondelete='CASCADE'), nullable=True)

    
    # Relationship
    user = relationship("User", back_populates="destinations")
    reviews = relationship("Review", back_populates="destination")
    images = relationship("Image", back_populates="destination")
    restaurant = relationship("Restaurant", back_populates="destination", uselist=False)
    hotel = relationship("Hotel", back_populates="destination", uselist=False)
    address = relationship("Address", back_populates="destination", uselist=False)
    # destination_journeys = relationship("DestinationJourney", back_populates="destination")  
    tours = relationship("Tour",secondary="destination_tour", back_populates="destinations")
    journeys = relationship("Journey",secondary="destination_journey", back_populates="destinations")
    tags = relationship("Tag", secondary="destination_tag", back_populates="destinations")
    likes = relationship("UserDestinationLike", back_populates="destination")
    
class Image(Base):
    __tablename__ = 'image'
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(100), nullable=True)
    blob_name = Column(String(100), nullable = True)
    
    # Khóa ngoại cho City
    city_id = Column(Integer, ForeignKey('city.id'), nullable=True)
    city = relationship("City", back_populates="images", uselist=False)

    # Khóa ngoại cho Destination
    destination_id = Column(Integer, ForeignKey('destination.id'), nullable=True)
    destination = relationship("Destination", back_populates="images", uselist=False)
    
    review_id = Column(Integer, ForeignKey('review.id'), nullable=True)
    review = relationship("Review", back_populates="images", uselist=False)
    
    userInfo_id = Column(Integer, ForeignKey('userInfo.id'), nullable=True)
    user_info = relationship("UserInfo", back_populates="image", uselist=False)
    
class City(Base):
    __tablename__ = 'city'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), default='Unnamed Destination')
    description = Column(String(50), default='No Description')
    
    # Foreign Key
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))

    # Relationship
    user = relationship("User", back_populates="city")
    
    addresses = relationship("Address", back_populates="city")
    images = relationship("Image", back_populates="city")
    tours = relationship("Tour", back_populates="city")
    
class Address(Base):
    __tablename__ = 'address'
    
    id = Column(Integer, primary_key=True, index=True)
    district = Column(String(100), nullable=True)
    street = Column(String(100), nullable=True)
    ward = Column(String(100), nullable=True)

    city_id = Column(Integer, ForeignKey('city.id')) 
    
    city = relationship("City", back_populates="addresses", uselist=False)
    destination = relationship("Destination", back_populates="address", uselist=False)
    user_info = relationship("UserInfo", back_populates="address", uselist=False)
    
class Hotel(Base):
    __tablename__ = 'hotel'

    id = Column(Integer, primary_key=True, index=True)
    property_amenities = Column(String(255), default='Free Parking, Pool, Free breakfast')
    room_features = Column(String(255), default='Soundproof room, Extra long bed')
    room_types = Column(String(255), default='Ocean view, City view, family room')
    hotel_class = Column(Integer, default=0)
    hotel_styles = Column(String(255), default='Ocean view, Trendy')
    languages = Column(String(255), default='Vietnamese, English, Chinese')
    phone =  Column(String(255), nullable=True)
    email =  Column(String(255), nullable=True)
    website =  Column(String(255), nullable=True)
    
    
    # destination_id = Column(Integer, ForeignKey('destination.id', name="fk_hotel_destination", ondelete='CASCADE'), nullable=True)

    destination = relationship("Destination", back_populates="hotel")

class Restaurant(Base):
    __tablename__ = 'restaurant'
    
    id = Column(Integer, primary_key=True, index=True)
    cuisine = Column(String(50), default='Mixed')
    special_diet = Column(String(50), nullable=True)
    feature = Column(String(255), nullable   = True)
    meal = Column(String(255), nullable = True)  
    
    
    
    # destination_id = Column(Integer, ForeignKey('destination.id', name="fk_hotel_destination", ondelete='CASCADE'), nullable=True)

    destination = relationship("Destination", back_populates="restaurant")
class Tour(Base):
    __tablename__ = 'tour'
    
    id = Column(Integer, primary_key=True, index=True)    
    name = Column(String(255))
    description = Column(String(255))
    duration = Column(Integer, nullable=True, default=0)  
    
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    city_id = Column(Integer, ForeignKey('city.id', ondelete='CASCADE'))
    
    # Relationship
    user = relationship("User", back_populates="tours")
    city = relationship("City", back_populates="tours")
    # Relationship with Destination through the intermediary table
    destinations = relationship("Destination", secondary="destination_tour", back_populates="tours")
    reviews = relationship("Review", back_populates="tour")


class DestinationTour(Base):
        
    __tablename__ = 'destination_tour' 
    
    id = Column(Integer, primary_key=True, index=True)
    
    tour_id = Column(Integer, ForeignKey('tour.id', ondelete='CASCADE'))
    destination_id = Column(Integer, ForeignKey('destination.id', ondelete='CASCADE'))

class DestinationTag(Base):
        
    __tablename__ = 'destination_tag' 
    
    id = Column(Integer, primary_key=True, index=True)
    
    tag_id = Column(Integer, ForeignKey('tag.id', ondelete='CASCADE'))
    destination_id = Column(Integer, ForeignKey('destination.id', ondelete='CASCADE'))
    
class Tag(Base):
    __tablename__ = 'tag'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), default='General')  
    
    destinations = relationship("Destination", secondary="destination_tag", back_populates="tags") 

class Journey(Base):
    __tablename__ = 'journey' 
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    duration = Column(Integer, nullable=True, default=0)  
    
    # Relationship
    user = relationship("User", back_populates="journeys")
    destinations = relationship("Destination", secondary="destination_journey", back_populates="journeys")

class DestinationJourney(Base):
    __tablename__ = 'destination_journey' 
    
    id = Column(Integer, primary_key=True, index=True)
    
    journey_id = Column(Integer, ForeignKey('journey.id', ondelete='CASCADE'))
    destination_id = Column(Integer, ForeignKey('destination.id', ondelete='CASCADE'))
    
    
class Review(Base):
    __tablename__ = 'review'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50), default='No Title')  
    content = Column(String(100), default='No Content')  
    rating = Column(Float, default=0.0)  
    date_create = Column(Date, nullable=True, default=None)  
    language = Column(String(255), nullable=True, default=None)
    companion =  Column(String(50), default='Solo')   
    
    # Foreign Key
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    destination_id = Column(Integer, ForeignKey('destination.id', ondelete='CASCADE'))
    tour_id = Column(Integer, ForeignKey('tour.id', ondelete='CASCADE'))

    # Relationship
    user = relationship("User", back_populates="reviews")
    destination = relationship("Destination", back_populates="reviews")
    tour = relationship("Tour", back_populates="reviews")
    images = relationship("Image", back_populates="review")

class Forum(Base):
    __tablename__ = 'forum'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50), default='Untitled Forum')  
    
    # Relationship
    forum_comments = relationship("ForumComment", back_populates="forum")

class ForumComment(Base):
    __tablename__ = 'forum_comment' 
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    forum_id = Column(Integer, ForeignKey('forum.id', ondelete='CASCADE'))
    
    # replied_user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=True)
    content = Column(String(100), default='No Content')  
    like_count = Column(Integer, default=0)  
    dislike_count = Column(Integer, default=0)  

    # Relationship
    forum = relationship("Forum", back_populates="forum_comments")
    user = relationship("User", back_populates="forum_comments")
    

class UserDestinationLike(Base):
    __tablename__ = 'user_destination_likes'
    
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    destination_id = Column(Integer, ForeignKey('destination.id'), primary_key=True)
    
    # Relationships
    user = relationship("User", back_populates="likes")
    destination = relationship("Destination", back_populates="likes")