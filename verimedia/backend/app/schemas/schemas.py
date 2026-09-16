from pydantic import BaseModel
from pydantic import ConfigDict
from typing import Optional
from datetime import datetime

class MediaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    file_hash: str
    file_type: str
    file_size: int
    created_at: datetime

class SignResponse(BaseModel):
    media_id: int
    hash: str
    algorithm: str
    signature: str
    public_key: str
    signed_at: datetime

class VerificationReport(BaseModel):
    id: int
    media_id: Optional[int] = None
    filename: str
    calculated_hash: str
    original_hash: Optional[str] = None
    hash_match: bool
    signature_valid: bool
    ai_probability: float
    ai_assessment: str
    ai_flags: Optional[list] = []
    ai_signals: Optional[dict] = {}
    
    # Cryptographic Attestation Fields
    attestation_payload: Optional[dict] = None
    authority_signature: Optional[str] = None
    authority_public_key: Optional[str] = None
    
    overall_status: str
    verified_at: datetime
