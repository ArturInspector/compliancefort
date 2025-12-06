#!/usr/bin/env python3
"""
Compliance Fort - Example Usage
Demonstrates how to use the Compliance Fort API
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def print_response(title: str, response: requests.Response):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))

def example_create_proof():
    """Example: Create a ZK proof"""
    print("\n🔐 Creating Zero-Knowledge Proof...")
    
    payload = {
        "id": 1,
        "data": 100,
        "secret_key": 7
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/proof/create",
        json=payload
    )
    
    print_response("Create ZK Proof", response)
    return response.json()

def example_verify_proof(proof_data: Dict[str, Any]):
    """Example: Verify a ZK proof"""
    print("\n✅ Verifying Zero-Knowledge Proof...")
    
    payload = {
        "id": proof_data["id"],
        "data": proof_data["data"],
        "proof_r": proof_data["proof_r"],
        "proof_s": proof_data["proof_s"],
        "public_key": proof_data["public_key"]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/proof/verify",
        json=payload
    )
    
    print_response("Verify ZK Proof", response)
    return response.json()

def example_generate_public_key():
    """Example: Generate public key from secret"""
    print("\n🔑 Generating Public Key...")
    
    payload = {
        "secret_key": 7
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/key/generate",
        json=payload
    )
    
    print_response("Generate Public Key", response)
    return response.json()

def example_invalid_proof():
    """Example: Try to verify invalid proof"""
    print("\n❌ Testing Invalid Proof (should fail)...")
    
    payload = {
        "id": 1,
        "data": 100,
        "proof_r": 999,  # Invalid proof
        "proof_s": 888,   # Invalid proof
        "public_key": 17
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/proof/verify",
        json=payload
    )
    
    print_response("Verify Invalid Proof", response)
    return response.json()

def main():
    """Run all examples"""
    print("="*60)
    print("  Compliance Fort - Example Usage")
    print("="*60)
    
    try:
        # Check health
        health = requests.get(f"{BASE_URL}/health")
        print(f"\n🏥 Health Check: {health.json()['status']}")
        
        # Generate public key
        pub_key_data = example_generate_public_key()
        
        # Create proof
        proof_data = example_create_proof()
        
        # Verify valid proof
        verify_result = example_verify_proof(proof_data)
        
        # Try invalid proof
        invalid_result = example_invalid_proof()
        
        print("\n" + "="*60)
        print("  Examples Complete!")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API")
        print("Make sure the API server is running:")
        print("  make run")
        print("  or")
        print("  docker-compose up")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()

