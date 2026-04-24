import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL)
Session = async_sessionmaker(engine, class_=AsyncSession)


async def main():
    from app.models.exhibit import Exhibit
    from app.tasks.qr_tasks import generate_qr_png as generate_qr_code
    async with Session() as session:
        result = await session.execute(select(Exhibit))
        exhibits = result.scalars().all()
        for e in exhibits:
            generate_qr_code.delay(str(e.id))
            print("Queued:", e.slug)


asyncio.run(main())
