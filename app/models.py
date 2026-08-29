from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    short_code = Column(String, unique=True, index=True, nullable=False)
    long_url = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    clicks = relationship("Click", back_populates="url")

class Click(Base):
    __tablename__ = "clicks"

    id = Column(Integer, primary_key=True, index=True)
    url_id = Column(Integer, ForeignKey("urls.id"), nullable=False)
    clicked_at = Column(DateTime(timezone=True), server_default=func.now())

    url = relationship("URL", back_populates="clicks")