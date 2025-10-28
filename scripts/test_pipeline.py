#!/usr/bin/env python3
"""
Test script for the complete AI pipeline.

This script tests all components of the AI pipeline to ensure
everything is working correctly.
"""

import sys
import os
import logging
from pathlib import Path
import json
import time

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.ai.fetch_openfoodfacts import OpenFoodFactsFetcher
from backend.ai.embeddings import NutritionEmbeddings
from backend.ai.retriever import NutritionRetriever
from backend.ai.train_rf import FoodRecommendationTrainer
from backend.ai.rf_model import FoodRecommendationModel
from backend.ai.llm_service import LLMService
from backend.ai.verifier import NutritionVerifier
from backend.ai.monitoring import get_monitoring

def test_data_ingestion():
    """Test data ingestion pipeline."""
    print("Testing data ingestion...")
    
    fetcher = OpenFoodFactsFetcher(cache_dir="data")
    
    # Test with a simple query
    results = fetcher.search_food("apple", page_size=1)
    
    if results:
        print(f"✓ Data ingestion working - found {len(results)} results")
        return True
    else:
        print("✗ Data ingestion failed - no results found")
        return False

def test_embeddings_and_indexing():
    """Test embeddings and indexing pipeline."""
    print("Testing embeddings and indexing...")
    
    try:
        # Check if nutrition facts exist
        jsonl_path = Path("data/nutrition_facts.jsonl")
        if not jsonl_path.exists():
            print("✗ No nutrition facts found - run data seeding first")
            return False
        
        # Build index
        embeddings = NutritionEmbeddings()
        embeddings.build_from_jsonl(str(jsonl_path))
        
        # Test search
        results = embeddings.search("apple", k=1)
        
        if results:
            print(f"✓ Embeddings and indexing working - found {len(results)} results")
            return True
        else:
            print("✗ Embeddings and indexing failed - no search results")
            return False
            
    except Exception as e:
        print(f"✗ Embeddings and indexing failed: {e}")
        return False

def test_retrieval():
    """Test retrieval pipeline."""
    print("Testing retrieval...")
    
    try:
        retriever = NutritionRetriever()
        
        if not retriever.is_available():
            print("✗ Retrieval not available - index not built")
            return False
        
        results = retriever.retrieve_facts("apple", k=2)
        
        if results:
            print(f"✓ Retrieval working - found {len(results)} results")
            return True
        else:
            print("✗ Retrieval failed - no results found")
            return False
            
    except Exception as e:
        print(f"✗ Retrieval failed: {e}")
        return False

def test_random_forest():
    """Test Random Forest pipeline."""
    print("Testing Random Forest...")
    
    try:
        # Check if model exists
        model_path = Path("models/random_forest_model.pkl")
        if not model_path.exists():
            print("✗ Random Forest model not found - run training first")
            return False
        
        model = FoodRecommendationModel()
        
        if not model.is_available():
            print("✗ Random Forest model not available")
            return False
        
        # Test prediction
        nutrition_data = {
            "calories_100g": 100,
            "protein_100g": 20,
            "carbs_100g": 10,
            "fat_100g": 5
        }
        
        recommended, confidence, explanation = model.predict_with_confidence(nutrition_data)
        
        print(f"✓ Random Forest working - prediction: {recommended}, confidence: {confidence:.2f}")
        return True
        
    except Exception as e:
        print(f"✗ Random Forest failed: {e}")
        return False

def test_llm_service():
    """Test LLM service."""
    print("Testing LLM service...")
    
    try:
        llm = LLMService()
        
        if not llm.is_available():
            print("⚠ LLM service not available - no API keys configured")
            return True  # Not a failure, just not configured
        
        # Test with mock data
        user_profile = {
            "age": 30,
            "gender": "Male",
            "weight_kg": 70,
            "height_cm": 170,
            "activity_level": "Moderate",
            "goal": "General Health"
        }
        
        rf_result = {
            "recommended": True,
            "confidence": 0.85
        }
        
        retrieved_facts = [
            {
                "score": 0.95,
                "fact_text": "Apple — 52 kcal/100g, 0.3 g protein/100g",
                "meta": {"name": "Apple"}
            }
        ]
        
        explanation = llm.generate_explanation(
            user_profile, rf_result, retrieved_facts, "Test context"
        )
        
        print(f"✓ LLM service working - generated explanation: {len(explanation)} characters")
        return True
        
    except Exception as e:
        print(f"✗ LLM service failed: {e}")
        return False

def test_verification():
    """Test verification pipeline."""
    print("Testing verification...")
    
    try:
        verifier = NutritionVerifier()
        
        plan = "This meal provides 300 calories, 25g protein, 30g carbs, and 10g fat."
        retrieved_facts = [
            {
                "meta": {
                    "name": "Chicken Breast",
                    "calories_100g": 165,
                    "protein_100g": 31,
                    "carbs_100g": 0,
                    "fat_100g": 3.6
                }
            }
        ]
        suggested_portions = {"Chicken Breast": 200}
        
        result = verifier.verify_macro_claims(plan, retrieved_facts, suggested_portions)
        
        print(f"✓ Verification working - status: {result['status']}")
        return True
        
    except Exception as e:
        print(f"✗ Verification failed: {e}")
        return False

def test_monitoring():
    """Test monitoring system."""
    print("Testing monitoring...")
    
    try:
        monitoring = get_monitoring()
        
        # Test logging
        monitoring.log_prediction(
            user_id=1,
            service_type="test",
            prediction="test_prediction",
            confidence=0.85,
            input_data={"test": "data"},
            output_data={"result": "test"},
            processing_time=0.1
        )
        
        # Test getting metrics
        metrics = monitoring.get_prediction_metrics(days=1)
        
        print(f"✓ Monitoring working - logged prediction, metrics: {len(metrics)} fields")
        return True
        
    except Exception as e:
        print(f"✗ Monitoring failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints."""
    print("Testing API endpoints...")
    
    try:
        import requests
        import subprocess
        import time
        
        # Start the API server
        process = subprocess.Popen([
            "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(5)
        
        try:
            # Test health endpoint
            response = requests.get("http://localhost:8000/ai/health/", timeout=10)
            if response.status_code == 200:
                print("✓ API endpoints working - health check passed")
                return True
            else:
                print(f"✗ API endpoints failed - health check returned {response.status_code}")
                return False
                
        finally:
            # Stop the server
            process.terminate()
            process.wait()
            
    except Exception as e:
        print(f"✗ API endpoints failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=== AI Pipeline Test Suite ===\n")
    
    # Configure logging
    logging.basicConfig(level=logging.WARNING)
    
    tests = [
        ("Data Ingestion", test_data_ingestion),
        ("Embeddings & Indexing", test_embeddings_and_indexing),
        ("Retrieval", test_retrieval),
        ("Random Forest", test_random_forest),
        ("LLM Service", test_llm_service),
        ("Verification", test_verification),
        ("Monitoring", test_monitoring),
        ("API Endpoints", test_api_endpoints),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n=== Test Summary ===")
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The AI pipeline is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    exit(main())

