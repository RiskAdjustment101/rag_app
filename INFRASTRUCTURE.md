# RAG Application Infrastructure Architecture

## 🏗️ Complete Infrastructure Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              Production Environment                     |
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────┐        ┌─────────────────┐      ┌──────────────┐   │
│  │                 │        │                 │      │              │   │
│  │  Vercel (CDN)   │◄──────►│  Render         │◄────►│  Supabase    │   │
│  │  - Next.js App  │  API   │  - FastAPI      │      │  - Auth      │   │
│  │  - React UI     │  Calls │  - REST API     │      │  - Database  │   │
│  │  - Static Files │        │  - Python 3.10  │      │  - Storage   │   │
│  │                 │        │                 │      │              │   │
│  └─────────────────┘        └────────┬────────┘      └──────────────┘   │
│                                      │                                  │
│                             ┌────────▼────────┐                         │
│                             │                 │                         │
│                             │  Redis Cache    │                         │
│                             │  (Render)       │                         │
│                             │                 │                         │
│                             └────────┬────────┘                         │
│                                      │                                  │
│                    ┌─────────────────┴─────────────────┐                │
│                    │                                   │                │
│          ┌─────────▼────────┐              ┌──────────▼──────────┐      │
│          │                  │              │                     │      │
│          │  ChromaDB        │              │  Together AI        │      │ 
│          │  Vector Store    │              │  LLM API            │      │
│          │  (Railway)       │              │                     │      │
│          │                  │              │                     │      │
│          └──────────────────┘              └─────────────────---─┘      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## 📋 Service Components

### 1. **Frontend - Vercel**
- **Purpose**: Hosts Next.js application
- **Features**:
  - Automatic HTTPS/SSL
  - Global CDN distribution
  - Automatic deployments from GitHub
  - Preview environments for PRs
  - Edge functions support
- **URL Structure**:
  - Production: `https://your-app.vercel.app` or custom domain
  - Preview: `https://your-app-git-branch-name.vercel.app`

### 2. **Backend API - Render**
- **Purpose**: Hosts FastAPI application
- **Components**:
  - FastAPI web server
  - Redis for caching (Render Redis addon)
  - ChromaDB for vector storage
  - Background job processing
- **URL**: `https://your-app.onrender.com`

### 3. **Database & Auth - Supabase**
- **Purpose**: PostgreSQL database and authentication
- **Features**:
  - PostgreSQL database
  - Row Level Security (RLS)
  - Authentication (Email, OAuth)
  - Realtime subscriptions
  - File storage for documents
- **Endpoints**:
  - Database: `postgresql://[user]:[pass]@db.[project].supabase.co:5432/postgres`
  - Auth API: `https://[project].supabase.co/auth/v1`
  - Storage API: `https://[project].supabase.co/storage/v1`

### 4. **Vector Database - ChromaDB**
- **Purpose**: Store and query document embeddings
- **Deployment**: Self-hosted on Railway
- **Features**:
  - Persistent storage
  - User-specific collections
  - Semantic search

### 5. **LLM Provider - Together AI**
- **Purpose**: Language model inference
- **Models**:
  - Chat: `meta-llama/Llama-2-70b-chat-hf`
  - Embeddings: `togethercomputer/m2-bert-80M-8k-retrieval`
- **API**: `https://api.together.xyz`

### 6. **Caching - Redis**
- **Purpose**: Cache frequently accessed data
- **Use cases**:
  - Session storage
  - Rate limiting
  - Query results caching
  - Temporary file storage

## 🔐 Security & Authentication Flow

```
User Login Flow:
1. User → Vercel Frontend → Supabase Auth
2. Supabase returns JWT token
3. Frontend stores token in secure cookie
4. All API calls include JWT in Authorization header
5. Backend validates JWT with Supabase
6. Backend checks user permissions in database
```

## 🚀 Development to Production Workflow

### Git Repository Structure
```
rag_app/
├── .github/
│   ├── workflows/
│   │   ├── frontend-deploy.yml    # Vercel deployment
│   │   ├── backend-deploy.yml     # Railway deployment
│   │   └── tests.yml              # Run tests on PR
│   └── dependabot.yml
├── frontend/                      # Next.js application
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── public/
│   ├── package.json
│   └── .env.local.example
├── backend/                       # FastAPI application
│   ├── api/
│   ├── auth/
│   ├── rag/
│   ├── models/
│   ├── requirements.txt
│   └── .env.example
├── docs/                         # Documentation
├── scripts/                      # Deployment & setup scripts
├── docker-compose.yml            # Local development
├── .gitignore
├── README.md
└── CLAUDE.md
```

### Branching Strategy
```
main (production)
├── develop (staging)
├── feature/user-auth
├── feature/rag-engine
├── feature/chat-ui
└── hotfix/security-patch
```

### Deployment Pipeline

#### Frontend (Vercel)
1. **Development**: Push to feature branch → Preview deployment
2. **Staging**: Merge to develop → Staging deployment
3. **Production**: Merge to main → Production deployment

```yaml
# .github/workflows/frontend-deploy.yml
name: Deploy Frontend
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: vercel/action@v3
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
```

#### Backend (Railway)
1. **Development**: Local testing with Docker
2. **Staging**: Deploy to Railway staging environment
3. **Production**: Deploy to Railway production

```yaml
# .github/workflows/backend-deploy.yml
name: Deploy Backend
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install Railway CLI
        run: npm i -g @railway/cli
      - name: Deploy to Railway
        run: railway up
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

## 🔑 Environment Variables & Secrets

### Required API Keys & Services

1. **Supabase**
   - Sign up at: https://supabase.com
   - Create new project
   - Required keys:
     - `SUPABASE_URL`
     - `SUPABASE_ANON_KEY` (Frontend)
     - `SUPABASE_SERVICE_KEY` (Backend)

2. **Together AI**
   - Sign up at: https://together.ai
   - Get API key from dashboard
   - Required: `TOGETHER_API_KEY`

3. **Railway**
   - Sign up at: https://railway.app
   - Create new project
   - Required: `RAILWAY_TOKEN` (for CI/CD)

4. **Vercel**
   - Sign up at: https://vercel.com
   - Import GitHub repo
   - Required: `VERCEL_TOKEN` (for CI/CD)

### Environment Configuration

#### Frontend (.env.local)
```bash
# Public variables (exposed to browser)
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
NEXT_PUBLIC_API_URL=https://your-api.railway.app

# Server-only variables
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Backend (.env)
```bash
# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Database
DATABASE_URL=postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres

# Redis
REDIS_URL=redis://default:password@redis.railway.internal:6379

# AI/ML
TOGETHER_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  # Alternative

# Security
SECRET_KEY=your-secret-key-here-min-32-chars
JWT_SECRET=your-jwt-secret-here

# CORS
FRONTEND_URL=https://your-app.vercel.app

# Application
APP_ENV=production
LOG_LEVEL=INFO
```

## 🛠️ Local Development Setup

### Prerequisites
```bash
# Required software
- Node.js 18+
- Python 3.11+
- Docker & Docker Compose
- Git
```

### Setup Steps
```bash
# 1. Clone repository
git clone https://github.com/yourusername/rag_app.git
cd rag_app

# 2. Install dependencies
cd frontend && npm install
cd ../backend && pip install -r requirements.txt

# 3. Set up environment variables
cp frontend/.env.local.example frontend/.env.local
cp backend/.env.example backend/.env
# Edit both files with your credentials

# 4. Start local services
docker-compose up -d  # Starts Redis, ChromaDB

# 5. Run migrations
cd backend && alembic upgrade head

# 6. Start development servers
# Terminal 1: Frontend
cd frontend && npm run dev

# Terminal 2: Backend
cd backend && uvicorn main:app --reload
```

### Docker Compose for Local Development
```yaml
# docker-compose.yml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8000:8000"
    volumes:
      - chroma_data:/chroma/chroma
    environment:
      - IS_PERSISTENT=TRUE
      - PERSIST_DIRECTORY=/chroma/chroma

volumes:
  redis_data:
  chroma_data:
```

## 📊 Monitoring & Observability

### 1. **Application Monitoring**
- **Frontend**: Vercel Analytics & Web Vitals
- **Backend**: Railway Metrics & Custom Prometheus metrics
- **Database**: Supabase Dashboard

### 2. **Error Tracking**
- Implement Sentry for both frontend and backend
- Log aggregation with Railway logs

### 3. **Performance Monitoring**
- API response time tracking
- Database query performance
- LLM inference latency

## 🔄 CI/CD Pipeline

### Automated Testing
```yaml
# .github/workflows/tests.yml
name: Run Tests
on: [push, pull_request]

jobs:
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: cd frontend && npm ci
      - run: cd frontend && npm run test
      - run: cd frontend && npm run lint

  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: cd backend && pip install -r requirements.txt
      - run: cd backend && pytest
      - run: cd backend && ruff check .
```

### Deployment Checklist
- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Database migrations run
- [ ] SSL certificates active
- [ ] Monitoring configured
- [ ] Backup strategy in place

## 💰 Cost Estimates

### Monthly Costs (Estimated)
- **Vercel**: $0-20 (Free tier usually sufficient)
- **Railway**: $5-20 (Usage based)
- **Supabase**: $0-25 (Free tier for small projects)
- **Together AI**: $0.0008/1K tokens (~$10-50 based on usage)
- **Total**: ~$15-115/month

## 🚨 Disaster Recovery

### Backup Strategy
1. **Database**: Supabase automatic daily backups
2. **Code**: GitHub repository
3. **Environment**: Document all configs
4. **Vector DB**: Regular export to S3/storage

### Recovery Steps
1. Restore database from Supabase backup
2. Redeploy applications from GitHub
3. Restore vector database from backup
4. Update DNS if needed
