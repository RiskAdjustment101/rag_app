# RAG Application

A Claude-like Retrieval Augmented Generation (RAG) application with document intelligence capabilities.

## 🚀 Features

- **Document Intelligence**: Upload and query PDFs, Word docs, and text files
- **Natural Language Chat**: Claude-inspired conversational interface
- **Advanced RAG Engine**: Powered by ChromaDB and Together AI
- **Secure Authentication**: Supabase-based auth with social login support
- **Real-time Responses**: Streaming chat responses for better UX

## 🏗️ Architecture

- **Frontend**: Next.js + TypeScript + Tailwind CSS (Hosted on Vercel)
- **Backend**: FastAPI + Python (Hosted on Render)
- **Database**: PostgreSQL via Supabase
- **Vector Store**: ChromaDB
- **LLM**: Together AI (Llama 2 70B)
- **Caching**: Redis

## 📖 Documentation

- [Infrastructure Overview](./INFRASTRUCTURE.md) - Complete architecture and deployment guide
- [Implementation Plan](./IMPLEMENTATION_PLAN.md) - Step-by-step development roadmap
- [Claude Context](./CLAUDE.md) - AI assistant instructions and standards

## 🛠️ Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+
- Docker & Docker Compose
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/RiskAdjustment101/rag_app.git
   cd rag_app
   ```

2. **Set up environment variables**
   ```bash
   cp frontend/.env.local.example frontend/.env.local
   cp backend/.env.example backend/.env
   # Edit both files with your credentials
   ```

3. **Install dependencies**
   ```bash
   # Frontend
   cd frontend && npm install
   
   # Backend
   cd ../backend && pip install -r requirements.txt
   ```

4. **Start local services**
   ```bash
   docker-compose up -d
   ```

5. **Run the application**
   ```bash
   # Terminal 1: Frontend
   cd frontend && npm run dev
   
   # Terminal 2: Backend
   cd backend && uvicorn main:app --reload
   ```

## 🚀 Deployment

- **Frontend**: Automatically deployed to Vercel on push to main
- **Backend**: Deployed to Railway via GitHub Actions
- **Database**: Managed by Supabase

See [INFRASTRUCTURE.md](./INFRASTRUCTURE.md) for detailed deployment instructions.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Inspired by Claude's interface and capabilities
- Built with Meta's engineering best practices
- Powered by open-source technologies