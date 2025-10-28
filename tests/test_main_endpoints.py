import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models import DailyLog, Food
from unittest.mock import patch, MagicMock
import io

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="function")
def db_session(autouse=True):
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_delete_log():
    # Create a food and a log
    db = TestingSessionLocal()
    food = Food(name="test food", calories=100, protein=10, carbs=10, fats=10)
    db.add(food)
    db.commit()
    db.refresh(food)

    log = DailyLog(food_id=food.id, quantity=1, date="2025-10-13", user_id=1)
    db.add(log)
    db.commit()
    db.refresh(log)

    response = client.delete(f"/logs/{log.id}")
    assert response.status_code == 200
    assert response.json() == {"ok": True}

    # Verify the log is deleted
    deleted_log = db.query(DailyLog).filter(DailyLog.id == log.id).first()
    assert deleted_log is None
    db.close()

def test_identify_food():
    with patch('app.ai.ai_routes.identify_food_from_image', new_callable=MagicMock) as mock_identify:
        mock_identify.return_value = "test food"
        
        # Create a dummy image file
        file_content = b"dummy image content"
        file = io.BytesIO(file_content)
        
        response = client.post("/ai/identify-food/", files={"file": ("test.jpg", file, "image/jpeg")})
        
        assert response.status_code == 200
        assert response.json() == {"food_name": "test food"}