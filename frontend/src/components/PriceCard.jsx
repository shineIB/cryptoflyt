/**
 * Price card component showing real-time crypto price.
 */
import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

const symbolIcons = {
  BTCUSDT: '₿',
  ETHUSDT: 'Ξ',
  SOLUSDT: '◎',
  XRPUSDT: '✕',
  DOGEUSDT: 'Ð',
};

const symbolNames = {
  BTCUSDT: 'Bitcoin',
  ETHUSDT: 'Ethereum',
  SOLUSDT: 'Solana',
  XRPUSDT: 'XRP',
  DOGEUSDT: 'Dogecoin',
};

export function PriceCard({ symbol, price, change24h, high24h, low24h, onClick }) {
  const isPositive = change24h >= 0;
  const displaySymbol = symbol?.replace('USDT', '');
  
  return (
    <div 
      onClick={onClick}
      className="card card-hover p-5 cursor-pointer animate-fade-in"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-xl
            ${isPositive ? 'bg-green-500/10' : 'bg-red-500/10'}`}>
            <span>{symbolIcons[symbol] || '○'}</span>
          </div>
          <div>
            <h3 className="font-bold text-lg">{displaySymbol}</h3>
            <p className="text-sm text-gray-500">{symbolNames[symbol] || symbol}</p>
          </div>
        </div>
        <div className={`flex items-center gap-1 px-2 py-1 rounded-lg text-sm font-medium
          ${isPositive ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'}`}>
          {isPositive ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
          <span>{isPositive ? '+' : ''}{change24h?.toFixed(2)}%</span>
        </div>
      </div>
      
      <div className="mb-4">
        <p className="text-3xl font-bold font-mono">
          ${price?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </p>
      </div>
      
      <div className="flex items-center justify-between text-sm">
        <div>
          <p className="text-gray-500">24h High</p>
          <p className="text-green-400 font-mono">
            ${high24h?.toLocaleString(undefined, { maximumFractionDigits: 2 })}
          </p>
        </div>
        <div className="text-right">
          <p className="text-gray-500">24h Low</p>
          <p className="text-red-400 font-mono">
            ${low24h?.toLocaleString(undefined, { maximumFractionDigits: 2 })}
          </p>
        </div>
      </div>
    </div>
  );
}
