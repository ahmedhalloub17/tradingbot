from typing import Tuple
import numpy as np
from loguru import logger

class RiskManager:
    def __init__(
        self, 
        balance: float, 
        risk_per_trade: float = 0.01, 
        max_risk_per_trade: float = 0.02,
        max_drawdown: float = 0.10,
        position_size_limit: float = 0.20,
        max_trades: int = 3
    ):
        """
        Initialize RiskManager with enhanced parameters
        
        Args:
            balance: Current account balance
            risk_per_trade: Initial risk per trade (default 1%)
            max_risk_per_trade: Maximum risk per trade (default 2%)
            max_drawdown: Maximum allowed drawdown (default 10%)
            position_size_limit: Maximum position size as % of balance (default 20%)
            max_trades: Maximum number of concurrent trades (default 3)
        """
        self.balance = balance
        self.initial_risk_per_trade = risk_per_trade
        self.risk_per_trade = risk_per_trade
        self.max_risk_per_trade = max_risk_per_trade
        self.max_drawdown = max_drawdown
        self.position_size_limit = position_size_limit
        self.max_trades = max_trades
        self.open_trades = 0
        
        logger.info(f"RiskManager initialized with balance: {balance}, "
                   f"risk_per_trade: {risk_per_trade}, "
                   f"max_drawdown: {max_drawdown}")

    def calculate_position_size(self, price: float, risk_per_trade: float = None) -> float:
        """
        Calculate optimal position size based on account balance and risk parameters
        
        Args:
            price (float): Current market price
            risk_per_trade (float, optional): Percentage of balance to risk per trade
        
        Returns:
            float: Calculated position size
        """
        try:
            # Use default risk if not provided
            if risk_per_trade is None:
                risk_per_trade = self.risk_per_trade
            
            # Validate inputs
            if price <= 0 or self.balance <= 0:
                logger.warning("Invalid price or balance for position sizing")
                return 0.0
            
            # Calculate risk amount
            risk_amount = self.balance * risk_per_trade
            
            # Prevent over-leveraging
            max_trade_amount = self.balance * self.position_size_limit
            
            # Calculate position size
            position_size = risk_amount / price
            
            # Ensure position size is within limits
            position_size = min(position_size, max_trade_amount / price)
            
            # Round to exchange precision (typically 6 decimal places)
            position_size = round(position_size, 6)
            
            # Final validation
            if position_size * price > max_trade_amount:
                logger.warning(f"Position size {position_size} exceeds max trade amount")
                position_size = max_trade_amount / price
            
            return position_size
        
        except Exception as e:
            logger.error(f"Position size calculation error: {e}")
            return 0.0
    
    def adjust_risk(self, drawdown: float, volatility: float) -> None:
        """
        Dynamically adjust risk based on market conditions and account performance
        """
        try:
            # Reduce risk as drawdown increases
            drawdown_factor = max(0, 1 - (drawdown / 100))
            
            # Adjust risk based on volatility (higher volatility = lower risk)
            volatility_factor = max(0.5, 1 - (volatility / 100))
            
            # Combine factors and apply to base risk
            adjusted_risk = self.initial_risk_per_trade * drawdown_factor * volatility_factor
            
            # Ensure risk stays within bounds
            self.risk_per_trade = max(0.005, min(self.max_risk_per_trade, adjusted_risk))
            
            logger.info(f"Risk adjusted to {self.risk_per_trade:.4f} based on drawdown: {drawdown:.2f}% and volatility: {volatility:.2f}%")
            
        except Exception as e:
            logger.error(f"Error adjusting risk: {e}")
            
    def can_open_trade(self) -> bool:
        """Check if we can open a new trade based on current conditions"""
        return self.open_trades < self.max_trades
    
    def calculate_volatility(self, prices: np.ndarray, window: int = 20) -> float:
        """
        Calculate price volatility using standard deviation of returns
        """
        try:
            if len(prices) < window:
                return 0.0
                
            returns = np.diff(prices) / prices[:-1]
            volatility = np.std(returns[-window:]) * np.sqrt(252)  # Annualized volatility
            return volatility * 100  # Convert to percentage
            
        except Exception as e:
            logger.error(f"Error calculating volatility: {e}")
            return 0.0
    
    def calculate_drawdown(self, equity_curve: np.ndarray) -> float:
        """
        Calculate current drawdown from equity curve
        """
        try:
            peak = np.maximum.accumulate(equity_curve)
            drawdown = (peak - equity_curve) / peak * 100
            return float(drawdown[-1])
            
        except Exception as e:
            logger.error(f"Error calculating drawdown: {e}")
            return 0.0
            
    def update_balance(self, new_balance: float) -> None:
        """
        Update account balance after trades
        """
        self.balance = new_balance
        logger.info(f"Balance updated to: {self.balance}")
