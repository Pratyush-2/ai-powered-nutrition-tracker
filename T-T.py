from google.cloud import vision
from google.oauth2 import service_account
import io
import json
from llama_cpp import Llama

# ========== CONFIGURATION ==========

LLAMA_MODEL_PATH = "models/your_model.gguf"  # Path to your local LLaMA model
VISION_CREDENTIALS_PATH = "gen-lang-client-0841175445-a7b8df25933b.json"
IMAGE_PATH = "test_images/000010.JPG"

# Dummy food data (you can replace with actual output from Vision API analysis)
inputJSON = '''[
  { "expiresIn": 5, "object": "Apple" },
  { "expiresIn": 14, "object": "Banana" },
  { "expiresIn": 1, "object": "Carrot" },
  { "expiresIn": 1, "object": "Bread" },
  { "expiresIn": 1, "object": "Cheese" },
  { "expiresIn": 10, "object": "Milk" },
  { "expiresIn": 12, "object": "Eggs" },
  { "expiresIn": 13, "object": "Tomato" },
  { "expiresIn": 2, "object": "Chicken" },
  { "expiresIn": 5, "object": "Orange" },
  { "expiresIn": 5, "object": "Yogurt" },
  { "expiresIn": 23, "object": "Potato" }
]'''

json_data = json.loads(inputJSON)
formatted_json = json.dumps(json_data, indent=2)

# ========== FUNCTIONS ==========

def load_image(image_path):
    with io.open(image_path, 'rb') as image_file:
        return image_file.read()

def analyze_image(image_path, client):
    image = vision.Image(content=load_image(image_path))

    # OCR
    text_response = client.text_detection(image=image)
    texts = text_response.text_annotations
    full_text = texts[0].description.strip() if texts else ""

    if text_response.error.message:
        raise Exception(f"Vision API Text Error: {text_response.error.message}")

    # Labels
    label_response = client.label_detection(image=image)
    labels = label_response.label_annotations
    label_descriptions = [label.description for label in labels]

    if label_response.error.message:
        raise Exception(f"Vision API Label Error: {label_response.error.message}")

    return full_text, label_descriptions

def generate_prompt_recipe(json_string):
    return (
        f"You received a JSON array containing food items and their expiration days:\n"
        f"{json_string}\n\n"
        f"Using this information, generate a recipe that uses these ingredients.\n"
        f"Please ignore any vague items such as 'food', 'drink', etc.\n"
        f"Use ingredients with shorter expiration times first.\n"
        f"Return only the recipe — do not include extra commentary or repeat yourself.\n"
    )

def generate_prompt_food_analysis(extracted_text, labels, num_kind=1):
    return (
        f"Based on the extracted information below:\n"
        f"Text in image: {extracted_text}\n"
        f"Identified food items: {', '.join(labels)}\n\n"
        f"List the top {num_kind} specific foods with quantities and confidence.\n"
        f"Use JSON format with fields: object, expiry, location.\n"
        f"Estimate storage time if expiry is not available.\n"
        f"Only include the response once, no additional explanation.\n"
    )

def run_llama(prompt, model):
    result = model(
        prompt,
        max_tokens=1024,
        temperature=0.7,
        top_p=0.95
    )
    if "choices" in result:
        return "".join([c["text"] for c in result["choices"]])
    return result.get("text", str(result))

# ========== MAIN ==========

def main():
    # Set up Vision API
    credentials = service_account.Credentials.from_service_account_file(VISION_CREDENTIALS_PATH)
    vision_client = vision.ImageAnnotatorClient(credentials=credentials)

    # Analyze image
    extracted_text, labels = analyze_image(IMAGE_PATH, vision_client)
    print("Extracted image text:", extracted_text)
    print("Identified labels:", labels)

    # Init LLaMA model
    print("Loading local LLaMA model... (this may take a while)")
    llm = Llama(model_path=LLAMA_MODEL_PATH)

    # --------- First: Food identification prompt ---------
    analysis_prompt = generate_prompt_food_analysis(extracted_text, labels, num_kind=1)
    print("\n🔍 Food Analysis Prompt:\n", analysis_prompt)
    analysis_result = run_llama(analysis_prompt, llm)
    print("\n🍱 Food Analysis Result:\n", analysis_result)

    # --------- Second: Recipe generation prompt ---------
    recipe_prompt = generate_prompt_recipe(formatted_json)
    print("\n📋 Recipe Prompt:\n", recipe_prompt)
    recipe_result = run_llama(recipe_prompt, llm)
    print("\n🍳 Generated Recipe:\n", recipe_result)

if __name__ == "__main__":
    main()
