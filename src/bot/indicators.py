import numpy as np
import pandas as pd
import ta
from ta.momentum import RSIIndicator
from ta.trend import ADXIndicator, MACD
from ta.volatility import BollingerBands
from loguru import logger
from typing import Dict, Any, Optional
import json

class Indicators:
    def __init__(self):
        pass
    
    def validate_dataframe(self, df: pd.DataFrame) -> bool:
        """Validate input DataFrame"""
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        return all(col in df.columns for col in required_columns)
    
    def compute_indicators(self, df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """
        Compute comprehensive technical indicators
        
        Args:
            df (pd.DataFrame): Input OHLCV DataFrame
        
        Returns:
            pd.DataFrame or None: DataFrame with added indicators
        """
        try:
            if not self.validate_dataframe(df):
                logger.error("DataFrame missing required columns")
                return None
                
            # Trend indicators
            df['ema20'] = ta.trend.EMAIndicator(close=df['close'], window=20).ema_indicator()
            df['ema50'] = ta.trend.EMAIndicator(close=df['close'], window=50).ema_indicator()
            df['ema200'] = ta.trend.EMAIndicator(close=df['close'], window=200).ema_indicator()
            
            # ADX for trend strength with error handling
            adx_result = self.calculate_adx(df)
            df['adx'] = adx_result['adx']
            df['di_plus'] = adx_result['adx_pos']
            df['di_minus'] = adx_result['adx_neg']
            
            # RSI with error handling
            df['rsi'] = self.calculate_rsi(df)
            
            # MACD with error handling
            macd_result = self.calculate_macd(df)
            df['macd'] = macd_result['macd']
            df['macd_signal'] = macd_result['macd_signal']
            
            # Custom indicators
            df['atr'] = self.calculate_atr(df, period=14)
            df['trend_strength'] = self.calculate_trend_strength(df)
            
            return df
            
        except Exception as e:
            logger.error(f"Error computing indicators: {e}")
            return None
    
    def _fill_na(self, series: pd.Series) -> pd.Series:
        """
        Fill NA values using forward fill and then replace remaining NAs with 0
        
        Args:
            series: Input pandas Series
        
        Returns:
            Filled pandas Series
        """
        return series.ffill().fillna(0)

    def calculate_rsi(self, data: pd.DataFrame) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI) with robust error handling
        
        Args:
            data (pd.DataFrame): Price data
        
        Returns:
            pd.Series: RSI values
        """
        try:
            # Ensure we have enough data
            if len(data) < 14:
                logger.warning(f"Insufficient data for RSI calculation. Needed 14 rows, got {len(data)}")
                return pd.Series(np.nan, index=data.index)
            
            # Calculate RSI
            rsi_indicator = RSIIndicator(close=data['close'], window=14)
            rsi_series = rsi_indicator.rsi()
            
            # Safely fill NaN values
            rsi_series = rsi_series.ffill().fillna(0)
            
            return rsi_series
        except Exception as e:
            logger.error(f"RSI calculation error: {e}")
            return pd.Series(np.nan, index=data.index)

    def calculate_macd(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        """
        Calculate Moving Average Convergence Divergence (MACD) with robust error handling
        
        Args:
            data (pd.DataFrame): Price data
        
        Returns:
            Dict[str, pd.Series]: MACD and signal line series
        """
        try:
            # Ensure we have enough data
            if len(data) < 26:
                logger.warning(f"Insufficient data for MACD calculation. Needed 26 rows, got {len(data)}")
                return {
                    'macd': pd.Series(np.nan, index=data.index),
                    'macd_signal': pd.Series(np.nan, index=data.index)
                }
            
            # Calculate MACD
            macd_indicator = MACD(
                close=data['close'], 
                window_slow=26, 
                window_fast=12, 
                window_sign=9
            )
            
            macd_series = macd_indicator.macd()
            macd_signal_series = macd_indicator.macd_signal()
            
            # Safely fill NaN values
            macd_series = macd_series.ffill().fillna(0)
            macd_signal_series = macd_signal_series.ffill().fillna(0)
            
            return {
                'macd': macd_series,
                'macd_signal': macd_signal_series
            }
        except Exception as e:
            logger.error(f"MACD calculation error: {e}")
            return {
                'macd': pd.Series(np.nan, index=data.index),
                'macd_signal': pd.Series(np.nan, index=data.index)
            }
    
    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        try:
            high = df['high']
            low = df['low']
            close = df['close']
            
            # True Range Calculation
            tr1 = high - low
            tr2 = np.abs(high - close.shift(1))
            tr3 = np.abs(low - close.shift(1))
            
            tr = np.maximum(tr1, np.maximum(tr2, tr3))
            
            # ATR Calculation
            atr = tr.ewm(span=period, adjust=False).mean()
            
            return atr
        except Exception as e:
            logger.warning(f"ATR calculation error: {e}")
            return pd.Series(np.nan, index=df.index)
    
    def calculate_trend_strength(self, df: pd.DataFrame) -> pd.Series:
        """Calculate trend strength based on EMA crossovers"""
        try:
            ema20 = df['ema20']
            ema50 = df['ema50']
            ema200 = df['ema200']
            
            # Trend strength based on EMA alignment
            trend_score = np.where(
                (ema20 > ema50) & (ema50 > ema200), 1,  # Strong Uptrend
                np.where(
                    (ema20 < ema50) & (ema50 < ema200), -1,  # Strong Downtrend
                    0  # Neutral
                )
            )
            
            return pd.Series(trend_score, index=df.index)
        except Exception as e:
            logger.warning(f"Trend strength calculation error: {e}")
            return pd.Series(0, index=df.index)
    
    def calculate_adx(self, data: pd.DataFrame) -> dict:
        """
        Calculate Average Directional Index (ADX) with improved error handling
        
        Args:
            data (pd.DataFrame): Price data
        
        Returns:
            dict: ADX indicators with null checks
        """
        try:
            # Ensure we have enough data
            if len(data) < 14:
                logger.warning(f"Insufficient data for ADX calculation. Needed 14 rows, got {len(data)}")
                return {
                    'adx': None,
                    'adx_pos': None,
                    'adx_neg': None
                }
            
            # Use safe division and error handling
            with np.errstate(divide='ignore', invalid='ignore'):
                adx_indicator = ADXIndicator(
                    high=data['high'], 
                    low=data['low'], 
                    close=data['close'], 
                    window=14,
                    fillna=True
                )
                
                adx = adx_indicator.adx()
                adx_pos = adx_indicator.adx_pos()
                adx_neg = adx_indicator.adx_neg()
            
            # Replace potential inf or nan values
            adx = adx.ffill().fillna(0).replace([np.inf, -np.inf], 0).iloc[-1]
            adx_pos = adx_pos.ffill().fillna(0).replace([np.inf, -np.inf], 0).iloc[-1]
            adx_neg = adx_neg.ffill().fillna(0).replace([np.inf, -np.inf], 0).iloc[-1]
            
            return {
                'adx': float(adx),
                'adx_pos': float(adx_pos),
                'adx_neg': float(adx_neg)
            }
        
        except Exception as e:
            logger.error(f"Error in ADX calculation: {e}")
            return {
                'adx': None,
                'adx_pos': None,
                'adx_neg': None
            }
    
    def calculate_indicators(self, df: pd.DataFrame) -> dict:
        """
        Calculate multiple technical indicators with robust error handling
        
        Args:
            df (pd.DataFrame): OHLCV DataFrame
        
        Returns:
            dict: Dictionary of calculated indicators
        """
        try:
            # Ensure we have enough data
            if len(df) < 30:
                logger.warning("Insufficient data for indicator calculation")
                return {}
            
            # Calculate RSI
            rsi = self.calculate_rsi(df)
            
            # Calculate MACD
            macd_data = self.calculate_macd(df)
            
            # Calculate ADX
            adx_data = self.calculate_adx(df)
            
            # Calculate EMAs
            ema_20 = ta.trend.EMAIndicator(close=df['close'], window=20).ema_indicator()
            ema_50 = ta.trend.EMAIndicator(close=df['close'], window=50).ema_indicator()
            ema_200 = ta.trend.EMAIndicator(close=df['close'], window=200).ema_indicator()
            
            # Calculate ATR for volatility
            atr = self.calculate_atr(df)
            
            # Get latest values
            current_idx = -1
            
            return {
                'rsi': float(rsi.iloc[current_idx]) if not pd.isna(rsi.iloc[current_idx]) else None,
                'macd': float(macd_data['macd'].iloc[current_idx]) if not pd.isna(macd_data['macd'].iloc[current_idx]) else None,
                'macd_signal': float(macd_data['macd_signal'].iloc[current_idx]) if not pd.isna(macd_data['macd_signal'].iloc[current_idx]) else None,
                'adx': float(adx_data['adx']) if adx_data['adx'] is not None else None,
                'adx_pos': float(adx_data['adx_pos']) if adx_data['adx_pos'] is not None else None,
                'adx_neg': float(adx_data['adx_neg']) if adx_data['adx_neg'] is not None else None,
                'ema_20': float(ema_20.iloc[current_idx]) if not pd.isna(ema_20.iloc[current_idx]) else None,
                'ema_50': float(ema_50.iloc[current_idx]) if not pd.isna(ema_50.iloc[current_idx]) else None,
                'ema_200': float(ema_200.iloc[current_idx]) if not pd.isna(ema_200.iloc[current_idx]) else None,
                'atr': float(atr.iloc[current_idx]) if not pd.isna(atr.iloc[current_idx]) else None,
                'close': float(df['close'].iloc[current_idx]),
                'volume': float(df['volume'].iloc[current_idx])
            }
            
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return {}

    def generate_signal(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate comprehensive trading signal using multiple technical indicators
        
        Args:
            df (pd.DataFrame): OHLCV price data
        
        Returns:
            Dict with signal details: action, confidence, price, and additional metrics
        """
        try:
            # Ensure sufficient data
            if len(df) < 30:
                logger.warning("Insufficient data for signal generation")
                return {
                    "action": "hold", 
                    "confidence": 0.0, 
                    "score": 0.0,
                    "reason": "Insufficient historical data"
                }
            
            # Calculate technical indicators with forward fill to avoid deprecation warnings
            df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi().ffill()
            df['macd'] = ta.trend.MACD(df['close']).macd().ffill()
            df['macd_signal'] = ta.trend.MACD(df['close']).macd_signal().ffill()
            df['ema_short'] = ta.trend.EMAIndicator(df['close'], window=12).ema_indicator().ffill()
            df['ema_long'] = ta.trend.EMAIndicator(df['close'], window=26).ema_indicator().ffill()
            df['adx'] = ta.trend.ADXIndicator(df['high'], df['low'], df['close']).adx().ffill()
            
            # Latest values
            latest = df.iloc[-1]
            
            # Scoring mechanism
            indicators = {
                "rsi": {
                    "value": latest['rsi'],
                    "buy_threshold": 30,
                    "sell_threshold": 70
                },
                "macd": {
                    "value": latest['macd'],
                    "signal": latest['macd_signal'],
                    "crossover": latest['macd'] > latest['macd_signal']
                },
                "ema": {
                    "short": latest['ema_short'],
                    "long": latest['ema_long'],
                    "crossover": latest['ema_short'] > latest['ema_long']
                },
                "adx": {
                    "value": latest['adx'],
                    "strong_trend_threshold": 25
                }
            }
            
            # Confidence calculation
            confidence = 0.0
            score = 0.0
            action = "hold"
            reasons = []
            
            # RSI Analysis
            if indicators['rsi']['value'] <= indicators['rsi']['buy_threshold']:
                confidence += 0.3
                reasons.append("RSI indicates oversold condition")
                action = "buy"
            elif indicators['rsi']['value'] >= indicators['rsi']['sell_threshold']:
                confidence += 0.3
                reasons.append("RSI indicates overbought condition")
                action = "sell"
            
            # MACD Analysis
            if indicators['macd']['crossover']:
                confidence += 0.2
                reasons.append("MACD shows bullish momentum")
                action = "buy"
            
            # EMA Analysis
            if indicators['ema']['crossover']:
                confidence += 0.2
                reasons.append("Short-term EMA crossed above long-term EMA")
                action = "buy"
            
            # ADX Trend Strength
            if indicators['adx']['value'] >= indicators['adx']['strong_trend_threshold']:
                confidence += 0.2
                reasons.append("Strong trend detected")
            
            # Final scoring
            score = confidence * 100
            
            # Normalize confidence
            confidence = min(confidence, 1.0)
            
            # Determine final action
            if confidence < 0.4:
                action = "hold"
            
            result = {
                "action": action,
                "confidence": confidence,
                "score": score,
                "price": latest['close'],
                "reasons": reasons
            }
            
            logger.info(f"Signal Generation: Generated Signal: {json.dumps(result)}")
            return result
        
        except Exception as e:
            logger.error(f"Signal generation error: {e}")
            return {
                "action": "hold", 
                "confidence": 0.0, 
                "score": 0.0,
                "reason": f"Error in signal generation: {str(e)}"
            }

    def signal_score(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate a comprehensive trading signal score
        
        Args:
            df (pd.DataFrame): DataFrame with indicators
        
        Returns:
            Dict with signal details
        """
        try:
            # Validate input
            if df is None or len(df) == 0:
                return {'total_score': 0, 'signals': {}, 'strength': 0}
            
            # Extract last row of indicators
            last_row = df.iloc[-1]
            
            # Initialize signal components
            signals = {}
            
            # RSI Signal
            if last_row['rsi'] < 30:
                signals['rsi'] = 2  # Strong buy
            elif last_row['rsi'] > 70:
                signals['rsi'] = -2  # Strong sell
            else:
                signals['rsi'] = 0
            
            # MACD Signal
            if last_row['macd'] > last_row['macd_signal']:
                signals['macd'] = 1  # Bullish
            elif last_row['macd'] < last_row['macd_signal']:
                signals['macd'] = -1  # Bearish
            else:
                signals['macd'] = 0
            
            # ADX Trend Strength
            if last_row['adx'] > 25:
                signals['adx'] = 1 if last_row['di_plus'] > last_row['di_minus'] else -1
            else:
                signals['adx'] = 0
            
            # EMA Trend
            signals['trend'] = last_row['trend_strength']
            
            # Calculate total score
            total_score = sum(signals.values())
            
            return {
                'total_score': total_score, 
                'signals': signals, 
                'strength': abs(total_score) / 6
            }
        
        except Exception as e:
            logger.error(f"Error calculating signal score: {e}")
            return {'total_score': 0, 'signals': {}, 'strength': 0}
