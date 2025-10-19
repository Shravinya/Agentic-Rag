"""Vector store implementation using FAISS for RAG"""
import os
import pickle
import numpy as np
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
import faiss
import config
from utils.text_processing import chunk_text, clean_text

class VectorStore:
    """FAISS-based vector store for document retrieval"""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or config.EMBEDDING_MODEL
        self.model = SentenceTransformer(self.model_name)
        self.index = None
        self.documents = []
        self.metadata = []
        
    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """Create embeddings for a list of texts"""
        embeddings = self.model.encode(texts, show_progress_bar=True)
        return embeddings
    
    def build_index(self, documents: List[str], metadata: List[Dict] = None):
        """Build FAISS index from documents"""
        print("🔨 Building vector index...")
        
        # Store documents
        self.documents = documents
        self.metadata = metadata or [{} for _ in documents]
        
        # Create embeddings
        embeddings = self.create_embeddings(documents)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.astype('float32'))
        
        print(f"✅ Index built with {len(documents)} documents")
    
    def add_documents(self, documents: List[str], metadata: List[Dict] = None):
        """Add new documents to existing index"""
        if self.index is None:
            self.build_index(documents, metadata)
            return
        
        # Create embeddings for new documents
        embeddings = self.create_embeddings(documents)
        
        # Add to index
        self.index.add(embeddings.astype('float32'))
        
        # Store documents and metadata
        self.documents.extend(documents)
        self.metadata.extend(metadata or [{} for _ in documents])
        
        print(f"✅ Added {len(documents)} documents to index")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for similar documents"""
        if self.index is None:
            raise ValueError("Index not built. Call build_index first.")
        
        # Create query embedding
        query_embedding = self.model.encode([query])
        
        # Search
        distances, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        # Prepare results
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.documents):
                results.append({
                    'rank': i + 1,
                    'document': self.documents[idx],
                    'metadata': self.metadata[idx],
                    'distance': float(dist),
                    'similarity': 1 / (1 + float(dist))  # Convert distance to similarity
                })
        
        return results
    
    def save(self, path: str = None):
        """Save index and documents to disk"""
        path = path or config.VECTOR_DB_DIR
        
        # Save FAISS index
        index_path = os.path.join(path, "faiss_index.bin")
        faiss.write_index(self.index, index_path)
        
        # Save documents and metadata
        data_path = os.path.join(path, "documents.pkl")
        with open(data_path, 'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'metadata': self.metadata,
                'model_name': self.model_name
            }, f)
        
        print(f"✅ Vector store saved to {path}")
    
    def load(self, path: str = None):
        """Load index and documents from disk"""
        path = path or config.VECTOR_DB_DIR
        
        # Load FAISS index
        index_path = os.path.join(path, "faiss_index.bin")
        if os.path.exists(index_path):
            self.index = faiss.read_index(index_path)
        else:
            raise FileNotFoundError(f"Index not found at {index_path}")
        
        # Load documents and metadata
        data_path = os.path.join(path, "documents.pkl")
        with open(data_path, 'rb') as f:
            data = pickle.load(f)
            self.documents = data['documents']
            self.metadata = data['metadata']
            self.model_name = data.get('model_name', self.model_name)
        
        print(f"✅ Vector store loaded from {path}")
        print(f"📊 Loaded {len(self.documents)} documents")

def build_knowledge_base():
    """Build knowledge base from scraped policies"""
    print("🏗️ Building knowledge base...")
    
    # Initialize vector store
    vector_store = VectorStore()
    
    # Load policy documents
    policy_dir = config.RAW_POLICIES_DIR
    documents = []
    metadata = []
    
    # Read all policy files
    for filename in os.listdir(policy_dir):
        if filename.endswith('.txt'):
            filepath = os.path.join(policy_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Clean and chunk the document
            cleaned = clean_text(content)
            chunks = chunk_text(cleaned, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
            
            # Add chunks with metadata
            for chunk in chunks:
                documents.append(chunk)
                metadata.append({
                    'source_file': filename,
                    'form_type': filename.replace('policy_', '').replace('.txt', '').replace('_', ' ')
                })
    
    print(f"📄 Loaded {len(documents)} document chunks from {len(os.listdir(policy_dir))} files")
    
    # Build index
    vector_store.build_index(documents, metadata)
    
    # Save
    vector_store.save()
    
    return vector_store

if __name__ == "__main__":
    build_knowledge_base()
