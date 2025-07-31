"""
RAG API Endpoints
Handles document upload, processing, and question answering
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from pydantic import BaseModel

from backend.auth.middleware import get_current_user
from backend.rag import get_rag_service

router = APIRouter(prefix="/rag", tags=["RAG"])

# Request/Response Models
class QueryRequest(BaseModel):
    query: str
    document_ids: Optional[List[str]] = None
    chat_history: Optional[List[Dict[str, str]]] = None

class QueryResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]]
    context_used: int
    model: str
    query: str
    timestamp: str
    total_documents_searched: int

class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    file_size: int
    file_type: str
    chunks_created: int
    total_tokens: int
    processing_status: str

class UserStatsResponse(BaseModel):
    user_id: str
    total_documents: int
    rag_enabled: bool
    vector_store_status: str
    llm_status: str

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: Dict = Depends(get_current_user)
):
    """
    Upload and process a document for RAG
    
    Supported formats: PDF, DOCX, TXT
    Maximum size: 50MB
    """
    rag_service = get_rag_service()
    
    result = await rag_service.ingest_document(
        file=file,
        user_id=current_user["id"]
    )
    
    return DocumentUploadResponse(**result)

@router.post("/query", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Query your documents using RAG
    
    Retrieves relevant document chunks and generates AI-powered responses
    """
    rag_service = get_rag_service()
    
    result = await rag_service.query_documents(
        query=request.query,
        user_id=current_user["id"],
        document_ids=request.document_ids,
        chat_history=request.chat_history
    )
    
    return QueryResponse(**result)

@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Delete a document from your knowledge base
    """
    rag_service = get_rag_service()
    
    result = await rag_service.delete_document(
        document_id=document_id,
        user_id=current_user["id"]
    )
    
    return result

@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(
    current_user: Dict = Depends(get_current_user)
):
    """
    Get your RAG usage statistics
    """
    rag_service = get_rag_service()
    
    stats = rag_service.get_user_stats(current_user["id"])
    
    return UserStatsResponse(**stats)