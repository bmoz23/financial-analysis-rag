# scripts/init_db.py
import asyncio, time, sys
from shared.db import engine, Base
from shared.models import Price

async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("YEESSS!!!! Tables created.")

if __name__=="__main__":
    for i in range(10):
        try:
            asyncio.run(init())
            sys.exit(0)
        except Exception as e:
            print("DB not ready, retrying...", e)
            time.sleep(2)
    print("Could not initialize DB after retries.")
    sys.exit(1)