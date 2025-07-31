"""
RAG Service - Main orchestrator for Retrieval Augmented Generation
"""
import os
from typing import List, Dict, Any, Optional, Tuple
import logging
from fastapi import UploadFile, HTTPException

from backend.rag.vector_store import get_vector_store
from backend.rag.document_processor import get_document_processor
from backend.rag.llm_client import get_llm_client

logger = logging.getLogger(__name__)

class RAGService:
    """Main RAG service for document processing and question answering"""
    
    def __init__(self):
        self.vector_store = get_vector_store()
        self.document_processor = get_document_processor()
        self.llm_client = get_llm_client()
    
    async def ingest_document(
        self, 
        file: UploadFile, 
        user_id: str
    ) -> Dict[str, Any]:
        """
        Ingest a document into the RAG system
        
        Args:
            file: Uploaded file
            user_id: User identifier
            
        Returns:
            Dict with ingestion results and metadata
        """
        try:
            # Validate file
            if not file.filename:
                raise HTTPException(status_code=400, detail="No filename provided")
            
            # Check file size (50MB limit)
            max_size = 50 * 1024 * 1024  # 50MB
            file_content = await file.read()
            
            if len(file_content) > max_size:
                raise HTTPException(
                    status_code=413, 
                    detail=f"File too large. Maximum size is {max_size//1024//1024}MB"
                )
            
            # Check file type
            allowed_extensions = {'pdf', 'docx', 'doc', 'txt'}
            file_extension = file.filename.lower().split('.')[-1]
            
            if file_extension not in allowed_extensions:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
                )
            
            # Process document
            logger.info(f"Processing document {file.filename} for user {user_id}")
            document_id, chunks_with_metadata = await self.document_processor.process_document(
                file_content, file.filename, user_id
            )
            
            # Extract texts and metadata for vector store
            texts = [chunk['text'] for chunk in chunks_with_metadata]
            metadatas = [chunk['metadata'] for chunk in chunks_with_metadata]
            
            # Add to vector store
            chunk_ids = self.vector_store.add_documents(
                texts=texts,
                metadatas=metadatas,
                user_id=user_id,
                document_id=document_id
            )
            
            # Prepare response
            result = {
                "document_id": document_id,
                "filename": file.filename,
                "file_size": len(file_content),
                "file_type": file_extension,
                "chunks_created": len(chunks_with_metadata),
                "total_tokens": sum(metadata['token_count'] for metadata in metadatas),
                "processing_status": "completed"
            }
            
            logger.info(f"Successfully ingested document {file.filename}: {len(chunks_with_metadata)} chunks")
            return result
            
        except Exception as e:
            logger.error(f"Document ingestion failed: {e}")
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")
    
    async def query_documents(
        self,
        query: str,
        user_id: str,
        document_ids: Optional[List[str]] = None,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Query documents using RAG
        
        Args:
            query: User's question
            user_id: User identifier
            document_ids: Optional list of specific documents to search
            chat_history: Previous conversation messages
            
        Returns:
            Dict with response, sources, and metadata
        """
        try:
            if not query.strip():
                raise HTTPException(status_code=400, detail="Query cannot be empty")
            
            # Retrieve relevant document chunks
            logger.info(f"Searching for relevant chunks for query: {query[:100]}...")
            relevant_chunks = self.vector_store.search_similar(
                query=query,
                user_id=user_id,
                n_results=5,
                document_ids=document_ids
            )
            
            if not relevant_chunks:
                return {
                    "response": "I couldn't find any relevant information in your documents to answer this question. Please make sure you have uploaded documents related to your query.",
                    "sources": [],
                    "context_used": 0,
                    "suggestions": [
                        "Try rephrasing your question",
                        "Upload documents related to your topic",
                        "Check if your documents contain the information you're looking for"
                    ]
                }
            
            # Generate response using LLM
            logger.info(f"Generating response with {len(relevant_chunks)} relevant chunks")
            response_data = await self.llm_client.generate_response(
                query=query,
                context_chunks=relevant_chunks,
                chat_history=chat_history
            )
            
            # Add query metadata
            response_data.update({
                "query": query,
                "timestamp": self._get_timestamp(),
                "total_documents_searched": self.vector_store.get_user_document_count(user_id)
            })
            
            return response_data
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=f"Failed to process query: {str(e)}")
    
    async def delete_document(self, document_id: str, user_id: str) -> Dict[str, Any]:
        """
        Delete a document from the RAG system
        
        Args:
            document_id: Document identifier
            user_id: User identifier
            
        Returns:
            Dict with deletion results
        """
        try:
            # Delete from vector store
            success = self.vector_store.delete_document(document_id, user_id)
            
            if success:
                logger.info(f"Successfully deleted document {document_id} for user {user_id}")
                return {
                    "document_id": document_id,
                    "status": "deleted",
                    "message": "Document successfully removed from knowledge base"
                }
            else:
                raise HTTPException(
                    status_code=404, 
                    detail="Document not found or you don't have permission to delete it"
                )
                
        except Exception as e:
            logger.error(f"Document deletion failed: {e}")
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's RAG statistics
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict with user statistics
        """
        try:
            document_count = self.vector_store.get_user_document_count(user_id)
            
            return {
                "user_id": user_id,
                "total_documents": document_count,
                "rag_enabled": document_count > 0,
                "vector_store_status": "active" if self.vector_store else "inactive",
                "llm_status": self.llm_client._get_active_model()
            }
            
        except Exception as e:
            logger.error(f"Failed to get user stats: {e}")
            return {
                "user_id": user_id,
                "total_documents": 0,
                "rag_enabled": False,
                "error": str(e)
            }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

# Global RAG service instance
rag_service = None

def get_rag_service() -> RAGService:
    """Get or create global RAG service instance"""
    global rag_service
    if rag_service is None:
        rag_service = RAGService()
    return rag_service