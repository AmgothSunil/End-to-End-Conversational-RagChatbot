# End-to-End Conversational RAG Chatbot

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red)](https://streamlit.io/)

An **enterprise-grade Retrieval-Augmented Generation (RAG) system** that enables conversational interactions with uploaded documents and urls. Built with FastAPI backend, Streamlit frontend, Pinecone vector store, MongoDB memory, Groq LLM, and automated AWS ECS deployment via GitHub Actions CI/CD.

## 🎯 Key Features

- **📄 Document Processing**: Upload and ingest PDF/TXT documents with automatic chunking and embedding
- **🔍 Semantic Search**: Retrieve relevant document chunks using HuggingFace MiniLM-L6-v2 embeddings + Pinecone
- **💬 Conversational RAG**: History-aware queries with context rewriting to prevent hallucinations
- **📚 Session Isolation**: Each conversation stored in separate Pinecone namespace for data integrity
- **🗄️ Persistent Memory**: MongoDB stores all chat history for session restoration
- **🎨 User-Friendly UI**: Streamlit interface for non-technical users
- **🚀 Production-Ready Deployment**: Automated CI/CD pipeline to AWS ECS Fargate via GitHub Actions
- **🔒 Enterprise Security**: Environment-based configuration, error handling, centralized logging

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Streamlit Frontend                          │
│              (Document Upload + Chat Interface)                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                            │
│                    (REST API Routes)                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐    │
│  │ Preprocessor │  │  RAG Chain   │  │  Groq LLM API    │    │
│  │  (Chunking)  │  │ (Retrieval)  │  │ (Answer Gen)     │    │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘    │
│         │                 │                    │               │
│         ▼                 ▼                    ▼               │
│  ┌──────────────────────────────────────────────────┐          │
│  │          Pinecone Vector Database                │          │
│  │      (Session-scoped Namespaces)                │          │
│  └──────────────────────────────────────────────────┘          │
│                                                                 │
│  ┌──────────────────────────────────────────────────┐          │
│  │      MongoDB (Motor Async Client)                │          │
│  │       (Chat History Storage)                     │          │
│  └──────────────────────────────────────────────────┘          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                           ▲
                           │
        ┌──────────────────┴──────────────────┐
        │                                     │
        ▼                                     ▼
┌──────────────────┐            ┌──────────────────┐
│   AWS ECR Repo   │            │  GitHub Actions  │
│  (Docker Image)  │            │   (CI/CD Pipel.) │
└──────────────────┘            └──────────────────┘
        ▲
        │ (Auto-Deploy)
        ▼
┌──────────────────────────────────────┐
│    AWS ECS Fargate Cluster           │
│  (Production Container Hosting)      │
└──────────────────────────────────────┘
```

## 📁 Project Structure

```
END-TO-END-CONVERSATIONAL-RAGCHATBOT/
│
├── .github/
│   └── workflows/
│       └── deploy.yaml                      # GitHub Actions CI/CD pipeline
│
├── app/                                     # FastAPI Backend
│   ├── api/
│   │   ├── __init__.py
│   │   └── fastapi_app.py                   # All API endpoints
│   │
│   ├── core/
│   │   ├── exception.py                     # Custom exception handlers
│   │   ├── logger.py                        # Centralized logging configuration
│   │   └── __init__.py
│   │
│   ├── db/
│   │   ├── mongo_database.py                # Async MongoDB client & session manager
│   │   └── __init__.py
│   │
│   ├── prompts/
│   │   ├── chain_prompt.txt                 # retrival chain prompt text
│   │   ├── history_prompt.txt               # history aware retriever prompt text
│   │   └── __init__.py
│   │
│   ├── services/
│   │   ├── preprocess.py                    # Document upload, splitting, embedding
│   │   ├── rag_chain.py                     # LangChain RAG pipeline builder
│   │   └── rag_chatbot.py                   # Chat orchestration & response generation
│   │
│   ├── utils/
│   │   ├── params.py                        # YAML config loader
│   │   ├── session_prompt.py                # Session manager & prompt loader
│   │   └── __init__.py
│   │
│   ├── config/
│   │   └── params.yaml                      # Configuration (chunk size, log file paths, etc.)
│   │
│   └── __init__.py
│
├── frontend/                                # Streamlit Frontend
│   ├── streamlit_app.py
│   ├── requirements.txt
│   └── __init__.py
│
├── .dockerignore
├── .gitignore
├── .env.example                             # Environment variables template
├── .python-version                          # Python version specification
├── Dockerfile                               # Docker image definition
├── ecs-task-def.json                        # ECS Task Definition template
├── LICENSE                                  # MIT License
├── pyproject.toml                           # Project metadata & uv config
└── README.md                                # This file
├── requirements.txt                         # Backend Python dependencies
├── uv.lock                                  # Locked dependency versions
```

## ⚙️ Tech Stack

### Backend
- **FastAPI** – High-performance async API framework
- **LangChain** – RAG orchestration and chain management
- **Pinecone** – Vector database for semantic search
- **HuggingFace MiniLM-L6-v2** – Fast, efficient embedding model
- **Groq API** – LLM inference (LLaMA3, Mixtral, GPT-OSS)
- **MongoDB + Motor** – Async document database for chat history
- **Pydantic** – Data validation and settings management

### Frontend
- **Streamlit** – Interactive web UI framework
- **Requests** – HTTP client for backend communication

### Infrastructure & DevOps
- **Docker** – Containerization
- **AWS ECR** – Elastic Container Registry
- **AWS ECS Fargate** – Serverless container orchestration
- **GitHub Actions** – CI/CD automation

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Docker & Docker Desktop
- AWS Account (for deployment)
- GitHub Account (for CI/CD)
- API Keys: Langchain, Huggingface, Groq, Pinecone, Mangodb

### Local Development Setup

**1. Clone the repository**
```bash
git clone https://github.com/AmgothSunil/End-to-End-Conversational-RagChatbot.git
cd End-to-End-Conversational-RagChatbot
```

**2. Create and activate virtual environment**
```bash
python -m venv .venv

# On Windows
.venv\Scripts\activate

# On macOS/Linux
source .venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys and settings
```

**5. Start FastAPI server**
```bash
uvicorn app.api.fastapi_app:app --host 0.0.0.0 --port 8000 --reload
or with uv --> uv run -m app.api.fastapi_app
```

**6. In a new terminal, start Streamlit UI**
```bash
streamlit run frontend/streamlit_app.py
```

**7. Access the application**
- Streamlit UI: [http://localhost:8501](http://localhost:8501)
- API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## 🔧 Environment Configuration

Create a `.env` file in the root directory:

```bash
# Groq LLM Configuration
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-20b 

# Pinecone Vector Database
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=rag-chatbot
PINECONE_ENVIRONMENT=us-east-1-aws  # Your region

# MongoDB Configuration
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGO_DB_NAME=chatbot_db
MONGO_COLLECTION=chat_history

# HuggingFace Embeddings
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
HF_TOKEN=your_huggingface_token  # Optional, for private models

# Application Settings
DEBUG=False
LOG_LEVEL=INFO
MAX_CHUNK_SIZE=1000
CHUNK_OVERLAP=150
TOP_K_RETRIEVAL=5

# Frontend Configuration
BACKEND_URL=http://localhost:8000

# AWS Configuration (for deployment)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

## 🐳 Docker Build & Deployment

### Build Docker Image Locally
```bash
docker build -t rag-chatbot-backend:latest .
```

### Run Container Locally
```bash
docker run -p 8000:8000 \
  --env-file .env \
  --name rag-chatbot-backend \
  rag-chatbot-backend:latest
```

### Push to AWS ECR
```bash
# Authenticate Docker with ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  your_account_id.dkr.ecr.us-east-1.amazonaws.com

# Tag image
docker tag rag-chatbot-backend:latest \
  your_account_id.dkr.ecr.us-east-1.amazonaws.com/rag-chatbot:latest

# Push to ECR
docker push your_account_id.dkr.ecr.us-east-1.amazonaws.com/rag-chatbot:latest
```

## ☁️ AWS ECS Deployment (Automated CI/CD)

### Prerequisites
1. Create ECR repository: `conversational-rag-chatbot`
2. Create ECS cluster and service
3. Create IAM role for ECS task execution

### GitHub Secrets Setup
Add these secrets to your GitHub repository (Settings → Secrets and variables):

```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_REGION                    # e.g., us-east-1
ECR_REPOSITORY           # e.g., rag-chatbot
ECS_CLUSTER              # e.g., production-cluster
ECS_SERVICE              # e.g., rag-chatbot-service
CONTAINER_NAME                # e.g., rag-chatbot-backend
```

### Automated Deployment
The `.github/workflows/deploy.yaml` pipeline automatically:
1. Triggers on push to `main` branch
2. Builds Docker image
3. Authenticates with AWS ECR
4. Pushes image to registry
5. Updates ECS task definition
6. Deploys to ECS Fargate cluster
7. Performs rolling update (zero-downtime deployment)

Simply push your code:
```bash
git add .
git commit -m "Feature: Add RAG enhancement"
git push origin main
```

The pipeline handles the rest! 🚀

## 📡 API Endpoints

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

### Upload Documents
```http
POST /upload-docs
Content-Type: multipart/form-data

session_id: <string>
files: <list of PDF/TXT files>
```

**Response:**
```json
{
  "session_id": "user-123-session",
  "documents_uploaded": 3,
  "total_chunks": 156,
  "embedding_status": "success"
}
```

### Chat
```http
POST /chat
Content-Type: application/json

{
  "session_id": "user-123-session",
  "question": "What is the main topic of the document?"
}
```

**Response:**
```json
{
  "session_id": "user-123-session",
  "question": "What is the main topic of the document?",
  "answer": "Based on the uploaded documents...",
  "sources": [
    {
      "chunk_id": "doc-1-chunk-5",
      "score": 0.89
    }
  ],
  "timestamp": "2025-11-13T15:30:45Z"
}
```

## 🛠️ Development & Troubleshooting

### Common Issues

**MongoDB Connection Error**
```
Error: Could not connect to MongoDB at mongodb+srv://...
```
- Verify connection string format
- Check IP whitelist in MongoDB Atlas
- Ensure network connectivity to MongoDB server

**Pinecone API Key Invalid**
```
Error: Unauthorized - Invalid API key
```
- Verify `PINECONE_API_KEY` in `.env`
- Ensure index exists in Pinecone console
- Check API key permissions

**Groq API Rate Limit**
```
Error: Rate limit exceeded
```
- Implement exponential backoff retry logic
- Check Groq plan limits
- Reduce query frequency or batch requests

### Debugging

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

View application logs:
```bash
tail -f logs/server.log
```

## 📊 Performance Metrics

- **Document Upload**: ~2-5 seconds per 10MB
- **Precessing Document**: ~10-15 seconds
- **Embedding Generation**: ~100ms per document chunk
- **Vector Retrieval**: ~50-100ms for top-K search
- **LLM Response**: ~2-5 seconds (Groq API)
- **End-to-End Latency**: ~5-10 seconds per chat message

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

**Guidelines:**
- Follow PEP 8 style guide
- Write descriptive commit messages
- Include tests for new features
- Update README for significant changes
- Link related issues in PR description

## 📝 License

This project is licensed under the **MIT License** – see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Groq** for fast LLM inference API
- **Pinecone** for vector database infrastructure
- **LangChain** for RAG framework
- **HuggingFace** for transformer models
- **AWS** for cloud infrastructure
- **Streamlit** for rapid UI development

## 📞 Support & Contact

- **Issues**: GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions
- **Email**: sunilpowar523@gmail.com

---

**Made with ❤️ for building production-grade AI applications**

