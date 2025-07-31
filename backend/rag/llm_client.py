"""
LLM Client for RAG responses
Supports Together AI and OpenAI
"""
import os
from typing import List, Dict, Any, Optional
import logging
from together import Together
import openai

logger = logging.getLogger(__name__)

class LLMClient:
    """Client for generating RAG responses using LLMs"""
    
    def __init__(self):
        self.together_client = None
        self.openai_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize LLM clients based on available API keys"""
        # Together AI setup
        together_api_key = os.getenv("TOGETHER_API_KEY")
        if together_api_key:
            try:
                self.together_client = Together(api_key=together_api_key)
                logger.info("Together AI client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Together AI: {e}")
        
        # OpenAI setup
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            try:
                self.openai_client = openai.OpenAI(api_key=openai_api_key)
                logger.info("OpenAI client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI: {e}")
        
        if not self.together_client and not self.openai_client:
            logger.warning("No LLM clients available - responses will be limited")
    
    async def generate_response(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Generate a response using RAG context
        
        Args:
            query: User's question
            context_chunks: Relevant document chunks
            chat_history: Previous conversation messages
            
        Returns:
            Dict with response, sources, and metadata
        """
        try:
            # Build context from retrieved chunks
            context = self._build_context(context_chunks)
            
            # Create system prompt
            system_prompt = self._create_system_prompt()
            
            # Create user prompt with context
            user_prompt = self._create_user_prompt(query, context, chat_history)
            
            # Generate response using available client
            if self.together_client:
                response = await self._generate_together_response(system_prompt, user_prompt)
            elif self.openai_client:
                response = await self._generate_openai_response(system_prompt, user_prompt)
            else:
                # Fallback response when no LLM is available
                response = self._generate_fallback_response(query, context_chunks)
            
            # Extract source information
            sources = self._extract_sources(context_chunks)
            
            return {
                "response": response,
                "sources": sources,
                "context_used": len(context_chunks),
                "model": self._get_active_model()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            return {
                "response": "I apologize, but I encountered an error while processing your question. Please try again.",
                "sources": [],
                "context_used": 0,
                "error": str(e)
            }
    
    def _build_context(self, context_chunks: List[Dict[str, Any]]) -> str:
        """Build context string from retrieved chunks"""
        if not context_chunks:
            return "No relevant documents found."
        
        context_parts = []
        for i, chunk in enumerate(context_chunks[:5]):  # Limit to top 5 chunks
            filename = chunk.get('metadata', {}).get('filename', 'Unknown')
            text = chunk.get('text', '')
            score = chunk.get('score', 0)
            
            context_parts.append(
                f"Document {i+1} ({filename}, relevance: {score:.2f}):\n{text}\n"
            )
        
        return "\n---\n".join(context_parts)
    
    def _create_system_prompt(self) -> str:
        """Create system prompt for the LLM"""
        return """You are a helpful AI assistant that answers questions based on provided document context. 

Guidelines:
- Use the provided document context to answer questions accurately
- If the context doesn't contain enough information, clearly state this
- Cite specific documents when referencing information
- Be concise but comprehensive in your responses
- If asked about something not in the context, explain that you can only answer based on the provided documents
- Maintain a professional and helpful tone"""
    
    def _create_user_prompt(
        self, 
        query: str, 
        context: str, 
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Create user prompt with context and history"""
        prompt_parts = []
        
        # Add chat history if available
        if chat_history:
            prompt_parts.append("Previous conversation:")
            for msg in chat_history[-3:]:  # Last 3 messages for context
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                prompt_parts.append(f"{role.title()}: {content}")
            prompt_parts.append("")
        
        # Add document context
        prompt_parts.append("Relevant document context:")
        prompt_parts.append(context)
        prompt_parts.append("")
        
        # Add current query
        prompt_parts.append(f"Question: {query}")
        prompt_parts.append("")
        prompt_parts.append("Please provide a helpful answer based on the document context above.")
        
        return "\n".join(prompt_parts)
    
    async def _generate_together_response(self, system_prompt: str, user_prompt: str) -> str:
        """Generate response using Together AI"""
        try:
            response = self.together_client.chat.completions.create(
                model="meta-llama/Llama-2-70b-chat-hf",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.7,
                top_p=0.9
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Together AI request failed: {e}")
            raise
    
    async def _generate_openai_response(self, system_prompt: str, user_prompt: str) -> str:
        """Generate response using OpenAI"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI request failed: {e}")
            raise
    
    def _generate_fallback_response(self, query: str, context_chunks: List[Dict[str, Any]]) -> str:
        """Generate fallback response when no LLM is available"""
        if not context_chunks:
            return "I found no relevant documents to answer your question. Please try uploading documents related to your query."
        
        # Simple keyword-based response
        context_preview = ""
        for chunk in context_chunks[:2]:
            text = chunk.get('text', '')[:200]
            filename = chunk.get('metadata', {}).get('filename', 'document')
            context_preview += f"\n\nFrom {filename}: {text}..."
        
        return f"I found {len(context_chunks)} relevant document(s) for your query. Here's what I found:{context_preview}\n\n(Note: Full AI responses require API key configuration)"
    
    def _extract_sources(self, context_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract source information from context chunks"""
        sources = []
        seen_docs = set()
        
        for chunk in context_chunks:
            metadata = chunk.get('metadata', {})
            doc_id = metadata.get('document_id')
            
            if doc_id and doc_id not in seen_docs:
                sources.append({
                    "document_id": doc_id,
                    "filename": metadata.get('filename', 'Unknown'),
                    "relevance_score": chunk.get('score', 0),
                    "chunk_count": sum(1 for c in context_chunks 
                                     if c.get('metadata', {}).get('document_id') == doc_id)
                })
                seen_docs.add(doc_id)
        
        return sources
    
    def _get_active_model(self) -> str:
        """Get the name of the active model"""
        if self.together_client:
            return "meta-llama/Llama-2-70b-chat-hf"
        elif self.openai_client:
            return "gpt-3.5-turbo"
        else:
            return "fallback"

# Global LLM client instance
llm_client = None

def get_llm_client() -> LLMClient:
    """Get or create global LLM client instance"""
    global llm_client
    if llm_client is None:
        llm_client = LLMClient()
    return llm_client