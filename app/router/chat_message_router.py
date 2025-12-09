from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas import ChatMessage, ChatMessageCreate, ChatMessageUpdate
from app.services.chat_message_service import ChatMessageService
from app.repositories.chat_message_repository import ChatMessageRepository

router = APIRouter(prefix="/chat", tags=["chat"])

def get_chat_message_service(db: Session = Depends(get_db)) -> ChatMessageService:
    chat_message_repository = ChatMessageRepository(db)
    return ChatMessageService(chat_message_repository)

@router.get("/user/{user_id}", response_model=List[ChatMessage])
def get_user_messages(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    chat_message_service: ChatMessageService = Depends(get_chat_message_service)
):
    return chat_message_service.get_user_messages(user_id, skip, limit)

@router.get("/user/{user_id}/conversation", response_model=List[ChatMessage])
def get_conversation(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    chat_message_service: ChatMessageService = Depends(get_chat_message_service)
):
    return chat_message_service.get_conversation(user_id, skip, limit)

@router.get("/{message_id}", response_model=ChatMessage)
def get_message(
    message_id: int,
    chat_message_service: ChatMessageService = Depends(get_chat_message_service)
):
    message = chat_message_service.get(message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message

@router.post("/", response_model=ChatMessage)
def send_message(
    message_data: ChatMessageCreate,
    chat_message_service: ChatMessageService = Depends(get_chat_message_service)
):
    return chat_message_service.send_message(message_data.user_id, message_data.dict())

@router.put("/{message_id}", response_model=ChatMessage)
def update_message(
    message_id: int,
    message_data: ChatMessageUpdate,
    chat_message_service: ChatMessageService = Depends(get_chat_message_service)
):
    message = chat_message_service.get(message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    return chat_message_service.update(message_id, message_data.dict(exclude_unset=True))

@router.delete("/{message_id}")
def delete_message(
    message_id: int,
    chat_message_service: ChatMessageService = Depends(get_chat_message_service)
):
    success = chat_message_service.delete(message_id)
    if not success:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"message": "Message deleted successfully"}