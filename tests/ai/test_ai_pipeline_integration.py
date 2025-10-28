"""
Integration tests for the complete AI pipeline.

This module tests the end-to-end functionality of the AI pipeline
including data ingestion, indexing, retrieval, classification, and LLM generation.
"""

import pytest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys
import sqlite3

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.ai.fetch_openfoodfacts import OpenFoodFactsFetcher
from backend.ai.embeddings import NutritionEmbeddings
from backend.ai.retriever import NutritionRetriever
from backend.ai.train_rf import FoodRecommendationTrainer
from backend.ai.rf_model import FoodRecommendationModel
from backend.ai.llm_service import LLMService
from backend.ai.verifier import NutritionVerifier

class TestAIPipelineIntegration:
    """Integration tests for the complete AI pipeline."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.temp_dir) / "data"
        self.models_dir = Path(self.temp_dir) / "models"
        self.indexes_dir = Path(self.temp_dir) / "indexes"
        
        # Create directories
        self.data_dir.mkdir()
        self.models_dir.mkdir()
        self.indexes_dir.mkdir()
        
        # Create database and tables
        from app.database import Base, engine
        Base.metadata.create_all(bind=engine)
        
        # Set environment variables
        os.environ["FAISS_INDEX_PATH"] = str(self.indexes_dir / "nutrition.index")
        os.environ["RF_MODEL_PATH"] = str(self.models_dir / "random_forest_model.pkl")
        
        # Create test nutrition facts
        self.test_facts = [
            {
                "name": "Apple",
                "barcode": "123456789",
                "url": "https://example.com/apple",
                "calories_100g": 52,
                "protein_100g": 0.3,
                "carbs_100g": 14,
                "fat_100g": 0.2,
                "fact_text": "Apple — 52 kcal/100g, 0.3 g protein/100g"
            },
            {
                "name": "Chicken Breast",
                "barcode": "987654321",
                "url": "https://example.com/chicken",
                "calories_100g": 165,
                "protein_100g": 31,
                "carbs_100g": 0,
                "fat_100g": 3.6,
                "fact_text": "Chicken Breast — 165 kcal/100g, 31 g protein/100g"
            },
            {
                "name": "Paneer",
                "barcode": "456789123",
                "url": "https://example.com/paneer",
                "calories_100g": 296,
                "protein_100g": 28,
                "carbs_100g": 2,
                "fat_100g": 22,
                "fact_text": "Paneer — 296 kcal/100g, 28 g protein/100g"
            },
            {
                "name": "Banana",
                "barcode": "111222333",
                "url": "https://example.com/banana",
                "calories_100g": 89,
                "protein_100g": 1.1,
                "carbs_100g": 23,
                "fat_100g": 0.3,
                "fact_text": "Banana — 89 kcal/100g, 1.1 g protein/100g"
            },
            {
                "name": "Salmon",
                "barcode": "444555666",
                "url": "https://example.com/salmon",
                "calories_100g": 208,
                "protein_100g": 20,
                "carbs_100g": 0,
                "fat_100g": 13,
                "fact_text": "Salmon — 208 kcal/100g, 20 g protein/100g"
            }
        ]

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
        
        # Create database and tables
        from app.database import Base, engine
        Base.metadata.create_all(bind=engine)
    
    def test_data_ingestion_pipeline(self):
        """Test the data ingestion pipeline."""
        # Create JSONL file
        jsonl_path = self.data_dir / "nutrition_facts.jsonl"
        with open(jsonl_path, 'w', encoding='utf-8') as f:
            for fact in self.test_facts:
                f.write(json.dumps(fact) + "\n")
        
        # Test fetcher
        fetcher = OpenFoodFactsFetcher(cache_dir=str(self.data_dir), db_path=str(self.data_dir / "nutrition_facts.db"))
        
        # Test caching
        fetcher.cache_to_jsonl(self.test_facts)
        fetcher.cache_to_sqlite(self.test_facts)
        
        # Verify data was cached
        assert jsonl_path.exists()
        assert (self.data_dir / "nutrition_facts.db").exists()
    
    def test_embeddings_and_indexing_pipeline(self):
        """Test the embeddings generation and FAISS indexing pipeline."""
        # Create JSONL file
        jsonl_path = self.data_dir / "nutrition_facts.jsonl"
        with open(jsonl_path, 'w', encoding='utf-8') as f:
            for fact in self.test_facts:
                f.write(json.dumps(fact) + "\n")
        
        # Test embeddings
        embeddings = NutritionEmbeddings(
            index_path=str(self.indexes_dir / "nutrition.index")
        )
        
        # Build index
        embeddings.build_from_jsonl(str(jsonl_path), save_embeddings=True)
        
        # Verify index was created
        assert (self.indexes_dir / "nutrition.index").exists()
        assert (self.indexes_dir / "metadata.jsonl").exists()
        assert (self.indexes_dir / "embeddings.npy").exists()
        
        # Test search
        results = embeddings.search("apple", k=1)
        assert len(results) == 1
        assert "Apple" in results[0]["name"]
    
    def test_retrieval_pipeline(self):
        """Test the retrieval pipeline."""
        # Create test index
        jsonl_path = self.data_dir / "nutrition_facts.jsonl"
        with open(jsonl_path, 'w', encoding='utf-8') as f:
            for fact in self.test_facts:
                f.write(json.dumps(fact) + "\n")
        
        # Build index
        embeddings = NutritionEmbeddings(
            index_path=str(self.indexes_dir / "nutrition.index")
        )
        embeddings.build_from_jsonl(str(jsonl_path))
        
        # Test retriever
        retriever = NutritionRetriever(
            index_path=str(self.indexes_dir / "nutrition.index")
        )
        
        # Test retrieval
        results = retriever.retrieve_facts("apple", k=2)
        assert len(results) <= 2
        assert all("score" in result for result in results)
        assert all("fact_text" in result for result in results)
        assert all("meta" in result for result in results)
    
    def test_random_forest_pipeline(self):
        """Test the Random Forest training and prediction pipeline."""
        # Create training data
        training_data = []
        for fact in self.test_facts:
            # Add synthetic labels
            fact_with_label = fact.copy()
            fact_with_label["recommended"] = 1 if fact["protein_100g"] > 10 else 0
            training_data.append(fact_with_label)
        
        trainer = FoodRecommendationTrainer(
            model_path=str(self.models_dir / "random_forest_model.pkl"),
            scaler_path=str(self.models_dir / "scaler.pkl")
        )
        
        # Train model
        metrics = trainer.train(training_data, test_size=0.5)
        
        # Verify training
        assert metrics["accuracy"] > 0.5  # Should be better than random
        assert metrics["n_train"] > 0
        assert metrics["n_test"] > 0
        
        # Save model
        trainer.save_model()
        
        # Verify model was saved
        assert (self.models_dir / "random_forest_model.pkl").exists()
        assert (self.models_dir / "scaler.pkl").exists()
        assert (self.models_dir / "feature_names.json").exists()
        
        # Test model loading and prediction
        model = FoodRecommendationModel(
            model_path=str(self.models_dir / "random_forest_model.pkl")
        )
        
        # Test prediction
        nutrition_data = {
            "calories_100g": 100,
            "protein_100g": 20,
            "carbs_100g": 10,
            "fat_100g": 5
        }
        results = model.predict_multiple_with_confidence(nutrition_data)
        assert isinstance(results, list)
        assert len(results) > 0
        recommended, confidence, explanation = results[0]["recommended"], results[0]["confidence"], results[0]["explanation"]
        
        assert isinstance(recommended, bool)
        assert 0 <= confidence <= 1
        assert isinstance(explanation, str)
        assert len(explanation) > 0
    
    def test_llm_service_pipeline(self):
        # Mock user profile, RF result, and retrieved facts
        user_profile = {"age": 30, "gender": "male", "weight_kg": 70, "height_cm": 175, "activity_level": "moderate", "goal": "weight_loss"}
        rf_result = {"recommended": True, "confidence": 0.85}
        retrieved_facts = [{
            "fact_text": "Apples contain 52 kcal per 100g",
            "calories_100g": 52,
            "protein_100g": 0.3,
            "carbs_100g": 13.8,
            "fat_100g": 0.2
        }]

        # Patch _initialize_backends to prevent actual OpenAI client initialization
        with patch('backend.ai.llm_service.openai') as mock_openai:
            llm = LLMService(openai_api_key="test_key")
            
            # Manually create and assign a MagicMock for openai_client
            mock_openai_client = MagicMock()
            llm.openai_client = mock_openai_client

            # Configure the mock to return a predefined response
            mock_openai_client.chat.completions.create.return_value = MagicMock(
                choices=[MagicMock(message=MagicMock(content="Test LLM response"))]
            )

            # Call the method under test
            response = llm.generate_explanation(
                user_profile=user_profile,
                rf_result=rf_result,
                retrieved_facts=retrieved_facts
            )

            # Assertions
            assert response == "Test LLM response"
            mock_openai_client.chat.completions.create.assert_called_once()

            # Create a mock for openai_client and assign it to the LLMService instance
            mock_openai_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock(message=MagicMock(content="Test explanation with [1] citation"))]
            mock_openai_client.chat.completions.create.return_value = mock_response
            llm.openai_client = mock_openai_client

            # Execute the LLM service pipeline
            explanation = llm.generate_explanation(user_profile, rf_result, retrieved_facts)

            # Verify the mock was called and the result is correct
            mock_openai_client.chat.completions.create.assert_called_once()
            assert "Test explanation with [1] citation" in explanation
    
    def test_verification_pipeline(self):
        """Test the verification pipeline."""
        verifier = NutritionVerifier(tolerance_percent=5.0)
        
        # Test macro claim verification
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
        
        assert "status" in result
        assert "claimed_values" in result
        assert "expected_values" in result
        assert "corrected_plan" in result
    
    def test_complete_pipeline_integration(self):
        """Test the complete end-to-end pipeline."""
        # Step 1: Data ingestion
        jsonl_path = self.data_dir / "nutrition_facts.jsonl"
        with open(jsonl_path, 'w', encoding='utf-8') as f:
            for fact in self.test_facts:
                f.write(json.dumps(fact) + "\n")
        
        # Step 2: Build embeddings and index
        embeddings = NutritionEmbeddings(
            index_path=str(self.indexes_dir / "nutrition.index")
        )
        embeddings.build_from_jsonl(str(jsonl_path))
        
        # Step 3: Train Random Forest
        training_data = []
        for fact in self.test_facts:
            fact_with_label = fact.copy()
            fact_with_label["recommended"] = 1 if fact["protein_100g"] > 10 else 0
            training_data.append(fact_with_label)
        
        trainer = FoodRecommendationTrainer(
            model_path=str(self.models_dir / "random_forest_model.pkl")
        )
        trainer.train(training_data, test_size=0.5)
        trainer.save_model()
        
        # Step 4: Test complete pipeline
        retriever = NutritionRetriever(
            index_path=str(self.indexes_dir / "nutrition.index")
        )
        
        model = FoodRecommendationModel(
            model_path=str(self.models_dir / "random_forest_model.pkl")
        )
        
        # Test end-to-end flow
        query = "apple"
        
        # Retrieve facts
        facts = retriever.retrieve_facts(query, k=2)
        assert len(facts) > 0
        
        # Classify food
        if facts:
            fact = facts[0]
            nutrition_data = {
                "calories_100g": fact["meta"]["calories_100g"],
                "protein_100g": fact["meta"]["protein_100g"],
                "carbs_100g": fact["meta"]["carbs_100g"],
                "fat_100g": fact["meta"]["fat_100g"]
            }
            
            results = model.predict_multiple_with_confidence(nutrition_data)
            assert isinstance(results, list)
            assert len(results) > 0
            recommended, confidence, explanation = results[0]["recommended"], results[0]["confidence"], results[0]["explanation"]
            
            assert isinstance(recommended, bool)
            assert 0 <= confidence <= 1
            assert isinstance(explanation, str)
    
    def test_error_handling(self):
        """Test error handling in the pipeline."""
        # Test with invalid data
        retriever = NutritionRetriever(index_path="nonexistent.index")
        assert not retriever.is_available()
        
        # Test with invalid model
        model = FoodRecommendationModel(model_path="nonexistent.pkl")
        assert not model.is_available()
        
        # Test with empty query
        with pytest.raises(Exception):
            from backend.ai.security import input_validator
            input_validator.validate_query("")
    
    def test_performance_metrics(self):
        """Test performance metrics collection."""
        import time
        
        # Test timing
        start_time = time.time()
        
        # Simulate some work
        time.sleep(0.01)
        
        processing_time = time.time() - start_time
        
        assert processing_time > 0
        assert processing_time < 1.0  # Should be fast
    
    def test_monitoring_integration(self):
        """Test monitoring integration."""
        from backend.ai.monitoring import AIMonitoring
        
        # Ensure the database file is deleted before starting the test
        db_file_path = self.data_dir / "ai_metrics.db"
        if db_file_path.exists():
            db_file_path.unlink()

        # Initialize AIMonitoring with a temporary database path
        monitoring = AIMonitoring(db_path=self.data_dir / "ai_metrics.db")
        monitoring._init_database() # Explicitly initialize the database

        # Log a dummy prediction
        monitoring.log_prediction(
            user_id=1,
            service_type="test_service",
            prediction="test_prediction",
            confidence=0.9,
            input_data={"test_input": "data"},
            output_data={"test_output": "data"},
            processing_time=0.1,
            metadata={"test_meta": "data"}
        )

        # Verify that a prediction was logged
        conn = sqlite3.connect(monitoring.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM ai_metrics")
        count = cursor.fetchone()[0]
        conn.close()
        assert count == 1, "Expected 1 prediction in the database, but found " + str(count)

        metrics = monitoring.get_prediction_metrics(days=1)
        assert 'total_predictions' in metrics

        # Test logging retrieval hit
        monitoring.log_retrieval_hit(
            query="test_query",
            retrieved_count=5,
            top_score=0.95,
            user_id=1
        )

        # Test getting metrics
        metrics = monitoring.get_prediction_metrics(days=1)
        print(f"Test: Retrieved metrics: {metrics}")
        assert "total_predictions" in metrics

