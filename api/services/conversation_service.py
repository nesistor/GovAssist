from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.models import Conversation

async def get_conversation_history(session: AsyncSession, user_id: str, session_id: str):
    """Pobiera historię rozmów dla danego użytkownika i sesji."""
    result = await session.execute(
        select(Conversation).where(
            Conversation.user_id == user_id,
            Conversation.session_id == session_id
        ).order_by(Conversation.timestamp)
    )
    return [{"role": conv.role, "content": conv.content} for conv in result.scalars()]

async def add_message(session: AsyncSession, user_id: str, session_id: str, role: str, content: str):
    """Dodaje nową wiadomość do bazy danych."""
    message = Conversation(user_id=user_id, session_id=session_id, role=role, content=content)
    session.add(message)
    await session.commit()
