/**
 * Portfolio page - manage crypto holdings.
 */
import React, { useState, useEffect } from 'react';
import { Wallet, Plus, TrendingUp, TrendingDown, X } from 'lucide-react';
import { PortfolioCard } from '../components';
import { usePortfolioStore } from '../store';
import { portfolioAPI } from '../services/api';

const SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'XRPUSDT', 'DOGEUSDT'];

export function Portfolio() {
  const { holdings, totalValue, totalPnl, totalPnlPercent, setPortfolio, setLoading } = usePortfolioStore();
  const [showForm, setShowForm] = useState(false);
  const [editHolding, setEditHolding] = useState(null);
  const [formData, setFormData] = useState({
    symbol: 'BTCUSDT',
    amount: '',
    average_buy_price: '',
  });
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // Fetch portfolio on mount
  useEffect(() => {
    const fetchPortfolio = async () => {
      setLoading(true);
      try {
        const response = await portfolioAPI.get();
        setPortfolio(response.data);
      } catch (error) {
        console.error('Failed to fetch portfolio:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchPortfolio();
  }, [setPortfolio, setLoading]);

  const handleEdit = (holding) => {
    setEditHolding(holding);
    setFormData({
      symbol: holding.symbol,
      amount: holding.amount.toString(),
      average_buy_price: holding.average_buy_price?.toString() || '',
    });
    setShowForm(true);
  };

  const handleDelete = async (holding) => {
    if (!confirm(`Remove ${holding.symbol.replace('USDT', '')} from portfolio?`)) return;
    
    try {
      await portfolioAPI.deleteHolding(holding.id);
      const response = await portfolioAPI.get();
      setPortfolio(response.data);
    } catch (error) {
      console.error('Failed to delete holding:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);

    try {
      const data = {
        symbol: formData.symbol,
        amount: parseFloat(formData.amount),
        average_buy_price: formData.average_buy_price ? parseFloat(formData.average_buy_price) : null,
      };

      if (editHolding) {
        await portfolioAPI.updateHolding(editHolding.id, data);
      } else {
        await portfolioAPI.addHolding(data);
      }

      // Refresh portfolio
      const response = await portfolioAPI.get();
      setPortfolio(response.data);
      
      setShowForm(false);
      setEditHolding(null);
      setFormData({ symbol: 'BTCUSDT', amount: '', average_buy_price: '' });
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save holding');
    } finally {
      setSubmitting(false);
    }
  };

  const closeForm = () => {
    setShowForm(false);
    setEditHolding(null);
    setFormData({ symbol: 'BTCUSDT', amount: '', average_buy_price: '' });
    setError('');
  };

  const isPositive = totalPnlPercent >= 0;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Portfolio</h1>
          <p className="text-gray-400">Track your crypto holdings</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Add Holding
        </button>
      </div>

      {/* Portfolio summary */}
      <div className="card p-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-crypto-accent to-purple-600 flex items-center justify-center">
              <Wallet className="w-7 h-7 text-white" />
            </div>
            <div>
              <p className="text-sm text-gray-400">Total Portfolio Value</p>
              <p className="text-4xl font-bold font-mono">
                ${totalValue.toLocaleString(undefined, { minimumFractionDigits: 2 })}
              </p>
            </div>
          </div>
          
          {totalValue > 0 && (
            <div className={`flex items-center gap-3 px-4 py-3 rounded-xl
              ${isPositive ? 'bg-green-500/10' : 'bg-red-500/10'}`}>
              {isPositive ? (
                <TrendingUp className="w-6 h-6 text-green-400" />
              ) : (
                <TrendingDown className="w-6 h-6 text-red-400" />
              )}
              <div>
                <p className={`text-2xl font-bold ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
                  {isPositive ? '+' : ''}{totalPnlPercent.toFixed(2)}%
                </p>
                <p className={`text-sm ${isPositive ? 'text-green-400/80' : 'text-red-400/80'}`}>
                  {isPositive ? '+' : ''}${totalPnl.toLocaleString(undefined, { maximumFractionDigits: 2 })}
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Holdings */}
      {holdings.length === 0 ? (
        <div className="card p-12 text-center">
          <Wallet className="w-12 h-12 text-gray-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-400 mb-2">No holdings yet</h3>
          <p className="text-sm text-gray-500 mb-4">Add your crypto holdings to track your portfolio.</p>
          <button onClick={() => setShowForm(true)} className="btn-primary">
            Add Your First Holding
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {holdings.map((holding) => (
            <PortfolioCard
              key={holding.id}
              holding={holding}
              onEdit={handleEdit}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}

      {/* Add/Edit Form Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="card w-full max-w-md animate-slide-up">
            <div className="flex items-center justify-between p-4 border-b border-crypto-border">
              <h2 className="font-semibold">
                {editHolding ? 'Edit Holding' : 'Add Holding'}
              </h2>
              <button onClick={closeForm} className="text-gray-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-4 space-y-4">
              {error && (
                <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 text-red-400 text-sm">
                  {error}
                </div>
              )}

              <div>
                <label className="block text-sm text-gray-400 mb-2">Symbol</label>
                <select
                  value={formData.symbol}
                  onChange={(e) => setFormData({ ...formData, symbol: e.target.value })}
                  className="input"
                  disabled={!!editHolding}
                >
                  {SYMBOLS.map((s) => (
                    <option key={s} value={s}>{s.replace('USDT', '/USDT')}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-2">Amount</label>
                <input
                  type="number"
                  step="any"
                  value={formData.amount}
                  onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                  placeholder="e.g., 0.5"
                  className="input font-mono"
                  required
                />
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-2">
                  Average Buy Price (optional)
                </label>
                <input
                  type="number"
                  step="any"
                  value={formData.average_buy_price}
                  onChange={(e) => setFormData({ ...formData, average_buy_price: e.target.value })}
                  placeholder="e.g., 45000"
                  className="input font-mono"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Used to calculate profit/loss
                </p>
              </div>

              <button
                type="submit"
                disabled={submitting}
                className="w-full btn-primary py-3 disabled:opacity-50"
              >
                {submitting ? 'Saving...' : (editHolding ? 'Update Holding' : 'Add Holding')}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
