"""
RAG Service - Retrieve knowledge base documents using vector similarity search
"""
import os
import json
import numpy as np
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from ..db.models import KnowledgeBase
from dotenv import load_dotenv

load_dotenv()


class RAGService:
    """
    RAG Service for vector similarity search on Knowledge Base
    """
    
    def __init__(self):
        """Initialize embedding model"""
        self.embedding_model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        self.embedding_model = SentenceTransformer(self.embedding_model_name)
        self.top_k = int(os.getenv("TOP_K_RESULTS", 3))
        self.similarity_threshold = float(os.getenv("VECTOR_SEARCH_THRESHOLD", 0.5))
    
    def generate_embedding(self, text: str) -> list:
        """
        Generate embedding for text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list
        """
        embedding = self.embedding_model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def _compute_similarity(self, query_embedding: list, doc_embedding_json: str) -> float:
        """
        Compute cosine similarity between query and document embeddings
        
        Args:
            query_embedding: Query embedding as list
            doc_embedding_json: Document embedding stored as JSON string
            
        Returns:
            Similarity score (0-1)
        """
        try:
            # Parse document embedding from JSON
            doc_embedding = json.loads(doc_embedding_json)
            
            # Convert to numpy arrays
            query_vec = np.array(query_embedding).reshape(1, -1)
            doc_vec = np.array(doc_embedding).reshape(1, -1)
            
            # Compute cosine similarity
            similarity = float(cosine_similarity(query_vec, doc_vec)[0][0])
            return similarity
        except Exception as e:
            print(f"Error computing similarity: {e}")
            return 0.0
    
    def search_knowledge_base(self, db: Session, query: str, top_k: int = None) -> list:
        """
        Search knowledge base for relevant documents using vector similarity
        
        Args:
            db: Database session
            query: User query
            top_k: Number of top results to return (defaults to configured TOP_K_RESULTS)
            
        Returns:
            List of relevant KnowledgeBase documents with similarity scores
        """
        if top_k is None:
            top_k = self.top_k
        
        try:
            # Generate embedding for the query
            query_embedding = self.generate_embedding(query)
            
            # Get all knowledge base documents
            all_docs = db.query(KnowledgeBase).all()
            
            # Compute similarity for each document
            doc_scores = []
            for doc in all_docs:
                if doc.embedding:
                    similarity = self._compute_similarity(query_embedding, doc.embedding)
                    doc_scores.append((doc, similarity))
            
            # Sort by similarity and filter by threshold
            doc_scores.sort(key=lambda x: x[1], reverse=True)
            filtered_results = [
                (doc, similarity) for doc, similarity in doc_scores
                if similarity >= self.similarity_threshold
            ]
            
            # Return top-k results
            return filtered_results[:top_k]
        
        except Exception as e:
            print(f"Error searching knowledge base: {e}")
            return []
    
    def format_kb_context(self, results: list) -> str:
        """
        Format search results as context for the LLM
        
        Args:
            results: List of (KnowledgeBase, similarity_score) tuples
            
        Returns:
            Formatted context string
        """
        if not results:
            return ""
        
        context_parts = []
        
        for doc, similarity in results:
            context_parts.append(
                f"[{doc.category}] {doc.title} (relevance: {similarity:.2%})\n"
                f"{doc.content}\n"
            )
        
        return "\n".join(context_parts)
    
    def get_relevant_docs_for_query(
        self, 
        db: Session, 
        query: str, 
        top_k: int = None
    ) -> tuple:
        """
        Get relevant documents and formatted context for a query
        
        Args:
            db: Database session
            query: User query
            top_k: Number of results
            
        Returns:
            Tuple of (formatted_context, list_of_docs)
        """
        results = self.search_knowledge_base(db, query, top_k)
        
        docs = [doc for doc, _ in results]
        context = self.format_kb_context(results)
        
        return context, docs
    
    def get_all_kb_documents(self, db: Session) -> list:
        """Get all knowledge base documents"""
        return db.query(KnowledgeBase).all()
    
    def add_kb_document(
        self,
        db: Session,
        title: str,
        content: str,
        category: str
    ) -> KnowledgeBase:
        """
        Add a new knowledge base document
        
        Args:
            db: Database session
            title: Document title
            content: Document content
            category: Document category
            
        Returns:
            Created KnowledgeBase object
        """
        try:
            # Generate embedding
            combined_text = f"{title} {content}"
            embedding = self.generate_embedding(combined_text)
            
            # Create document
            kb_doc = KnowledgeBase(
                title=title,
                content=content,
                category=category,
                embedding=embedding
            )
            
            db.add(kb_doc)
            db.commit()
            db.refresh(kb_doc)
            
            return kb_doc
        
        except Exception as e:
            print(f"Error adding KB document: {e}")
            db.rollback()
            raise


# Global RAG service instance
_rag_service = None


def get_rag_service() -> RAGService:
    """Get or create RAG service instance"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
