
from sqlalchemy.orm import  declarative_base
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession, async_sessionmaker

Base = declarative_base()

database_url = "postgresql+asyncpg://boss:pussinboot123@localhost/chatdb"
engine: AsyncEngine = create_async_engine(database_url, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
