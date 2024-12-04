import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import logging
from datetime import datetime, timedelta
import json
import os
import traceback

from src.bot.core import TradingBot
from src.bot.config import Config

class TradingDashboard:
    def __init__(self, config_path=None):
        # Initialize trading bot and configuration
        self.config = Config(config_path).get_all()
        self.trading_bot = TradingBot(config_path)
        
        # Initialize Dash app
        self.app = dash.Dash(__name__, 
                              external_stylesheets=[dbc.themes.BOOTSTRAP],
                              meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}])
        
        # Setup logging
        self.log_file = 'logs/trading_bot.log'
        self.setup_logging()
        
        # Layout
        self.app.layout = self.create_layout()
        
        # Callbacks
        self.register_callbacks()

    def setup_logging(self):
        # Configure logging to write to file with a more detailed format
        logging.basicConfig(
            filename=self.log_file, 
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    def create_layout(self):
        return dbc.Container([
            # Latest Status Section
            html.Div(id='latest-status', className='mb-4'),
            
            # Header with gradient and modern styling
            html.Div([
                html.H1("Crypto Trading Bot Dashboard", 
                        className="text-center my-4 text-white", 
                        style={
                            'background': 'linear-gradient(to right, #6a11cb 0%, #2575fc 100%)',
                            'padding': '20px',
                            'borderRadius': '10px'
                        }
                )
            ]),
            
            # Global Performance Metrics with card-like design
            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Global PNL"),
                        dbc.CardBody(html.Div(id='global-pnl', className='text-center'))
                    ], className="shadow-sm"), 
                    width=4
                ),
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Total Balance"),
                        dbc.CardBody(html.Div(id='total-balance', className='text-center'))
                    ], className="shadow-sm"), 
                    width=4
                ),
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Open Positions"),
                        dbc.CardBody(html.Div(id='open-positions-count', className='text-center'))
                    ], className="shadow-sm"), 
                    width=4
                )
            ], className="mb-4"),
            
            # Detailed Sections with modern tabs
            dbc.Tabs([
                dbc.Tab(label="Open Positions", children=[
                    html.Div(id='open-positions-table', className='mt-3')
                ]),
                dbc.Tab(label="Trade Logs", children=[
                    dcc.Interval(id='interval-component', interval=5*1000, n_intervals=0),
                    html.Div(id='latest-status', className='mb-3'),
                    html.Div(id='log-output', className='mt-3')
                ]),
                dbc.Tab(label="Performance Charts", children=[
                    dcc.Graph(id='pnl-chart', className='mt-3'),
                    dcc.Graph(id='trade-volume-chart', className='mt-3')
                ])
            ])
        ], fluid=True, style={'backgroundColor': '#f4f6f9'})
        return dbc.Container([
            # Latest Status Section
            html.Div(id='latest-status', className='mb-4'),
            
            # Header with gradient and modern styling
            html.Div([
                html.H1("Crypto Trading Bot Dashboard", 
                        className="text-center my-4 text-white", 
                        style={
                            'background': 'linear-gradient(to right, #6a11cb 0%, #2575fc 100%)',
                            'padding': '20px',
                            'borderRadius': '10px'
                        }
                )
            ]),
            
            # Global Performance Metrics with card-like design
            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Global PNL"),
                        dbc.CardBody(html.Div(id='global-pnl', className='text-center'))
                    ], className="shadow-sm"), 
                    width=4
                ),
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Total Balance"),
                        dbc.CardBody(html.Div(id='total-balance', className='text-center'))
                    ], className="shadow-sm"), 
                    width=4
                ),
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Open Positions"),
                        dbc.CardBody(html.Div(id='open-positions-count', className='text-center'))
                    ], className="shadow-sm"), 
                    width=4
                )
            ], className="mb-4"),
            
            # Detailed Sections with modern tabs
            dbc.Tabs([
                dbc.Tab(label="Open Positions", children=[
                    html.Div(id='open-positions-table', className='mt-3')
                ]),
                dbc.Tab(label="Trade Logs", children=[
                    dcc.Interval(id='interval-component', interval=5*1000, n_intervals=0),
                    html.Div(id='latest-status', className='mb-3'),  # Add this line
                    html.Div(id='log-output', className='mt-3')
                ]),
                dbc.Tab(label="Performance Charts", children=[
                    dcc.Graph(id='pnl-chart', className='mt-3'),
                    dcc.Graph(id='trade-volume-chart', className='mt-3')
                ])
            ])
        ], fluid=True, style={'backgroundColor': '#f4f6f9'})
        return dbc.Container([
            # Header with gradient and modern styling
            html.Div([
                html.H1("Crypto Trading Bot Dashboard", 
                        className="text-center my-4 text-white", 
                        style={
                            'background': 'linear-gradient(to right, #6a11cb 0%, #2575fc 100%)',
                            'padding': '20px',
                            'borderRadius': '10px'
                        }
                )
            ]),
            
            # Global Performance Metrics with card-like design
            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Global PNL"),
                        dbc.CardBody(html.Div(id='global-pnl', className='text-center'))
                    ], className="shadow-sm"), 
                    width=4
                ),
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Total Balance"),
                        dbc.CardBody(html.Div(id='total-balance', className='text-center'))
                    ], className="shadow-sm"), 
                    width=4
                ),
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Open Positions"),
                        dbc.CardBody(html.Div(id='open-positions-count', className='text-center'))
                    ], className="shadow-sm"), 
                    width=4
                )
            ], className="mb-4"),
            
            # Detailed Sections with modern tabs
            dbc.Tabs([
                dbc.Tab(label="Open Positions", children=[
                    html.Div(id='open-positions-table', className='mt-3')
                ]),
                dbc.Tab(label="Trade Logs", children=[
                    dcc.Interval(id='interval-component', interval=5*1000, n_intervals=0),
                    html.Div(id='log-output', className='mt-3')
                ]),
                dbc.Tab(label="Performance Charts", children=[
                    dcc.Graph(id='pnl-chart', className='mt-3'),
                    dcc.Graph(id='trade-volume-chart', className='mt-3')
                ])
            ])
        ], fluid=True, style={'backgroundColor': '#f4f6f9'})
    def register_callbacks(self):
        @self.app.callback(
            [Output('global-pnl', 'children'),
             Output('total-balance', 'children'),
             Output('open-positions-count', 'children')],
            [Input('interval-component', 'n_intervals')]
        )
        def update_global_metrics(n):
            # Fetch global metrics
            global_pnl = self.calculate_global_pnl()
            total_balance = self.fetch_total_balance()
            open_positions = len(self.trading_bot.active_trades)
            
            return [
                html.H4(f"Global PNL: ${global_pnl:.2f}", className="text-success"),
                html.H4(f"Total Balance: ${total_balance:.2f}", className="text-info"),
                html.H4(f"Open Positions: {open_positions}", className="text-warning")
            ]
        
        @self.app.callback(
            Output('open-positions-table', 'children'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_open_positions(n):
            # Create table of open positions
            if not self.trading_bot.active_trades:
                return html.P("No open positions")
            
            positions_df = pd.DataFrame.from_dict(
                self.trading_bot.active_trades, 
                orient='index'
            ).reset_index()
            positions_df.columns = ['Symbol', 'Entry Price', 'Position Size', 'Timestamp']
            
            return dash_table.DataTable(
                id='positions-table',
                columns=[{"name": i, "id": i} for i in positions_df.columns],
                data=positions_df.to_dict('records'),
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left'}
            )
        
        
        @self.app.callback(
            [Output('log-output', 'children'),
            Output('latest-status', 'children')],
            [Input('interval-component', 'n_intervals')]
        )
        def update_logs(n):
            try:
                with open(self.log_file, 'r') as f:
                    logs = f.readlines()[-200:]  # Increased to 200 for more context
                
                # Parse logs into a structured format
                parsed_logs = []
                for log in logs:
                    try:
                        # Split log into components
                        # Adjust this parsing to match your actual log format
                        parts = log.strip().split('|')
                        
                        if len(parts) >= 3:
                            timestamp = parts[0].strip()
                            level = parts[1].strip()
                            message = '|'.join(parts[2:]).strip()
                            
                            # Custom timestamp parsing
                            try:
                                # Try parsing the timestamp
                                parsed_timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
                            except ValueError:
                                # Fallback parsing
                                parsed_timestamp = datetime.now()
                        
                            parsed_log = {
                                'timestamp': parsed_timestamp,
                                'level': level,
                                'message': message,
                                'type': 'INFO'  # Default type
                            }
                        
                            # Classify log type
                            if 'ERROR' in level.upper():
                                parsed_log['type'] = 'ERROR'
                            elif 'WARNING' in level.upper():
                                parsed_log['type'] = 'WARNING'
                            elif 'TRADE' in message.upper():
                                parsed_log['type'] = 'TRADE'
                        
                            parsed_logs.append(parsed_log)
                        else:
                            # Fallback for malformed logs
                            parsed_logs.append({
                                'timestamp': datetime.now(),
                                'level': 'UNKNOWN',
                                'message': log.strip(),
                                'type': 'RAW'
                            })
                    
                    except Exception as parse_error:
                        # Catch any parsing errors
                        parsed_logs.append({
                            'timestamp': datetime.now(),
                            'level': 'PARSE_ERROR',
                            'message': f"Failed to parse log: {log.strip()} - {str(parse_error)}",
                            'type': 'ERROR'
                        })
                
                # Convert to DataFrame and sort by timestamp (newest first)
                df = pd.DataFrame(parsed_logs)
                df = df.sort_values('timestamp', ascending=False).reset_index(drop=True)
                
                # Color mapping for badge
                color_map = {
                    'TRADE': 'success', 
                    'ERROR': 'danger', 
                    'WARNING': 'warning'
                }
                
                # Prepare latest status
                latest_status = html.Div([
                    html.H4("Latest Bot Status", className="mb-3"),
                    html.Div([
                        html.Span("Last Updated: ", className="font-weight-bold"),
                        html.Span(df['timestamp'].iloc[0].strftime('%Y-%m-%d %H:%M:%S'), className="text-muted"),
                        html.Span(" | ", className="mx-2"),
                        html.Span("Latest Event: ", className="font-weight-bold"),
                        html.Span(
                            df['type'].iloc[0], 
                            className=f"badge badge-{color_map.get(df['type'].iloc[0], 'info')}"
                        )
                    ], className="d-flex justify-content-between align-items-center")
                ], className="alert alert-light")
                
                # Create DataTable with advanced styling
                log_table = dash_table.DataTable(
                    id='log-table',
                    columns=[
                        {"name": col.replace('_', ' ').title(), "id": col} for col in df.columns
                    ],
                    data=df.to_dict('records'),
                    style_table={
                        'overflowX': 'auto',
                        'maxHeight': '500px',
                        'overflowY': 'scroll'
                    },
                    style_cell={
                        'textAlign': 'left',
                        'padding': '5px',
                        'whiteSpace': 'normal',
                        'height': 'auto',
                        'maxWidth': '200px',
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis'
                    },
                    style_header={
                        'backgroundColor': 'rgb(230, 230, 230)',
                        'fontWeight': 'bold',
                        'textTransform': 'uppercase'
                    },
                    style_data_conditional=[
                        # Color coding for log levels
                        {
                            'if': {'filter_query': '{type} = "ERROR"'},
                            'backgroundColor': 'rgb(255, 220, 220)'
                        },
                        {
                            'if': {'filter_query': '{type} = "WARNING"'},
                            'backgroundColor': 'rgb(255, 245, 220)'
                        },
                        {
                            'if': {'filter_query': '{type} = "TRADE"'},
                            'backgroundColor': 'rgb(220, 255, 220)'
                        }
                    ],
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    page_size=20,
                    tooltip_delay=0,
                    tooltip_duration=None
                )
                
                return [log_table, latest_status]
            
            except Exception as e:
                error_display = html.Div([
                    html.H4("Error Loading Logs"),
                    html.P(str(e)),
                    html.Pre(traceback.format_exc())
                ])
                return [error_display, html.Div("Unable to load status")]
            try:
                with open(self.log_file, 'r') as f:
                    logs = f.readlines()[-200:]  # Increased to 200 for more context
                
                # Parse logs into a structured format
                parsed_logs = []
                for log in logs:
                    try:
                        # Split log into components
                        timestamp, rest = log.split(' - ', 1)
                        level, message = rest.split(':', 1)
                        
                        # Classify log type and extract details
                        log_type = 'INFO'
                        trade_details = {}
                        
                        if 'Trade Execution' in message:
                            log_type = 'TRADE'
                            # Parse trade execution log
                            parts = message.strip().split('|')
                            for part in parts:
                                try:
                                    key, value = part.split(':', 1)
                                    trade_details[key.strip()] = value.strip()
                                except ValueError:
                                    pass
                        elif 'ERROR' in level:
                            log_type = 'ERROR'
                        elif 'WARNING' in level:
                            log_type = 'WARNING'
                        
                        parsed_log = {
                            'timestamp': timestamp.strip(),
                            'level': level.strip(),
                            'message': message.strip(),
                            'type': log_type,
                            **trade_details
                        }
                        parsed_logs.append(parsed_log)
                    except Exception:
                        # Fallback for malformed logs
                        parsed_logs.append({
                            'timestamp': 'Unknown',
                            'level': 'UNKNOWN',
                            'message': log.strip(),
                            'type': 'RAW'
                        })
                
                # Convert to DataFrame and sort by timestamp (newest first)
                df = pd.DataFrame(parsed_logs)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp', ascending=False).reset_index(drop=True)
                
                # Prepare latest status
                latest_status = html.Div([
                html.H4("Latest Bot Status", className="mb-3"),
                html.Div([
                    html.Span("Last Updated: ", className="font-weight-bold"),
                    html.Span(df['timestamp'].iloc[0].strftime('%Y-%m-%d %H:%M:%S'), className="text-muted"),
                    html.Span(" | ", className="mx-2"),
                    html.Span("Latest Event: ", className="font-weight-bold"),
                    html.Span(
                        df['type'].iloc[0], 
                        className=f"badge badge-{
                            'success' if df['type'].iloc[0] == 'TRADE' else 
                            'danger' if df['type'].iloc[0] == 'ERROR' else 
                            'warning' if df['type'].iloc[0] == 'WARNING' else 
                            'info'
                        }"
                    )
                ], className="d-flex justify-content-between align-items-center")
            ], className="alert alert-light")
                
                # Create DataTable with advanced styling
                log_table = dash_table.DataTable(
                    id='log-table',
                    columns=[
                        {"name": col.replace('_', ' ').title(), "id": col} for col in df.columns
                    ],
                    data=df.to_dict('records'),
                    style_table={
                        'overflowX': 'auto',
                        'maxHeight': '500px',
                        'overflowY': 'scroll'
                    },
                    style_cell={
                        'textAlign': 'left',
                        'padding': '5px',
                        'whiteSpace': 'normal',
                        'height': 'auto',
                        'maxWidth': '200px',
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis'
                    },
                    style_header={
                        'backgroundColor': 'rgb(230, 230, 230)',
                        'fontWeight': 'bold',
                        'textTransform': 'uppercase'
                    },
                    style_data_conditional=[
                        # Color coding for log levels
                        {
                            'if': {'filter_query': '{type} = "ERROR"'},
                            'backgroundColor': 'rgb(255, 220, 220)'
                        },
                        {
                            'if': {'filter_query': '{type} = "WARNING"'},
                            'backgroundColor': 'rgb(255, 245, 220)'
                        },
                        {
                            'if': {'filter_query': '{type} = "TRADE"'},
                            'backgroundColor': 'rgb(220, 255, 220)'
                        }
                    ],
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    page_size=20,
                    tooltip_delay=0,
                    tooltip_duration=None
                )
                
                return [log_table, latest_status]
            
            except Exception as e:
                error_display = html.Div([
                    html.H4("Error Loading Logs"),
                    html.P(str(e)),
                    html.Pre(traceback.format_exc())
                ])
                return [error_display, html.Div("Unable to load status")]
            try:
                with open(self.log_file, 'r') as f:
                    logs = f.readlines()[-100:]  # Increased to 100 for more context
                
                # Parse logs into a structured format
                parsed_logs = []
                for log in logs:
                    try:
                        # Split log into components
                        timestamp, rest = log.split(' - ', 1)
                        level, message = rest.split(':', 1)
                        
                        # Classify log type
                        if 'Trade Execution' in message:
                            log_type = 'TRADE'
                        elif 'ERROR' in level:
                            log_type = 'ERROR'
                        elif 'WARNING' in level:
                            log_type = 'WARNING'
                        else:
                            log_type = 'INFO'
                        
                        # Extract additional details for trades
                        trade_details = {}
                        if log_type == 'TRADE':
                            # Parse trade execution log
                            parts = message.strip().split('|')
                            for part in parts:
                                key, value = part.split(':', 1)
                                trade_details[key.strip()] = value.strip()
                        
                        parsed_logs.append({
                            'timestamp': timestamp.strip(),
                            'level': level.strip(),
                            'message': message.strip(),
                            'type': log_type,
                            **trade_details  # Unpack trade details if available
                        })
                    except Exception:
                        # Fallback for malformed logs
                        parsed_logs.append({
                            'timestamp': 'Unknown',
                            'level': 'UNKNOWN',
                            'message': log.strip(),
                            'type': 'RAW'
                        })
                
                # Create DataFrame for more flexible display
                df = pd.DataFrame(parsed_logs)
                
                # Create color mapping for log levels
                level_colors = {
                    'ERROR': 'danger',
                    'WARNING': 'warning',
                    'INFO': 'info',
                    'TRADE': 'success',
                    'UNKNOWN': 'secondary',
                    'RAW': 'light'
                }
                
                # Create DataTable with advanced styling
                return dash_table.DataTable(
                    id='log-table',
                    columns=[
                        {"name": col, "id": col} for col in df.columns
                    ],
                    data=df.to_dict('records'),
                    style_table={
                        'overflowX': 'auto',
                        'maxHeight': '500px',
                        'overflowY': 'scroll'
                    },
                    style_cell={
                        'textAlign': 'left',
                        'padding': '5px',
                        'whiteSpace': 'normal',
                        'height': 'auto'
                    },
                    style_header={
                        'backgroundColor': 'rgb(230, 230, 230)',
                        'fontWeight': 'bold'
                    },
                    style_data_conditional=[
                        # Color coding for log levels
                        {
                            'if': {'filter_query': '{type} = "ERROR"'},
                            'backgroundColor': 'rgb(255, 220, 220)'
                        },
                        {
                            'if': {'filter_query': '{type} = "WARNING"'},
                            'backgroundColor': 'rgb(255, 245, 220)'
                        },
                        {
                            'if': {'filter_query': '{type} = "TRADE"'},
                            'backgroundColor': 'rgb(220, 255, 220)'
                        }
                    ],
                    filter_action="native",  # Enable filtering
                    sort_action="native",    # Enable sorting
                    sort_mode="multi",       # Allow multi-column sorting
                    page_size=20,            # Number of rows per page
                )
            except Exception as e:
                return html.Div([
                    html.H4("Error Loading Logs"),
                    html.P(str(e))
                ])
    def calculate_global_pnl(self):
        # Implement PNL calculation logic
        total_pnl = sum(
            (self.trading_bot.exchange.fetch_ticker(symbol)['last'] - trade['entry_price']) * trade['position_size']
            for symbol, trade in self.trading_bot.active_trades.items()
        )
        return total_pnl

    def fetch_total_balance(self):
        # Fetch total balance across all exchanges
        try:
            balance = self.trading_bot.exchange.fetch_balance()
            return balance['total']['USDT']  # Assuming USDT as base currency
        except Exception as e:
            logging.error(f"Balance fetch error: {e}")
            return 0.0

    def run(self, debug=True, port=8050):
        self.app.run_server(debug=debug, port=port)

if __name__ == '__main__':
    dashboard = TradingDashboard('config/config.yaml')
    dashboard.run()