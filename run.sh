#!/bin/bash
# Main run script for the nutrition AI application

echo "=== Nutrition AI Application Setup ==="
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p data models backend/indexes

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env file with your API keys and configuration"
fi

# Seed nutrition facts if not already done
if [ ! -f "data/nutrition_facts.jsonl" ]; then
    echo "Seeding nutrition facts database..."
    python backend/ai/fetch_openfoodfacts.py --seed "paneer,apple,banana,spinach,almonds,white rice,chicken breast,dal,yogurt,oats"
fi

# Build FAISS index if not already done
if [ ! -f "backend/indexes/nutrition.index" ]; then
    echo "Building FAISS index..."
    python scripts/build_faiss_index.py
fi

# Train Random Forest model if not already done
if [ ! -f "models/random_forest_model.pkl" ]; then
    echo "Training Random Forest model..."
    python backend/ai/train_rf.py --jsonl data/nutrition_facts.jsonl
fi

# Start the application
echo
echo "Starting FastAPI application..."
echo "API will be available at http://localhost:8000"
echo "API documentation at http://localhost:8000/docs"
echo
echo "Press Ctrl+C to stop the server"
echo

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

