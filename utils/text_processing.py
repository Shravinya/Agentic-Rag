"""Text processing utilities"""
import re
from typing import List

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep important punctuation
    text = re.sub(r'[^\w\s\.\,\:\;\-\(\)\%\₹\$]', '', text)
    return text.strip()

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks"""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    
    return chunks

def extract_key_info(text: str) -> dict:
    """Extract key information patterns from text"""
    info = {
        "ages": re.findall(r'\b(\d{1,2})\s*(?:years?|yrs?)\b', text, re.IGNORECASE),
        "amounts": re.findall(r'[₹$]\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:lakh|crore|thousand|L|Cr|K)?', text, re.IGNORECASE),
        "percentages": re.findall(r'(\d+(?:\.\d+)?)\s*%', text),
        "documents": re.findall(r'\b(Aadhaar|PAN|Passport|Voter ID|Driving License|Bank Statement)\b', text, re.IGNORECASE)
    }
    return info
