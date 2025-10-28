#!/usr/bin/env python3
"""Test the new rule-based nutrition engine."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ai_pipeline.nutrition_engine import classify_food

def test_examples():
    """Test with various food examples."""
    
    # Test data
    test_cases = [
        {
            "name": "Grilled Chicken Breast",
            "food": {"calories": 165, "protein": 31, "fat": 3.6, "sugar": 0, "carbohydrates": 0},
            "user": {"age": 30, "bmi": 25.0, "activity_level": 2},
            "goal": "muscle_gain"
        },
        {
            "name": "Chocolate Bar",
            "food": {"calories": 500, "protein": 5, "fat": 25, "sugar": 45, "carbohydrates": 60},
            "user": {"age": 30, "bmi": 25.0, "activity_level": 2},
            "goal": "weight_loss"
        },
        {
            "name": "Apple",
            "food": {"calories": 52, "protein": 0.3, "fat": 0.2, "sugar": 10, "carbohydrates": 14},
            "user": {"age": 65, "bmi": 27.0, "activity_level": 1},
            "goal": "general_health"
        }
    ]
    
    for case in test_cases:
        # Mock goal object
        class MockGoal:
            def __init__(self, goal_type):
                self.goal_type = goal_type
        
        user_goals = [MockGoal(case["goal"])]
        
        result = classify_food(case["food"], case["user"], user_goals)
        
        print(f"\n🍎 {case['name']} ({case['goal']}):")
        print(f"   Score: {result['score']}/100")
        print(f"   Recommended: {'✅' if result['recommended'] else '❌'}")
        print(f"   Reasoning: {result['reasoning']}")

if __name__ == "__main__":
    test_examples()
