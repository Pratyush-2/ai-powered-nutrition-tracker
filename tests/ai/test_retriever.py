"""
Tests for the nutrition retriever module.
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch

from backend.ai.retriever import NutritionRetriever, retrieve_facts
from backend.ai.embeddings import NutritionEmbeddings

class TestNutritionRetriever:
    """Test cases for NutritionRetriever."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.index_path = Path(self.temp_dir) / "test_index.index"
        
        # Create test metadata
        self.test_metadata = [
            {
                "index": 0,
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
                "index": 1,
                "name": "Chicken Breast",
                "barcode": "987654321",
                "url": "https://example.com/chicken",
                "calories_100g": 165,
                "protein_100g": 31,
                "carbs_100g": 0,
                "fat_100g": 3.6,
                "fact_text": "Chicken Breast — 165 kcal/100g, 31 g protein/100g"
            }
        ]
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('backend.ai.retriever.NutritionEmbeddings')
    def test_retriever_initialization(self, mock_embeddings):
        """Test retriever initialization."""
        # Create a dummy index file for the retriever to find
        self.index_path.touch()
        mock_embeddings.return_value = Mock()
        
        retriever = NutritionRetriever(index_path=str(self.index_path))
        
        assert retriever.index_path == str(self.index_path)
        mock_embeddings.assert_called_once()
    
    @patch('backend.ai.retriever.NutritionEmbeddings')
    def test_retrieve_facts_success(self, mock_embeddings):
        """Test successful fact retrieval."""
        # Create a dummy index file for the retriever to find
        self.index_path.touch()
        # Mock embeddings
        mock_emb = Mock()
        mock_emb.search.return_value = [
            {
                "score": 0.95,
                "fact_text": "Apple — 52 kcal/100g, 0.3 g protein/100g",
                "name": "Apple",
                "barcode": "123456789",
                "url": "https://example.com/apple",
                "calories_100g": 52,
                "protein_100g": 0.3,
                "carbs_100g": 14,
                "fat_100g": 0.2
            }
        ]
        mock_embeddings.return_value = mock_emb
        
        retriever = NutritionRetriever(index_path=str(self.index_path))
        results = retriever.retrieve_facts("apple", k=1)
        
        assert len(results) == 1
        assert results[0]["score"] == 0.95
        assert "Apple" in results[0]["fact_text"]
        assert results[0]["meta"]["name"] == "Apple"
    
    @patch('backend.ai.retriever.NutritionEmbeddings')
    def test_retrieve_facts_empty(self, mock_embeddings):
        """Test retrieval with no results."""
        mock_emb = Mock()
        mock_emb.search.return_value = []
        mock_embeddings.return_value = mock_emb
        
        retriever = NutritionRetriever(index_path=str(self.index_path))
        results = retriever.retrieve_facts("nonexistent", k=5)
        
        assert results == []
    
    @patch('backend.ai.retriever.NutritionEmbeddings')
    def test_retrieve_facts_error(self, mock_embeddings):
        """Test retrieval with error."""
        mock_emb = Mock()
        mock_emb.search.side_effect = Exception("Search error")
        mock_embeddings.return_value = mock_emb
        
        retriever = NutritionRetriever(index_path=str(self.index_path))
        results = retriever.retrieve_facts("test", k=5)
        
        assert results == []
    
    def test_is_available(self):
        """Test availability check."""
        # Create a dummy index file for the retriever to find
        self.index_path.touch()
        with patch('backend.ai.retriever.NutritionEmbeddings') as mock_embeddings:
            mock_emb = Mock()
            mock_embeddings.return_value = mock_emb
            
            retriever = NutritionRetriever(index_path=str(self.index_path))
            assert retriever.is_available() == True
    
    def test_is_available_false(self):
        """Test availability check when not available."""
        with patch('backend.ai.retriever.NutritionEmbeddings') as mock_embeddings:
            mock_embeddings.side_effect = Exception("Init error")
            
            retriever = NutritionRetriever(index_path=str(self.index_path))
            assert retriever.is_available() == False


class TestRetrieveFactsFunction:
    """Test cases for the convenience function."""
    
    @patch('backend.ai.retriever.get_retriever')
    def test_retrieve_facts_function(self, mock_get_retriever):
        """Test the convenience function."""
        mock_retriever = Mock()
        mock_retriever.retrieve_facts.return_value = [{"score": 0.9, "fact": "test"}]
        mock_get_retriever.return_value = mock_retriever
        
        results = retrieve_facts("test", k=1)
        
        assert len(results) == 1
        assert results[0]["score"] == 0.9
        mock_retriever.retrieve_facts.assert_called_once_with("test", 1)

