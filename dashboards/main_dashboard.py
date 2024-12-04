import streamlit as st
import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dashboards.market_overview import MarketOverviewDashboard
from dashboards.technical_analysis import TechnicalAnalysisDashboard
from dashboards.portfolio_management import PortfolioManagementDashboard

def main():
    st.set_page_config(page_title="Crypto Trading Dashboard", layout="wide")
    
    st.sidebar.title(" Crypto Trading Dashboard")
    
    # Dashboard Selection
    dashboard_options = [
        "Market Overview", 
        "Technical Analysis", 
        "Portfolio Management"
    ]
    selected_dashboard = st.sidebar.radio("Select Dashboard", dashboard_options)
    
    # Render Selected Dashboard
    if selected_dashboard == "Market Overview":
        dashboard = MarketOverviewDashboard()
        dashboard.render_dashboard()
    
    elif selected_dashboard == "Technical Analysis":
        dashboard = TechnicalAnalysisDashboard()
        dashboard.render_dashboard()
    
    elif selected_dashboard == "Portfolio Management":
        dashboard = PortfolioManagementDashboard()
        dashboard.render_dashboard()

if __name__ == "__main__":
    main()
