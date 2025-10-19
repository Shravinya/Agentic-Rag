"""Extraction Agent - Dynamically extracts fields from any form"""
import os
import json
import base64
from typing import Dict, List, Any
from groq import Groq
from PIL import Image
import config

class ExtractionAgent:
    """Agent for extracting fields from bank forms dynamically"""
    
    def __init__(self):
        self.client = Groq(api_key=config.GROQ_API_KEY)
        self.model = config.LLM_MODEL
        self.vision_model = "meta-llama/llama-4-scout-17b-16e-instruct"  # Current vision model (Llama 4)
    
    def extract_fields(self, file_path: str) -> Dict[str, Any]:
        """Extract all fields from a form (image or PDF)"""
        print(f"📄 Extracting fields from: {file_path}")
        
        # Check file type
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            # Convert PDF to image for vision model
            image_path = self._convert_pdf_to_image(file_path)
            if not image_path:
                return {
                    "error": "Could not convert PDF to image",
                    "extracted_fields": {},
                    "unfilled_fields": [],
                    "form_type": "Unknown"
                }
        else:
            image_path = file_path
        
        # Use Vision Model to analyze the image directly
        result = self._analyze_form_with_vision(image_path)
        
        return result
    
    def _convert_pdf_to_image(self, pdf_path: str) -> str:
        """Convert first page of PDF to image"""
        try:
            from pdf2image import convert_from_path
            images = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=300)
            if images:
                # Save temporary image
                temp_path = pdf_path.replace('.pdf', '_temp.png')
                images[0].save(temp_path, 'PNG')
                return temp_path
        except Exception as e:
            print(f"⚠️ PDF conversion error: {e}")
        return None
    
    def _encode_image_to_base64(self, image_path: str) -> str:
        """Encode image to base64 for API"""
        try:
            with open(image_path, 'rb') as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"❌ Error encoding image: {e}")
            return None
    
    def _analyze_form_with_vision(self, image_path: str) -> Dict[str, Any]:
        """Use Vision Model to analyze form image directly - MOST ACCURATE METHOD"""
        
        print("🔍 Analyzing form with Vision AI...")
        
        # Encode image
        base64_image = self._encode_image_to_base64(image_path)
        if not base64_image:
            return {
                "error": "Could not encode image",
                "extracted_fields": {},
                "unfilled_fields": [],
                "form_type": "Unknown"
            }
        
        prompt = """Analyze this bank form image and extract ALL fields with maximum accuracy.

INSTRUCTIONS:
1. Identify form type (Loan, Account, Credit Card, KYC, Insurance, etc.)
2. Extract EVERY field you see - both filled and empty
3. For each field provide:
   - Exact field name/label as shown
   - Field value (if filled) or "UNFILLED" (if empty)
   - Field type (text/number/date/checkbox/signature/dropdown)
   - Whether required (look for * or "required")

4. Extract these categories thoroughly:
   - Personal: Name, DOB, Age, Gender, Marital Status
   - Contact: Mobile, Email, Address
   - Financial: Income, Amount, Account Number
   - Documents: PAN, Aadhaar, Passport
   - Employment: Type, Company, Experience
   - Form: Signature, Date, Checkboxes

RETURN EXACT JSON:
{
  "form_type": "exact form type",
  "form_category": "Loan/Account/KYC/Insurance/Credit Card",
  "bank_name": "bank name if visible",
  "extracted_fields": {
    "Field Name": {
      "value": "actual value or UNFILLED",
      "type": "text/number/date/checkbox/signature",
      "required": true/false
    }
  },
  "filled_fields": ["list of filled field names"],
  "unfilled_fields": ["list of empty field names"],
  "total_fields": 0,
  "confidence": "high/medium/low"
}

Be thorough - extract EVERY field visible."""

        try:
            response = self.client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.1,
                max_tokens=3000
            )
            
            result_text = response.choices[0].message.content
            print(f"✅ Vision analysis complete")
            
            # Extract JSON from response
            result = self._extract_json(result_text)
            result['total_fields'] = len(result.get('extracted_fields', {}))
            
            return result
            
        except Exception as e:
            print(f"❌ Error with vision analysis: {e}")
            # Fallback to text-based analysis
            print("⚠️ Falling back to OCR-based extraction...")
            return self._fallback_ocr_extraction(image_path)
    
    def _fallback_ocr_extraction(self, image_path: str) -> Dict[str, Any]:
        """Fallback OCR-based extraction if vision model fails"""
        try:
            from utils.ocr_utils import extract_text_from_file
            extracted_text = extract_text_from_file(image_path)
            
            if extracted_text and len(extracted_text) > 50:
                # Use text-based LLM analysis
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert bank form analyzer. Extract all fields from the text. Return valid JSON."
                        },
                        {
                            "role": "user",
                            "content": f"Extract all fields from this form text:\n\n{extracted_text}\n\nReturn JSON with form_type, extracted_fields, filled_fields, unfilled_fields."
                        }
                    ],
                    temperature=0.1,
                    max_tokens=2000
                )
                return self._extract_json(response.choices[0].message.content)
        except Exception as e:
            print(f"⚠️ Fallback extraction failed: {e}")
        
        return {
            "error": "All extraction methods failed",
            "form_type": "Unknown",
            "extracted_fields": {},
            "unfilled_fields": []
        }
    
    def _extract_json(self, text: str) -> Dict:
        """Extract JSON from LLM response"""
        try:
            # Try to find JSON in the response
            start = text.find('{')
            end = text.rfind('}') + 1
            
            if start != -1 and end > start:
                json_str = text[start:end]
                return json.loads(json_str)
            else:
                return json.loads(text)
        except json.JSONDecodeError:
            print("⚠️ Could not parse JSON from response")
            return {
                "error": "JSON parsing failed",
                "raw_response": text[:500],
                "form_type": "Unknown",
                "extracted_fields": {},
                "unfilled_fields": []
            }
    
    def extract_and_save(self, file_path: str, output_path: str = None) -> Dict:
        """Extract fields and save to JSON"""
        result = self.extract_fields(file_path)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved extraction result to {output_path}")
        
        return result

if __name__ == "__main__":
    # Test the extraction agent
    agent = ExtractionAgent()
    
    # Example usage
    test_file = "data/uploaded_forms/test_form.pdf"
    if os.path.exists(test_file):
        result = agent.extract_fields(test_file)
        print(json.dumps(result, indent=2))
