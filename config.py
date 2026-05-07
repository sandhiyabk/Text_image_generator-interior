import os
from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

GROQ_MODEL = "llama-3.1-8b-instant"
HF_IMAGE_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"

CHROMA_PATH = "data/chroma_db"
FAISS_INDEX_PATH = "data/faiss_index"
OUTPUTS_PATH = "outputs"
DB_PATH = "sqlite:///interior_copilot.db"

TEXT_EMBED_MODEL = "all-MiniLM-L6-v2"

ROOM_TYPES = ["Living Room", "Bedroom", "Kitchen", "Dining Room", "Home Office", "Bathroom"]
STYLES = ["Modern", "Scandinavian", "Bohemian", "Industrial", "Japandi", "Luxury", "Minimalist", "Rustic"]
BUDGET_RANGES = {"Low (under ₹50,000)": 50000, "Medium (₹50k–₹1.5L)": 150000, "High (₹1.5L–₹3L)": 300000, "Luxury (₹3L+)": 600000}

FURNITURE_CATEGORIES = ["sofa", "dining_table", "bed", "wardrobe", "coffee_table", "bookshelf", "tv_unit", "study_desk", "accent_chair", "lighting"]

BUDGET_ALLOCATION = {
    "Living Room":  {"sofa": 0.40, "coffee_table": 0.15, "tv_unit": 0.25, "accent_chair": 0.12, "lighting": 0.08},
    "Bedroom":      {"bed": 0.45, "wardrobe": 0.30, "study_desk": 0.15, "lighting": 0.10},
    "Kitchen":     {"dining_table": 0.55, "accent_chair": 0.30, "lighting": 0.15},
    "Dining Room": {"dining_table": 0.60, "accent_chair": 0.25, "lighting": 0.15},
    "Home Office": {"study_desk": 0.45, "bookshelf": 0.30, "accent_chair": 0.17, "lighting": 0.08},
    "Bathroom":   {"lighting": 0.60, "accent_chair": 0.40},
}

os.makedirs(OUTPUTS_PATH, exist_ok=True)
os.makedirs(CHROMA_PATH, exist_ok=True)
os.makedirs(FAISS_INDEX_PATH, exist_ok=True)