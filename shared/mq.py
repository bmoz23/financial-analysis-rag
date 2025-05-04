# shared/mq.py

from shared.db import AsyncSession
from shared.models import Price

async def send_price(data: dict) -> None:
    async with AsyncSession() as session:
        session.add(Price(**data))
        await session.commit()