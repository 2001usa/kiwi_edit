from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey
from app.infrastructure.database.models.base import Base

class Sponsor(Base):
    __tablename__ = "sponsors"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(BigInteger, unique=True, index=True)
    channel_name = Column(String)
    channel_link = Column(String)
    # type: simple, request
    type = Column(String, default="simple") 
    user_limit = Column(Integer, default=0)

class SponsorRequest(Base):
    __tablename__ = "sponsor_request"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(BigInteger) # channel_id
    user_id = Column(BigInteger)
