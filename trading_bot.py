#!/usr/bin/env python3
import json
import logging
from pathlib import Path
from src.bot.core import TradingBot

def setup_logging():
    log_dir = Path("data/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "trading_bot.log"),
            logging.StreamHandler()
        ]
    )

def load_config():
    with open("config/config.json") as f:
        return json.load(f)

def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        config = load_config()
        bot = TradingBot(config)
        bot.run()
    except Exception as e:
        logger.error(f"Error running trading bot: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()
