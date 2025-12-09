# Makefile for Data Center Digital Twin
# Provides convenient shortcuts for common operations

.PHONY: help build run stop clean validate train test docker-build docker-run docker-stop

# Default target
help:
	@echo "Data Center Digital Twin - Available Commands"
	@echo "=============================================="
	@echo ""
	@echo "Docker Commands:"
	@echo "  make build          - Build Docker image"
	@echo "  make run            - Run application with Docker"
	@echo "  make stop           - Stop Docker containers"
	@echo "  make logs           - View Docker logs"
	@echo "  make shell          - Open shell in container"
	@echo ""
	@echo "Native Commands:"
	@echo "  make install        - Install Python dependencies"
	@echo "  make init           - Initialize database"
	@echo "  make train          - Train ML optimizer models"
	@echo "  make start          - Run application natively"
	@echo ""
	@echo "Utility Commands:"
	@echo "  make validate       - Validate dataset"
	@echo "  make clean          - Clean generated files"
	@echo "  make clean-all      - Clean everything including models"
	@echo ""
	@echo "Platform-Specific:"
	@echo "  make run-linux      - Run on Linux"
	@echo "  make run-mac        - Run on macOS"
	@echo "  make run-windows    - Run on Windows"

# Docker commands
build:
	@echo "Building Docker image..."
	docker-compose build

run:
	@echo "Starting Data Center Digital Twin with Docker..."
	docker-compose up

stop:
	@echo "Stopping Docker containers..."
	docker-compose down

logs:
	docker-compose logs -f

shell:
	docker-compose run --rm datacenter-twin /bin/bash

# Platform-specific Docker runs
run-linux:
	@echo "Starting on Linux..."
	xhost +local:docker
	docker-compose up

run-mac:
	@echo "Starting on macOS..."
	@echo "Make sure XQuartz is running!"
	docker-compose -f docker-compose.yml -f docker-compose.mac.yml up

run-windows:
	@echo "Starting on Windows..."
	@echo "Make sure VcXsrv is running!"
	docker-compose -f docker-compose.yml -f docker-compose.windows.yml up

# Native installation commands
install:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt

init:
	@echo "Initializing database..."
	python init_db.py

train:
	@echo "Training ML optimizer models (this may take 2-3 minutes)..."
	python train_optimizer.py

start:
	@echo "Starting Data Center Digital Twin..."
	python what_if_engine.py

# Utility commands
validate:
	@echo "Validating dataset..."
	python validate_dataset.py data/datacenter_full_state_list.json

clean:
	@echo "Cleaning generated files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name "*.log" -delete 2>/dev/null || true
	rm -rf .pytest_cache 2>/dev/null || true
	rm -rf .coverage 2>/dev/null || true
	@echo "Cleanup complete!"

clean-all: clean
	@echo "Cleaning database and models..."
	rm -rf db/*.db 2>/dev/null || true
	rm -rf models/*.joblib 2>/dev/null || true
	@echo "Complete cleanup done!"

# Docker cleanup
docker-clean:
	@echo "Cleaning Docker resources..."
	docker-compose down -v
	docker system prune -f

# Development commands
dev-setup: install init train
	@echo "Development environment ready!"

# Quick start (all-in-one)
quick-start: build run

# Test commands (placeholder)
test:
	@echo "Running tests..."
	@echo "TODO: Implement test suite"
	# pytest tests/
