import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from loguru import logger
from datetime import datetime
from ..src.bot.indicators import Indicators
from ..src.bot.risk_management import RiskManager

class Backtester:
    def __init__(self, initial_balance: float = 10000):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.indicators = Indicators()
        self.risk_manager = RiskManager(balance=initial_balance)
        self.trades: List[Dict] = []
        self.equity_curve: List[float] = [initial_balance]
        
    def run_backtest(self, df: pd.DataFrame) -> Dict:
        """
        Run backtest on historical data
        """
        try:
            # Compute indicators
            df = self.indicators.compute_indicators(df)
            if df is None:
                return self._generate_empty_results()
                
            # Initialize tracking variables
            position = None
            entry_price = 0.0
            position_size = 0.0
            
            # Iterate through each candle
            for i in range(1, len(df)):
                current_price = df['close'].iloc[i]
                
                if position is None:
                    # Look for entry signals
                    signal = self.indicators.signal_score(df.iloc[:i+1])
                    
                    if self._should_enter_trade(signal):
                        # Calculate position size and stop loss
                        stop_loss = self._calculate_stop_loss(df.iloc[i], signal['signals']['trend'])
                        position_size, risk_amount = self.risk_manager.calculate_position_size(
                            current_price, stop_loss
                        )
                        
                        # Enter position
                        position = signal['signals']['trend']
                        entry_price = current_price
                        self._record_trade('enter', current_price, position_size, stop_loss)
                        
                else:
                    # Check for exit conditions
                    if self._should_exit_trade(df.iloc[:i+1], position, entry_price, current_price):
                        # Exit position
                        pnl = self._calculate_pnl(position, entry_price, current_price, position_size)
                        self.balance += pnl
                        self._record_trade('exit', current_price, position_size, None, pnl)
                        
                        # Reset position
                        position = None
                        position_size = 0.0
                        
                # Update equity curve
                self.equity_curve.append(self.balance)
                
            return self._generate_results()
            
        except Exception as e:
            logger.error(f"Error in backtest: {e}")
            return self._generate_empty_results()
            
    def monte_carlo_simulation(self, returns: np.ndarray, iterations: int = 1000) -> Dict:
        """
        Perform Monte Carlo simulation on trading returns
        """
        try:
            simulated_equity_curves = []
            
            for _ in range(iterations):
                # Randomly sample returns with replacement
                sampled_returns = np.random.choice(returns, size=len(returns), replace=True)
                
                # Generate equity curve
                equity_curve = self.initial_balance * np.cumprod(1 + sampled_returns)
                simulated_equity_curves.append(equity_curve)
                
            simulated_equity_curves = np.array(simulated_equity_curves)
            
            return {
                'worst_drawdown': self._calculate_worst_drawdown(simulated_equity_curves),
                'avg_drawdown': self._calculate_avg_drawdown(simulated_equity_curves),
                'confidence_intervals': self._calculate_confidence_intervals(simulated_equity_curves),
                'final_balance_distribution': self._analyze_final_balance(simulated_equity_curves)
            }
            
        except Exception as e:
            logger.error(f"Error in Monte Carlo simulation: {e}")
            return {}
            
    def _should_enter_trade(self, signal: Dict) -> bool:
        """
        Determine if we should enter a trade based on signals
        """
        return (
            signal['total_score'] >= 2 and
            signal['strength'] >= 0.5 and
            self.risk_manager.can_open_trade()
        )
        
    def _should_exit_trade(self, df: pd.DataFrame, position: str, entry_price: float, 
                          current_price: float) -> bool:
        """
        Determine if we should exit the current trade
        """
        signal = self.indicators.signal_score(df)
        
        # Exit on signal reversal
        if position == 'bullish' and signal['total_score'] < 0:
            return True
        if position == 'bearish' and signal['total_score'] > 0:
            return True
            
        # Exit on profit target or stop loss
        pnl_percentage = (current_price - entry_price) / entry_price * 100
        if abs(pnl_percentage) > 5:  # 5% profit target or stop loss
            return True
            
        return False
        
    def _calculate_stop_loss(self, candle: pd.Series, trend: str) -> float:
        """
        Calculate stop loss price based on ATR and trend
        """
        atr = candle['atr']
        if trend == 'bullish':
            return candle['close'] - (2 * atr)
        return candle['close'] + (2 * atr)
        
    def _calculate_pnl(self, position: str, entry_price: float, exit_price: float, 
                      position_size: float) -> float:
        """
        Calculate profit/loss for a trade
        """
        if position == 'bullish':
            return (exit_price - entry_price) * position_size
        return (entry_price - exit_price) * position_size
        
    def _record_trade(self, action: str, price: float, size: float, 
                     stop_loss: Optional[float], pnl: Optional[float] = None) -> None:
        """
        Record trade details
        """
        self.trades.append({
            'timestamp': datetime.now(),
            'action': action,
            'price': price,
            'size': size,
            'stop_loss': stop_loss,
            'pnl': pnl,
            'balance': self.balance
        })
        
    def _generate_results(self) -> Dict:
        """
        Generate backtest results and statistics
        """
        equity_curve = np.array(self.equity_curve)
        returns = np.diff(equity_curve) / equity_curve[:-1]
        
        return {
            'initial_balance': self.initial_balance,
            'final_balance': self.balance,
            'total_return': (self.balance - self.initial_balance) / self.initial_balance * 100,
            'sharpe_ratio': self._calculate_sharpe_ratio(returns),
            'max_drawdown': self._calculate_max_drawdown(equity_curve),
            'win_rate': self._calculate_win_rate(),
            'profit_factor': self._calculate_profit_factor(),
            'trades': self.trades,
            'equity_curve': self.equity_curve
        }
        
    def _generate_empty_results(self) -> Dict:
        """
        Generate empty results when backtest fails
        """
        return {
            'initial_balance': self.initial_balance,
            'final_balance': self.initial_balance,
            'total_return': 0,
            'sharpe_ratio': 0,
            'max_drawdown': 0,
            'win_rate': 0,
            'profit_factor': 0,
            'trades': [],
            'equity_curve': [self.initial_balance]
        }
        
    def _calculate_sharpe_ratio(self, returns: np.ndarray) -> float:
        """
        Calculate Sharpe ratio
        """
        if len(returns) < 2:
            return 0.0
        return np.mean(returns) / np.std(returns) * np.sqrt(252)
        
    def _calculate_max_drawdown(self, equity_curve: np.ndarray) -> float:
        """
        Calculate maximum drawdown
        """
        peak = np.maximum.accumulate(equity_curve)
        drawdown = (peak - equity_curve) / peak
        return float(np.max(drawdown) * 100)
        
    def _calculate_win_rate(self) -> float:
        """
        Calculate win rate
        """
        if not self.trades:
            return 0.0
        
        winning_trades = sum(1 for trade in self.trades if trade.get('pnl', 0) > 0)
        return winning_trades / len(self.trades) * 100
        
    def _calculate_profit_factor(self) -> float:
        """
        Calculate profit factor
        """
        gross_profit = sum(trade['pnl'] for trade in self.trades if trade.get('pnl', 0) > 0)
        gross_loss = abs(sum(trade['pnl'] for trade in self.trades if trade.get('pnl', 0) < 0))
        
        return gross_profit / gross_loss if gross_loss != 0 else 0.0
        
    @staticmethod
    def _calculate_confidence_intervals(equity_curves: np.ndarray) -> Dict[str, float]:
        """
        Calculate confidence intervals for equity curves
        """
        percentiles = np.percentile(equity_curves, [5, 25, 50, 75, 95], axis=0)
        return {
            '5th': float(percentiles[0, -1]),
            '25th': float(percentiles[1, -1]),
            'median': float(percentiles[2, -1]),
            '75th': float(percentiles[3, -1]),
            '95th': float(percentiles[4, -1])
        }
        
    @staticmethod
    def _analyze_final_balance(equity_curves: np.ndarray) -> Dict[str, float]:
        """
        Analyze distribution of final balance
        """
        final_balances = equity_curves[:, -1]
        return {
            'mean': float(np.mean(final_balances)),
            'std': float(np.std(final_balances)),
            'min': float(np.min(final_balances)),
            'max': float(np.max(final_balances))
        }
