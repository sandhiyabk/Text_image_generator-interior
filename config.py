import os
from dotenv import load_dotenv
load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

CLAUDE_MODEL = "claude-haiku-4-5"
SDXL_MODEL = "stability-ai/sdxl:39ed52f2319f9f28e9d77a9d1a7edfa59ff87d71c7fd9e2c98f2bb8a50ec7f09"

CHROMA_PATH = "data/chroma_db"
FAISS_INDEX_PATH = "data/faiss_index"
OUTPUTS_PATH = "outputs"
DB_PATH = "sqlite:///interior_copilot.db"

CLIP_MODEL_NAME = "openai/clip-vit-base-patch32"
TEXT_EMBED_MODEL = "all-MiniLM-L6-v2"

ROOM_TYPES = ["Living Room", "Bedroom", "Kitchen", "Dining Room", "Home Office", "Bathroom"]
STYLES = ["Modern", "Scandinavian", "Bohemian", "Industrial", "Japandi", "Luxury", "Minimalist", "Rustic"]
BUDGET_RANGES = {"Low (under ₹50,000)": 50000, "Medium (₹50k–₹1.5L)": 150000, "High (₹1.5L–₹3L)": 300000, "Luxury (₹3L+)": 600000}

FURNITURE_CATEGORIES = ["sofa", "dining_table", "bed", "wardrobe", "coffee_table", "bookshelf", "tv_unit", "study_desk", "accent_chair", "lighting"]

BUDGET_ALLOCATION = {
    "sofa": 0.30, "dining_table": 0.20, "bed": 0.30, "wardrobe": 0.20,
    "coffee_table": 0.12, "bookshelf": 0.10, "tv_unit": 0.15, "study_desk": 0.18,
    "accent_chair": 0.10, "lighting": 0.08
}

os.makedirs(OUTPUTS_PATH, exist_ok=True)
os.makedirs(CHROMA_PATH, exist_ok=True)
os.makedirs(FAISS_INDEX_PATH, exist_ok=True)