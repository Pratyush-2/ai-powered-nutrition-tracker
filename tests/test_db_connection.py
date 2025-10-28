from app.database import engine

def test_db_connection():
    try:
        with engine.connect() as conn:
            print("✅ Database connection successful!")
            assert True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        assert False