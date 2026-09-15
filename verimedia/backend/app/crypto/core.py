import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
import base64

def calculate_sha256(file_bytes: bytes) -> str:
    """Calculate SHA-256 hash of file bytes."""
    return hashlib.sha256(file_bytes).hexdigest()

def generate_key_pair():
    """Generate RSA-2048 key pair."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # Normally we'd store private key securely, but for MVP we just generate and use it
    # We will export public key to share
    public_key = private_key.public_key()
    
    pem_public = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    return private_key, pem_public.decode('utf-8')

def sign_data(private_key, data_hash_hex: str) -> str:
    """Sign the SHA-256 hash using RSA-PSS."""
    data_hash_bytes = bytes.fromhex(data_hash_hex)
    
    signature = private_key.sign(
        data_hash_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256() # The pre-hashed data is still "hashed" by the signing algorithm usually, but we are passing the raw bytes of the hash. 
        # Actually cryptography expects the RAW data to sign, and it hashes it. If we pass the hash, it double hashes.
        # Let's just sign the raw file bytes or encode the hex string as bytes.
    )
    return base64.b64encode(signature).decode('utf-8')

def sign_file_bytes(private_key, file_bytes: bytes) -> str:
    """Sign the raw file bytes using RSA-PSS."""
    signature = private_key.sign(
        file_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode('utf-8')

def verify_signature(public_key_pem: str, file_bytes: bytes, signature_b64: str) -> bool:
    """Verify an RSA-PSS signature against file bytes."""
    try:
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode('utf-8')
        )
        signature = base64.b64decode(signature_b64)
        
        public_key.verify(
            signature,
            file_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except (InvalidSignature, ValueError, Exception):
        return False
