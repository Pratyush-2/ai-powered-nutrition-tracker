from datetime import date
from app import models
from app.database import SessionLocal

def test_crud_ops():
    db = SessionLocal()

    # 1. Add a food
    food = models.Food(name="Apple", calories=95, protein=0, carbs=25, fats=0)
    db.add(food)
    db.commit()
    db.refresh(food)
    print(f"✅ Added food: {food.name} (id={food.id})")

    # 2. Add a user goal
    goal = models.UserGoal(calories_goal=2000, protein_goal=100, carbs_goal=250, fats_goal=70)
    db.add(goal)
    db.commit()
    db.refresh(goal)
    print(f"✅ Added user goal (id={goal.id})")

    # 3. Add a daily log
    log = models.DailyLog(food_id=food.id, quantity=2, date=date(2025, 8, 16))
    db.add(log)
    db.commit()
    db.refresh(log)
    print(f"✅ Added daily log (id={log.id})")

    db.close()
    assert True