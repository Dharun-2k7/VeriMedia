from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.models.database import Base

class Media(Base):
    __tablename__ = "media"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(512), index=True)
    file_hash = Column(String(64), index=True)
    file_type = Column(String(128))
    file_size = Column(Integer)
    storage_path = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Signature(Base):
    __tablename__ = "signatures"
    
    id = Column(Integer, primary_key=True, index=True)
    media_id = Column(Integer, index=True)
    algorithm = Column(String(128))
    signature = Column(Text)
    public_key = Column(Text)
    signed_at = Column(DateTime(timezone=True), server_default=func.now())

class Verification(Base):
    __tablename__ = "verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    media_id = Column(Integer, index=True)
    calculated_hash = Column(String(64))
    signature_valid = Column(Boolean)
    ai_probability = Column(Float)
    ai_assessment = Column(String(128))
    ai_flags = Column(Text, default="[]")   # JSON list of triggered signal labels
    overall_status = Column(String(128))
    verified_at = Column(DateTime(timezone=True), server_default=func.now())

