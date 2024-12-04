import asyncio
import sys
import os
from loguru import logger

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.bot.core import TradingBot
from src.bot.config import Config

# Configure logging
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add("logs/trading_bot.log", rotation="10 MB")

async def main():
    try:
        # Initialize the trading bot
        config_path = 'config/config.yaml'
        bot = TradingBot(config_path)
        
        logger.info("Trading bot initialized successfully")
        
        # Run the bot's main trading loop
        await bot.run()
        
    except Exception as e:
        logger.error(f"Critical error in trading bot: {e}")
        
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Trading bot stopped by user")
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
