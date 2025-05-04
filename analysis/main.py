# analysis/main.py

from fastapi import FastAPI, Query
from shared.db import AsyncSession
from sqlalchemy import select
from shared.models import Price
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

app = FastAPI(title="Analysis Service")

@app.get("/predict")
async def predict_price(symbol: str = Query(..., description="Stock symbol like AAPL or MSFT")):
    async with AsyncSession() as session:
        result = await session.execute(
            select(Price)
            .where(Price.symbol == symbol)
            .order_by(Price.timestamp)
        )
        rows = result.scalars().all()

    if len(rows) < 2:
        return {"error": "Not enough data for prediction"}

    df = pd.DataFrame([{"ts": r.timestamp.value//10**9, "close": r.close} for r in rows])
    X = df[["ts"]].values
    y = df["close"].values

    model = LinearRegression().fit(X, y)
    next_ts = df["ts"].max() + 3600
    pred = model.predict([[next_ts]])[0]

    return {
        "symbol": symbol,
        "predicted_price_next_hour": float(pred),
        "latest_known_price": float(y[-1])
    }
