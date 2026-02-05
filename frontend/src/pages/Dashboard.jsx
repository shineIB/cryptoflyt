/**
 * Dashboard page - main overview of prices and portfolio.
 */
import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Wallet } from 'lucide-react';
import { PriceCard, PriceChart, AIAnalysis } from '../components';
import { usePriceStore, usePortfolioStore } from '../store';
import { portfolioAPI } from '../services/api';

const SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'XRPUSDT', 'DOGEUSDT'];

export function Dashboard() {
  const prices = usePriceStore((s) => s.prices);
  const { totalValue, totalPnl, totalPnlPercent, setPortfolio } = usePortfolioStore();
  const [selectedSymbol, setSelectedSymbol] = useState('BTCUSDT');

  // Fetch portfolio on mount
  useEffect(() => {
    const fetchPortfolio = async () => {
      try {
        const response = await portfolioAPI.get();
        setPortfolio(response.data);
      } catch (error) {
        console.error('Failed to fetch portfolio:', error);
      }
    };
    fetchPortfolio();
  }, [setPortfolio]);

  const isPositive = totalPnlPercent >= 0;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-gray-400">Real-time crypto prices and portfolio overview</p>
      </div>

      {/* Portfolio summary */}
      <div className="card p-6">
        <div className="flex items-center gap-4 mb-4">
          <div className="w-12 h-12 rounded-xl bg-crypto-accent/20 flex items-center justify-center">
            <Wallet className="w-6 h-6 text-crypto-accent" />
          </div>
          <div>
            <p className="text-sm text-gray-400">Portfolio Value</p>
            <p className="text-3xl font-bold font-mono">
              ${totalValue.toLocaleString(undefined, { minimumFractionDigits: 2 })}
            </p>
          </div>
        </div>
        
        {totalValue > 0 && (
          <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg
            ${isPositive ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'}`}>
            {isPositive ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
            <span className="font-medium">
              {isPositive ? '+' : ''}{totalPnlPercent.toFixed(2)}%
            </span>
            <span className="text-sm opacity-80">
              ({isPositive ? '+' : ''}${totalPnl.toLocaleString(undefined, { maximumFractionDigits: 2 })})
            </span>
          </div>
        )}
      </div>

      {/* Price cards grid */}
      <div>
        <h2 className="text-lg font-semibold mb-4">Live Prices</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
          {SYMBOLS.map((symbol) => {
            const priceData = prices[symbol] || {};
            return (
              <PriceCard
                key={symbol}
                symbol={symbol}
                price={priceData.price}
                change24h={priceData.change_24h_percent}
                high24h={priceData.high_24h}
                low24h={priceData.low_24h}
                onClick={() => setSelectedSymbol(symbol)}
              />
            );
          })}
        </div>
      </div>

      {/* Chart and AI Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <PriceChart 
          symbol={selectedSymbol} 
          currentPrice={prices[selectedSymbol]?.price}
        />
        <AIAnalysis />
      </div>
    </div>
  );
}
