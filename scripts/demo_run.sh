#!/bin/bash
# Demo script to test the complete AI pipeline

echo "=== Nutrition AI Pipeline Demo ==="
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

# Step 1: Seed nutrition facts database
echo
echo "=== Step 1: Seeding Nutrition Facts Database ==="
python backend/ai/fetch_openfoodfacts.py --seed "paneer,apple,banana,spinach,almonds,white rice,chicken breast,dal,yogurt,oats"

# Step 2: Build FAISS index
echo
echo "=== Step 2: Building FAISS Index ==="
python scripts/build_faiss_index.py

# Step 3: Train Random Forest model
echo
echo "=== Step 3: Training Random Forest Model ==="
python backend/ai/train_rf.py --jsonl data/nutrition_facts.jsonl --seed-db

# Step 4: Start the API server
echo
echo "=== Step 4: Starting API Server ==="
echo "Starting FastAPI server in background..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
SERVER_PID=$!

# Wait for server to start
echo "Waiting for server to start..."
sleep 10

# Step 5: Test the API endpoints
echo
echo "=== Step 5: Testing API Endpoints ==="

# Test health check
echo "Testing health check..."
curl -s http://localhost:8000/ai/health/ | python -m json.tool

echo
echo "Testing nutrition facts retrieval..."
curl -s "http://localhost:8000/ai/get-nutrition-facts/?q=paneer&k=3" | python -m json.tool

echo
echo "Testing food classification..."
curl -s -X POST "http://localhost:8000/ai/classify-food/" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "food_name": "paneer", "quantity_g": 100}' | python -m json.tool

echo
echo "Testing explanation generation..."
curl -s -X POST "http://localhost:8000/ai/generate-explanation/" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "food_name": "paneer", "quantity_g": 100, "extra_context": ""}' | python -m json.tool

echo
echo "Testing chat endpoint..."
curl -s -X POST "http://localhost:8000/ai/chat/" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "message": "What should I eat for breakfast?", "food_context": null}' | python -m json.tool

echo
echo "=== Demo Completed Successfully! ==="
echo "API server is running on http://localhost:8000"
echo "API documentation available at http://localhost:8000/docs"
echo
echo "To stop the server, run: kill $SERVER_PID"
echo "Or press Ctrl+C to stop this script"

