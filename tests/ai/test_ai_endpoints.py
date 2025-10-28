"""
Tests for AI endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import json

from app.main import app

client = TestClient(app)

class TestAIEndpoints:
    """Test cases for AI endpoints."""
    
    def test_get_nutrition_facts_success(self):
        """Test successful nutrition facts retrieval."""
        with patch('backend.ai.ai_routes.retrieve_facts') as mock_retrieve:
            mock_retrieve.return_value = [
                {
                    "score": 0.95,
                    "fact_text": "Apple — 52 kcal/100g, 0.3 g protein/100g",
                    "meta": {
                        "name": "Apple",
                        "calories_100g": 52,
                        "protein_100g": 0.3
                    }
                }
            ]
            
            response = client.get("/ai/get-nutrition-facts/?q=apple&k=1")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["score"] == 0.95
            assert "Apple" in data[0]["fact"]
    
    def test_get_nutrition_facts_error(self):
        """Test nutrition facts retrieval with error."""
        with patch('backend.ai.ai_routes.retrieve_facts') as mock_retrieve:
            mock_retrieve.side_effect = Exception("Retrieval error")
            
            response = client.get("/ai/get-nutrition-facts/?q=apple&k=1")
            
            assert response.status_code == 500
            assert "Error retrieving facts" in response.json()["detail"]
    
    def test_classify_food_success(self):
        """Test successful food classification."""
        with patch('backend.ai.ai_routes.fetcher.get_food_data') as mock_get_food, \
             patch('backend.ai.ai_routes.predict_food_recommendation') as mock_predict:
            
            mock_get_food.return_value = {
                "name": "Apple",
                "calories_100g": 52,
                "protein_100g": 0.3,
                "carbs_100g": 14,
                "fat_100g": 0.2
            }
            mock_predict.return_value = (True, 0.85, "Good nutritional profile")
            
            request_data = {
                "user_id": 1,
                "food_name": "apple",
                "quantity_g": 100
            }
            
            response = client.post("/ai/classify-food/", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["recommended"] == True
            assert data["confidence"] == 0.85
            assert "Good nutritional profile" in data["explanation"]
    
    def test_classify_food_not_found(self):
        """Test food classification with food not found."""
        with patch('backend.ai.ai_routes.fetcher.get_food_data') as mock_get_food:
            mock_get_food.return_value = None
            
            request_data = {
                "user_id": 1,
                "food_name": "nonexistent",
                "quantity_g": 100
            }
            
            response = client.post("/ai/classify-food/", json=request_data)
            
            assert response.status_code == 404
            assert "Food data not found" in response.json()["detail"]
    
    def test_generate_explanation_success(self):
        """Test successful explanation generation."""
        with patch('backend.ai.ai_routes.fetcher.get_food_data') as mock_get_food, \
             patch('backend.ai.ai_routes.predict_food_recommendation') as mock_predict, \
             patch('backend.ai.ai_routes.retrieve_facts') as mock_retrieve, \
             patch('backend.ai.ai_routes.generate_explanation') as mock_llm:
            mock_get_food.return_value = {
                "name": "Apple",
                "calories_100g": 52,
                "protein_100g": 0.3,
                "carbs_100g": 14,
                "fat_100g": 0.2,
                "food_id": 1
            }
            mock_predict.return_value = (True, 0.85, "Good nutritional profile")
            mock_retrieve.return_value = [
                {
                    "score": 0.95,
                    "fact_text": "Apple — 52 kcal/100g, 0.3 g protein/100g",
                    "meta": {"name": "Apple", "calories_100g": 52}
                }
            ]
            mock_llm.return_value = "This apple is recommended for your health goals."
            
            request_data = {
                "user_id": 1,
                "food_name": "apple",
                "quantity_g": 100,
                "extra_context": ""
            }
            
            response = client.post("/ai/generate-explanation/", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["recommendation"] == True
            assert data["confidence"] == 0.85
            assert "This apple is recommended" in data["explanation"]
            assert len(data["evidence"]) == 1
            assert "timings" in data
    
    def test_chat_success(self):
        """Test successful chat response."""
        with patch('backend.ai.llm_service.chat_message') as mock_chat:
            mock_chat.return_value = "I can help you with nutrition questions."
            
            request_data = {
                "user_id": 1,
                "message": "What should I eat for breakfast?",
                "food_context": None
            }
            
            response = client.post("/ai/chat/", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert "I can help you" in data["response"]
            assert "timings" in data
    
        with patch('backend.ai.retriever.get_retriever') as mock_retriever, \
             patch('backend.ai.rf_model.get_model') as mock_model, \
             patch('backend.ai.llm_service.get_llm_service') as mock_llm:
            
            mock_retriever.return_value.is_available.return_value = True
            mock_model.return_value.is_available.return_value = True
            mock_llm.return_value.is_available.return_value = True
            
            response = client.get("/ai/health/")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["services"]["overall"] == True
    
    def test_health_check_degraded(self):
        """Test health check with degraded services."""
        with patch('backend.ai.retriever.get_retriever') as mock_retriever, \
             patch('backend.ai.rf_model.get_model') as mock_model, \
             patch('backend.ai.llm_service.get_llm_service') as mock_llm:
            
            mock_retriever.return_value.is_available.return_value = True
            mock_model.return_value.is_available.return_value = False
            mock_llm.return_value.is_available.return_value = True
            
            response = client.get("/ai/health/")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "degraded"
            assert data["services"]["overall"] == False

