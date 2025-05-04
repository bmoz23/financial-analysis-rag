import asyncio
from datetime import datetime
import httpx
from tenacity import retry, wait_exponential, stop_after_attempt
from .config import settings
from shared.mq import send_price

BASE_URL = "https://api.twelvedata.com/time_series"

@retry(wait=wait_exponential(multiplier=1, min=2, max=30),
       stop=stop_after_attempt(5))
async def fetch_symbol(session: httpx.AsyncClient, symbol: str) -> dict:
    params = {
        "symbol": symbol,
        "interval": "1min",
        "apikey": settings.twelve_api_key,
        "outputsize": 1
    }
    r = await session.get(BASE_URL, params=params, timeout=20)
    r.raise_for_status()
    raw = r.json()
    latest = raw["values"][0]
    return {
        "symbol": symbol,
        "timestamp": datetime.strptime(latest["datetime"], "%Y-%m-%d %H:%M:%S"),
        "open": float(latest["open"]),
        "high": float(latest["high"]),
        "low": float(latest["low"]),
        "close": float(latest["close"]),
        "volume": int(float(latest["volume"]))
    }

async def producer_loop():
    async with httpx.AsyncClient() as session:
        while True:
            coros = [fetch_symbol(session, s) for s in settings.symbols]
            for c in asyncio.as_completed(coros):
                data = await c
                await send_price(data)
                print(f"✅ Inserted {data['symbol']} into DB")
            await asyncio.sleep(60)
