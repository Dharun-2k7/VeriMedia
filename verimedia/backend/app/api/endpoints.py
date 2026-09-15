from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from app.models import database, models
from app.schemas import schemas
from app.crypto import core
from app.detection import analyzer
import os
import uuid
import json

router = APIRouter()

STORAGE_DIR = "../storage/files"
os.makedirs(STORAGE_DIR, exist_ok=True)

@router.post("/media/upload", response_model=schemas.MediaResponse)
async def upload_media(file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    # 1. Read bytes & calculate hash
    file_bytes = await file.read()
    file_hash = core.calculate_sha256(file_bytes)
    
    # 2. Store file
    safe_filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = os.path.join(STORAGE_DIR, safe_filename)
    
    with open(file_path, "wb") as f:
        f.write(file_bytes)
        
    # 3. Save to DB
    db_media = models.Media(
        filename=file.filename,
        file_hash=file_hash,
        file_type=file.content_type or "unknown",
        file_size=len(file_bytes),
        storage_path=file_path
    )
    db.add(db_media)
    db.commit()
    db.refresh(db_media)
    
    return db_media

@router.post("/media/sign", response_model=schemas.SignResponse)
async def sign_media(file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    file_bytes = await file.read()
    file_hash = core.calculate_sha256(file_bytes)
    
    # Generate RSA keys
    private_key, public_key_pem = core.generate_key_pair()
    
    # Sign file bytes
    signature_b64 = core.sign_file_bytes(private_key, file_bytes)
    
    # Save media
    safe_filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = os.path.join(STORAGE_DIR, safe_filename)
    with open(file_path, "wb") as f:
        f.write(file_bytes)
        
    db_media = models.Media(
        filename=file.filename,
        file_hash=file_hash,
        file_type=file.content_type or "unknown",
        file_size=len(file_bytes),
        storage_path=file_path
    )
    db.add(db_media)
    db.commit()
    db.refresh(db_media)
    
    # Save signature
    db_signature = models.Signature(
        media_id=db_media.id,
        algorithm="RSA-2048 / RSA-PSS / SHA-256",
        signature=signature_b64,
        public_key=public_key_pem
    )
    db.add(db_signature)
    db.commit()
    db.refresh(db_signature)
    
    return schemas.SignResponse(
        media_id=db_media.id,
        hash=file_hash,
        algorithm=db_signature.algorithm,
        signature=signature_b64,
        public_key=public_key_pem,
        signed_at=db_signature.signed_at
    )

@router.post("/media/verify", response_model=schemas.VerificationReport)
async def verify_media(
    file: UploadFile = File(...),
    signature: str = Form(...),
    public_key: str = Form(...),
    db: Session = Depends(database.get_db)
):
    file_bytes = await file.read()
    current_hash = core.calculate_sha256(file_bytes)
    
    # Cryptographic Verification
    is_valid_sig = core.verify_signature(public_key, file_bytes, signature)
    
    # Find matching signature in DB to get original hash (optional, but good for reporting)
    db_signature = db.query(models.Signature).filter(models.Signature.signature == signature).first()
    db_media = db.query(models.Media).filter(models.Media.id == db_signature.media_id).first() if db_signature else None
    
    original_hash = db_media.file_hash if db_media else None
    hash_match = (original_hash == current_hash) if original_hash else False
    
    # Real AI Analysis
    ai_result = analyzer.analyze_media(file_bytes, file.content_type or "unknown")
    ai_prob = ai_result["manipulation_probability"] / 100.0
    ai_assess = ai_result["assessment"]
    ai_flags = ai_result.get("flags", [])
    ai_signals = ai_result.get("signals", {})
    
    # Result Logic Interpretation
    if is_valid_sig and ai_prob < 0.5:
        overall = "VERIFIED / LOW RISK"
    elif is_valid_sig and ai_prob >= 0.5:
        overall = "SIGNED BUT AI-SUSPICIOUS"
    elif not is_valid_sig and db_signature and ai_prob < 0.5:
        overall = "FILE MODIFIED AFTER SIGNING"
    elif not is_valid_sig and db_signature and ai_prob >= 0.5:
        overall = "HIGHLY SUSPICIOUS"
    elif not db_signature and ai_prob < 0.5:
        overall = "UNVERIFIED"
    else:
        overall = "SUSPICIOUS"
        
    if not is_valid_sig and db_signature:
        overall = "MEDIA TAMPERED" # For tamper test
        
    db_verification = models.Verification(
        media_id=db_media.id if db_media else None,
        calculated_hash=current_hash,
        signature_valid=is_valid_sig,
        ai_probability=ai_prob,
        ai_assessment=ai_assess,
        ai_flags=json.dumps(ai_flags),
        overall_status=overall
    )
    db.add(db_verification)
    db.commit()
    db.refresh(db_verification)
    
    return schemas.VerificationReport(
        id=db_verification.id,
        media_id=db_verification.media_id,
        filename=file.filename,
        calculated_hash=current_hash,
        original_hash=original_hash,
        hash_match=hash_match,
        signature_valid=is_valid_sig,
        ai_probability=ai_prob,
        ai_assessment=ai_assess,
        ai_flags=ai_flags,
        ai_signals=ai_signals,
        overall_status=overall,
        verified_at=db_verification.verified_at
    )

@router.get("/verifications", response_model=list[schemas.VerificationReport])
def get_verifications(db: Session = Depends(database.get_db)):
    verifications = db.query(models.Verification).order_by(models.Verification.id.desc()).all()
    results = []
    for v in verifications:
        media = db.query(models.Media).filter(models.Media.id == v.media_id).first()
        try:
            flags = json.loads(v.ai_flags) if v.ai_flags else []
        except Exception:
            flags = []
        results.append(schemas.VerificationReport(
            id=v.id,
            media_id=v.media_id,
            filename=media.filename if media else "Unknown",
            calculated_hash=v.calculated_hash,
            original_hash=media.file_hash if media else None,
            hash_match=(media.file_hash == v.calculated_hash) if media else False,
            signature_valid=v.signature_valid,
            ai_probability=v.ai_probability,
            ai_assessment=v.ai_assessment,
            ai_flags=flags,
            overall_status=v.overall_status,
            verified_at=v.verified_at
        ))
    return results

@router.get("/verifications/{id}", response_model=schemas.VerificationReport)
def get_verification(id: int, db: Session = Depends(database.get_db)):
    v = db.query(models.Verification).filter(models.Verification.id == id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Not found")
    try:
        flags = json.loads(v.ai_flags) if v.ai_flags else []
    except Exception:
        flags = []
    media = db.query(models.Media).filter(models.Media.id == v.media_id).first()
    return schemas.VerificationReport(
        id=v.id,
        media_id=v.media_id,
        filename=media.filename if media else "Unknown",
        calculated_hash=v.calculated_hash,
        original_hash=media.file_hash if media else None,
        hash_match=(media.file_hash == v.calculated_hash) if media else False,
        signature_valid=v.signature_valid,
        ai_probability=v.ai_probability,
        ai_assessment=v.ai_assessment,
        ai_flags=flags,
        overall_status=v.overall_status,
        verified_at=v.verified_at
    )

@router.get("/media/{id}/package")
def get_media_package(id: int, db: Session = Depends(database.get_db)):
    # Used to download signed media package for tamper test demo
    media = db.query(models.Media).filter(models.Media.id == id).first()
    signature = db.query(models.Signature).filter(models.Signature.media_id == id).first()
    
    if not media or not signature:
        raise HTTPException(status_code=404, detail="Not found")
        
    return {
        "filename": media.filename,
        "signature": signature.signature,
        "public_key": signature.public_key,
        "original_hash": media.file_hash
    }

@router.get("/media/signed")
def get_signed_media(db: Session = Depends(database.get_db)):
    # Helper to get previously signed media for tamper test UI
    signatures = db.query(models.Signature).all()
    results = []
    for sig in signatures:
        media = db.query(models.Media).filter(models.Media.id == sig.media_id).first()
        if media:
            results.append({
                "id": media.id,
                "filename": media.filename,
                "signed_at": sig.signed_at
            })
    return results

@router.get("/health")
def health_check():
    return {"status": "ok"}
