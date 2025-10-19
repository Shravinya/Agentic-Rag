"""Quick setup script - runs all setup steps"""
import os
import sys

print("="*70)
print(" 🏦 AI BANK FORM VALIDATOR - QUICK SETUP")
print("="*70)

# Step 1: Test imports
print("\n📦 Step 1/5: Testing imports...")
try:
    from dotenv import load_dotenv
    from groq import Groq
    print("✅ Core dependencies imported")
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)

# Step 2: Load environment
print("\n🔑 Step 2/5: Loading API key...")
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("❌ GROQ_API_KEY not found in .env")
    sys.exit(1)
print(f"✅ API key loaded: {api_key[:20]}...")

# Step 3: Test API
print("\n🧪 Step 3/5: Testing Groq API...")
try:
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Say 'Working!' if you can read this."}],
        max_tokens=10
    )
    print(f"✅ API Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ API Error: {e}")
    sys.exit(1)

# Step 4: Generate policies
print("\n📚 Step 4/5: Generating bank policies...")
try:
    from scrapers.bank_scraper import BankFormScraper
    scraper = BankFormScraper()
    policies = scraper.scrape_all()
    print(f"✅ Generated {len(policies)} policies")
except Exception as e:
    print(f"❌ Error generating policies: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 5: Build vector database
print("\n🔨 Step 5/5: Building vector database...")
print("⏳ This may take 2-3 minutes (downloading embedding model)...")
try:
    from rag.vector_store import build_knowledge_base
    vector_store = build_knowledge_base()
    print("✅ Vector database built successfully")
except Exception as e:
    print(f"❌ Error building vector database: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Create sample forms
print("\n🎨 Bonus: Creating sample forms...")
try:
    from create_sample_forms import create_all_samples
    create_all_samples()
except Exception as e:
    print(f"⚠️ Could not create sample forms: {e}")

print("\n" + "="*70)
print(" ✅ SETUP COMPLETE!")
print("="*70)
print("\n📌 Next Steps:")
print("  1. Run: streamlit run streamlit_app.py")
print("  2. Or double-click: run.bat")
print("\n💡 Sample forms created in: data/sample_forms/")
print("="*70)
