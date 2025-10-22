"""Streamlit UI for Bank Form Validator"""
import warnings
import os
import sys
import logging

# Suppress all warnings and logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['PYTHONWARNINGS'] = 'ignore'
warnings.filterwarnings('ignore')
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)

# Suppress logging
logging.getLogger().setLevel(logging.ERROR)
logging.getLogger('transformers').setLevel(logging.ERROR)
logging.getLogger('sentence_transformers').setLevel(logging.ERROR)

import streamlit as st

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="AI Bank Form Validator",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Now import other modules
import json
from datetime import datetime
import config
from agents.extraction_agent import ExtractionAgent
from agents.validation_agent import ValidationAgent
from rag.vector_store import VectorStore

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-approved {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #28a745;
    }
    .status-rejected {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #dc3545;
    }
    .status-review {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #ffc107;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'extraction_result' not in st.session_state:
    st.session_state.extraction_result = None
if 'validation_result' not in st.session_state:
    st.session_state.validation_result = None
if 'vector_store_loaded' not in st.session_state:
    st.session_state.vector_store_loaded = False

@st.cache_resource
def load_vector_store():
    """Load vector store (cached)"""
    try:
        vs = VectorStore()
        vs.load()
        return vs
    except Exception as e:
        st.error(f"Error loading vector store: {e}")
        return None

@st.cache_resource
def get_extraction_agent():
    """Get extraction agent (cached)"""
    return ExtractionAgent()

@st.cache_resource
def get_validation_agent(_vector_store):
    """Get validation agent (cached)"""
    return ValidationAgent(_vector_store)

def main():
    # Header
    st.markdown('<div class="main-header">🏦 AI-Powered Bank Form Validator</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/bank-building.png", width=100)
        st.title("Navigation")
        
        page = st.radio(
            "Select Page",
            ["📝 Form Validation", "📊 Knowledge Base", "ℹ️ About"],
            label_visibility="collapsed"
        )
        
        st.divider()
        
        st.subheader("System Status")
        
        # Check vector store
        if not st.session_state.vector_store_loaded:
            with st.spinner("Loading knowledge base..."):
                vector_store = load_vector_store()
                if vector_store:
                    st.session_state.vector_store_loaded = True
                    st.success("✅ Knowledge base loaded")
                else:
                    st.warning("⚠️ Knowledge base not found")
        else:
            st.success("✅ Knowledge base loaded")
        
        st.info(f"📚 Model: {config.LLM_MODEL}")
    
    # Main content
    if page == "📝 Form Validation":
        show_validation_page()
    elif page == "📊 Knowledge Base":
        show_knowledge_base_page()
    else:
        show_about_page()

def show_validation_page():
    """Form validation page"""
    st.header("📝 Upload and Validate Bank Form")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Step 1: Upload Form")
        
        uploaded_file = st.file_uploader(
            "Choose a form (PDF or Image)",
            type=['pdf', 'png', 'jpg', 'jpeg', 'bmp', 'tiff'],
            help="Upload a bank form in PDF or image format"
        )
        
        if uploaded_file:
            # Save uploaded file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{uploaded_file.name}"
            filepath = os.path.join(config.UPLOADED_FORMS_DIR, filename)
            
            with open(filepath, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            
            # Show preview
            if uploaded_file.type.startswith('image'):
                st.image(uploaded_file, caption="Uploaded Form", use_column_width=True)
            else:
                st.info("📄 PDF uploaded successfully")
            
            # Extract button
            if st.button("🔍 Extract Fields", type="primary", use_container_width=True):
                with st.spinner("Extracting fields from form..."):
                    agent = get_extraction_agent()
                    result = agent.extract_fields(filepath)
                    st.session_state.extraction_result = result
                    st.rerun()
    
    with col2:
        st.subheader("Step 2: Extraction Results")
        
        if st.session_state.extraction_result:
            result = st.session_state.extraction_result
            
            # Form type
            st.metric("Form Type", result.get('form_type', 'Unknown'))
            
            # Show extracted fields
            if 'extracted_fields' in result and result['extracted_fields']:
                st.write("**Extracted Fields:**")
                
                for field_name, field_data in result['extracted_fields'].items():
                    if isinstance(field_data, dict):
                        value = field_data.get('value', 'N/A')
                        field_type = field_data.get('type', 'unknown')
                        
                        if value == "UNFILLED":
                            st.warning(f"⚠️ **{field_name}**: {value} ({field_type})")
                        else:
                            st.success(f"✅ **{field_name}**: {value} ({field_type})")
                    else:
                        st.info(f"• **{field_name}**: {field_data}")
            
            # Show unfilled fields
            if 'unfilled_fields' in result and result['unfilled_fields']:
                st.error(f"❌ **Unfilled Fields ({len(result['unfilled_fields'])}):**")
                for field in result['unfilled_fields']:
                    st.write(f"  • {field}")
            
            # Validate button
            st.divider()
            if st.button("✅ Validate Form", type="primary", use_container_width=True):
                if st.session_state.vector_store_loaded:
                    with st.spinner("Validating against bank policies..."):
                        vector_store = load_vector_store()
                        validation_agent = get_validation_agent(vector_store)
                        validation_result = validation_agent.validate(result)
                        st.session_state.validation_result = validation_result
                        st.rerun()
                else:
                    st.error("❌ Knowledge base not loaded. Please build it first.")
        else:
            st.info("👆 Upload a form to start extraction")
    
    # Validation results (full width)
    if st.session_state.validation_result:
        st.divider()
        st.header("📊 Validation Results")
        
        result = st.session_state.validation_result
        status = result.get('status', 'UNKNOWN')
        
        # Status banner
        if status == 'APPROVED':
            st.markdown('<div class="status-approved"><h3>✅ APPROVED</h3></div>', unsafe_allow_html=True)
        elif status == 'REJECTED':
            st.markdown('<div class="status-rejected"><h3>❌ REJECTED</h3></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-review"><h3>⚠️ NEEDS REVIEW</h3></div>', unsafe_allow_html=True)
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            completeness = result.get('completeness_score', 0)
            st.metric("Completeness Score", f"{completeness}%", 
                     delta=f"{completeness - 100}%" if completeness < 100 else "Perfect!")
        
        with col2:
            compliance = result.get('compliance_score', 0)
            st.metric("Compliance Score", f"{compliance}%",
                     delta=f"{compliance - 100}%" if compliance < 100 else "Perfect!")
        
        with col3:
            policies_checked = result.get('policies_checked', 0)
            st.metric("Policies Checked", policies_checked)
        
        # Details
        col1, col2 = st.columns(2)
        
        with col1:
            # Missing fields
            missing = result.get('missing_fields', [])
            if missing:
                st.subheader("⚠️ Missing Required Fields")
                for field in missing:
                    st.error(f"• {field}")
            
            # Policy violations
            violations = result.get('policy_violations', [])
            if violations:
                st.subheader("❌ Policy Violations")
                for v in violations:
                    with st.expander(f"🔴 {v.get('field', 'Unknown')} - {v.get('severity', 'Unknown').upper()}"):
                        st.write(f"**Issue:** {v.get('issue', 'N/A')}")
                        st.write(f"**Policy:** {v.get('policy', 'N/A')}")
        
        with col2:
            # Recommendations
            recommendations = result.get('recommendations', [])
            if recommendations:
                st.subheader("💡 Recommendations")
                for rec in recommendations:
                    st.info(f"• {rec}")
            
            # Summary
            st.subheader("📝 Summary")
            st.write(result.get('summary', 'No summary available'))
        
        # Download report
        st.divider()
        report_data = {
            "extraction": st.session_state.extraction_result,
            "validation": st.session_state.validation_result,
            "timestamp": datetime.now().isoformat()
        }
        
        st.download_button(
            label="📥 Download Full Report (JSON)",
            data=json.dumps(report_data, indent=2),
            file_name=f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

def show_knowledge_base_page():
    """Knowledge base management page"""
    st.header("📊 Knowledge Base Management")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Policy Documents")
        
        # Check if policies exist
        policy_dir = config.RAW_POLICIES_DIR
        if os.path.exists(policy_dir):
            files = [f for f in os.listdir(policy_dir) if f.endswith('.txt')]
            st.info(f"📚 {len(files)} policy documents available")
            
            # Search policies
            search_query = st.text_input("🔍 Search policies", placeholder="e.g., personal loan, age requirements")
            
            if search_query and st.session_state.vector_store_loaded:
                vector_store = load_vector_store()
                results = vector_store.search(search_query, top_k=5)
                
                st.subheader("Search Results")
                for i, result in enumerate(results):
                    with st.expander(f"Result {i+1} - Similarity: {result['similarity']:.2%}"):
                        st.write(result['document'])
                        st.caption(f"Source: {result['metadata'].get('source_file', 'Unknown')}")
        else:
            st.warning("⚠️ No policy documents found")
    
    with col2:
        st.subheader("Actions")
        
        if st.button("🔄 Rebuild Knowledge Base", use_container_width=True):
            with st.spinner("Rebuilding knowledge base..."):
                try:
                    from rag.vector_store import build_knowledge_base
                    build_knowledge_base()
                    st.session_state.vector_store_loaded = False
                    st.success("✅ Knowledge base rebuilt successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        
        st.divider()
        
        st.subheader("Statistics")
        if st.session_state.vector_store_loaded:
            vector_store = load_vector_store()
            st.metric("Total Documents", len(vector_store.documents))
            st.metric("Embedding Model", config.EMBEDDING_MODEL.split('/')[-1])

def show_about_page():
    """About page"""
    st.header("ℹ️ About AI Bank Form Validator")
    
    st.markdown("""
    ### 🎯 Purpose
    This system helps bank employees validate customer forms automatically by:
    - **Extracting** all fields from uploaded forms (PDF/Images)
    - **Validating** data against official bank policies
    - **Generating** detailed compliance reports
    
    ### 🏗️ Architecture
    
    **1. Extraction Agent**
    - Uses OCR (Tesseract) to extract text from forms
    - Uses LLM (Llama 3.1) to identify and extract fields dynamically
    - Works with ANY form type - no predefined templates needed
    
    **2. Validation Agent**
    - Uses RAG (Retrieval-Augmented Generation) with FAISS vector database
    - Retrieves relevant policies based on form type and fields
    - Validates completeness and policy compliance
    
    **3. Knowledge Base**
    - 100+ bank form policies covering:
      - Account opening
      - Loans (Home, Personal, Car, Education, etc.)
      - Credit cards
      - Investments
      - KYC & Services
      - Insurance
      - NRI services
    
    ### 🛠️ Technology Stack
    - **LLM**: Groq (Llama 3.3 70B)
    - **Vector DB**: FAISS
    - **Embeddings**: Sentence Transformers
    - **OCR**: Tesseract + OpenCV
    - **UI**: Streamlit
    - **Backend**: Python
    
    ### 📋 Supported Form Types
    - ✅ Any bank form (dynamic extraction)
    - ✅ PDF documents
    - ✅ Image formats (PNG, JPG, TIFF, etc.)
    - ✅ Handwritten and printed forms
    
    ### 🚀 Features
    - **Dynamic Field Extraction**: No predefined templates
    - **Policy-Based Validation**: Uses official bank policies
    - **Comprehensive Reports**: Detailed validation results
    - **Scalable**: Easy to add new policies and banks
    """)
    
    st.divider()
    
    st.subheader("📞 Support")
    st.info("For technical support or questions, please contact the development team.")

if __name__ == "__main__":
    main()
