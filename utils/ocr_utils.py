"""OCR utilities for extracting text from images and PDFs"""
import os
from typing import List, Union
import io

# Import with error handling
try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("⚠️ OpenCV not available. Installing: pip install opencv-python")

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️ PIL not available. Installing: pip install Pillow")

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
    # Set tesseract path (update if needed)
    try:
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    except:
        pass
except ImportError:
    PYTESSERACT_AVAILABLE = False
    print("⚠️ pytesseract not available. Installing: pip install pytesseract")

try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False
    print("⚠️ pdf2image not available. Installing: pip install pdf2image")

def preprocess_image(image):
    """Preprocess image for better OCR results"""
    if not CV2_AVAILABLE:
        return image
    
    import numpy as np
    
    # Convert PIL to numpy if needed
    if PIL_AVAILABLE and isinstance(image, Image.Image):
        image = np.array(image)
    
    # Convert to grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    
    # Apply thresholding
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Denoise
    denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
    
    return denoised

def extract_text_from_image(image_path: str) -> str:
    """Extract text from image using OCR"""
    if not CV2_AVAILABLE or not PYTESSERACT_AVAILABLE:
        return f"[OCR not available - missing dependencies. Please install: pip install opencv-python pytesseract]"
    
    try:
        # Read image
        image = cv2.imread(image_path)
        
        # Preprocess
        processed = preprocess_image(image)
        
        # Extract text
        text = pytesseract.image_to_string(processed, lang='eng')
        
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return f"[Error: {str(e)}]"

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF using OCR"""
    if not PDF2IMAGE_AVAILABLE or not PYTESSERACT_AVAILABLE:
        return f"[PDF OCR not available - missing dependencies. Please install: pip install pdf2image pytesseract]"
    
    try:
        # Convert PDF to images
        images = convert_from_path(pdf_path, dpi=300)
        
        all_text = []
        for i, image in enumerate(images):
            # Preprocess and extract text
            processed = preprocess_image(image)
            text = pytesseract.image_to_string(processed, lang='eng')
            all_text.append(text)
        
        return "\n\n".join(all_text).strip()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return f"[Error: {str(e)}]"

def extract_text_from_file(file_path: str) -> str:
    """Extract text from file (image or PDF)"""
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
        return extract_text_from_image(file_path)
    elif ext == '.pdf':
        return extract_text_from_pdf(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

def get_image_layout_data(image_path: str) -> dict:
    """Extract layout information from image"""
    if not CV2_AVAILABLE or not PYTESSERACT_AVAILABLE:
        return {}
    
    try:
        image = cv2.imread(image_path)
        processed = preprocess_image(image)
        
        # Get detailed OCR data
        data = pytesseract.image_to_data(processed, output_type=pytesseract.Output.DICT)
        
        return data
    except Exception as e:
        print(f"Error getting layout data: {e}")
        return {}
