# Claude-like RAG Application - Claude Code Implementation Guide

*A step-by-step guide for building a Claude-like RAG application using Claude Code*

**Target**: Production-ready AI SaaS with document intelligence  
**Tech Stack**: React/Next.js Frontend, Python FastAPI Backend, Supabase, Railway, Vercel  
**Timeline**: 4-week implementation cycle  

---

## 🎯 Project Overview

We're building a Claude-like application with three core components:

1. **User Authentication** - Supabase Auth with social login
2. **Chat Interface** - React/Next.js UI similar to Claude
3. **RAG Engine** - Document processing with intelligent responses

### Architecture Summary
```
React/Next.js Frontend → FastAPI Backend → RAG Engine (Chroma + Together AI)
                     ↓
                Supabase (Auth + DB) + Railway (Backend) + Vercel (Frontend)
```

---

## 🏗️ Meta Engineering Best Practices

### Documentation Standards

#### Repository Structure
```
claude-rag-app/
├── README.md                    # Project overview, quick start
├── ARCHITECTURE.md              # System design, decisions
├── DEPLOYMENT.md               # Infrastructure, environment setup
├── API.md                      # API documentation
├── CONTRIBUTING.md             # Development guidelines
├── CHANGELOG.md                # Version history
├── docs/
│   ├── user-guide.md           # End-user documentation
│   ├── development.md          # Local development setup
│   └── troubleshooting.md      # Common issues & solutions
└── .github/
    ├── ISSUE_TEMPLATE.md
    └── PULL_REQUEST_TEMPLATE.md
```

#### Code Documentation Requirements
```python
# Every function needs proper docstrings
async def process_document(file_content: bytes, filename: str, user_id: str) -> Dict:
    """
    Process uploaded document and store in vector database.
    
    Args:
        file_content: Raw file bytes from upload
        filename: Original filename with extension
        user_id: UUID of the user uploading the document
        
    Returns:
        Dict containing:
            - document_id: Unique identifier for processed document
            - filename: Original filename
            - chunks_processed: Number of text chunks created
            - status: Processing status ('success' or 'error')
            
    Raises:
        ValueError: If file format is unsupported
        ProcessingError: If document extraction fails
        
    Example:
        result = await process_document(pdf_bytes, "report.pdf", "user-123")
        print(f"Processed {result['chunks_processed']} chunks")
    """
```

#### API Documentation Format
```python
# FastAPI automatically generates docs, but add descriptions
@router.post("/documents/upload", 
    summary="Upload document for RAG processing",
    description="Accepts PDF, DOCX, or TXT files and processes them for semantic search",
    response_description="Document processing result with metadata"
)
```

### Git Workflow Standards

#### **Commit Message Convention**
```
<type>(<scope>): <description>

feat(auth): add Google OAuth integration
fix(rag): resolve embedding generation timeout
docs(api): update RAG endpoint documentation  
refactor(db): optimize vector search queries
test(chat): add integration tests for message flow
chore(deps): upgrade FastAPI to v0.104.0
```

#### **Branch Strategy**
```
main                    # Production-ready code
├── develop            # Integration branch
├── feature/auth-ui    # Feature branches
├── feature/rag-engine
├── hotfix/security-patch
└── release/v1.0.0
```

#### **PR Requirements**
- [ ] Descriptive title and description
- [ ] Tests pass (unit + integration)
- [ ] Documentation updated
- [ ] Security review for auth/data changes
- [ ] Performance impact assessed
- [ ] Breaking changes documented

### Claude Code Context Management

#### **1. Maintain Clear Requirements**
```markdown
# Always start Claude Code sessions with:

## Current Context:
- Building Claude-like RAG application
- Tech stack: React/Next.js + FastAPI + Supabase + Chroma
- Target: Production-ready with safety-first architecture
- Phase: [Authentication/RAG Engine/Frontend/Deployment]

## Specific Task:
[Detailed description of what needs to be built]

## Requirements:
- Follow Meta engineering standards
- Include comprehensive error handling
- Add proper logging and monitoring
- Write tests for critical paths
- Document all public APIs
```

#### **2. Iterative Development Approach**
```markdown
# Claude Code Session Pattern:

1. **Start with Architecture**: "Create the module structure for [component]"
2. **Core Implementation**: "Implement the main functionality with error handling"
3. **Testing**: "Add unit tests and integration tests"
4. **Documentation**: "Add comprehensive docstrings and API docs"
5. **Security Review**: "Add input validation and security measures"
6. **Performance**: "Optimize for production use"
```

#### **3. Context Preservation Commands**
```
# Always provide context in prompts:

"In our Claude-like RAG application using FastAPI + React:
- We have Supabase auth already implemented
- Vector database is Chroma with user-specific collections  
- LLM integration uses Together AI
- Current task: [specific task]
- Previous implementation: [brief summary]
- Required: [specific requirements]"
```

#### **4. Preventing Context Drift**
- Create detailed ARCHITECTURE.md with all decisions
- Use consistent naming conventions across all components
- Document component interfaces and data models
- Reference existing code structure in new requests
- Maintain a project glossary for domain terms

### Quality Assurance Standards

#### **Testing Requirements**
```python
# Test structure for each component
tests/
├── unit/
│   ├── test_auth.py
│   ├── test_rag_engine.py
│   └── test_document_processor.py
├── integration/
│   ├── test_api_endpoints.py
│   └── test_rag_pipeline.py
└── e2e/
    └── test_user_flows.py

# Coverage requirements: >80% for critical paths
pytest --cov=src --cov-report=html --cov-fail-under=80
```

#### **Security Standards**
```python
# Input validation for all endpoints
from pydantic import BaseModel, validator

class ChatRequest(BaseModel):
    message: str
    conversation_id: str
    
    @validator('message')
    def validate_message(cls, v):
        if len(v) > 10000:
            raise ValueError('Message too long')
        return v.strip()

# Rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
limiter = Limiter(key_func=get_user_id)

@app.post("/chat/query")
@limiter.limit("10/minute")
async def chat_query(request: Request, ...):
    pass
```

#### **Performance Standards**
```python
# Monitoring and metrics
import time
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests')
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    REQUEST_LATENCY.observe(process_time)
    REQUEST_COUNT.inc()
    return response
```

### Code Review Checklist

#### **Before Committing**
- [ ] Code follows PEP 8 (Python) / Prettier (JavaScript)
- [ ] All functions have proper docstrings
- [ ] Error handling covers edge cases
- [ ] No hardcoded secrets or URLs
- [ ] Performance impact considered
- [ ] Security implications reviewed

#### **Claude Code Handoff**
```markdown
# When switching Claude Code sessions, always provide:

## Previous Work Summary:
- Completed: [list of implemented features]
- Current state: [what's working/tested]
- Next steps: [specific next tasks]
- Known issues: [any bugs or limitations]

## Code Structure:
- Entry points: [main files to start from]
- Key dependencies: [important imports/connections]
- Data models: [schemas and interfaces defined]

## Environment Setup:
- Required env vars: [list with examples]
- Database schema: [current table structure]
- API endpoints: [what's implemented]
```

---

## 📋 Claude Code Commands Sequence

### Phase 1: Project Setup & Authentication

#### Command 1: Initialize FastAPI Backend
```
Create a FastAPI application with the following structure:
- User authentication using Supabase
- CORS middleware for frontend communication  
- Environment variable configuration
- Basic health check endpoint
- Error handling middleware
- Logging configuration

Include these dependencies in requirements.txt:
- fastapi
- uvicorn
- supabase
- python-multipart
- python-jose[cryptography]
- passlib[bcrypt]
- redis
- sqlalchemy
- alembic

Create main.py with:
- FastAPI app initialization
- Supabase client setup
- CORS configuration
- Basic endpoints: /health, /auth/verify
- Environment variables: SUPABASE_URL, SUPABASE_KEY, REDIS_URL
```

#### Command 2: Create React Frontend with Next.js
```
Initialize a Next.js project with Claude-like UI:
- Create Next.js app with TypeScript and Tailwind CSS
- Setup Supabase client for authentication
- Implement Claude-inspired design system
- Create authentication pages (login/register)
- Build chat interface components
- Setup environment variables for API endpoints

Project structure:
pages/
├── index.js - Landing page
├── login.js - Authentication
├── dashboard.js - Main chat interface
└── api/auth/[...nextauth].js - Auth API

components/
├── Chat/
│   ├── ChatInterface.jsx
│   ├── MessageList.jsx
│   ├── ChatInput.jsx
│   └── DocumentUpload.jsx
├── Auth/
│   ├── LoginForm.jsx
│   └── RegisterForm.jsx
└── Layout/
    ├── Header.jsx
    └── Sidebar.jsx

Dependencies to include:
- @supabase/supabase-js
- @tailwindcss/forms
- @headlessui/react
- lucide-react (for icons)
- react-hot-toast (for notifications)

Design requirements:
- Claude-inspired color scheme (orange/cream palette)
- Responsive design for mobile/desktop
- Dark mode support
- Smooth animations and transitions
- File upload drag-and-drop interface
```
#### Command 3: Setup Supabase Authentication Backend
- JWT token verification middleware
- User profile management
- Social login support (Google, GitHub)
- Protected route decorators
- User session management

Files to create:
- auth/supabase_client.py - Supabase connection
- auth/middleware.py - JWT verification
- auth/models.py - User models
- auth/routes.py - Auth endpoints

Include error handling for:
- Invalid tokens
- Expired sessions
- User not found
- Permission