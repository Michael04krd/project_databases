from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy import String
from typing import Annotated, AsyncGenerator
from backend.app.config import settings

async_engine = create_async_engine(
    url=settings.DATABASE_URL_asyncpg,
    echo=False,
)
AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)

intpk=Annotated[int,mapped_column(primary_key=True)]
str_200=Annotated[str,255]
class Base(DeclarativeBase):
    type_annotation_map={
        str_200:String(255)
    }
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()
