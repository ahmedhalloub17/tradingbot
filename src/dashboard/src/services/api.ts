import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export interface BinanceConfig {
  api_key: string;
  api_secret: string;
  testnet: boolean;
}

export interface ApiResponse<T> {
  status: string;
  data: T;
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getBinanceConfig = async (): Promise<ApiResponse<{ config: BinanceConfig }>> => {
  const response = await api.get('/config/binance');
  return response.data;
};

export const updateBinanceConfig = async (config: BinanceConfig): Promise<ApiResponse<{ config: BinanceConfig }>> => {
  const response = await api.post('/config/binance', config);
  return response.data;
};

export const getTradingPairs = async (): Promise<ApiResponse<{ pairs: string[] }>> => {
  const response = await api.get('/trading-pairs');
  return response.data;
};

export const updateTradingPairs = async (pairs: { symbol: string; enabled: boolean }[]): Promise<ApiResponse<{ pairs: string[] }>> => {
  const response = await api.post('/trading-pairs', pairs);
  return response.data;
};

export const getActiveTrades = async (): Promise<ApiResponse<{ trades: Record<string, any> }>> => {
  const response = await api.get('/trades/active');
  return response.data;
};

export const getTradeHistory = async (): Promise<ApiResponse<{ history: any[] }>> => {
  const response = await api.get('/trades/history');
  return response.data;
};

export const getBalance = async (): Promise<ApiResponse<{ balance: number }>> => {
  const response = await api.get('/balance');
  return response.data;
};

export const startBot = async (): Promise<ApiResponse<{ message: string }>> => {
  const response = await api.post('/bot/start');
  return response.data;
};

export const stopBot = async (): Promise<ApiResponse<{ message: string }>> => {
  const response = await api.post('/bot/stop');
  return response.data;
};
