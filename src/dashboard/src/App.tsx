import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import Dashboard from './pages/Dashboard';
import Settings from './pages/Settings';
import { TradingPairs } from './pages/TradingPairs';
import { Toaster } from './components/ui/toaster';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gray-100">
          <nav className="bg-white shadow-sm">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between h-16">
                <div className="flex">
                  <div className="flex-shrink-0 flex items-center">
                    <h1 className="text-xl font-bold">Trading Bot</h1>
                  </div>
                  <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                    <Link to="/" className="nav-link">Dashboard</Link>
                    <Link to="/settings" className="nav-link">Settings</Link>
                    <Link to="/trading-pairs" className="nav-link">Trading Pairs</Link>
                  </div>
                </div>
              </div>
            </div>
          </nav>

          <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/trading-pairs" element={<TradingPairs />} />
            </Routes>
          </main>
        </div>
      </Router>
      <Toaster />
    </QueryClientProvider>
  );
}

export default App;
