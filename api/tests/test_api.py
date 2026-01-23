"""
Tests for Compliance Fort API
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

client = TestClient(app)

def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Compliance Fort"
    assert data["status"] == "operational"

def test_health():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data

def test_generate_public_key():
    """Test public key generation"""
    response = client.post(
        "/api/v1/key/generate",
        json={"secret_key": 7}
    )
    assert response.status_code == 200
    data = response.json()
    assert "public_key" in data
    assert "timestamp" in data

def test_create_proof():
    """Test ZK proof creation"""
    response = client.post(
        "/api/v1/proof/create",
        json={
            "id": 1,
            "data": 100,
            "secret_key": 7
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "proof_r" in data
    assert "proof_s" in data
    assert "public_key" in data

def test_verify_proof():
    """Test ZK proof verification"""
    # First create a proof
    create_response = client.post(
        "/api/v1/proof/create",
        json={
            "id": 1,
            "data": 100,
            "secret_key": 7
        }
    )
    proof_data = create_response.json()
    
    # Then verify it
    verify_response = client.post(
        "/api/v1/proof/verify",
        json={
            "id": proof_data["id"],
            "data": proof_data["data"],
            "proof_r": proof_data["proof_r"],
            "proof_s": proof_data["proof_s"],
            "public_key": proof_data["public_key"]
        }
    )
    assert verify_response.status_code == 200
    verify_data = verify_response.json()
    assert verify_data["valid"] == True

def test_verify_invalid_proof():
    """Test verification of invalid proof"""
    response = client.post(
        "/api/v1/proof/verify",
        json={
            "id": 1,
            "data": 100,
            "proof_r": 999,
            "proof_s": 888,
            "public_key": 17
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "valid" in data


def test_batch_create():
    """Test batch proof creation"""
    response = client.post(
        "/api/v1/batch/create",
        json={
            "secret_key": 7,
            "items": [
                {"id": 1, "data": 10},
                {"id": 2, "data": 20},
                {"id": 3, "data": 30}
            ]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["proofs"]) == 3
    assert "elapsed_ms" in data


def test_batch_verify():
    """Test batch proof verification"""
    # Create proofs first
    create_resp = client.post(
        "/api/v1/batch/create",
        json={
            "secret_key": 7,
            "items": [
                {"id": 1, "data": 10},
                {"id": 2, "data": 20}
            ]
        }
    )
    proofs = create_resp.json()["proofs"]
    pub_key = proofs[0]["public_key"]
    
    # Verify batch
    verify_resp = client.post(
        "/api/v1/batch/verify",
        json={
            "public_key": pub_key,
            "proofs": [
                {
                    "id": p["id"],
                    "data": p["data"],
                    "proof_r": p["proof_r"],
                    "proof_s": p["proof_s"],
                    "public_key": p["public_key"]
                }
                for p in proofs
            ]
        }
    )
    assert verify_resp.status_code == 200
    data = verify_resp.json()
    assert data["total"] == 2
    assert data["valid_count"] == 2
    assert "elapsed_ms" in data

