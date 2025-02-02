from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from api.db.models import ConversationMessage

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
