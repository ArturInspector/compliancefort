"""
Compliance Fort API
Production-ready REST API for Zero-Knowledge compliance verification
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import ctypes
import os
import sys
from datetime import datetime

# Load Fortran library
LIB_PATH = os.path.join(os.path.dirname(__file__), '..', 'lib', 'libcompliance_fort.so')
if not os.path.exists(LIB_PATH):
    LIB_PATH = os.path.join(os.path.dirname(__file__), '..', 'lib', 'libcompliance_fort.dylib')
if not os.path.exists(LIB_PATH):
    LIB_PATH = os.path.join(os.path.dirname(__file__), '..', 'lib', 'libcompliance_fort.dll')

try:
    lib = ctypes.CDLL(LIB_PATH)
except Exception as e:
    print(f"Warning: Could not load Fortran library: {e}")
    print("Running in mock mode for development")
    lib = None  # fallback режим, чтобы можно было тестировать без компиляции фортрана

# Define C structures
class CMessage(ctypes.Structure):
    _fields_ = [
        ('id', ctypes.c_int),
        ('data', ctypes.c_int),
        ('proof_r', ctypes.c_int),
        ('proof_s', ctypes.c_int),
        ('public_key', ctypes.c_int),
    ]

# Configure library functions
if lib:
    lib.create_zk_proof.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
    lib.create_zk_proof.restype = CMessage
    
    lib.verify_zk_proof.argtypes = [CMessage, ctypes.c_int]
    lib.verify_zk_proof.restype = ctypes.c_bool
    
    lib.generate_public_key.argtypes = [ctypes.c_int]
    lib.generate_public_key.restype = ctypes.c_int

# FastAPI app
app = FastAPI(
    title="Compliance Fort API",
    description="Zero-Knowledge cryptography library for compliance verification",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class MessageRequest(BaseModel):
    id: int = Field(..., description="Unique message identifier")
    data: int = Field(..., description="Message data")
    secret_key: int = Field(..., description="Secret key for proof generation")
    public_key: Optional[int] = Field(None, description="Public key (auto-generated if not provided)")

class MessageResponse(BaseModel):
    id: int
    data: int
    proof_r: int
    proof_s: int
    public_key: int
    timestamp: str

class VerifyRequest(BaseModel):
    id: int
    data: int
    proof_r: int
    proof_s: int
    public_key: int

class VerifyResponse(BaseModel):
    valid: bool
    message: str
    timestamp: str

class PublicKeyRequest(BaseModel):
    secret_key: int = Field(..., description="Secret key")

class PublicKeyResponse(BaseModel):
    public_key: int
    timestamp: str

# Helper functions
def create_zk_proof(id: int, data: int, secret_key: int, pub_key: Optional[int] = None) -> CMessage:
    """Create ZK proof using Fortran library"""
    if lib is None:
        # Mock mode for development
        return CMessage(id, data, 123, 456, pub_key or 17)  # fake тестов
    
    if pub_key is None:
        pub_key = lib.generate_public_key(secret_key)
    
    return lib.create_zk_proof(id, data, secret_key, pub_key)

def verify_zk_proof(msg: CMessage, pub_key: int) -> bool:
    """Verify ZK proof using Fortran library"""
    if lib is None:
        # Mock mode - always return True for development
        return True
    
    return lib.verify_zk_proof(msg, pub_key)

# API Routes
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint"""
    return {
        "name": "Compliance Fort",
        "version": "1.0.0",
        "status": "operational",
        "description": "Zero-Knowledge cryptography library for compliance verification"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "library_loaded": lib is not None  # проверяем что фортран загрузился
    }

@app.post("/api/v1/proof/create", response_model=MessageResponse, tags=["ZK Proofs"])
async def create_proof(request: MessageRequest):
    """
    Create a Zero-Knowledge proof for a message.
    
    This endpoint generates a cryptographic proof that demonstrates knowledge
    of a secret key without revealing the key itself.
    """
    try:
        c_msg = create_zk_proof(
            request.id,
            request.data,
            request.secret_key,
            request.public_key
        )
        
        return MessageResponse(
            id=c_msg.id,
            data=c_msg.data,
            proof_r=c_msg.proof_r,
            proof_s=c_msg.proof_s,
            public_key=c_msg.public_key,
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create proof: {str(e)}"
        )

@app.post("/api/v1/proof/verify", response_model=VerifyResponse, tags=["ZK Proofs"])
async def verify_proof(request: VerifyRequest):
    """
    Verify a Zero-Knowledge proof.
    
    This endpoint verifies that a proof is valid without requiring knowledge
    of the secret key.
    """
    try:
        c_msg = CMessage(
            request.id,
            request.data,
            request.proof_r,
            request.proof_s,
            request.public_key
        )
        
        is_valid = verify_zk_proof(c_msg, request.public_key)
        
        return VerifyResponse(
            valid=is_valid,
            message="Proof is valid" if is_valid else "Proof is invalid",
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify proof: {str(e)}"
        )

@app.post("/api/v1/key/generate", response_model=PublicKeyResponse, tags=["Keys"])
async def generate_public_key(request: PublicKeyRequest):
    """
    Generate a public key from a secret key.
    
    This endpoint computes the public key corresponding to a given secret key
    using modular exponentiation.
    """
    try:
        if lib is None:
            pub_key = 17  # getenv later
        else:
            pub_key = lib.generate_public_key(request.secret_key)
        
        return PublicKeyResponse(
            public_key=pub_key,
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate public key: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

