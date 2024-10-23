from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Date, Time
from blog.database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, default='Guest')
    password = Column(String(255), default='password123')  
    email = Column(String(50), unique=True)
    role = Column(String(10), default="guest") #guest/business/admin

    
    # Relationship
    business_type = relationship("BusinessType", back_populates="user")
    user_info = relationship("UserInfo", back_populates="user", uselist=False)  
    reviews = relationship("Review", back_populates="user")
    journeys=  relationship("Journey", back_populates="user")
    destinations = relationship("Destination", back_populates="user")
    forum_comments = relationship("ForumComment", back_populates="user")
    city = relationship("City", back_populates="user")
    tours = relationship("Tour", back_populates="user")

    
class UserInfo(Base):
    __tablename__ = 'userInfo'

    id = Column(Integer, primary_key=True, index=True)
    business_description = Column(String(200), default='No Description')
    phone_number = Column(String(12), default='N/A')
    
    # Foreign Key
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))

    # Relationship
    user = relationship("User", back_populates="user_info")

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
    name = Column(String(50), default='Unnamed Destination')
    price_bottom = Column(Integer, nullable=True, default=0)  
    price_top = Column(Integer, nullable=True, default=0)  
    date_create = Column(Date, nullable=True, default=None)  
    age = Column(Integer, nullable=True, default=0)  
    opentime = Column(Time, nullable=True, default=None)  
    duration = Column(Integer, nullable=True, default=3)  

    # Foreign Key
    user_id = Column(Integer, ForeignKey('user.id', name="fk_destination_user", ondelete='CASCADE'))
    address_id = Column(Integer, ForeignKey('address.id', name="fk_destination_address", ondelete='CASCADE'))
    hotel_id = Column(Integer, ForeignKey('hotel.id', name="fk_destination_hotel", ondelete='CASCADE'), nullable=True)
    restaurant_id = Column(Integer, ForeignKey('restaurant.id', name="fk_destination_restaurant", ondelete='CASCADE'), nullable=True)

    
    # Relationship
    user = relationship("User", back_populates="destinations")
    tags = relationship("Tag", back_populates="destinations")
    reviews = relationship("Review", back_populates="destination")
    images = relationship("Image", back_populates="destination")
    
    restaurant = relationship("Restaurant", back_populates="destination", uselist=False)
    hotel = relationship("Hotel", back_populates="destination", uselist=False)
    address = relationship("Address", back_populates="destination", uselist=False)
    # destination_journeys = relationship("DestinationJourney", back_populates="destination")  
    tours = relationship("Tour",secondary="destination_tour", back_populates="destinations")
    journeys = relationship("Journey",secondary="destination_journey", back_populates="destinations")

class Image(Base):
    __tablename__ = 'image'
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(100), nullable=True)
    
    # Khóa ngoại cho City
    city_id = Column(Integer, ForeignKey('city.id'), nullable=True)
    city = relationship("City", back_populates="images", uselist=False)

    # Khóa ngoại cho Destination
    destination_id = Column(Integer, ForeignKey('destination.id'), nullable=True)
    destination = relationship("Destination", back_populates="images", uselist=False)
    
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
    
    
class Address(Base):
    __tablename__ = 'address'
    
    id = Column(Integer, primary_key=True, index=True)
    district = Column(String(100), nullable=True)
    street = Column(String(100), nullable=True)
    ward = Column(String(100), nullable=True)

    city_id = Column(Integer, ForeignKey('city.id')) 
    
    city = relationship("City", back_populates="addresses", uselist=False)
    destination = relationship("Destination", back_populates="address", uselist=False)
class Restaurant(Base):
    __tablename__ = 'restaurant'
    
    id = Column(Integer, primary_key=True, index=True)
    cuisine = Column(String(50), default='Mixed')
    special_diet = Column(String(50), nullable=True)
    
    # destination_id = Column(Integer, ForeignKey('destination.id', name="fk_hotel_destination", ondelete='CASCADE'), nullable=True)

    destination = relationship("Destination", back_populates="restaurant")

    
class Hotel(Base):
    __tablename__ = 'hotel'

    id = Column(Integer, primary_key=True, index=True)
    property_amenities = Column(String(255), default='Free Parking, Pool, Free breakfast')
    room_features = Column(String(255), default='Soundproof room, Extra long bed')
    room_types = Column(String(255), default='Ocean view, City view, family room')
    hotel_class = Column(Integer, default=0)
    hotel_styles = Column(String(255), default='Ocean view, Trendy')
    Languages = Column(String(255), default='Vietnamese, English, Chinese')
 
    
    # destination_id = Column(Integer, ForeignKey('destination.id', name="fk_hotel_destination", ondelete='CASCADE'), nullable=True)

    destination = relationship("Destination", back_populates="hotel")

class Tour(Base):
    __tablename__ = 'tour'
    
    id = Column(Integer, primary_key=True, index=True)    
    name = Column(String(255))
    
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    
    # Relationship
    user = relationship("User", back_populates="tours")
    # Relationship with Destination through the intermediary table
    destinations = relationship("Destination", secondary="destination_tour", back_populates="tours")


class DestinationTour(Base):
        
    __tablename__ = 'destination_tour' 
    
    id = Column(Integer, primary_key=True, index=True)
    
    tour_id = Column(Integer, ForeignKey('tour.id', ondelete='CASCADE'))
    destination_id = Column(Integer, ForeignKey('destination.id', ondelete='CASCADE'))
class Tag(Base):
    __tablename__ = 'tag'
    
    id = Column(Integer, primary_key=True, index=True)  # Thêm trường id cho tag
    destination_id = Column(Integer, ForeignKey('destination.id', ondelete='CASCADE'))
    tag_type = Column(String(50), default='General')  
    
    destinations = relationship("Destination", back_populates="tags")  

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
    
    # Foreign Key
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    destination_id = Column(Integer, ForeignKey('destination.id', ondelete='CASCADE'))

    # Relationship
    user = relationship("User", back_populates="reviews")
    destination = relationship("Destination", back_populates="reviews")

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
    

