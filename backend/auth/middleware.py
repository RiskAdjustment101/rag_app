"""
Authentication middleware for JWT token validation.
"""

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import logging
from typing import Dict, Optional
from backend.auth.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict:
    """
    Validate JWT token and return current user information.
    
    Args:
        credentials: HTTP Bearer token from request
        
    Returns:
        Dict containing user information
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        
        # Get Supabase client
        supabase = get_supabase_client()
        if not supabase:
            logger.error("Supabase client not available")
            raise credentials_exception
        
        # Verify token with Supabase
        try:
            user_response = supabase.auth.get_user(token)
            if not user_response.user:
                logger.warning("Invalid token: user not found")
                raise credentials_exception
                
            user = user_response.user
            
            return {
                "user_id": user.id,
                "email": user.email,
                "aud": user.aud,
                "role": user.role if hasattr(user, 'role') else 'authenticated'
            }
            
        except Exception as e:
            logger.error(f"Token validation failed: {str(e)}")
            raise credentials_exception
            
    except JWTError as e:
        logger.error(f"JWT decode error: {str(e)}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise credentials_exception

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict]:
    """
    Get current user if token is provided, otherwise return None.
    Useful for endpoints that work with or without authentication.
    
    Args:
        credentials: Optional HTTP Bearer token
        
    Returns:
        User dict if authenticated, None otherwise
    """
    if not credentials:
        return None
        
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None