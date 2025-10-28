# Prompt Templates Documentation

This document describes the exact prompt templates used in the AI system for reproducibility and consistency.

## System Prompt

The system prompt is designed to be safety-first and evidence-based:

```
You are a nutrition assistant. Use ONLY the EVIDENCE provided below. If the evidence is insufficient, respond "No verified evidence — suggest safe alternatives" and do not hallucinate. Always include inline citations like [1],[2] after claims. Always provide numeric macros (calories, protein, carbs, fat) and a confidence score. Never provide medical advice; include a standard disclaimer and recommend consulting a qualified professional.
```

## Explanation Generation Prompt

Used for generating food recommendations and explanations:

```
EVIDENCE: 
[1] {fact1}
[2] {fact2}
...

USER_PROFILE: {age, sex, weight, height, activity, goals}

RF_PREDICTION: {Recommended/Not Recommended} (Confidence: {confidence}%)

INSTRUCTIONS: Propose a meal/portion or say "No verified evidence", show the calculation used to compute totals using the retrieved facts, and list sources at the end.

{extra_context}
```

### Example Input:
```
EVIDENCE: 
[1] Paneer — 296 kcal/100g, 28 g protein/100g
[2] Chicken Breast — 165 kcal/100g, 31 g protein/100g

USER_PROFILE: Age: 30, Sex: Male, Weight: 70 kg, Height: 170 cm, Activity Level: Moderate, Goals: Muscle Building

RF_PREDICTION: Recommended (Confidence: 85%)

INSTRUCTIONS: Propose a meal/portion or say "No verified evidence", show the calculation used to compute totals using the retrieved facts, and list sources at the end.

I'm trying to build muscle
```

### Expected Output:
```
Based on the evidence [1], paneer is an excellent choice for muscle building. With 296 calories and 28g protein per 100g, it provides high-quality protein for muscle synthesis.

For a 100g serving:
- Calories: 296 kcal
- Protein: 28g (37.8% of calories)
- Carbs: 2g (2.7% of calories)  
- Fat: 22g (66.8% of calories)

This macronutrient profile is ideal for muscle building due to the high protein content [1]. The protein-to-calorie ratio of 0.094g protein per calorie is excellent for muscle growth.

Sources:
[1] Paneer nutritional data from OpenFoodFacts

Disclaimer: This is general nutritional information. Please consult a qualified healthcare professional for personalized dietary advice.
```

## Chat Prompt

Used for general nutrition conversations:

```
{system_prompt}

USER_PROFILE: {user_profile}

{conversation_history}

USER: {current_message}
```

### Example Input:
```
You are a nutrition assistant. Use ONLY the EVIDENCE provided below. If the evidence is insufficient, respond "No verified evidence — suggest safe alternatives" and do not hallucinate. Always include inline citations like [1],[2] after claims. Always provide numeric macros (calories, protein, carbs, fat) and a confidence score. Never provide medical advice; include a standard disclaimer and recommend consulting a qualified professional.

USER_PROFILE: Age: 30, Sex: Male, Weight: 70 kg, Height: 170 cm, Activity Level: Moderate, Goals: General Health

USER: What should I eat for breakfast?
```

### Expected Output:
```
For a healthy breakfast, I recommend focusing on a balanced meal with protein, complex carbohydrates, and healthy fats. Here are some evidence-based suggestions:

**High Protein Options:**
- Eggs: ~6g protein per large egg, ~70 calories
- Greek yogurt: ~10g protein per 100g, ~59 calories
- Oatmeal with nuts: ~5g protein per 100g oats + ~6g protein per 30g almonds

**Complex Carbohydrates:**
- Oatmeal: ~12g carbs per 100g, provides sustained energy
- Whole grain bread: ~12g carbs per slice, fiber-rich
- Fruits: Natural sugars with vitamins and fiber

**Healthy Fats:**
- Nuts and seeds: ~15g fat per 30g almonds
- Avocado: ~15g fat per 100g, monounsaturated fats
- Olive oil: Heart-healthy monounsaturated fats

**Sample Breakfast:**
- 1 cup oatmeal (150g) = 150 calories, 5g protein, 27g carbs
- 1 tbsp almond butter (15g) = 95 calories, 3g protein, 3g fat
- 1 banana (120g) = 105 calories, 1g protein, 27g carbs

**Total: ~350 calories, 9g protein, 54g carbs, 3g fat**

This provides a balanced macronutrient profile for sustained energy and satiety.

Disclaimer: This is general nutritional information. Please consult a qualified healthcare professional for personalized dietary advice.
```

## Verification Prompt

Used when correcting nutritional claims:

```
You made an error in your nutritional calculations. The correct values are:

{corrected_values}

Please revise your response to use these accurate numbers and explain the calculation method used.

{original_plan}
```

### Example Input:
```
You made an error in your nutritional calculations. The correct values are:

Calories: 296 (not 250)
Protein: 28g (not 25g)
Carbs: 2g (not 5g)
Fat: 22g (not 20g)

Please revise your response to use these accurate numbers and explain the calculation method used.

Based on the evidence, paneer provides 250 calories and 25g protein per 100g, making it suitable for muscle building.
```

### Expected Output:
```
Based on the evidence, paneer provides 296 calories and 28g protein per 100g, making it excellent for muscle building.

**Calculation Method:**
- Used verified nutritional data from OpenFoodFacts
- Scaled to 100g serving size
- Protein content: 28g (37.8% of total calories)
- Calorie breakdown: 296 total calories

This high protein content makes paneer an ideal choice for muscle building goals.
```

## Fallback Templates

When LLM services are unavailable, the system uses template-based responses:

### Food Recommendation Template:
```
Based on the nutritional analysis, this food is {recommended/not recommended} (confidence: {confidence}%). 

The nutritional profile shows {calories} calories, {protein}g protein, {carbs}g carbs, and {fat}g fat per 100g. 

{user_specific_advice}

Disclaimer: This is general nutritional information. Please consult a qualified healthcare professional for personalized dietary advice.
```

### Chat Response Template:
```
I understand you're asking about nutrition. Based on your profile (age: {age}, goal: {goal}), I'd recommend focusing on a balanced diet with adequate protein, healthy carbs, and good fats.

For more specific advice, please provide more details about your question or consult with a qualified nutritionist.

Disclaimer: This is general information. Please consult a healthcare professional for personalized advice.
```

## Prompt Engineering Guidelines

1. **Safety First**: Always include disclaimers and avoid medical advice
2. **Evidence-Based**: Only use provided evidence, never hallucinate
3. **Citations**: Include inline citations [1], [2] for all claims
4. **Numeric Precision**: Always provide specific nutritional values
5. **Confidence Scores**: Include confidence levels for predictions
6. **User Context**: Incorporate user profile information
7. **Fallback Ready**: Have template responses for service failures
8. **Consistent Format**: Use standardized response formats
9. **Verification Ready**: Design prompts to be easily verifiable
10. **Reproducible**: Use deterministic prompts for consistent results

## Temperature Settings

- **Factual Responses**: temperature=0.0 (deterministic)
- **Creative Responses**: temperature=0.7 (balanced creativity)
- **Chat Responses**: temperature=0.7 (conversational)
- **Explanations**: temperature=0.0 (consistent and accurate)

## Token Limits

- **System Prompt**: ~200 tokens
- **Explanation Prompt**: ~500-1000 tokens
- **Chat Prompt**: ~300-800 tokens
- **Response Limit**: 500 tokens (explanations), 300 tokens (chat)

