import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
import base64
import os
import json

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

# ---------------------------------------------------------
# Authority Identity (Oracle Pattern)
# ---------------------------------------------------------
def get_or_create_authority_keys(storage_dir: str):
    """
    Get or create the persistent VeriMedia Authority keypair.
    This identity is used to sign AI Verification Reports (Attestations).
    """
    os.makedirs(storage_dir, exist_ok=True)
    priv_path = os.path.join(storage_dir, "authority_private.pem")
    pub_path = os.path.join(storage_dir, "authority_public.pem")
    
    if os.path.exists(priv_path) and os.path.exists(pub_path):
        with open(priv_path, "rb") as f:
            private_key = serialization.load_pem_private_key(
                f.read(),
                password=None
            )
        with open(pub_path, "r") as f:
            pem_public = f.read()
    else:
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        pem_private = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        pem_public_bytes = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        pem_public = pem_public_bytes.decode('utf-8')
        
        with open(priv_path, "wb") as f:
            f.write(pem_private)
        with open(pub_path, "w") as f:
            f.write(pem_public)
            
    return private_key, pem_public

def sign_json_payload(private_key, payload: dict) -> str:
    """
    Deterministically stringifies a JSON payload and signs it.
    Used for creating AI Analysis Attestations.
    """
    # Use deterministic JSON formatting (sorted keys, no spaces)
    payload_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    payload_bytes = payload_str.encode('utf-8')
    
    signature = private_key.sign(
        payload_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode('utf-8')
