import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { getBinanceConfig, updateBinanceConfig, BinanceConfig } from '../services/api';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Switch } from '../components/ui/switch';
import { useToast } from '../components/ui/use-toast';

export default function Settings() {
  const [formData, setFormData] = useState<BinanceConfig>({
    api_key: '',
    api_secret: '',
    testnet: false,
  });
  const [isFormDirty, setIsFormDirty] = useState(false);
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const { data: configData, isLoading } = useQuery('binance-config', async () => {
    const response = await getBinanceConfig();
    return response.data.config;
  });

  const updateConfigMutation = useMutation(updateBinanceConfig, {
    onSuccess: (response) => {
      toast({
        title: 'Success',
        description: 'Configuration updated successfully',
      });
      queryClient.invalidateQueries('binance-config');
      setIsFormDirty(false);
    },
    onError: (error) => {
      toast({
        title: 'Error',
        description: 'Failed to update configuration',
        variant: 'destructive',
      });
    },
  });

  useEffect(() => {
    if (configData) {
      setFormData(configData);
    }
  }, [configData]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value
    }));
    setIsFormDirty(true);
  };

  const handleTestnetToggle = (checked: boolean) => {
    setFormData(prev => ({
      ...prev,
      testnet: checked
    }));
    setIsFormDirty(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    updateConfigMutation.mutate(formData);
  };

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <Card>
        <CardHeader>
          <CardTitle>Binance API Configuration</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="api_key">API Key</Label>
              <Input
                id="api_key"
                name="api_key"
                type="password"
                value={formData.api_key}
                onChange={handleInputChange}
                placeholder="Enter your Binance API key"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="api_secret">API Secret</Label>
              <Input
                id="api_secret"
                name="api_secret"
                type="password"
                value={formData.api_secret}
                onChange={handleInputChange}
                placeholder="Enter your Binance API secret"
              />
            </div>

            <div className="flex items-center space-x-2">
              <Switch
                id="testnet"
                checked={formData.testnet}
                onCheckedChange={handleTestnetToggle}
              />
              <Label htmlFor="testnet">Use Testnet</Label>
            </div>

            <Button
              type="submit"
              disabled={!isFormDirty || updateConfigMutation.isLoading}
            >
              {updateConfigMutation.isLoading ? 'Saving...' : 'Save Changes'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
