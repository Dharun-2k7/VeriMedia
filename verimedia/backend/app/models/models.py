from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.models.database import Base

class Media(Base):
    __tablename__ = "media"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    file_hash = Column(String, index=True)
    file_type = Column(String)
    file_size = Column(Integer)
    storage_path = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Signature(Base):
    __tablename__ = "signatures"
    
    id = Column(Integer, primary_key=True, index=True)
    media_id = Column(Integer, index=True)
    algorithm = Column(String)
    signature = Column(String)
    public_key = Column(String)
    signed_at = Column(DateTime(timezone=True), server_default=func.now())

class Verification(Base):
    __tablename__ = "verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    media_id = Column(Integer, index=True)
    calculated_hash = Column(String)
    signature_valid = Column(Boolean)
    ai_probability = Column(Float)
    ai_assessment = Column(String)
    ai_flags = Column(Text, default="[]")   # JSON list of triggered signal labels
    overall_status = Column(String)
    verified_at = Column(DateTime(timezone=True), server_default=func.now())
