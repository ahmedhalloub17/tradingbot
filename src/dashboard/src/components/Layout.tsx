import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  HomeIcon,
  ChartBarIcon,
  CogIcon,
  CurrencyDollarIcon,
  SignalIcon,
} from '@heroicons/react/24/outline';

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Active Trades', href: '/trades', icon: ChartBarIcon },
  { name: 'Trading Pairs', href: '/pairs', icon: CurrencyDollarIcon },
  { name: 'Signals', href: '/signals', icon: SignalIcon },
  { name: 'Settings', href: '/settings', icon: CogIcon },
];

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-primary-800">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-white text-xl font-bold">Trading Bot</h1>
              </div>
              <div className="hidden md:block">
                <div className="ml-10 flex items-baseline space-x-4">
                  {navigation.map((item) => {
                    const isActive = location.pathname === item.href;
                    return (
                      <Link
                        key={item.name}
                        to={item.href}
                        className={`${
                          isActive
                            ? 'bg-primary-900 text-white'
                            : 'text-primary-300 hover:bg-primary-700 hover:text-white'
                        } px-3 py-2 rounded-md text-sm font-medium flex items-center`}
                      >
                        <item.icon className="h-5 w-5 mr-2" />
                        {item.name}
                      </Link>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        </div>
      </nav>

      <main className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6">
        {children}
      </main>
    </div>
  );
};
