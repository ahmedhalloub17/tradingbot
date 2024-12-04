import asyncio
import ccxt
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
from loguru import logger
import json
import logging
from .indicators import Indicators
from .risk_management import RiskManager
from .config import Config


class TradingBot:
    def __init__(self, config_path: str = None):
        self.config = Config(config_path).get_all()
        # Use async-compatible exchange
        self.exchange = self._initialize_exchange()
        self.indicators = Indicators()
        
        risk_settings = Config(config_path).get_risk_settings()
        self.risk_manager = RiskManager(
            balance=float(self.get_balance()),
            risk_per_trade=risk_settings['risk_per_trade'],
            max_drawdown=risk_settings['max_drawdown'],
            position_size_limit=risk_settings['position_size_limit']
        )
        
        self.active_trades: Dict[str, Dict] = {}
        
        # Filter valid trading pairs
        self.trading_pairs = self._validate_trading_pairs(
            Config(config_path).get_trading_pairs()
        )
        
        self.timeframes = Config(config_path).get_timeframes()
        
    def _initialize_exchange(self):
        """
        Initialize async-compatible exchange with robust configuration
        
        Supports multiple trading modes: spot, futures, margin
        Handles different exchange configurations
        """
        try:
            exchange_id = self.config.get('exchange', 'binance').lower()
            trading_mode = self.config.get('trading_mode', 'spot').lower()
            
            # Get credentials from config
            credentials = Config(None).get_exchange_credentials()
            
            # Exchange configuration
            exchange_config = {
                'apiKey': credentials['api_key'],
                'secret': credentials['api_secret'],
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot'  # Default to spot trading
                }
            }
            
            # Specialized configurations
            if trading_mode == 'futures':
                exchange_config['options']['defaultType'] = 'future'
            elif trading_mode == 'margin':
                exchange_config['options']['defaultType'] = 'margin'
            
            # Initialize exchange
            exchange_class = getattr(ccxt, exchange_id)
            exchange = exchange_class(exchange_config)
            
            # Verify exchange connectivity
            exchange.load_markets()
            
            logger.info(f"Exchange {exchange_id} initialized in {trading_mode} mode")
            return exchange
        
        except ccxt.NetworkError:
            logger.error("Network error connecting to exchange. Check internet connection.")
            raise
        except ccxt.AuthenticationError:
            logger.error("Authentication failed. Check API key and secret.")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize exchange: {str(e)}")
            raise

    def get_balance(self) -> float:
        """
        Retrieve account balance with comprehensive error handling
        
        Returns:
            float: Total account balance in USDT
        """
        try:
            # Fetch balance with multiple retry strategies
            balance_strategies = [
                lambda: self.exchange.fetch_balance(),
                lambda: self.exchange.fetch_total_balance(),
                lambda: self.exchange.privateGetBalance()
            ]
            
            for strategy in balance_strategies:
                try:
                    balance = strategy()
                    
                    # Multiple balance retrieval methods
                    balance_methods = [
                        lambda b: b.get('total', {}).get('USDT', 0.0),
                        lambda b: b.get('free', {}).get('USDT', 0.0),
                        lambda b: b.get('USDT', {}).get('total', 0.0),
                        lambda b: sum(float(v) for v in b.get('total', {}).values() if isinstance(v, (int, float))),
                        lambda b: sum(float(v) for v in b.get('free', {}).values() if isinstance(v, (int, float)))
                    ]
                    
                    for method in balance_methods:
                        try:
                            bal = method(balance)
                            if isinstance(bal, (int, float)) and bal > 0:
                                logger.info(f"Balance retrieved: {bal} USDT")
                                return float(bal)
                        except Exception:
                            continue
                
                except Exception as strategy_error:
                    logger.warning(f"Balance retrieval strategy failed: {strategy_error}")
                    continue
            
            logger.error("Unable to retrieve balance from any strategy")
            return 0.0
        
        except ccxt.AuthenticationError:
            logger.error("Authentication failed. Verify API key permissions.")
            return 0.0
        except ccxt.NetworkError:
            logger.error("Network error while fetching balance.")
            return 0.0
        except Exception as e:
            logger.error(f"Unexpected balance retrieval error: {e}")
            return 0.0
            
    async def fetch_ohlcv(self, symbol: str, timeframe: str) -> Optional[pd.DataFrame]:
        """
        Fetch OHLCV data with proper async handling and error recovery

        Args:
            symbol: Trading pair symbol
            timeframe: Timeframe for candlestick data
            
        Returns:
            Optional[pd.DataFrame]: OHLCV data as DataFrame or None on error
        """
        try:
            # Use synchronous fetch method wrapped in run_in_executor
            loop = asyncio.get_event_loop()
            ohlcv = await loop.run_in_executor(
                None, 
                lambda: self.exchange.fetch_ohlcv(symbol, timeframe)
            )
            
            if not ohlcv or len(ohlcv) < 30:  # Minimum required candles
                logger.warning(f"Insufficient OHLCV data for {symbol} on {timeframe}")
                return None
                
            # Convert to DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            return df
            
        except ccxt.NetworkError as e:
            logger.error(f"Network error fetching OHLCV data for {symbol}: {str(e)}")
            return None
        except ccxt.ExchangeError as e:
            logger.error(f"Exchange error fetching OHLCV data for {symbol}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error fetching OHLCV data for {symbol}: {str(e)}")
            return None

    async def analyze_market(self, symbol: str, timeframe: str) -> Optional[Dict[str, Any]]:
        """
        Comprehensive market analysis for a specific trading pair
        
        Args:
            symbol (str): Trading pair symbol
            timeframe (str): Timeframe for analysis
        
        Returns:
            Optional[Dict[str, Any]]: Market analysis results or None
        """
        try:
            # Fetch OHLCV data
            df = await self.fetch_ohlcv(symbol, timeframe)
            
            if df is None:
                logger.warning(f"No OHLCV data available for {symbol}")
                return None
            
            # Get current balance information
            balances = self.exchange.fetch_balance()
            markets = self.exchange.load_markets()
            
            base_currency = markets[symbol]['base']
            quote_currency = markets[symbol]['quote']
            
            base_balance = float(balances.get('total', {}).get(base_currency, 0))
            quote_balance = float(balances.get('total', {}).get(quote_currency, 0))
            
            # Calculate technical indicators
            try:
                # Generate comprehensive signal
                signal = self.indicators.generate_signal(df)
                
                # Balance-based analysis
                action = signal.get('action', 'hold')
                confidence = signal.get('confidence', 0.0)
                current_price = df['close'].iloc[-1]
                
                # Adjust action based on balance
                if quote_balance == 0 and base_balance > 0:
                    # We only have base currency, consider selling
                    if action != 'sell' and confidence > 0.6:
                        action = 'hold'  # Be more conservative about selling
                    confidence *= 0.9  # Reduce confidence slightly
                elif base_balance == 0 and quote_balance > 0:
                    # We only have quote currency, look for buying opportunities
                    if action != 'buy':
                        action = 'buy'
                        confidence *= 1.1  # Increase confidence for buy signals
                elif base_balance == 0 and quote_balance == 0:
                    # No balance in either currency
                    action = 'hold'
                    confidence = 0
                    logger.warning(f"No balance available for trading {symbol}")
                
                analysis_result = {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "action": action,
                    "confidence": min(confidence, 1.0),  # Cap confidence at 1.0
                    "score": signal.get('score', 0.0),
                    "price": current_price,
                    "reasons": signal.get('reasons', []),
                    "base_balance": base_balance,
                    "quote_balance": quote_balance,
                    "base_currency": base_currency,
                    "quote_currency": quote_currency
                }
                
                # Log detailed analysis
                logger.info(f"Market Analysis for {symbol}: {json.dumps(analysis_result)}")
                
                return analysis_result
            
            except Exception as indicator_error:
                logger.error(f"Indicator calculation error for {symbol}: {indicator_error}")
                return None
        
        except Exception as e:
            logger.error(f"Market analysis error for {symbol}: {e}")
            return None

    async def execute_trade(self, symbol: str = None, side: str = None, size: float = None, signal: dict = None) -> bool:
        try:
            # If a signal is provided, use the new approach
            if signal:
                # Extract necessary information from signal
                symbol = signal.get('symbol') or signal.get('pair')
                side = signal.get('action', '').lower()
                
                # Calculate size based on risk management
                price = signal.get('price', 0)
                confidence = signal.get('confidence', 0)
                
                # Add additional validation for risk management calculation
                try:
                    size = self.risk_manager.calculate_trade_amount(symbol, price, confidence)
                except Exception as risk_error:
                    logging.error(f"Risk management calculation error for {symbol}: {risk_error}")
                    return False

            # Validate inputs for the old method signature
            if not symbol or not side:
                logging.error(f"Invalid trade parameters: symbol={symbol}, side={side}")
                return False

            # Skip trade if action is hold or size is zero or negative
            if side == 'hold' or (size is not None and size <= 0):
                logging.info(f"Hold signal or invalid trade size for {symbol}. No trade executed.")
                return True

            # Fetch current market price with error handling
            try:
                loop = asyncio.get_event_loop()
                ticker = await loop.run_in_executor(None, lambda: self.exchange.fetch_ticker(symbol))
                current_price = ticker['last']
                
                if current_price is None:
                    logging.error(f"Unable to fetch current price for {symbol}")
                    return False
            except Exception as price_error:
                logging.error(f"Error fetching price for {symbol}: {price_error}")
                return False

            # Ensure size is set
            if size is None:
                logging.error(f"Trade size not determined for {symbol}")
                return False
            
            # Prepare trade parameters
            trade_params = {
                'symbol': symbol,
                'type': 'market',
                'side': side.upper(),  # Ensure uppercase for exchange compatibility
                'amount': size
            }
            
            # Execute trade with proper async handling
            try:
                if side == 'buy':
                    trade_result = await loop.run_in_executor(None, lambda: self.exchange.create_market_buy_order(symbol, size))
                elif side == 'sell':
                    trade_result = await loop.run_in_executor(None, lambda: self.exchange.create_market_sell_order(symbol, size))
                else:
                    logging.error(f"Unsupported trade side: {side}")
                    return False
                
                # Log trade details
                logging.info(f"Trade Execution: {symbol} | Side: {side} | Size: {size:.4f} | Price: {current_price:.4f} | Total Value: {size * current_price:.2f}")
                
                # Update active trades if it's a buy order
                if side == 'buy':
                    self.active_trades[symbol] = {
                        'entry_price': current_price,
                        'position_size': size,
                        'timestamp': datetime.now(),
                        'side': side,
                        'stop_loss': self._calculate_stop_loss(current_price, signal or {})
                    }
                    logging.info(f"Added {symbol} to active trades with stop loss at {self.active_trades[symbol]['stop_loss']}")
                
                return True
                
            except Exception as trade_error:
                logging.error(f"Trade execution error for {symbol}: {trade_error}")
                # Log full error details for debugging
                logging.error(f"Trade details: {trade_params}")
                return False
            
        except Exception as e:
            logging.error(f"Unexpected error executing trade for {symbol}: {e}")
            # Log the full traceback for comprehensive debugging
            logging.error(f"Full error details:", exc_info=True)
            return False

    async def manage_trades(self):
        """Manage existing trades"""
        try:
            for symbol, trade in self.active_trades.items():
                loop = asyncio.get_event_loop()
                current_price = float((await loop.run_in_executor(
                    None, 
                    lambda: self.exchange.fetch_ticker(symbol)
                ))['last'])
                
                # Update trade metrics
                trade['current_price'] = current_price
                trade['pnl'] = self._calculate_pnl(trade)
                trade['pnl_percentage'] = (trade['pnl'] / (trade['entry_price'] * trade['position_size'])) * 100
                
                # Get current market analysis
                analysis = await self.analyze_market(symbol, self.timeframes['primary'])
                
                # Check for sell conditions
                should_sell = False
                sell_reason = ""
                
                # 1. Stop Loss Check
                if current_price <= trade.get('stop_loss', 0):
                    should_sell = True
                    sell_reason = "Stop loss triggered"
                
                # 2. Take Profit Check (2% profit)
                elif trade['pnl_percentage'] >= 2.0:
                    should_sell = True
                    sell_reason = "Take profit target reached"
                
                # 3. Technical Analysis Based Exit
                elif analysis and analysis.get('action') == 'sell' and analysis.get('confidence', 0) >= 0.4:
                    should_sell = True
                    sell_reason = f"Sell signal generated: {', '.join(analysis.get('reasons', []))}"
                
                # 4. Trailing Stop Loss (if in profit)
                elif trade['pnl_percentage'] > 0:
                    # Update trailing stop to lock in 50% of the profit
                    new_stop = trade['entry_price'] + (current_price - trade['entry_price']) * 0.5
                    if new_stop > trade.get('stop_loss', 0):
                        trade['stop_loss'] = new_stop
                        logger.info(f"Updated trailing stop for {symbol} to {new_stop}")
                
                # Execute sell if conditions are met
                if should_sell:
                    logger.info(f"Selling {symbol} - Reason: {sell_reason}")
                    trade_result = await self.execute_trade(
                        symbol=symbol,
                        side='sell',
                        size=trade['position_size']
                    )
                    
                    if trade_result:
                        logger.info(f"Successfully sold {symbol} - PnL: {trade['pnl_percentage']:.2f}%")
                        del self.active_trades[symbol]
                    else:
                        logger.error(f"Failed to sell {symbol}")
                
                # Log trade status
                logger.info(f"Trade Status - {symbol}: Price: {current_price:.8f}, "
                          f"PnL: {trade['pnl_percentage']:.2f}%, "
                          f"Stop Loss: {trade.get('stop_loss', 0):.8f}")
                
        except Exception as e:
            logger.error(f"Error managing trades: {e}")

    def _calculate_pnl(self, trade: Dict) -> float:
        """Calculate unrealized PnL for a trade"""
        if trade['side'] == 'buy':
            return (trade['current_price'] - trade['entry_price']) * trade['position_size']
        return (trade['entry_price'] - trade['current_price']) * trade['position_size']
        
    async def run(self):
        """
        Main trading bot execution loop
        Manages active trades, analyzes markets, and executes trades
        """
        logger.info("Starting trading bot in live mode")
        
        while True:
            try:
                # Update balance
                current_balance = self.get_balance()
                self.risk_manager.update_balance(current_balance)
                
                # Log number of valid trading pairs
                logger.info(f"Monitoring {len(self.trading_pairs)} valid trading pairs")
                
                # Manage existing trades
                await self.manage_trades()
                
                # Analyze markets and execute new trades
                for symbol in self.trading_pairs:
                    # Log analysis attempt
                    logger.info(f"Analyzing {symbol}...")
                    
                    if symbol in self.active_trades:
                        logger.info(f"Skipping {symbol} - Already in active trades")
                        continue
                        
                    if not self.risk_manager.can_open_trade():
                        logger.info(f"Skipping {symbol} - Risk manager preventing new trades")
                        continue
                        
                    analysis = await self.analyze_market(symbol, self.timeframes['primary'])
                    
                    if not analysis:
                        logger.warning(f"No analysis available for {symbol}")
                        continue
                        
                    # Log analysis results
                    logger.info(f"Analysis for {symbol}: Action={analysis.get('action')}, Confidence={analysis.get('confidence')}")
                    
                    # Updated signal processing
                    if analysis.get('action') != 'buy':
                        logger.info(f"No buy signal for {symbol}")
                        continue
                        
                    if analysis.get('confidence', 0) < 0.4:
                        logger.info(f"Confidence too low for {symbol}: {analysis.get('confidence')}")
                        continue
                    
                    # Calculate position size
                    loop = asyncio.get_event_loop()
                    position_size = self.risk_manager.calculate_position_size(
                        price=analysis.get('price', 0),
                        risk_per_trade=self.risk_manager.risk_per_trade
                    )
                    
                    logger.info(f"Calculated position size for {symbol}: {position_size}")
                    
                    # Execute trade
                    if position_size > 0:
                        trade_success = await self.execute_trade(
                            symbol=symbol, 
                            side='buy', 
                            size=position_size
                        )
                        
                        if trade_success:
                            self.active_trades[symbol] = {
                                'entry_price': analysis.get('price', 0),
                                'position_size': position_size,
                                'timestamp': datetime.now()
                            }
                            logger.info(f"Successfully opened trade for {symbol}")
                    else:
                        logger.warning(f"Position size too small for {symbol}")
                
                # Sleep to prevent excessive API calls
                await asyncio.sleep(self.config.get('trading_interval', 300))
            
            except Exception as e:
                logger.error(f"Error in trading bot main loop: {e}")
                await asyncio.sleep(60)  # Wait before retrying
                
    def _validate_trading_pairs(self, pairs: List[str]) -> List[str]:
            """
            Validate trading pairs against exchange markets and balance
            
            Args:
                pairs: List of trading pairs to validate
            
            Returns:
                List of valid trading pairs
            """
            valid_pairs = []
            try:
                markets = self.exchange.load_markets()
                balances = self.exchange.fetch_balance()
                
                for pair in pairs:
                    try:
                        # Check if pair exists in exchange
                        if pair not in markets:
                            logger.warning(f"Pair {pair} not found in exchange markets")
                            continue
                            
                        # Extract base and quote currencies
                        base_currency = markets[pair]['base']
                        quote_currency = markets[pair]['quote']
                        
                        # Check if we have balance in either currency
                        base_balance = float(balances.get('total', {}).get(base_currency, 0))
                        quote_balance = float(balances.get('total', {}).get(quote_currency, 0))
                        
                        # Check minimum trade requirements
                        market_limits = markets[pair].get('limits', {})
                        min_amount = market_limits.get('amount', {}).get('min', 0)
                        min_cost = market_limits.get('cost', {}).get('min', 0)
                        
                        # Validate against minimum requirements
                        if (base_balance > min_amount or quote_balance > min_cost):
                            valid_pairs.append(pair)
                            logger.info(f"Validated pair {pair} - Base balance: {base_balance} {base_currency}, Quote balance: {quote_balance} {quote_currency}")
                        else:
                            logger.warning(f"Pair {pair} does not meet minimum balance requirements")
                            
                    except Exception as pair_error:
                        logger.error(f"Error validating pair {pair}: {str(pair_error)}")
                        continue
                        
                return valid_pairs
                
            except Exception as e:
                logger.error(f"Error validating trading pairs: {str(e)}")
                return []

    def _calculate_stop_loss(self, current_price: float, analysis: Dict) -> float:
        """Calculate stop loss price based on ATR and signal strength"""
        atr = analysis.get('higher_tf', {}).get('atr', current_price * 0.02)  # Default to 2% if ATR not available
        
        if analysis['signal'] == 'buy':
            return current_price - (2 * atr)
        return current_price + (2 * atr)
