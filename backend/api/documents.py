"""
Document upload and management endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from typing import List, Dict, Any
import uuid
from datetime import datetime
import mimetypes

from backend.auth.middleware import get_current_user
from backend.auth.supabase_client import get_supabase_client
from backend.config.settings import get_settings

router = APIRouter()
settings = get_settings()

ALLOWED_EXTENSIONS = {'.pdf', '.txt', '.docx', '.md'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Upload a document to Supabase Storage.
    
    Args:
        file: The uploaded file
        current_user: Authenticated user info
        
    Returns:
        Document metadata including storage path
    """
    # Validate file extension
    file_ext = '.' + file.filename.split('.')[-1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_ext} not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Validate file size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Reset file pointer
    await file.seek(0)
    
    # Generate unique filename
    document_id = str(uuid.uuid4())
    storage_path = f"{current_user['user_id']}/{document_id}{file_ext}"
    
    # Upload to Supabase Storage
    supabase = get_supabase_client()
    try:
        # Upload file
        response = supabase.storage.from_('documents').upload(
            path=storage_path,
            file=contents,
            file_options={"content-type": file.content_type}
        )
        
        # Create document record in database
        document_data = {
            'id': document_id,
            'user_id': current_user['user_id'],
            'filename': file.filename,
            'file_type': file_ext,
            'file_size': len(contents),
            'storage_path': storage_path,
            'created_at': datetime.utcnow().isoformat(),
            'status': 'uploaded'
        }
        
        db_response = supabase.table('documents').insert(document_data).execute()
        
        return {
            'message': 'Document uploaded successfully',
            'document': db_response.data[0]
        }
        
    except Exception as e:
        # Clean up storage if database insert fails
        try:
            supabase.storage.from_('documents').remove([storage_path])
        except:
            pass
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}"
        )

@router.get("/")
async def list_documents(
    current_user: Dict = Depends(get_current_user),
    limit: int = 20,
    offset: int = 0
) -> Dict[str, Any]:
    """
    List user's documents.
    
    Args:
        current_user: Authenticated user info
        limit: Number of documents to return
        offset: Pagination offset
        
    Returns:
        List of user's documents
    """
    supabase = get_supabase_client()
    
    try:
        response = supabase.table('documents') \
            .select('*') \
            .eq('user_id', current_user['user_id']) \
            .order('created_at', desc=True) \
            .range(offset, offset + limit - 1) \
            .execute()
        
        # Get total count
        count_response = supabase.table('documents') \
            .select('id', count='exact') \
            .eq('user_id', current_user['user_id']) \
            .execute()
        
        return {
            'documents': response.data,
            'total': count_response.count,
            'limit': limit,
            'offset': offset
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch documents: {str(e)}"
        )

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Delete a document.
    
    Args:
        document_id: ID of the document to delete
        current_user: Authenticated user info
        
    Returns:
        Success message
    """
    supabase = get_supabase_client()
    
    try:
        # Get document info
        doc_response = supabase.table('documents') \
            .select('*') \
            .eq('id', document_id) \
            .eq('user_id', current_user['user_id']) \
            .single() \
            .execute()
        
        if not doc_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        document = doc_response.data
        
        # Delete from storage
        supabase.storage.from_('documents').remove([document['storage_path']])
        
        # Delete from database
        supabase.table('documents') \
            .delete() \
            .eq('id', document_id) \
            .eq('user_id', current_user['user_id']) \
            .execute()
        
        return {'message': 'Document deleted successfully'}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )