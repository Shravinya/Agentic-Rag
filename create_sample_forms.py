"""Create sample bank forms for testing"""
import os
from PIL import Image, ImageDraw, ImageFont
import config

def create_sample_loan_form():
    """Create a sample loan application form"""
    
    # Create image
    width, height = 800, 1000
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a font, fallback to default
    try:
        title_font = ImageFont.truetype("arial.ttf", 24)
        header_font = ImageFont.truetype("arial.ttf", 16)
        text_font = ImageFont.truetype("arial.ttf", 12)
    except:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    
    y = 30
    
    # Title
    draw.text((250, y), "PERSONAL LOAN APPLICATION", fill='black', font=title_font)
    y += 50
    
    # Bank name
    draw.text((300, y), "ABC Bank Limited", fill='blue', font=header_font)
    y += 40
    
    # Form fields
    fields = [
        ("Applicant Name:", "John Doe"),
        ("Date of Birth:", "15/03/1990"),
        ("Age:", "17"),  # Intentionally wrong for testing
        ("Gender:", "Male"),
        ("Mobile Number:", "+91 9876543210"),
        ("Email:", "john.doe@email.com"),
        ("PAN Number:", ""),  # Unfilled
        ("Aadhaar Number:", "1234 5678 9012"),
        ("Current Address:", "123 Main Street, Mumbai, Maharashtra"),
        ("Employment Type:", "Salaried"),
        ("Company Name:", "Tech Corp India"),
        ("Monthly Income:", "₹45,000"),
        ("Loan Amount Required:", "₹5,00,000"),
        ("Loan Tenure:", "36 months"),
        ("Purpose of Loan:", "Home Renovation"),
        ("Existing Loans:", "None"),
        ("Bank Account Number:", ""),  # Unfilled
        ("IFSC Code:", "ABCD0001234"),
        ("Signature:", ""),  # Unfilled
        ("Date:", "")  # Unfilled
    ]
    
    for field_name, field_value in fields:
        draw.text((50, y), field_name, fill='black', font=text_font)
        if field_value:
            draw.text((300, y), field_value, fill='blue', font=text_font)
        else:
            draw.rectangle([300, y, 700, y+20], outline='gray')
        y += 35
    
    # Save
    filepath = os.path.join(config.SAMPLE_FORMS_DIR, "sample_personal_loan.png")
    img.save(filepath)
    print(f"✅ Created: {filepath}")
    
    return filepath

def create_sample_account_form():
    """Create a sample account opening form"""
    
    width, height = 800, 1000
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype("arial.ttf", 24)
        header_font = ImageFont.truetype("arial.ttf", 16)
        text_font = ImageFont.truetype("arial.ttf", 12)
    except:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    
    y = 30
    
    draw.text((220, y), "SAVINGS ACCOUNT APPLICATION", fill='black', font=title_font)
    y += 50
    
    draw.text((300, y), "XYZ Bank Limited", fill='blue', font=header_font)
    y += 40
    
    fields = [
        ("Full Name:", "Jane Smith"),
        ("Father's Name:", "Robert Smith"),
        ("Date of Birth:", "20/05/1995"),
        ("Age:", "28"),
        ("Gender:", "Female"),
        ("Marital Status:", "Single"),
        ("Mobile Number:", "+91 9876543211"),
        ("Email:", "jane.smith@email.com"),
        ("PAN Number:", "ABCDE1234F"),
        ("Aadhaar Number:", "9876 5432 1098"),
        ("Residential Address:", "456 Park Avenue, Delhi"),
        ("Occupation:", "Software Engineer"),
        ("Annual Income:", "₹12,00,000"),
        ("Account Type:", "Savings Account"),
        ("Initial Deposit:", "₹10,000"),
        ("Nominee Name:", ""),  # Unfilled
        ("Nominee Relationship:", ""),  # Unfilled
        ("Previous Bank Account:", "Yes"),
        ("Debit Card Required:", "Yes"),
        ("Internet Banking:", "Yes")
    ]
    
    for field_name, field_value in fields:
        draw.text((50, y), field_name, fill='black', font=text_font)
        if field_value:
            draw.text((300, y), field_value, fill='blue', font=text_font)
        else:
            draw.rectangle([300, y, 700, y+20], outline='gray')
        y += 35
    
    filepath = os.path.join(config.SAMPLE_FORMS_DIR, "sample_savings_account.png")
    img.save(filepath)
    print(f"✅ Created: {filepath}")
    
    return filepath

def create_sample_credit_card_form():
    """Create a sample credit card application"""
    
    width, height = 800, 900
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype("arial.ttf", 24)
        header_font = ImageFont.truetype("arial.ttf", 16)
        text_font = ImageFont.truetype("arial.ttf", 12)
    except:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    
    y = 30
    
    draw.text((220, y), "CREDIT CARD APPLICATION", fill='black', font=title_font)
    y += 50
    
    draw.text((280, y), "Premium Bank Limited", fill='blue', font=header_font)
    y += 40
    
    fields = [
        ("Applicant Name:", "Raj Kumar"),
        ("Date of Birth:", "10/08/1988"),
        ("Age:", "35"),
        ("Mobile Number:", "+91 9876543212"),
        ("Email:", "raj.kumar@email.com"),
        ("PAN Number:", "PQRST5678U"),
        ("Aadhaar Number:", "5555 6666 7777"),
        ("Current Address:", "789 Business District, Bangalore"),
        ("Employment Status:", "Self-Employed"),
        ("Business Name:", "Kumar Enterprises"),
        ("Monthly Income:", "₹85,000"),
        ("Card Type Requested:", "Premium Credit Card"),
        ("Existing Credit Cards:", "2"),
        ("Credit Limit Required:", "₹3,00,000"),
        ("Bank Account Number:", "123456789012"),
        ("IFSC Code:", "PREM0005678"),
        ("Signature:", "Raj Kumar"),
        ("Date:", "19/10/2025")
    ]
    
    for field_name, field_value in fields:
        draw.text((50, y), field_name, fill='black', font=text_font)
        if field_value:
            draw.text((300, y), field_value, fill='blue', font=text_font)
        else:
            draw.rectangle([300, y, 700, y+20], outline='gray')
        y += 35
    
    filepath = os.path.join(config.SAMPLE_FORMS_DIR, "sample_credit_card.png")
    img.save(filepath)
    print(f"✅ Created: {filepath}")
    
    return filepath

def create_all_samples():
    """Create all sample forms"""
    print("🎨 Creating sample bank forms...")
    
    forms = []
    forms.append(create_sample_loan_form())
    forms.append(create_sample_account_form())
    forms.append(create_sample_credit_card_form())
    
    print(f"\n✅ Created {len(forms)} sample forms in {config.SAMPLE_FORMS_DIR}")
    print("\n📝 Sample forms:")
    for form in forms:
        print(f"  • {os.path.basename(form)}")
    
    return forms

if __name__ == "__main__":
    create_all_samples()
