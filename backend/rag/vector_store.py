"""
Vector Store Configuration using ChromaDB
"""
import os
import uuid
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

class VectorStore:
    """ChromaDB vector store for document embeddings"""
    
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.chroma_client = None
        self.collection = None
        self._initialize_chroma()
    
    def _initialize_chroma(self):
        """Initialize ChromaDB client and collection"""
        try:
            # Use persistent storage in production, in-memory for development
            chroma_data_path = os.getenv("CHROMA_DATA_PATH", "./chroma_data")
            
            self.chroma_client = chromadb.PersistentClient(
                path=chroma_data_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection for document chunks
            self.collection = self.chroma_client.get_or_create_collection(
                name="document_chunks",
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info(f"ChromaDB initialized with {self.collection.count()} existing documents")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
    
    def add_documents(
        self, 
        texts: List[str], 
        metadatas: List[Dict[str, Any]], 
        user_id: str,
        document_id: str
    ) -> List[str]:
        """Add document chunks to vector store"""
        try:
            # Generate embeddings
            embeddings = self.embedding_model.encode(texts).tolist()
            
            # Generate unique IDs for each chunk
            chunk_ids = [f"{document_id}_{i}_{uuid.uuid4().hex[:8]}" for i in range(len(texts))]
            
            # Add user_id to all metadata
            for metadata in metadatas:
                metadata["user_id"] = user_id
                metadata["document_id"] = document_id
            
            # Add to ChromaDB
            self.collection.add(
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=chunk_ids
            )
            
            logger.info(f"Added {len(texts)} chunks for document {document_id}")
            return chunk_ids
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise
    
    def search_similar(
        self, 
        query: str, 
        user_id: str,
        n_results: int = 5,
        document_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar document chunks"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()[0]
            
            # Build where clause for user filtering
            where_clause = {"user_id": {"$eq": user_id}}
            
            # Add document filtering if specified
            if document_ids:
                where_clause["document_id"] = {"$in": document_ids}
            
            # Search ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and len(results['documents'][0]) > 0:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        "text": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "score": 1 - results['distances'][0][i],  # Convert distance to similarity
                        "document_id": results['metadatas'][0][i].get('document_id')
                    })
            
            logger.info(f"Found {len(formatted_results)} similar chunks for query")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search documents: {e}")
            raise
    
    def delete_document(self, document_id: str, user_id: str) -> bool:
        """Delete all chunks for a document"""
        try:
            # Find all chunks for this document
            results = self.collection.get(
                where={
                    "document_id": {"$eq": document_id},
                    "user_id": {"$eq": user_id}
                }
            )
            
            if results['ids']:
                # Delete the chunks
                self.collection.delete(ids=results['ids'])
                logger.info(f"Deleted {len(results['ids'])} chunks for document {document_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete document chunks: {e}")
            raise
    
    def get_user_document_count(self, user_id: str) -> int:
        """Get count of unique documents for a user"""
        try:
            results = self.collection.get(
                where={"user_id": {"$eq": user_id}},
                include=["metadatas"]
            )
            
            # Count unique document IDs
            unique_docs = set()
            for metadata in results['metadatas']:
                unique_docs.add(metadata.get('document_id'))
            
            return len(unique_docs)
            
        except Exception as e:
            logger.error(f"Failed to get document count: {e}")
            return 0

# Global vector store instance
vector_store = None

def get_vector_store() -> VectorStore:
    """Get or create global vector store instance"""
    global vector_store
    if vector_store is None:
        vector_store = VectorStore()
    return vector_store