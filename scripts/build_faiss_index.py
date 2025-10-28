import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import os
from app.ai.embeddings import build_faiss_index
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "app/indexes/nutrition.index")
    EMB_MODEL = os.getenv("EMB_MODEL", "all-MiniLM-L6-v2")
    JSONL_PATH = "data/nutrition_facts.jsonl"
    EMBEDDINGS_PATH = "app/indexes/embeddings.npy"
    METADATA_PATH = "app/indexes/metadata.jsonl"

    build_faiss_index(
        jsonl_path=JSONL_PATH,
        model_name=EMB_MODEL,
        index_path=FAISS_INDEX_PATH,
        embeddings_path=EMBEDDINGS_PATH,
        metadata_path=METADATA_PATH,
    )
