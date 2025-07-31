"""
RAG (Retrieval Augmented Generation) Module

This module provides document processing, vector storage, and AI-powered 
question answering capabilities for the RAG application.
"""

from backend.rag.rag_service import get_rag_service
from backend.rag.vector_store import get_vector_store
from backend.rag.document_processor import get_document_processor
from backend.rag.llm_client import get_llm_client

__all__ = [
    'get_rag_service',
    'get_vector_store', 
    'get_document_processor',
    'get_llm_client'
]