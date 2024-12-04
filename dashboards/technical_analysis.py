import yaml
import os
import streamlit as st
import ccxt
import pandas as pd
import numpy as np
import plotly.graph_objs as go

try:
    import talib
except ImportError:
    st.warning("TA-Lib not fully installed. Some technical indicators may not work.")
    talib = None

class TechnicalAnalysisDashboard:
    def __init__(self):
        # Load configuration
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.yaml')
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
        
        # Get trading pairs from config
        self.trading_pairs = self.config.get('trading_pairs', [])
        self.exchange_name = self.config.get('exchange', 'binance')
        
        # Get timeframes from config
        self.primary_timeframe = self.config.get('timeframes', {}).get('primary', '15m')
        self.secondary_timeframe = self.config.get('timeframes', {}).get('secondary', '1m')

    def fetch_ohlcv_data(self, pair, timeframe='15m', limit=100):
        try:
            exchange_class = getattr(ccxt, self.exchange_name)
            exchange = exchange_class()
            ohlcv = exchange.fetch_ohlcv(pair, timeframe, limit=limit)
            
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            st.error(f"Could not fetch OHLCV data for {pair}: {e}")
            return None

    def calculate_technical_indicators(self, df):
        if df is None or df.empty:
            return None
        
        # Calculate indicators
        if talib is not None:
            df['RSI'] = talib.RSI(df['close'], timeperiod=14)
            df['MACD'], df['MACD_signal'], df['MACD_hist'] = talib.MACD(df['close'])
            upper, middle, lower = talib.BBANDS(df['close'], timeperiod=20)
            df['Bollinger_Upper'] = upper
            df['Bollinger_Middle'] = middle
            df['Bollinger_Lower'] = lower
        
        return df

    def render_dashboard(self):
        st.title(f"{self.exchange_name.capitalize()} Technical Analysis")
        
        # Pair selection
        selected_pair = st.selectbox("Select Trading Pair", self.trading_pairs)
        
        # Timeframe selection
        timeframe = st.selectbox("Select Timeframe", 
                                 [self.primary_timeframe, self.secondary_timeframe])
        
        # Fetch and process data
        ohlcv_data = self.fetch_ohlcv_data(selected_pair, timeframe)
        if ohlcv_data is None:
            st.error("Could not retrieve market data.")
            return
        
        technical_data = self.calculate_technical_indicators(ohlcv_data)
        if technical_data is None:
            st.error("Could not calculate technical indicators.")
            return
        
        # Price Chart with Bollinger Bands
        fig_price = go.Figure()
        fig_price.add_trace(go.Scatter(x=technical_data['timestamp'], y=technical_data['close'], 
                                        mode='lines', name='Close Price'))
        if 'Bollinger_Upper' in technical_data.columns:
            fig_price.add_trace(go.Scatter(x=technical_data['timestamp'], y=technical_data['Bollinger_Upper'], 
                                            mode='lines', name='Bollinger Upper', line=dict(color='red', dash='dot')))
            fig_price.add_trace(go.Scatter(x=technical_data['timestamp'], y=technical_data['Bollinger_Lower'], 
                                            mode='lines', name='Bollinger Lower', line=dict(color='green', dash='dot')))
        fig_price.update_layout(title=f'{selected_pair} Price with Bollinger Bands')
        st.plotly_chart(fig_price)
        
        # RSI Chart
        if 'RSI' in technical_data.columns:
            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(x=technical_data['timestamp'], y=technical_data['RSI'], 
                                          mode='lines', name='RSI'))
            fig_rsi.add_hline(y=70, line_color='red', line_dash='dot')
            fig_rsi.add_hline(y=30, line_color='green', line_dash='dot')
            fig_rsi.update_layout(title=f'{selected_pair} RSI')
            st.plotly_chart(fig_rsi)
        
        # MACD Chart
        if 'MACD' in technical_data.columns:
            fig_macd = go.Figure()
            fig_macd.add_trace(go.Scatter(x=technical_data['timestamp'], y=technical_data['MACD'], 
                                           mode='lines', name='MACD'))
            fig_macd.add_trace(go.Scatter(x=technical_data['timestamp'], y=technical_data['MACD_signal'], 
                                           mode='lines', name='Signal'))
            fig_macd.add_trace(go.Bar(x=technical_data['timestamp'], y=technical_data['MACD_hist'], 
                                       name='Histogram'))
            fig_macd.update_layout(title=f'{selected_pair} MACD')
            st.plotly_chart(fig_macd)

def main():
    dashboard = TechnicalAnalysisDashboard()
    dashboard.render_dashboard()

if __name__ == "__main__":
    main()
