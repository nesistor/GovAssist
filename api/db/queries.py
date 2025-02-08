from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from api.db.models import ConversationMessage, DocumentAnalysis

async def get_conversation_history(session: AsyncSession, user_id: str, session_id: str):
    """
    Pobiera historię konwersacji użytkownika dla danej sesji.

    :param session: Obiekt sesji bazy danych.
    :param user_id: ID użytkownika.
    :param session_id: ID sesji rozmowy.
    :return: Lista wiadomości w formacie [{"role": "user/assistant", "content": "tekst"}].
    """
    result = await session.execute(
        select(ConversationMessage)
        .where(
            ConversationMessage.user_id == user_id,
            ConversationMessage.session_id == session_id
        )
        .order_by(ConversationMessage.timestamp)
    )
    messages = result.scalars().all()

    return [{"role": msg.role, "content": msg.content} for msg in messages]

async def add_message(session: AsyncSession, user_id: str, session_id: str, role: str, content: str):
    """
    Dodaje wiadomość do historii konwersacji w bazie danych.

    :param session: Obiekt sesji bazy danych.
    :param user_id: ID użytkownika.
    :param session_id: ID sesji rozmowy.
    :param role: Rola nadawcy wiadomości ("user" lub "assistant").
    :param content: Treść wiadomości.
    """
    message = ConversationMessage(
        user_id=user_id,
        session_id=session_id,
        role=role,
        content=content,
        timestamp=datetime.utcnow()
    )
    session.add(message)
    await session.commit()


# Function to get conversations with pagination asynchronously
async def get_conversations_with_pagination(
    session: AsyncSession, user_id: str, time_range: str, skip: int, limit: int
):
    """
    Pobiera konwersacje użytkownika z paginacją.
    
    :param session: Obiekt sesji bazy danych.
    :param user_id: ID użytkownika.
    :param time_range: Okres czasu ("today", "7days", "30days").
    :param skip: Liczba pominiętych wyników.
    :param limit: Maksymalna liczba wyników.
    :return: Lista konwersacji.
    """
    now = datetime.utcnow()

    if time_range == "today":
        start_date = now - timedelta(days=1)
    elif time_range == "7days":
        start_date = now - timedelta(days=7)
    elif time_range == "30days":
        start_date = now - timedelta(days=30)
    else:
        start_date = now - timedelta(days=1)  # Default: 1 day

    result = await session.execute(
        select(ConversationMessage)
        .where(
            ConversationMessage.user_id == user_id,
            ConversationMessage.timestamp >= start_date
        )
        .order_by(ConversationMessage.timestamp.desc())
        .offset(skip)
        .limit(limit)
    )

    conversations = result.scalars().all()
    
    return [{"role": msg.role, "content": msg.content, "timestamp": msg.timestamp} for msg in conversations]

async def get_document_analysis(session, session_id: str):
    result = await session.execute(
        select(DocumentAnalysis)
        .where(DocumentAnalysis.session_id == session_id)
    )
    return result.scalars().first()

async def save_document_analysis(session, session_id: str, document_path: str, fields: str):
    analysis = DocumentAnalysis(
        session_id=session_id,
        document_path=document_path,
        fields=fields
    )
    session.add(analysis)
    await session.commit()