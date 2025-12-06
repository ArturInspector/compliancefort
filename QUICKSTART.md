# 🚀 Compliance Fort - Quick Start Guide

Get up and running in 60 seconds!

## Option 1: Docker (Easiest) ⭐

```bash
# Clone and start
git clone <repo>
cd compliance-fort
docker-compose up --build

# That's it! API is running at http://localhost:8000
```

## Option 2: Local Development

```bash
# 1. Build Fortran library
make lib

# 2. Install Python dependencies
make api

# 3. Start API server
make run

# API running at http://localhost:8000
```

## Test It Out 🧪

### Using curl:

```bash
# Health check
curl http://localhost:8000/health

# Create a ZK proof
curl -X POST http://localhost:8000/api/v1/proof/create \
  -H "Content-Type: application/json" \
  -d '{"id": 1, "data": 100, "secret_key": 7}'

# Verify the proof
curl -X POST http://localhost:8000/api/v1/proof/verify \
  -H "Content-Type: application/json" \
  -d '{
    "id": 1,
    "data": 100,
    "proof_r": 10,
    "proof_s": 15,
    "public_key": 17
  }'
```

### Using Python:

```bash
# Run example script
cd api/examples
python example.py
```

### Using Swagger UI:

1. Open http://localhost:8000/docs
2. Try the endpoints interactively!

## Next Steps 📚

- Read the [full README](README.md)
- Check out [API examples](api/examples/)
- Explore [Swagger docs](http://localhost:8000/docs)

---

**Questions?** Open an issue or check the docs!


