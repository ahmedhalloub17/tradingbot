#!/usr/bin/env python3
import json
import logging
from pathlib import Path
from src.bot.core import TradingBot
import os
from dotenv import load_dotenv
import yaml

# Load environment variables
load_dotenv(dotenv_path='/app/config/.env')

def load_config(config_path='config/config.yaml'):
    logger = logging.getLogger(__name__)
    try:
        # Load YAML config
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Override config with environment variables
        config['binance']['api_key'] = os.getenv('BINANCE_API_KEY', config['binance']['api_key'])
        config['binance']['secret_key'] = os.getenv('BINANCE_SECRET_KEY', config['binance']['secret_key'])
        config['telegram']['bot_token'] = os.getenv('TELEGRAM_BOT_TOKEN', config['telegram']['bot_token'])
        
        # Optional: Override other config parameters from .env
        if os.getenv('TRADING_SYMBOL'):
            config['trading']['symbol'] = os.getenv('TRADING_SYMBOL')
        if os.getenv('LEVERAGE'):
            config['trading']['leverage'] = int(os.getenv('LEVERAGE'))
        
        logger.info("Configuration loaded successfully")
        return config
    
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        raise



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
