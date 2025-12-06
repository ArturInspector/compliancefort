#!/usr/bin/env python3
"""
Compliance Fort - Integration Example
Shows how to integrate Compliance Fort into your application
"""

import requests
from typing import Optional, Dict, Any

class ComplianceFortClient:
    """Client for Compliance Fort API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def generate_public_key(self, secret_key: int) -> int:
        """Generate public key from secret key"""
        response = self.session.post(
            f"{self.base_url}/api/v1/key/generate",
            json={"secret_key": secret_key}
        )
        response.raise_for_status()
        return response.json()["public_key"]
    
    def create_proof(self, message_id: int, data: int, secret_key: int, 
                     public_key: Optional[int] = None) -> Dict[str, Any]:
        """Create ZK proof for a message"""
        payload = {
            "id": message_id,
            "data": data,
            "secret_key": secret_key
        }
        if public_key:
            payload["public_key"] = public_key
        
        response = self.session.post(
            f"{self.base_url}/api/v1/proof/create",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def verify_proof(self, proof: Dict[str, Any]) -> bool:
        """Verify a ZK proof"""
        response = self.session.post(
            f"{self.base_url}/api/v1/proof/verify",
            json=proof
        )
        response.raise_for_status()
        return response.json()["valid"]


# Example: Financial Transaction Compliance
class TransactionCompliance:
    """Example: Using Compliance Fort for transaction compliance"""
    
    def __init__(self, client: ComplianceFortClient):
        self.client = client
    
    def create_transaction_proof(self, transaction_id: int, amount: int, 
                                  secret_key: int) -> Dict[str, Any]:
        """Create compliance proof for a transaction"""
        return self.client.create_proof(
            message_id=transaction_id,
            data=amount,
            secret_key=secret_key
        )
    
    def verify_transaction(self, proof: Dict[str, Any]) -> bool:
        """Verify transaction compliance"""
        return self.client.verify_proof(proof)


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = ComplianceFortClient()
    
    # Check health
    print("🏥 Health check:", client.health_check())
    
    # Generate keys
    secret_key = 7
    public_key = client.generate_public_key(secret_key)
    print(f"🔑 Generated public key: {public_key}")
    
    # Create transaction proof
    compliance = TransactionCompliance(client)
    proof = compliance.create_transaction_proof(
        transaction_id=1,
        amount=1000,
        secret_key=secret_key
    )
    print(f"🔐 Created proof: {proof['proof_r']}, {proof['proof_s']}")
    
    # Verify transaction
    is_valid = compliance.verify_transaction(proof)
    print(f"✅ Transaction valid: {is_valid}")

