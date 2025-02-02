import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager

# Use the DATABASE_URL environment variable or fallback to the default URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost/conversations")

# Pass the DATABASE_URL variable, not the string 'DATABASE_URL'
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    from api.db.models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Function to get async session
@asynccontextmanager
async def get_async_session():
    async with SessionLocal() as session:
        yield session