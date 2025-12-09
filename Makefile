# Compliance Fort - Production Build System

FC = gfortran
FFLAGS = -Wall -Wextra -O3 -fPIC -shared
PYTHON = python3

# Directories
SRC_DIR = src
LIB_DIR = lib
API_DIR = api
BUILD_DIR = build

# Targets
LIB_NAME = libcompliance_fort.so
LIB_SOURCE = $(SRC_DIR)/compliance_fort.f90
LIB_TARGET = $(LIB_DIR)/$(LIB_NAME)

.PHONY: all clean lib api docker-build docker-run test install

all: lib api

# Build Fortran library
lib: $(LIB_DIR) $(LIB_TARGET)

$(LIB_DIR):
	mkdir -p $(LIB_DIR)

$(LIB_TARGET): $(LIB_SOURCE)
	@echo "🔨 Building Fortran library..."
	$(FC) $(FFLAGS) -o $(LIB_TARGET) $(LIB_SOURCE)
	@echo "✅ Library built: $(LIB_TARGET)"

# Install Python dependencies
api:
	@echo "📦 Installing Python dependencies..."
	cd $(API_DIR) && $(PYTHON) -m pip install -r requirements.txt
	@echo "✅ Python dependencies installed"

# Run API server
run:
	@echo "🚀 Starting Compliance Fort API..."
	cd $(API_DIR) && $(PYTHON) app.py

# Run tests
test:
	@echo "🧪 Running tests..."
	cd $(API_DIR) && $(PYTHON) -m pytest tests/ -v

# Docker build
docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t compliance-fort:latest .

# Docker run
docker-run:
	@echo "🐳 Running Docker container..."
	docker run -p 8000:8000 compliance-fort:latest

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf $(LIB_DIR) $(BUILD_DIR) *.mod *.o
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	@echo "✅ Clean complete"

# Install (development)
install: lib api
	@echo "✅ Compliance Fort installed successfully!"
	@echo ""
	@echo "To start the API server:"
	@echo "  make run"
	@echo ""
	@echo "Or use Docker:"
	@echo "  make docker-build"
	@echo "  make docker-run"
