import sys
from typing import Optional
from langchain_core.runnables.history import RunnableWithMessageHistory

from app.core.logger import setup_logger
from app.core.exception import AppException
from app.utils.params import load_params
from app.utils.session_prompt import SessionPromptManager
from app.db.mango_database import AsyncMongoDatabase

# Load configuration
params = load_params("config/params.yaml")

rag_chatbot_params = params.get("rag_chatbot_params", {})
log_file_path = rag_chatbot_params.get("log_file_path", "rag_chatbot.log")
chat_history_limit = rag_chatbot_params.get("chat_history_limit", 5)

# Initialize logger
logger = setup_logger("RAGChatbot", log_file_path)
logger.debug(f"RAG Chatbot module loaded. Logger configured for: {log_file_path}")

# Shared dependencies (singletons)
session_manager = SessionPromptManager()
mongo_db = AsyncMongoDatabase()

class Chatbot:
    """
    Core orchestrator for the Conversational RAG Chatbot.

    Handles:
        - Loading the RAG chain
        - Retrieving conversation history
        - Invoking the LLM
        - Persisting results to MongoDB
        - Maintaining in-memory session context

    Args:
        question (str): User’s query input.
        session_id (str): Unique identifier for the session.
    """

    def __init__(self, question: str, session_id: str):
        self.question = question
        self.session_id = session_id

    async def chatbot(self, rag_chain: RunnableWithMessageHistory) -> Optional[str]:
        """
        Execute the RAG pipeline for a given session and question.

        Args:
            rag_chain (RunnableWithMessageHistory): Pre-built RAG chain instance.

        Returns:
            Optional[str]: The chatbot’s final response text.
        """
        try:
            logger.info(f"Chatbot session started for session_id={self.session_id}")

            # Step 2: Generate response via RAG chain
            logger.info("Invoking RAG chain for response generation...")
            response = await rag_chain.ainvoke(
                {"input": self.question},
                config={"configurable": {"session_id": self.session_id}}
            )

            bot_reply = response.get("answer", str(response)) if isinstance(response, dict) else str(response)
            logger.debug(f"Generated response (truncated): {bot_reply[:150]}...")

            # Step 3: Save to MongoDB
            await mongo_db.save_chat(self.session_id, self.question, bot_reply)
            logger.info("Chat message successfully saved to MongoDB.")

            logger.info(f"Chatbot session completed for session_id={self.session_id}")
            return bot_reply

        except AppException:
            logger.warning("AppException encountered during chatbot execution.", exc_info=True)
            raise

        except Exception as e:
            logger.error(f"Unexpected error during chatbot execution: {e}", exc_info=True)
            raise AppException("Error occurred during chatbot response generation.", sys)
