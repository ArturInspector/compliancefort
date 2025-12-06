# Multi-stage build for Compliance Fort
FROM gcc:latest AS fortran-builder

# Install Fortran compiler
RUN apt-get update && apt-get install -y \
    gfortran \
    && rm -rf /var/lib/apt/lists/*

# Build Fortran library
WORKDIR /build
COPY src/compliance_fort.f90 .
RUN mkdir -p lib && \
    gfortran -Wall -Wextra -O3 -fPIC -shared -o lib/libcompliance_fort.so compliance_fort.f90

# Python API stage
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgfortran5 \
    && rm -rf /var/lib/apt/lists/*

# Copy Fortran library
COPY --from=fortran-builder /build/lib/libcompliance_fort.so /app/lib/

# Copy Python API
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/ ./api/

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run API
CMD ["python", "-m", "uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]


