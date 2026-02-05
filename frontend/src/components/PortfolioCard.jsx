/**
 * Portfolio holding card component.
 */
import React from 'react';
import { Edit2, Trash2, TrendingUp, TrendingDown } from 'lucide-react';

export function PortfolioCard({ holding, onEdit, onDelete }) {
  const isPositive = holding.pnl >= 0;
  const displaySymbol = holding.symbol?.replace('USDT', '');

  return (
    <div className="card p-4 card-hover">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-lg font-bold
            ${isPositive ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'}`}>
            {displaySymbol?.slice(0, 2)}
          </div>
          <div>
            <h3 className="font-bold">{displaySymbol}</h3>
            <p className="text-sm text-gray-500">{holding.amount} units</p>
          </div>
        </div>

        <div className="flex items-center gap-1">
          <button
            onClick={() => onEdit(holding)}
            className="p-2 text-gray-400 hover:text-white hover:bg-crypto-card rounded-lg transition-all"
          >
            <Edit2 className="w-4 h-4" />
          </button>
          <button
            onClick={() => onDelete(holding)}
            className="p-2 text-gray-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-all"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-4">
        <div>
          <p className="text-xs text-gray-500">Current Value</p>
          <p className="text-lg font-bold font-mono">
            ${holding.current_value?.toLocaleString(undefined, { maximumFractionDigits: 2 })}
          </p>
        </div>
        <div className="text-right">
          <p className="text-xs text-gray-500">P&L</p>
          <div className={`flex items-center justify-end gap-1 ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
            {isPositive ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
            <span className="text-lg font-bold font-mono">
              {isPositive ? '+' : ''}{holding.pnl_percent?.toFixed(2)}%
            </span>
          </div>
          <p className={`text-sm font-mono ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
            {isPositive ? '+' : ''}${holding.pnl?.toLocaleString(undefined, { maximumFractionDigits: 2 })}
          </p>
        </div>
      </div>

      <div className="mt-3 pt-3 border-t border-crypto-border flex justify-between text-sm">
        <div>
          <span className="text-gray-500">Avg. Buy: </span>
          <span className="font-mono">
            ${holding.average_buy_price?.toLocaleString(undefined, { maximumFractionDigits: 2 }) || 'N/A'}
          </span>
        </div>
        <div>
          <span className="text-gray-500">Current: </span>
          <span className="font-mono">
            ${holding.current_price?.toLocaleString(undefined, { maximumFractionDigits: 2 })}
          </span>
        </div>
      </div>
    </div>
  );
}
