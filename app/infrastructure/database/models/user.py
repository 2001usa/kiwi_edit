from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, DECIMAL, Enum
from sqlalchemy.sql import func
import enum
from app.infrastructure.database.models.base import Base

class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    language = Column(String, default="uz")
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default=UserStatus.ACTIVE)
    
    # Premium features
    is_admin = Column(Boolean, default=False)
    is_staff = Column(Boolean, default=False)
    balance = Column(DECIMAL(10, 2), default=0)
    
    # Legacy fields support (will be refactored later to meaningful names)
    is_anipass = Column(Boolean, default=False) # or DateTime for expiration
    is_lux = Column(Boolean, default=False)
