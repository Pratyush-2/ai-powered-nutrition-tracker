#!/usr/bin/env python3
"""
Retrain Random Forest model from user feedback.

This script retrains the Random Forest model using accumulated user feedback
and updated nutrition data.
"""

import sys
import os
import logging
from pathlib import Path
import json
import sqlite3
from datetime import datetime, timedelta

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.ai.train_rf import FoodRecommendationTrainer
from backend.ai.fetch_openfoodfacts import OpenFoodFactsFetcher

def load_feedback_data(db_path: str, days: int = 30):
    """
    Load user feedback data from the database.
    
    Args:
        db_path: Path to the metrics database
        days: Number of days to look back for feedback
        
    Returns:
        List of feedback records
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get feedback from the last N days
    cursor.execute("""
        SELECT uf.*, am.input_data, am.output_data
        FROM user_feedback uf
        JOIN ai_metrics am ON uf.prediction_id = am.id
        WHERE uf.timestamp >= datetime('now', '-{} days')
        AND uf.feedback_type IN ('positive', 'negative', 'correction')
    """.format(days))
    
    feedback_data = []
    for row in cursor.fetchall():
        feedback_data.append({
            'id': row[0],
            'timestamp': row[1],
            'user_id': row[2],
            'prediction_id': row[3],
            'feedback_type': row[4],
            'feedback_score': row[5],
            'feedback_text': row[6],
            'corrected_prediction': row[7],
            'input_data': json.loads(row[8]) if row[8] else {},
            'output_data': json.loads(row[9]) if row[9] else {}
        })
    
    conn.close()
    return feedback_data

def create_training_data_from_feedback(feedback_data):
    """
    Create training data from user feedback.
    
    Args:
        feedback_data: List of feedback records
        
    Returns:
        List of training examples
    """
    training_data = []
    
    for feedback in feedback_data:
        input_data = feedback['input_data']
        feedback_type = feedback['feedback_type']
        feedback_score = feedback['feedback_score']
        
        # Extract nutrition data from input
        if 'raw_nutrition' in input_data:
            nutrition = input_data['raw_nutrition']
        else:
            # Try to extract from other fields
            nutrition = {
                'calories_100g': input_data.get('calories_100g', 0),
                'protein_100g': input_data.get('protein_100g', 0),
                'carbs_100g': input_data.get('carbs_100g', 0),
                'fat_100g': input_data.get('fat_100g', 0)
            }
        
        # Determine label based on feedback
        if feedback_type == 'positive' or feedback_score >= 4:
            label = 1  # Recommended
        elif feedback_type == 'negative' or feedback_score <= 2:
            label = 0  # Not recommended
        else:
            # Skip neutral feedback
            continue
        
        # Create training example
        training_example = {
            'name': input_data.get('food_name', 'Unknown'),
            'calories_100g': nutrition.get('calories_100g', 0),
            'protein_100g': nutrition.get('protein_100g', 0),
            'carbs_100g': nutrition.get('carbs_100g', 0),
            'fat_100g': nutrition.get('fat_100g', 0),
            'recommended': label,
            'feedback_id': feedback['id'],
            'feedback_score': feedback_score
        }
        
        training_data.append(training_example)
    
    return training_data

def main():
    """Main retraining function."""
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    # Paths
    db_path = "data/ai_metrics.db"
    model_path = "models/random_forest_model.pkl"
    
    # Check if feedback database exists
    if not Path(db_path).exists():
        logger.error(f"Feedback database not found: {db_path}")
        logger.info("No user feedback available for retraining.")
        return 1
    
    try:
        # Load feedback data
        logger.info("Loading user feedback data...")
        feedback_data = load_feedback_data(db_path, days=30)
        
        if not feedback_data:
            logger.info("No recent feedback data available for retraining.")
            return 0
        
        logger.info(f"Loaded {len(feedback_data)} feedback records")
        
        # Create training data
        logger.info("Creating training data from feedback...")
        training_data = create_training_data_from_feedback(feedback_data)
        
        if not training_data:
            logger.info("No valid training data created from feedback.")
            return 0
        
        logger.info(f"Created {len(training_data)} training examples")
        
        # Load existing nutrition facts for additional training data
        logger.info("Loading additional nutrition facts...")
        fetcher = OpenFoodFactsFetcher()
        
        # Get some additional facts from cache
        additional_facts = []
        try:
            with open("data/nutrition_facts.jsonl", 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        fact = json.loads(line)
                        # Add synthetic label using existing rules
                        fact['recommended'] = 1 if (
                            fact.get('calories_100g', 0) <= 300 and 
                            fact.get('protein_100g', 0) >= 8
                        ) else 0
                        additional_facts.append(fact)
        except FileNotFoundError:
            logger.warning("No additional nutrition facts found")
        
        # Combine training data
        all_training_data = training_data + additional_facts[:100]  # Limit additional data
        
        logger.info(f"Total training data: {len(all_training_data)} examples")
        
        # Train new model
        logger.info("Training new Random Forest model...")
        trainer = FoodRecommendationTrainer(model_path=model_path)
        
        # Generate labels for all data
        labeled_data = trainer.generate_synthetic_labels(all_training_data)
        
        # Train model
        metrics = trainer.train(labeled_data, test_size=0.2)
        
        # Save model
        trainer.save_model()
        
        # Log retraining metrics
        logger.info("Retraining completed successfully!")
        logger.info(f"Accuracy: {metrics['accuracy']:.3f}")
        logger.info(f"Training samples: {metrics['n_train']}")
        logger.info(f"Test samples: {metrics['n_test']}")
        
        # Save retraining log
        retrain_log = {
            'timestamp': datetime.now().isoformat(),
            'feedback_samples': len(training_data),
            'additional_samples': len(additional_facts),
            'total_samples': len(all_training_data),
            'accuracy': metrics['accuracy'],
            'n_train': metrics['n_train'],
            'n_test': metrics['n_test']
        }
        
        with open("models/retrain_log.json", 'w') as f:
            json.dump(retrain_log, f, indent=2)
        
        logger.info("Retraining log saved to models/retrain_log.json")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error during retraining: {e}")
        return 1

if __name__ == "__main__":
    exit(main())

