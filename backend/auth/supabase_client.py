"""
Supabase client configuration and management.
"""

from supabase import create_client, Client
from typing import Optional
import logging
from backend.config.settings import get_settings

logger = logging.getLogger(__name__)

class SupabaseClient:
    """Singleton Supabase client manager."""
    _instance: Optional[Client] = None
    
    @classmethod
    def get_client(cls) -> Optional[Client]:
        """
        Get or create Supabase client instance.
        
        Returns:
            Supabase client instance or None if not configured
        """
        if cls._instance is None:
            settings = get_settings()
            
            if not settings.supabase_url or not settings.supabase_service_key:
                logger.warning("Supabase credentials not configured")
                return None
            
            try:
                cls._instance = create_client(
                    settings.supabase_url, 
                    settings.supabase_service_key
                )
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {str(e)}")
                return None
        
        return cls._instance
    
    @classmethod
    def reset_client(cls):
        """Reset the Supabase client instance."""
        cls._instance = None

def get_supabase_client() -> Optional[Client]:
    """Get Supabase client instance."""
    return SupabaseClient.get_client()