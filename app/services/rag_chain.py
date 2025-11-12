import os
import sys
from dotenv import load_dotenv
from langchain.schema import BaseRetriever

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_groq import ChatGroq
from langchain.chains import (
    create_history_aware_retriever,
    create_retrieval_chain
)
from langchain.chains.combine_documents import create_stuff_documents_chain

from app.core.logger import setup_logger
from app.core.exception import AppException
from app.utils.params import load_params
from app.utils.session_prompt import SessionPromptManager
from app.services.preprocess import DocumentPreprocessor

# Load environment variables
load_dotenv()

# Load parameters and logger
params = load_params("config/params.yaml")
rag_chain_params = params.get("rag_chain_params", {})
log_file_path = rag_chain_params.get("log_file_path", "rag_chain.log")
logger = setup_logger("ConversationalRAGChain", log_file_path)
logger.debug(f"RAG Chain module loaded. Logger configured for: {log_file_path}")

# Global shared dependencies
session_manager = SessionPromptManager()
preprocess_docs = DocumentPreprocessor()

class ConversationalChain:
    """
    Builds a history-aware conversational RAG (Retrieval-Augmented Generation) chain.
    
    This class orchestrates:
        - Document preprocessing (upload → embeddings → retriever)
        - Prompt loading for system and history contexts
        - LLM initialization and conversational retrieval chain creation
    
    Args:
        uploaded_files: Optional list of uploaded document-like objects (from Streamlit or FastAPI).
                       Not currently used, but kept for backward compatibility.
    
    Usage example:
        >>> rag_chain = ConversationalChain()
        >>> conversational_rag = rag_chain.create_conversational_rag_chain(retriever)
        >>> response = conversational_rag.invoke({"question": "What is this document about?", "chat_history": []})
    """

    def __init__(self, uploaded_files=None):
        try:
            # Environment and API validation
            self.groq_api_key = os.getenv("GROQ_API_KEY")
            if not self.groq_api_key:
                raise AppException("GROQ_API_KEY not found in environment variables.", sys)

            # Initialize LLM
            self.llm = ChatGroq(model="openai/gpt-oss-20b", api_key=self.groq_api_key)

            logger.info("ConversationalChain initialized successfully.")

        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            raise AppException(e, sys)

    def create_conversational_rag_chain(self, retriever: BaseRetriever):
        """
        Builds a LangChain-based history-aware RAG chain with:
            - Document retrieval using Pinecone
            - Session memory tracking
            - Prompt templates for contextual conversations

        Returns:
            RunnableWithMessageHistory: Executable conversational chain.
        """
        try:
            logger.info("Initializing conversational RAG chain with retriever...")

            # Step 1: Load prompts
            history_prompt_text = session_manager.load_prompt("app/prompts/history_prompt.txt")
            chain_prompt_text = session_manager.load_prompt("app/prompts/chain_prompt.txt")

            # Step 2: Build prompt templates
            # Note: create_history_aware_retriever expects 'input' variable in the prompt
            # while create_retrieval_chain uses 'question'. The retrieval chain handles the mapping.
            history_prompt = ChatPromptTemplate.from_messages([
                ("system", history_prompt_text),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}")
            ])

            chain_prompt = ChatPromptTemplate.from_messages([
                ("system", chain_prompt_text),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}")
            ])

            logger.info("Prompt templates successfully created.")

            # Step 3: Build history-aware retriever
            # This creates a retriever that takes 'input' and 'chat_history' and generates a search query
            history_aware_retriever = create_history_aware_retriever(
                self.llm, retriever, history_prompt
            )
            logger.info("History-aware retriever created successfully.")

            # Step 4: Build document combination chain
            document_chain = create_stuff_documents_chain(self.llm, chain_prompt)
            logger.info("Document combination chain initialized successfully.")

            # Step 5: Combine into retrieval chain
            retrieval_chain = create_retrieval_chain(history_aware_retriever, document_chain)
            logger.info("Retrieval chain successfully assembled.")

            # Step 6: Add session memory
            # Note: create_retrieval_chain expects inputs with 'question' and 'chat_history'
            # The retrieval chain automatically maps 'question' to 'input' for the history_aware_retriever
            conversational_rag_chain = RunnableWithMessageHistory(
                retrieval_chain,
                session_manager.get_session_history,
                input_messages_key="input",
                history_messages_key="chat_history",
                output_messages_key="answer"
            )
            logger.info("Conversational RAG chain finalized successfully.")

            return conversational_rag_chain

        except Exception as e:
            logger.error(f"Error creating conversational RAG chain: {e}")
            raise AppException(e, sys)
