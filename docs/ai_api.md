# AI API Documentation

This document describes the AI endpoints available in the Nutrition API.

## Base URL
```
http://localhost:8000/ai
```

## Authentication
Currently, no authentication is required. In production, implement proper authentication.

## Endpoints

### 1. Get Nutrition Facts
Retrieve nutrition facts using semantic search.

**Endpoint:** `GET /ai/get-nutrition-facts/`

**Parameters:**
- `q` (string, required): Search query
- `k` (integer, optional): Number of results to return (default: 3)

**Example Request:**
```bash
curl "http://localhost:8000/ai/get-nutrition-facts/?q=paneer&k=3"
```

**Example Response:**
```json
[
  {
    "score": 0.95,
    "fact": "Paneer — 296 kcal/100g, 28 g protein/100g",
    "meta": {
      "name": "Paneer",
      "barcode": "123456789",
      "url": "https://world.openfoodfacts.org/product/123456789",
      "calories_100g": 296,
      "protein_100g": 28,
      "carbs_100g": 2,
      "fat_100g": 22
    }
  }
]
```

### 2. Classify Food
Classify food recommendation using Random Forest model.

**Endpoint:** `POST /ai/classify-food/`

**Request Body:**
```json
{
  "user_id": 1,
  "food_name": "paneer",
  "quantity_g": 100
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/ai/classify-food/" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "food_name": "paneer", "quantity_g": 100}'
```

**Example Response:**
```json
{
  "recommended": true,
  "confidence": 0.85,
  "explanation": "This food is recommended (confidence: 85%). High protein content (28g/100g) is beneficial.",
  "raw_nutrition": {
    "name": "Paneer",
    "calories_per_100g": 296,
    "protein_per_100g": 28,
    "carbs_per_100g": 2,
    "fat_per_100g": 22,
    "calories_for_quantity": 296,
    "protein_for_quantity": 28,
    "carbs_for_quantity": 2,
    "fat_for_quantity": 22,
    "quantity_g": 100
  }
}
```

### 3. Generate Explanation
Generate comprehensive explanation using the full AI pipeline.

**Endpoint:** `POST /ai/generate-explanation/`

**Request Body:**
```json
{
  "user_id": 1,
  "food_name": "paneer",
  "quantity_g": 100,
  "extra_context": "I'm trying to build muscle"
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/ai/generate-explanation/" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "food_name": "paneer", "quantity_g": 100, "extra_context": "I'\''m trying to build muscle"}'
```

**Example Response:**
```json
{
  "recommendation": true,
  "confidence": 0.85,
  "explanation": "Based on the nutritional analysis, this food is recommended (confidence: 85%). The nutritional profile shows 296 calories, 28g protein, 2g carbs, and 22g fat per 100g. For muscle building goals, this food's protein content is important.\n\nDisclaimer: This is general nutritional information. Please consult a qualified healthcare professional for personalized dietary advice.",
  "evidence": [
    {
      "score": 0.95,
      "fact": "Paneer — 296 kcal/100g, 28 g protein/100g",
      "meta": {
        "name": "Paneer",
        "calories_100g": 296,
        "protein_100g": 28
      }
    }
  ],
  "verifier_status": "verified",
  "timings": {
    "load_profile": 0.001,
    "fetch_food_data": 0.05,
    "rf_classification": 0.02,
    "retrieve_facts": 0.1,
    "verification": 0.01,
    "llm_generation": 0.5,
    "total": 0.681
  }
}
```

### 4. Chat
Chat endpoint for nutrition questions.

**Endpoint:** `POST /ai/chat/`

**Request Body:**
```json
{
  "user_id": 1,
  "message": "What should I eat for breakfast?",
  "food_context": null
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/ai/chat/" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "message": "What should I eat for breakfast?", "food_context": null}'
```

**Example Response:**
```json
{
  "response": "I understand you're asking about nutrition. Based on your profile (age: 30, goal: General Health), I'd recommend focusing on a balanced diet with adequate protein, healthy carbs, and good fats.\n\nFor more specific advice, please provide more details about your question or consult with a qualified nutritionist.\n\nDisclaimer: This is general information. Please consult a healthcare professional for personalized advice.",
  "timings": {
    "load_profile": 0.001,
    "llm_generation": 0.3,
    "total": 0.301
  }
}
```

### 5. Health Check
Check the health status of AI services.

**Endpoint:** `GET /ai/health/`

**Example Request:**
```bash
curl "http://localhost:8000/ai/health/"
```

**Example Response:**
```json
{
  "status": "healthy",
  "services": {
    "retriever": true,
    "rf_model": true,
    "llm_service": true,
    "overall": true
  },
  "timestamp": 1703123456.789
}
```

## Error Codes

- `400` - Bad Request: Invalid input data
- `404` - Not Found: Food data not found
- `500` - Internal Server Error: Server error
- `503` - Service Unavailable: External API down

## Flutter Integration Examples

### 1. Food Classification Service
```dart
class FoodClassificationService {
  static const String baseUrl = 'http://localhost:8000/ai';
  
  static Future<Map<String, dynamic>> classifyFood({
    required int userId,
    required String foodName,
    required double quantityG,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/classify-food/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'user_id': userId,
        'food_name': foodName,
        'quantity_g': quantityG,
      }),
    );
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to classify food: ${response.statusCode}');
    }
  }
}
```

### 2. Nutrition Facts Service
```dart
class NutritionFactsService {
  static const String baseUrl = 'http://localhost:8000/ai';
  
  static Future<List<Map<String, dynamic>>> getNutritionFacts({
    required String query,
    int k = 3,
  }) async {
    final response = await http.get(
      Uri.parse('$baseUrl/get-nutrition-facts/?q=$query&k=$k'),
    );
    
    if (response.statusCode == 200) {
      return List<Map<String, dynamic>>.from(jsonDecode(response.body));
    } else {
      throw Exception('Failed to get nutrition facts: ${response.statusCode}');
    }
  }
}
```

### 3. Chat Service
```dart
class ChatService {
  static const String baseUrl = 'http://localhost:8000/ai';
  
  static Future<String> sendMessage({
    required int userId,
    required String message,
    String? foodContext,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/chat/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'user_id': userId,
        'message': message,
        'food_context': foodContext,
      }),
    );
    
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['response'];
    } else {
      throw Exception('Failed to send message: ${response.statusCode}');
    }
  }
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse:
- Default: 60 requests per minute per IP
- Configurable via environment variables

## Monitoring

The API includes comprehensive monitoring:
- Request/response logging
- Performance metrics
- Error tracking
- User feedback collection

Access monitoring data via the health check endpoint or database queries.

