"""Configuration settings for the Bank Form Validator"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Model Configuration
LLM_MODEL = "llama-3.3-70b-versatile"  # Recommended text model (not deprecated)
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"  # Current vision model (Llama 4 Scout)
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Paths
DATA_DIR = "data"
RAW_POLICIES_DIR = os.path.join(DATA_DIR, "raw_policies")
PROCESSED_POLICIES_DIR = os.path.join(DATA_DIR, "processed_policies")
VECTOR_DB_DIR = os.path.join(DATA_DIR, "vector_db")
UPLOADED_FORMS_DIR = os.path.join(DATA_DIR, "uploaded_forms")
SAMPLE_FORMS_DIR = os.path.join(DATA_DIR, "sample_forms")

# Vector DB Configuration
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K_RESULTS = 5

# OCR Configuration
TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Update if needed

# Create directories
for directory in [DATA_DIR, RAW_POLICIES_DIR, PROCESSED_POLICIES_DIR, 
                  VECTOR_DB_DIR, UPLOADED_FORMS_DIR, SAMPLE_FORMS_DIR]:
    os.makedirs(directory, exist_ok=True)
