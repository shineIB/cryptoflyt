/**
 * Price chart component using Recharts.
 */
import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
} from 'recharts';
import { pricesAPI } from '../services/api';

const periods = [
  { label: '1H', value: '1h' },
  { label: '24H', value: '24h' },
  { label: '7D', value: '7d' },
  { label: '30D', value: '30d' },
];

export function PriceChart({ symbol, currentPrice }) {
  const [period, setPeriod] = useState('24h');
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      setLoading(true);
      try {
        const response = await pricesAPI.getHistory(symbol, period);
        setData(response.data.data || []);
      } catch (error) {
        console.error('Failed to fetch price history:', error);
        setData([]);
      } finally {
        setLoading(false);
      }
    };

    if (symbol) {
      fetchHistory();
    }
  }, [symbol, period]);

  // Calculate if price went up or down
  const isPositive = data.length > 1 && data[data.length - 1]?.price > data[0]?.price;

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip">
          <p className="text-lg font-bold font-mono">
            ${payload[0].value?.toLocaleString(undefined, { maximumFractionDigits: 2 })}
          </p>
          <p className="text-xs text-gray-500">
            {new Date(payload[0].payload.timestamp).toLocaleString()}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="card p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="font-semibold text-lg">{symbol?.replace('USDT', '')}/USDT</h3>
          <p className="text-2xl font-bold font-mono">
            ${currentPrice?.toLocaleString(undefined, { minimumFractionDigits: 2 })}
          </p>
        </div>
        <div className="flex gap-1 bg-crypto-dark rounded-lg p-1">
          {periods.map((p) => (
            <button
              key={p.value}
              onClick={() => setPeriod(p.value)}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all
                ${period === p.value 
                  ? 'bg-crypto-accent text-white' 
                  : 'text-gray-400 hover:text-white'
                }`}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      <div className="h-64">
        {loading ? (
          <div className="h-full flex items-center justify-center">
            <div className="w-8 h-8 border-2 border-crypto-accent border-t-transparent rounded-full animate-spin" />
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data}>
              <defs>
                <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                  <stop 
                    offset="5%" 
                    stopColor={isPositive ? '#22c55e' : '#ef4444'} 
                    stopOpacity={0.3}
                  />
                  <stop 
                    offset="95%" 
                    stopColor={isPositive ? '#22c55e' : '#ef4444'} 
                    stopOpacity={0}
                  />
                </linearGradient>
              </defs>
              <XAxis 
                dataKey="timestamp" 
                axisLine={false}
                tickLine={false}
                tick={false}
              />
              <YAxis 
                domain={['auto', 'auto']}
                axisLine={false}
                tickLine={false}
                tick={{ fill: '#6b7280', fontSize: 12 }}
                tickFormatter={(value) => `$${value.toLocaleString()}`}
                width={80}
              />
              <Tooltip content={<CustomTooltip />} />
              <Area
                type="monotone"
                dataKey="price"
                stroke={isPositive ? '#22c55e' : '#ef4444'}
                strokeWidth={2}
                fill="url(#colorPrice)"
              />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
