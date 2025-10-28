# Makefile for Nutrition AI Application

.PHONY: help install setup seed build-index train-model run test clean demo

# Default target
help:
	@echo "Nutrition AI Application - Available Commands:"
	@echo "  install     - Install dependencies"
	@echo "  setup       - Complete setup (install + seed + build + train)"
	@echo "  seed        - Seed nutrition facts database"
	@echo "  build-index - Build FAISS index"
	@echo "  train-model - Train Random Forest model"
	@echo "  run         - Start the application"
	@echo "  test        - Run tests"
	@echo "  demo        - Run demo script"
	@echo "  clean       - Clean up generated files"

# Install dependencies
install:
	python -m venv venv
	venv/bin/pip install -r requirements.txt

# Setup everything
setup: install seed build-index train-model
	@echo "Setup completed successfully!"

# Seed nutrition facts database
seed:
	python backend/ai/fetch_openfoodfacts.py --seed "paneer,apple,banana,spinach,almonds,white rice,chicken breast,dal,yogurt,oats"

# Build FAISS index
build-index:
	python scripts/build_faiss_index.py

# Train Random Forest model
train-model:
	python backend/ai/train_rf.py --jsonl data/nutrition_facts.jsonl

# Run the application
run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run tests
test:
	python -m pytest tests/ -v

# Run demo
demo:
	bash scripts/demo_run.sh

# Clean up
clean:
	rm -rf venv/
	rm -rf data/
	rm -rf models/
	rm -rf backend/indexes/
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete

