import requests

# Test Google Vision status
print("Testing Google Vision Status...")
response = requests.get("http://127.0.0.1:8000/ai/test-google-vision/")
print(f"Status: {response.json()}")
print()

# Test food recognition
print("Testing Food Recognition...")
image_path = r"C:\Users\Praty\Downloads\apple.jpg"

with open(image_path, 'rb') as f:
    files = {'file': ('apple.jpg', f, 'image/jpeg')}
    response = requests.post("http://127.0.0.1:8000/ai/identify-food/", files=files)

print(f"Response Status: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print("✅ SUCCESS!")
    print(f"Food Identified: {result.get('food_identified')}")
    print(f"Confidence: {result.get('confidence')}")
    print(f"Method: {result.get('recognition_method')}")
    print(f"Calories: {result.get('ready_to_log', {}).get('calories')}")
else:
    print(f"❌ Error: {response.text}")
