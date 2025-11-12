import os
import uvicorn
import tempfile
from typing import List, Optional
from contextlib import asynccontextmanager


from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from dotenv import load_dotenv

from app.core.logger import setup_logger
from app.core.exception import AppException
from app.utils.params import load_params
from app.services.preprocess import DocumentPreprocessor
from app.services.rag_chain import ConversationalChain
from app.services.rag_chatbot import Chatbot
from app.db.mango_database import AsyncMongoDatabase

# Load environment and configuration
load_dotenv()

# LangSmith tracing
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")
os.environ["LANGCHAIN_TRACING_V2"] = "true"


params = load_params("config/params.yaml")
server_params = params.get("server_params", {})

log_file_path = server_params.get("log_file_path", "server.log")

# Initialize logger
logger = setup_logger("ConversationalRAGServer", log_file_path)
logger.debug(f"FastAPI Server module loaded. Logger configured for: {log_file_path}")

# Global Shared Components
mongo_db = AsyncMongoDatabase()
document_preprocessor = DocumentPreprocessor()

# Cache retriever in memory
retriever_cache = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    # Startup
    logger.info("FastAPI Conversational RAG Server starting up...")
    try:
        # Ensure MongoDB index exists
        await mongo_db.collection.create_index("session_id")
        logger.info("MongoDB index ensured successfully.")
    except Exception as e:
        logger.error(f"MongoDB initialization failed: {e}", exc_info=True)
    
    yield  # App runs here
    
    # Shutdown
    logger.info("FastAPI RAG Server shutting down...")
    try:
        await mongo_db.close_connection()
        logger.info("MongoDB connection closed successfully.")
    except Exception as e:
        logger.error(f"Error closing MongoDB connection: {e}", exc_info=True)


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="End-to-End Conversational RAG Chatbot",
    description="An enterprise-grade RAG chatbot with document upload, chat history, and Pinecone retrieval.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Configuration (for Streamlit frontend or other clients)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this in production  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Welcome message
@app.get("/")
async def welcome():
    return {"message": "Welcome to Conversational RAG Chatbot API"}


# Health Check Endpoint
@app.get("/health", status_code=HTTP_200_OK)
async def health_check():
    """Simple health check for ECS load balancers."""
    logger.debug("Health check endpoint called")
    return {"status": "healthy", "service": "ConversationalRAGServer"}


# Document Upload Endpoint
@app.post("/upload-docs", status_code=HTTP_200_OK)
async def upload_documents(
    session_id: str = Form(...), 
    files: List[UploadFile] = File(None),
    urls: Optional[List[str]] = Form(None)
    ):

    """
    Upload one or more documents or urls to create embeddings and store them in Pinecone.
    """
    global retriever_cache
    try:
        if not files and not urls:
            logger.warning("No files or URLs were provided.")
            return JSONResponse(
                {"message": "No files or URLs provided."}, status_code=HTTP_400_BAD_REQUEST
            )

        logger.info("Received document(s) for preprocessing.")

        all_sources = []
        temp_file_paths = []
        
        # Handle uploaded files
        if files:
            logger.info(f"Received {len(files)} document(s).")
            for file in files:
                # ... (temp file creation logic remains the same)
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp:
                    content = await file.read()
                    temp.write(content)
                    temp.flush()
                    temp_file_paths.append(temp.name)
            all_sources.extend(temp_file_paths)

        # Handle URLs
        if urls:
            logger.info(f"Received {len(urls)} URL(s).")
            all_sources.extend(urls)

        # Preprocess and build retriever
        loaded_docs = document_preprocessor.load_documents(all_sources)
        session_retriever = document_preprocessor.build_retriever(loaded_docs, session_id=session_id)

        retriever_cache[session_id] = session_retriever

        logger.info("Documents successfully embedded into Pinecone.")
        return JSONResponse(
            {"message": "Documents uploaded and processed successfully."},
            status_code=HTTP_200_OK,
        )

    except AppException as e:
        logger.error(f"AppException during upload: {e}")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    except Exception as e:
        logger.error(f"Unexpected error during document upload: {e}", exc_info=True)
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Error processing uploaded documents.")


# Chat Endpoint
@app.post("/chat", status_code=HTTP_200_OK)
async def chat_with_bot(
    question: str = Form(...),
    session_id: str = Form(...),
):
    """
    Main conversational endpoint — processes user question and returns AI response.
    Requires document upload first.
    """
    try:
        global retriever_cache
        session_retriever = retriever_cache.get(session_id)

        if retriever_cache is None:
            logger.warning(f"Chat attempted for session {session_id} without document upload.")
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Please upload documents first.")

        # Step 1: Build conversational chain with cached retriever
        chain_builder = ConversationalChain()
        rag_chain = chain_builder.create_conversational_rag_chain(session_retriever)

        # Step 2: Initialize chatbot and get response
        chatbot = Chatbot(question=question, session_id=session_id)
        response = await chatbot.chatbot(rag_chain)

        logger.info(f"Chatbot successfully processed question for session {session_id}.")
        return JSONResponse(
            {"session_id": session_id, "question": question, "response": response},
            status_code=HTTP_200_OK,
        )

    except HTTPException as e:
        raise e  # Already logged

    except AppException as e:
        logger.error(f"AppException during chat: {e}")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    except Exception as e:
        logger.error(f"Unexpected chatbot error: {e}", exc_info=True)
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Error generating chatbot response.")


if __name__ == "__main__":
    uvicorn.run("app.api.fastapi_app:app", host="0.0.0.0", port=8000, reload=True)