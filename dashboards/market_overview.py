import yaml
import os
import streamlit as st
import ccxt
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

class MarketOverviewDashboard:
    def __init__(self):
        # Load configuration
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.yaml')
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
        
        # Get trading pairs from config
        self.trading_pairs = self.config.get('trading_pairs', [])
        self.exchange_name = self.config.get('exchange', 'binance')

    def fetch_market_data(self):
        # Initialize exchange
        exchange_class = getattr(ccxt, self.exchange_name)
        exchange = exchange_class()

        # Fetch data for configured pairs
        market_data = []
        for pair in self.trading_pairs:
            try:
                ticker = exchange.fetch_ticker(pair)
                market_data.append({
                    'Symbol': pair,
                    'Last Price': ticker['last'],
                    '24h Change %': ticker['percentage'],
                    'Volume': ticker['quoteVolume']
                })
            except Exception as e:
                st.warning(f"Could not fetch data for {pair}: {e}")
        
        return pd.DataFrame(market_data)

    def render_dashboard(self):
        st.title(f"{self.exchange_name.capitalize()} Market Overview")
        
        # Fetch market data
        market_df = self.fetch_market_data()
        
        if market_df.empty:
            st.error("No market data could be retrieved.")
            return
        
        # Price Comparison
        st.subheader("Price Comparison")
        fig_prices = px.bar(market_df, x='Symbol', y='Last Price', 
                            title='Current Prices of Trading Pairs')
        st.plotly_chart(fig_prices)
        
        # 24h Change Comparison
        st.subheader("24h Price Changes")
        fig_changes = px.bar(market_df, x='Symbol', y='24h Change %', 
                              title='24h Price Changes', 
                              color='24h Change %', 
                              color_continuous_scale='RdYlGn')
        st.plotly_chart(fig_changes)
        
        # Volume Comparison
        st.subheader("Trading Volume")
        fig_volume = px.bar(market_df, x='Symbol', y='Volume', 
                             title='Trading Volume')
        st.plotly_chart(fig_volume)
        
        # Display raw data
        st.subheader("Market Data")
        st.dataframe(market_df)

def main():
    dashboard = MarketOverviewDashboard()
    dashboard.render_dashboard()

if __name__ == "__main__":
    main()
