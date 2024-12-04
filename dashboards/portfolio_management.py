import yaml
import os
import streamlit as st
import ccxt
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

class PortfolioManagementDashboard:
    def __init__(self):
        # Load configuration
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.yaml')
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
        
        # Get trading pairs from config
        self.trading_pairs = self.config.get('trading_pairs', [])
        self.exchange_name = self.config.get('exchange', 'binance')

    def fetch_portfolio_data(self):
        try:
            # Initialize exchange
            exchange_class = getattr(ccxt, self.exchange_name)
            exchange = exchange_class({
                'apiKey': self.config['api_keys'][self.exchange_name]['api_key'],
                'secret': self.config['api_keys'][self.exchange_name]['api_secret']
            })

            # Fetch balance
            balance = exchange.fetch_balance()
            
            # Filter and process relevant coins
            portfolio_data = []
            for pair in self.trading_pairs:
                base_coin = pair.split('/')[0]
                if base_coin in balance['total'] and balance['total'][base_coin] > 0:
                    # Fetch current price
                    ticker = exchange.fetch_ticker(pair)
                    current_price = ticker['last']
                    
                    portfolio_data.append({
                        'Coin': base_coin,
                        'Amount': balance['total'][base_coin],
                        'Current Price': current_price,
                        'Total Value': balance['total'][base_coin] * current_price
                    })
            
            return pd.DataFrame(portfolio_data)
        
        except Exception as e:
            st.error(f"Could not fetch portfolio data: {e}")
            return pd.DataFrame()

    def render_dashboard(self):
        st.title(f"{self.exchange_name.capitalize()} Portfolio Management")
        
        # Fetch portfolio data
        portfolio_df = self.fetch_portfolio_data()
        
        if portfolio_df.empty:
            st.error("No portfolio data could be retrieved. Check your API keys and configuration.")
            return
        
        # Portfolio Composition
        st.subheader("Portfolio Composition")
        fig_composition = px.pie(portfolio_df, values='Total Value', names='Coin', 
                                  title='Portfolio Allocation')
        st.plotly_chart(fig_composition)
        
        # Coin Holdings
        st.subheader("Coin Holdings")
        fig_holdings = px.bar(portfolio_df, x='Coin', y='Amount', 
                               title='Amount of Each Coin Held')
        st.plotly_chart(fig_holdings)
        
        # Total Portfolio Value
        total_portfolio_value = portfolio_df['Total Value'].sum()
        st.metric("Total Portfolio Value", f"${total_portfolio_value:,.2f}")
        
        # Detailed Portfolio Table
        st.subheader("Portfolio Details")
        st.dataframe(portfolio_df)

def main():
    dashboard = PortfolioManagementDashboard()
    dashboard.render_dashboard()

if __name__ == "__main__":
    main()
