
from app.ai_pipeline.random_forest import train_model
from app.ai_pipeline.rag_module import RAGModule
import os

def main():
    print("Training Random Forest model...")
    # Ensure the models directory exists
    os.makedirs('models', exist_ok=True)
    train_model()
    print("Random Forest model trained and saved.")

    print("Building RAG index...")
    # Ensure the indexes directory exists
    os.makedirs('app/indexes', exist_ok=True)
    RAGModule()
    print("RAG index built and saved.")

if __name__ == "__main__":
    main()
