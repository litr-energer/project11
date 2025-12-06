# app/api/chat.py
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc, asc, func
from datetime import datetime, timedelta
import traceback

from app.database.database import get_async_session
from app.models.chat_massage import ChatMessageModel

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.get("/messages", response_model=List[dict])
async def get_chat_messages(
    user_id: Optional[int] = Query(None, description="Фильтр по пользователю"),
    message_type: Optional[str] = Query(None, description="Фильтр по типу сообщения"),
    is_from_user: Optional[bool] = Query(None, description="Фильтр по отправителю"),
    start_date: Optional[datetime] = Query(None, description="Начальная дата"),
    end_date: Optional[datetime] = Query(None, description="Конечная дата"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    order_by: str = Query("desc", description="Порядок сортировки: asc или desc"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить сообщения чата с фильтрацией и пагинацией
    """
    try:
        query = select(ChatMessageModel)
        
        # Применяем фильтры
        if user_id:
            query = query.where(ChatMessageModel.user_id == user_id)
        
        if message_type:
            query = query.where(ChatMessageModel.message_type == message_type)
        
        if is_from_user is not None:
            query = query.where(ChatMessageModel.is_from_user == is_from_user)
        
        if start_date:
            query = query.where(ChatMessageModel.sent_at >= start_date)
        
        if end_date:
            query = query.where(ChatMessageModel.sent_at <= end_date)
        
        # Сортировка
        if order_by.lower() == "asc":
            query = query.order_by(asc(ChatMessageModel.sent_at))
        else:
            query = query.order_by(desc(ChatMessageModel.sent_at))
        
        # Пагинация
        query = query.offset(skip).limit(limit)
        
        result = await session.execute(query)
        messages = result.scalars().all()
        
        return [msg.to_dict() for msg in messages]
        
    except Exception as e:
        print(f"Error in get_chat_messages: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/messages/{message_id}", response_model=dict)
async def get_chat_message(
    message_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить сообщение по ID
    """
    try:
        query = select(ChatMessageModel).where(ChatMessageModel.id == message_id)
        result = await session.execute(query)
        message = result.scalar_one_or_none()
        
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat message not found"
            )
        
        return message.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_chat_message: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/user/{user_id}/messages", response_model=List[dict])
async def get_user_chat_messages(
    user_id: int,
    limit: int = Query(50, ge=1, le=200, description="Количество сообщений"),
    days: int = Query(7, ge=1, le=365, description="За последние N дней"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить сообщения конкретного пользователя
    """
    try:
        # Рассчитываем дату начала периода
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = (
            select(ChatMessageModel)
            .where(ChatMessageModel.user_id == user_id)
            .where(ChatMessageModel.sent_at >= start_date)
            .order_by(desc(ChatMessageModel.sent_at))
            .limit(limit)
        )
        
        result = await session.execute(query)
        messages = result.scalars().all()
        
        return [msg.to_dict() for msg in messages]
        
    except Exception as e:
        print(f"Error in get_user_chat_messages: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/messages", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_chat_message(
    message_data: dict,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Создать новое сообщение в чате
    
    Пример тела запроса:
    {
        "user_id": 1,
        "message_text": "Привет! Как дела?",
        "message_type": "text",
        "is_from_user": true
    }
    """
    try:
        # Проверяем обязательные поля
        required_fields = ['user_id', 'message_text', 'message_type']
        for field in required_fields:
            if field not in message_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required field: {field}"
                )
        
        # Валидация данных
        user_id = message_data['user_id']
        message_text = message_data['message_text']
        message_type = message_data['message_type']
        is_from_user = message_data.get('is_from_user', True)
        
        if not message_text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message text cannot be empty"
            )
        
        if len(message_text) > 5000:  # Ограничение длины сообщения
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message text is too long (max 5000 characters)"
            )
        
        # Создаем новое сообщение
        db_message = ChatMessageModel(
            user_id=user_id,
            message_text=message_text.strip(),
            message_type=message_type,
            is_from_user=is_from_user,
            sent_at=datetime.utcnow()
        )
        
        session.add(db_message)
        await session.commit()
        await session.refresh(db_message)
        
        return {
            **db_message.to_dict(),
            "message": "Chat message created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in create_chat_message: {e}")
        print(traceback.format_exc())
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.put("/messages/{message_id}", response_model=dict)
async def update_chat_message(
    message_id: int,
    message_data: dict,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Обновить сообщение (например, исправить текст)
    """
    try:
        # Проверяем существование сообщения
        query = select(ChatMessageModel).where(ChatMessageModel.id == message_id)
        result = await session.execute(query)
        message = result.scalar_one_or_none()
        
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat message not found"
            )
        
        # Обновляем только разрешенные поля
        if 'message_text' in message_data:
            new_text = message_data['message_text'].strip()
            if not new_text:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Message text cannot be empty"
                )
            if len(new_text) > 5000:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Message text is too long (max 5000 characters)"
                )
            message.message_text = new_text
        
        if 'message_type' in message_data:
            message.message_type = message_data['message_type']
        
        if 'is_from_user' in message_data:
            message.is_from_user = message_data['is_from_user']
        
        message.sent_at = datetime.utcnow()  # Обновляем время
        
        await session.commit()
        await session.refresh(message)
        
        return {
            **message.to_dict(),
            "message": "Chat message updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in update_chat_message: {e}")
        print(traceback.format_exc())
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_message(
    message_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Удалить сообщение
    """
    try:
        query = select(ChatMessageModel).where(ChatMessageModel.id == message_id)
        result = await session.execute(query)
        message = result.scalar_one_or_none()
        
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat message not found"
            )
        
        await session.delete(message)
        await session.commit()
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in delete_chat_message: {e}")
        print(traceback.format_exc())
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/conversation/{user_id}", response_model=List[dict])
async def get_conversation(
    user_id: int,
    partner_id: Optional[int] = Query(None, description="ID собеседника (системы)"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить диалог пользователя (сообщения от пользователя и к пользователю)
    """
    try:
        query = select(ChatMessageModel).where(
            (ChatMessageModel.user_id == user_id) |
            (ChatMessageModel.is_from_user == False)
        )
        
        if partner_id:
            # Если указан партнер (например, система/бот)
            query = query.where(
                (ChatMessageModel.user_id == user_id) |
                (ChatMessageModel.user_id == partner_id)
            )
        
        query = query.order_by(asc(ChatMessageModel.sent_at))
        
        result = await session.execute(query)
        messages = result.scalars().all()
        
        return [msg.to_dict() for msg in messages]
        
    except Exception as e:
        print(f"Error in get_conversation: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/messages/batch", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_batch_messages(
    messages_data: List[dict],
    session: AsyncSession = Depends(get_async_session)
):
    """
    Создать несколько сообщений за раз
    """
    try:
        created_messages = []
        
        for message_data in messages_data:
            # Проверяем обязательные поля для каждого сообщения
            required_fields = ['user_id', 'message_text', 'message_type']
            for field in required_fields:
                if field not in message_data:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Missing required field '{field}' in one of the messages"
                    )
            
            # Создаем сообщение
            db_message = ChatMessageModel(
                user_id=message_data['user_id'],
                message_text=message_data['message_text'].strip(),
                message_type=message_data['message_type'],
                is_from_user=message_data.get('is_from_user', True),
                sent_at=datetime.utcnow()
            )
            
            session.add(db_message)
            created_messages.append(db_message)
        
        await session.commit()
        
        # Обновляем объекты, чтобы получить ID
        for msg in created_messages:
            await session.refresh(msg)
        
        return {
            "message": f"Successfully created {len(created_messages)} messages",
            "created_count": len(created_messages),
            "messages": [msg.to_dict() for msg in created_messages]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in create_batch_messages: {e}")
        print(traceback.format_exc())
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/statistics", response_model=dict)
async def get_chat_statistics(
    user_id: Optional[int] = Query(None, description="Статистика для конкретного пользователя"),
    days: int = Query(30, ge=1, le=365, description="За последние N дней"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получить статистику по чатам
    """
    try:
        from sqlalchemy import func
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Базовый запрос
        query = select(ChatMessageModel).where(ChatMessageModel.sent_at >= start_date)
        
        if user_id:
            query = query.where(ChatMessageModel.user_id == user_id)
        
        # Получаем все сообщения для анализа
        result = await session.execute(query)
        messages = result.scalars().all()
        
        # Статистика
        total_messages = len(messages)
        user_messages = sum(1 for m in messages if m.is_from_user)
        system_messages = total_messages - user_messages
        
        # Группировка по типам сообщений
        message_types = {}
        for msg in messages:
            msg_type = msg.message_type
            message_types[msg_type] = message_types.get(msg_type, 0) + 1
        
        # Группировка по дням
        messages_by_day = {}
        for msg in messages:
            day = msg.sent_at.date().isoformat() if msg.sent_at else "unknown"
            messages_by_day[day] = messages_by_day.get(day, 0) + 1
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": datetime.utcnow().isoformat(),
                "days": days
            },
            "user_id": user_id,
            "statistics": {
                "total_messages": total_messages,
                "user_messages": user_messages,
                "system_messages": system_messages,
                "messages_by_type": message_types,
                "messages_by_day": messages_by_day
            }
        }
        
    except Exception as e:
        print(f"Error in get_chat_statistics: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/health")
async def chat_health_check(session: AsyncSession = Depends(get_async_session)):
    """
    Проверка работоспособности чат-сервиса
    """
    try:
        # Проверяем подключение к БД
        result = await session.execute(select(func.count(ChatMessageModel.id)))
        count = result.scalar()
        
        return {
            "status": "healthy",
            "service": "chat-api",
            "database": "connected",
            "total_messages": count or 0,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "chat-api",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }