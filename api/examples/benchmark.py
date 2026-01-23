#!/usr/bin/env python3
"""
Benchmark: Batch vs Single operations

Демонстрирует преимущество batch-вызовов FFI.
"""

import requests
import time
import sys

BASE_URL = "http://localhost:8000"

def benchmark_single(count: int, secret_key: int = 7) -> float:
    """Создать и проверить proofs по одному"""
    
    # Получаем public key
    resp = requests.post(f"{BASE_URL}/api/v1/key/generate", json={"secret_key": secret_key})
    pub_key = resp.json()["public_key"]
    
    proofs = []
    
    # Создаём proofs по одному
    start = time.perf_counter()
    for i in range(count):
        resp = requests.post(f"{BASE_URL}/api/v1/proof/create", json={
            "id": i + 1,
            "data": (i + 1) * 10,
            "secret_key": secret_key
        })
        proofs.append(resp.json())
    
    # Проверяем proofs по одному
    for p in proofs:
        requests.post(f"{BASE_URL}/api/v1/proof/verify", json={
            "id": p["id"],
            "data": p["data"],
            "proof_r": p["proof_r"],
            "proof_s": p["proof_s"],
            "public_key": p["public_key"]
        })
    
    return (time.perf_counter() - start) * 1000

def benchmark_batch(count: int, secret_key: int = 7) -> tuple[float, float]:
    """Создать и проверить proofs одним вызовом"""
    
    # Batch create
    items = [{"id": i + 1, "data": (i + 1) * 10} for i in range(count)]
    
    start = time.perf_counter()
    resp = requests.post(f"{BASE_URL}/api/v1/batch/create", json={
        "secret_key": secret_key,
        "items": items
    })
    create_result = resp.json()
    
    # Batch verify
    proofs = [{
        "id": p["id"],
        "data": p["data"],
        "proof_r": p["proof_r"],
        "proof_s": p["proof_s"],
        "public_key": p["public_key"]
    } for p in create_result["proofs"]]
    
    resp = requests.post(f"{BASE_URL}/api/v1/batch/verify", json={
        "public_key": create_result["proofs"][0]["public_key"],
        "proofs": proofs
    })
    verify_result = resp.json()
    
    total = (time.perf_counter() - start) * 1000
    fortran_time = create_result["elapsed_ms"] + verify_result["elapsed_ms"]
    
    return total, fortran_time

def main():
    counts = [10, 50, 100, 500]
    
    print("=" * 60)
    print("  Benchmark: Batch vs Single FFI calls")
    print("=" * 60)
    print()
    
    # Check API
    try:
        resp = requests.get(f"{BASE_URL}/health")
        lib_loaded = resp.json().get("library_loaded", False)
        print(f"API Status: OK (Fortran lib: {'loaded' if lib_loaded else 'mock mode'})")
    except:
        print("Error: API not running. Start with: make run")
        sys.exit(1)
    
    print()
    print(f"{'Count':<10} {'Single(ms)':<15} {'Batch(ms)':<15} {'Speedup':<10}")
    print("-" * 50)
    
    for count in counts:
        single_time = benchmark_single(count)
        batch_time, fortran_time = benchmark_batch(count)
        speedup = single_time / batch_time if batch_time > 0 else 0
        
        print(f"{count:<10} {single_time:<15.1f} {batch_time:<15.1f} {speedup:<10.1f}x")
    
    print()
    print("Вывод:")
    print("- Single: N HTTP-запросов + N вызовов FFI")
    print("- Batch: 2 HTTP-запроса + 2 вызова FFI (create + verify)")
    print("- Speedup растёт с количеством proofs")

if __name__ == "__main__":
    main()
