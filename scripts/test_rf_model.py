#!/usr/bin/env python3
"""Test script to verify Random Forest model functionality."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ai_pipeline.random_forest import classify_food

def test_random_forest():
    # Test data similar to what would come from food search
    food_features = {
        "calories": 150,
        "protein": 8,
        "fat": 5,
        "sugar": 8,
        "carbohydrates": 18,
    }
    
    user_features = {
        "age": 30,
        "bmi": 25.0,
        "activity_level": 2,
    }
    
    # Mock user goals
    class MockGoal:
        def __init__(self):
            self.calories_goal = 2000.0
            self.protein_goal = 100.0
            self.carbs_goal = 250.0
            self.fats_goal = 70.0
    
    user_goals = [MockGoal()]
    
    try:
        result = classify_food(food_features, user_features, user_goals)
        print("✅ Random Forest model works!")
        print(f"Result: {result}")
        return True
    except Exception as e:
        print(f"❌ Random Forest model failed: {e}")
        return False

if __name__ == "__main__":
    test_random_forest()
