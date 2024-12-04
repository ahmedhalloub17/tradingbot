import os
import yaml
import json
from typing import Dict, Any, List

class Config:
    def __init__(self, config_path: str = None, config_file: str = "config.json"):
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'config',
                'config.yaml'
            )
        
        self.config_path = config_path
        self.config_file = config_file
        self.config_data = self._load_config()
        self.config = self._load_json_config()
        
        # Initialize with default values if not present
        if "binance" not in self.config:
            self.config["binance"] = {
                "api_key": "",
                "api_secret": "",
                "testnet": True
            }
        if "trading_pairs" not in self.config:
            self.config["trading_pairs"] = []
        if "risk_management" not in self.config:
            self.config["risk_management"] = {
                "max_position_size": 0.2,  # 20% of balance
                "risk_per_trade": 0.01,    # 1% risk per trade
                "max_trades": 3            # Maximum concurrent trades
            }
        
        self._save_json_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise
            
    def _load_json_config(self) -> dict:
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def _save_json_config(self):
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=4)

    def get_exchange_credentials(self) -> Dict[str, str]:
        """Get exchange API credentials"""
        exchange = self.config_data['exchange']
        return self.config_data['api_keys'][exchange]
        
    def get_trading_pairs(self) -> List[str]:
        """Get configured trading pairs"""
        return self.config_data['trading_pairs']
        
    def get_timeframes(self) -> Dict[str, str]:
        """Get configured timeframes"""
        return self.config_data['timeframes']
        
    def get_risk_settings(self) -> Dict[str, float]:
        """Get risk management settings"""
        return {
            'risk_per_trade': self.config_data['risk_per_trade'],
            'max_open_trades': self.config_data['max_open_trades'],
            'max_drawdown': self.config_data['max_drawdown'],
            'position_size_limit': self.config_data['position_size_limit']
        }
        
    def get_trading_mode(self) -> str:
        """Get trading mode (paper/live)"""
        return self.config_data['trading_mode']
        
    def get_all(self) -> Dict[str, Any]:
        """Get entire configuration"""
        return self.config_data

    @property
    def binance_api_key(self) -> str:
        return self.config["binance"]["api_key"]

    @property
    def binance_api_secret(self) -> str:
        return self.config["binance"]["api_secret"]

    @property
    def use_testnet(self) -> bool:
        return self.config["binance"].get("testnet", True)

    def update_exchange_credentials(self, api_key: str, api_secret: str, use_testnet: bool = True):
        self.config["binance"]["api_key"] = api_key
        self.config["binance"]["api_secret"] = api_secret
        self.config["binance"]["testnet"] = use_testnet
        self._save_json_config()

    def update_trading_pairs(self, pairs: List[str]):
        self.config["trading_pairs"] = pairs
        self._save_json_config()

    def get_risk_parameters(self) -> dict:
        return self.config["risk_management"]

    def update_risk_parameters(self, max_position_size: float, risk_per_trade: float, max_trades: int):
        self.config["risk_management"].update({
            "max_position_size": max_position_size,
            "risk_per_trade": risk_per_trade,
            "max_trades": max_trades
        })
        self._save_json_config()
