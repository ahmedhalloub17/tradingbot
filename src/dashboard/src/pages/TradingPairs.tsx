import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { getTradingPairs, updateTradingPairs } from '../services/api';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Switch } from '../components/ui/switch';
import { useToast } from '../components/ui/use-toast';

interface TradingPair {
  symbol: string;
  enabled: boolean;
}

export const TradingPairs: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const { data: pairsData, isLoading } = useQuery('trading-pairs', async () => {
    const response = await getTradingPairs();
    return response.data.pairs.map(symbol => ({ symbol, enabled: false }));
  });

  const updatePairsMutation = useMutation(updateTradingPairs, {
    onSuccess: (response) => {
      toast({
        title: 'Success',
        description: 'Trading pairs updated successfully',
      });
      queryClient.invalidateQueries('trading-pairs');
    },
    onError: (error) => {
      toast({
        title: 'Error',
        description: 'Failed to update trading pairs',
        variant: 'destructive',
      });
    }
  });

  const togglePair = (symbol: string, currentEnabled: boolean) => {
    if (!pairsData) return;

    const updatedPairs = pairsData.map((pair) =>
      pair.symbol === symbol ? { ...pair, enabled: !currentEnabled } : pair
    );

    updatePairsMutation.mutate(
      updatedPairs.filter(pair => pair.enabled).map(pair => ({
        symbol: pair.symbol,
        enabled: true
      }))
    );
  };

  const filteredPairs = pairsData?.filter((pair) =>
    pair.symbol.toLowerCase().includes(searchTerm.toLowerCase())
  ) ?? [];

  if (isLoading) {
    return <div>Loading trading pairs...</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <Card>
        <CardHeader>
          <CardTitle>Trading Pairs</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <Input
              type="text"
              placeholder="Search trading pairs..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Symbol
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredPairs.map((pair) => (
                  <tr key={pair.symbol}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {pair.symbol}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <Switch
                        checked={pair.enabled}
                        onCheckedChange={() => togglePair(pair.symbol, pair.enabled)}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
