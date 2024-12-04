import React, { useState, useEffect } from 'react';
import { useQuery, useQueryClient } from 'react-query';
import {
  getBalance,
  getActiveTrades,
  startBot,
  stopBot
} from '../services/api';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { useToast } from '../components/ui/use-toast';

export default function Dashboard() {
  const [isRunning, setIsRunning] = useState(false);
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const { data: balanceData, isLoading: balanceLoading } = useQuery(
    'balance',
    async () => {
      const response = await getBalance();
      return response.data.balance;
    },
    { refetchInterval: 5000 }
  );

  const { data: tradesData, isLoading: tradesLoading } = useQuery(
    'active-trades',
    async () => {
      const response = await getActiveTrades();
      return response.data.trades;
    },
    { refetchInterval: 5000 }
  );

  const handleStartBot = async () => {
    try {
      const response = await startBot();
      setIsRunning(true);
      toast({
        title: "Success",
        description: response.data.message,
      });
      // Refetch data
      queryClient.invalidateQueries('balance');
      queryClient.invalidateQueries('active-trades');
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to start bot",
        variant: "destructive",
      });
    }
  };

  const handleStopBot = async () => {
    try {
      const response = await stopBot();
      setIsRunning(false);
      toast({
        title: "Success",
        description: response.data.message,
      });
      // Refetch data
      queryClient.invalidateQueries('balance');
      queryClient.invalidateQueries('active-trades');
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to stop bot",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="container mx-auto p-4">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Bot Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <span className={`text-lg ${isRunning ? 'text-green-500' : 'text-red-500'}`}>
                {isRunning ? 'Running' : 'Stopped'}
              </span>
              <Button
                onClick={isRunning ? handleStopBot : handleStartBot}
                className={`${isRunning ? 'bg-red-500 hover:bg-red-600 text-white' : 'bg-green-500 hover:bg-green-600 text-white'}`}
              >
                {isRunning ? 'Stop Bot' : 'Start Bot'}
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Balance</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {balanceLoading ? (
                <span>Loading...</span>
              ) : (
                <span>${balanceData?.toFixed(2) || '0.00'}</span>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Active Trades</CardTitle>
          </CardHeader>
          <CardContent>
            {tradesLoading ? (
              <div>Loading...</div>
            ) : (
              <div className="space-y-4">
                {Object.entries(tradesData || {}).map(([symbol, trade]: [string, any]) => (
                  <div key={symbol} className="flex justify-between items-center">
                    <span>{symbol}</span>
                    <span className={trade.pnl_percentage >= 0 ? 'text-green-500' : 'text-red-500'}>
                      {trade.pnl_percentage.toFixed(2)}%
                    </span>
                  </div>
                ))}
                {Object.keys(tradesData || {}).length === 0 && (
                  <div className="text-gray-500">No active trades</div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
