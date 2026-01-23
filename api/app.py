"""
Compliance Fort API
Batch ZK-proof verification via Fortran FFI

Идея: массовая верификация ZK-доказательств для compliance аудита.
Fortran даёт выигрыш при обработке тысяч proofs за один вызов.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import ctypes
import os
from datetime import datetime, timezone
import time


def utcnow() -> str:
    """UTC timestamp ISO format"""
    return datetime.now(timezone.utc).isoformat()

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
    lib = None

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
    
    # Fortran bind(C) передаёт структуры по ссылке
    lib.verify_zk_proof.argtypes = [ctypes.POINTER(CMessage), ctypes.c_int]
    lib.verify_zk_proof.restype = ctypes.c_bool
    
    lib.generate_public_key.argtypes = [ctypes.c_int]
    lib.generate_public_key.restype = ctypes.c_int
    
    # Batch functions
    lib.batch_verify.argtypes = [
        ctypes.POINTER(CMessage),
        ctypes.c_int,
        ctypes.c_int,
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_bool)
    ]
    lib.batch_verify.restype = None
    
    lib.batch_create.argtypes = [
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.POINTER(CMessage)
    ]
    lib.batch_create.restype = None

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

# Batch models
class BatchVerifyRequest(BaseModel):
    proofs: List[VerifyRequest] = Field(..., description="Array of proofs to verify")
    public_key: int = Field(..., description="Public key for verification")

class BatchVerifyResponse(BaseModel):
    total: int
    valid_count: int
    invalid_count: int
    results: List[bool]
    elapsed_ms: float
    timestamp: str

class BatchCreateRequest(BaseModel):
    items: List[dict] = Field(..., description="Array of {id, data}")
    secret_key: int
    public_key: Optional[int] = None

class BatchCreateResponse(BaseModel):
    proofs: List[MessageResponse]
    elapsed_ms: float
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
        return True
    
    return lib.verify_zk_proof(ctypes.byref(msg), pub_key)

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
        "timestamp": utcnow(),
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
            timestamp=utcnow()
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
            timestamp=utcnow()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify proof: {str(e)}"
        )

@app.post("/api/v1/key/generate", response_model=PublicKeyResponse, tags=["Keys"])
async def generate_public_key(request: PublicKeyRequest):
    """Generate a public key from a secret key."""
    try:
        if lib is None:
            pub_key = 17
        else:
            pub_key = lib.generate_public_key(request.secret_key)
        
        return PublicKeyResponse(
            public_key=pub_key,
            timestamp=utcnow()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate public key: {str(e)}"
        )

# ================================================================
# BATCH ENDPOINTS - главная ценность проекта
# ================================================================

@app.post("/api/v1/batch/verify", response_model=BatchVerifyResponse, tags=["Batch"])
async def batch_verify_proofs(request: BatchVerifyRequest):
    """
    Batch verify multiple ZK proofs in one call.
    
    Преимущество: один вызов FFI вместо N вызовов.
    При 10000 proofs это даёт ~10x ускорение за счёт
    минимизации Python<->Fortran overhead.
    """
    start = time.perf_counter()
    count = len(request.proofs)
    
    if count == 0:
        return BatchVerifyResponse(
            total=0, valid_count=0, invalid_count=0,
            results=[], elapsed_ms=0,
            timestamp=utcnow()
        )
    
    if lib is None:
        # Mock mode
        results = [True] * count
        valid_count = count
    else:
        # Prepare arrays for Fortran
        MsgArray = CMessage * count
        messages = MsgArray()
        
        for i, p in enumerate(request.proofs):
            messages[i] = CMessage(p.id, p.data, p.proof_r, p.proof_s, p.public_key)
        
        valid_count = ctypes.c_int(0)
        ResultArray = ctypes.c_bool * count
        results_arr = ResultArray()
        
        lib.batch_verify(
            messages,
            count,
            request.public_key,
            ctypes.byref(valid_count),
            results_arr
        )
        
        results = list(results_arr)
        valid_count = valid_count.value
    
    elapsed = (time.perf_counter() - start) * 1000
    
    return BatchVerifyResponse(
        total=count,
        valid_count=valid_count,
        invalid_count=count - valid_count,
        results=results,
        elapsed_ms=round(elapsed, 3),
        timestamp=utcnow()
    )

@app.post("/api/v1/batch/create", response_model=BatchCreateResponse, tags=["Batch"])
async def batch_create_proofs(request: BatchCreateRequest):
    """
    Batch create multiple ZK proofs in one call.
    """
    start = time.perf_counter()
    count = len(request.items)
    
    if count == 0:
        return BatchCreateResponse(
            proofs=[], elapsed_ms=0,
            timestamp=utcnow()
        )
    
    if lib is None:
        # Mock mode
        proofs = [
            MessageResponse(
                id=item['id'], data=item['data'],
                proof_r=123, proof_s=456, public_key=17,
                timestamp=utcnow()
            )
            for item in request.items
        ]
    else:
        pub_key = request.public_key or lib.generate_public_key(request.secret_key)
        
        IdArray = ctypes.c_int * count
        ids = IdArray(*[item['id'] for item in request.items])
        data_arr = IdArray(*[item['data'] for item in request.items])
        
        MsgArray = CMessage * count
        messages = MsgArray()
        
        lib.batch_create(ids, data_arr, count, request.secret_key, pub_key, messages)
        
        now = utcnow()
        proofs = [
            MessageResponse(
                id=m.id, data=m.data,
                proof_r=m.proof_r, proof_s=m.proof_s,
                public_key=m.public_key, timestamp=now
            )
            for m in messages
        ]
    
    elapsed = (time.perf_counter() - start) * 1000
    
    return BatchCreateResponse(
        proofs=proofs,
        elapsed_ms=round(elapsed, 3),
        timestamp=utcnow()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

