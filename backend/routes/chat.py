from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlmodel import Session
from models.chat_models import Conversation, Message
from db import get_session
from auth import get_current_user_id
from services.chat_service import ChatService
from pydantic import BaseModel
from uuid import UUID
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None  # Optional conversation ID to continue existing conversation

class ChatResponse(BaseModel):
    response: str
    conversation_id: str

class ConversationResponse(BaseModel):
    id: str
    user_id: str
    title: str | None = None
    created_at: str
    updated_at: str

class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    timestamp: str
    metadata: dict | None = None

class ConversationWithMessagesResponse(BaseModel):
    conversation: ConversationResponse
    messages: List[MessageResponse]


@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat_endpoint(
    chat_request: ChatRequest,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> ChatResponse:
    """
    Endpoint to send a message to the AI chatbot and get a response.
    """
    try:
        chat_service = ChatService()

        # Convert conversation_id to UUID if provided
        conversation_id = None
        if chat_request.conversation_id:
            try:
                conversation_id = UUID(chat_request.conversation_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid conversation ID format"
                )

        result = await chat_service.process_chat_request(
            user_message=chat_request.message,
            user_id=user_id,
            conversation_id=conversation_id
        )

        logger.info(f"Chat request processed successfully for user: {user_id}")

        return ChatResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat request for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat request"
        )


@router.get("/conversations", response_model=List[ConversationResponse])
def get_conversations(
    user_id: str = Depends(get_current_user_id)
) -> List[ConversationResponse]:
    """
    Retrieve all conversations for the authenticated user.
    """
    try:
        chat_service = ChatService()
        conversations = chat_service.get_conversations(user_id)

        logger.info(f"Retrieved {len(conversations)} conversations for user: {user_id}")

        return [ConversationResponse(**conv) for conv in conversations]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving conversations for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversations"
        )


@router.get("/conversations/{conversation_id}", response_model=ConversationWithMessagesResponse)
def get_conversation_with_messages(
    conversation_id: str,
    user_id: str = Depends(get_current_user_id)
) -> ConversationWithMessagesResponse:
    """
    Retrieve a specific conversation with its messages.
    """
    try:
        # Convert conversation_id to UUID
        try:
            uuid_id = UUID(conversation_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid conversation ID format"
            )

        chat_service = ChatService()
        result = chat_service.get_conversation_with_messages(user_id, uuid_id)

        logger.info(f"Retrieved conversation {conversation_id} with {len(result['messages'])} messages for user: {user_id}")

        return ConversationWithMessagesResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving conversation {conversation_id} for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation"
        )


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conversation_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Delete a conversation.
    """
    try:
        # Convert conversation_id to UUID
        try:
            uuid_id = UUID(conversation_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid conversation ID format"
            )

        chat_service = ChatService()
        success = chat_service.delete_conversation(user_id, uuid_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or does not belong to the authenticated user"
            )

        logger.info(f"Deleted conversation {conversation_id} for user: {user_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation {conversation_id} for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete conversation"
        )