from app.ai_pipeline.enhanced_image_recognition import IntegratedFoodRecognizer

# Create a fresh instance
recognizer = IntegratedFoodRecognizer()

print("Testing direct recognition...")
print(f"GOOGLE_VISION_AVAILABLE: {recognizer.__class__.__module__.split('.')[1] == 'enhanced_image_recognition'}")
print(f"Vision client exists: {recognizer.vision_client is not None}")

# Test with a mock file-like object
class MockFile:
    def __init__(self, filename):
        self.filename = filename

mock_file = MockFile("apple.jpg")
result = recognizer.identify_food_from_image(mock_file)
print(f"Result: {result}")
