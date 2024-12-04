from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
import os
from datetime import datetime
from ..bot.config import Config
from ..bot.core import TradingBot

app = FastAPI(title="Trading Bot API")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class BinanceConfig(BaseModel):
    api_key: str
    api_secret: str
    testnet: bool = False

class TradingPair(BaseModel):
    symbol: str
    enabled: bool

class TradeStatus(BaseModel):
    symbol: str
    entry_price: float
    current_price: float
    pnl_percentage: float
    position_size: float

# Initialize bot
bot = None

@app.get("/config/binance")
async def get_binance_config():
    try:
        config = Config()
        return {
            "status": "success",
            "data": {
                "config": {
                    "api_key": config.binance_api_key,
                    "api_secret": config.binance_api_secret,
                    "testnet": config.use_testnet
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/config/binance")
async def update_binance_config(config: BinanceConfig):
    try:
        Config().update_exchange_credentials(
            api_key=config.api_key,
            api_secret=config.api_secret,
            use_testnet=config.testnet
        )
        return {
            "status": "success",
            "data": {
                "config": {
                    "api_key": config.api_key,
                    "api_secret": config.api_secret,
                    "testnet": config.testnet
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/trading-pairs")
async def get_trading_pairs():
    try:
        config = Config()
        pairs = config.get_trading_pairs()
        return {"status": "success", "data": {"pairs": pairs}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trading-pairs")
async def update_trading_pairs(pairs: List[TradingPair]):
    try:
        config = Config()
        enabled_pairs = [pair.symbol for pair in pairs if pair.enabled]
        config.update_trading_pairs(enabled_pairs)
        return {"status": "success", "data": {"pairs": enabled_pairs}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/trades/active")
async def get_active_trades():
    if not bot:
        return {"status": "success", "data": {"trades": {}}}
    return {"status": "success", "data": {"trades": bot.active_trades}}

@app.get("/trades/history")
async def get_trade_history():
    try:
        with open("trade_history.json", "r") as f:
            history = json.load(f)
        return {"status": "success", "data": {"history": history}}
    except FileNotFoundError:
        return {"status": "success", "data": {"history": []}}

@app.get("/balance")
async def get_balance():
    if not bot:
        return {"status": "success", "data": {"balance": 0.0}}
    balance = bot.get_balance()
    return {"status": "success", "data": {"balance": balance}}

@app.post("/bot/start")
async def start_bot():
    try:
        global bot
        if not bot:
            config = Config()
            bot = TradingBot(config)
        bot.start()
        return {"status": "success", "data": {"message": "Bot started successfully"}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/bot/stop")
async def stop_bot():
    try:
        global bot
        if bot:
            bot.stop()
        return {"status": "success", "data": {"message": "Bot stopped successfully"}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
