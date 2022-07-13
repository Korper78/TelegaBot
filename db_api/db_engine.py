from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

DATABASE_URI: str = 'postgres:pgsandy567737@localhost:5432/shop'

engine = create_async_engine(f'postgresql+asyncpg://{DATABASE_URI}')


def create_session(func):
    async def wrapper(**kwargs):
        async with AsyncSession(bind=engine) as session:
            return await func(**kwargs, session=session)
    return wrapper