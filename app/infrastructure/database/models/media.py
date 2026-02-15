from sqlalchemy import Column, Integer, String, Float, ForeignKey, BigInteger, Text, Boolean
from sqlalchemy.orm import relationship
from app.infrastructure.database.models.base import Base

class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(Integer, unique=True, index=True, nullable=True) # Unique search code
    
    name = Column(String, index=True)
    original_name = Column(String, nullable=True)
    
    type = Column(String, default="anime") # anime, movie, series
    status = Column(String, default="ongoing") # loading, ongoing, finished
    
    genre = Column(String, nullable=True)
    tags = Column(String, nullable=True)
    dubbing = Column(String, nullable=True) # Dub or Sub
    
    poster_file_id = Column(String, nullable=True)
    trailer_file_id = Column(String, nullable=True)
    
    views = Column(BigInteger, default=0)
    rating = Column(Float, default=0.0)
    
    is_vip = Column(Boolean, default=False)

    episodes = relationship("Episode", back_populates="media", cascade="all, delete-orphan")

class Episode(Base):
    __tablename__ = "episodes"

    id = Column(Integer, primary_key=True, index=True)
    media_id = Column(Integer, ForeignKey("media.id"))
    
    episode_number = Column(Integer)
    episode_file_id = Column(String) # Telegram File ID
    
    duration = Column(Integer, nullable=True) # in seconds
    
    media = relationship("Media", back_populates="episodes")
