/**
 * Alert creation/edit form component.
 */
import React, { useState } from 'react';
import { X, Bell, TrendingUp, TrendingDown } from 'lucide-react';
import { alertsAPI } from '../services/api';
import { useAlertStore, usePriceStore } from '../store';

const SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'XRPUSDT', 'DOGEUSDT'];

export function AlertForm({ onClose, editAlert = null }) {
  const prices = usePriceStore((s) => s.prices);
  const { addAlert, updateAlert } = useAlertStore();
  
  const [formData, setFormData] = useState({
    symbol: editAlert?.symbol || 'BTCUSDT',
    target_price: editAlert?.target_price || '',
    condition: editAlert?.condition || 'above',
    note: editAlert?.note || '',
    notify_telegram: editAlert?.notify_telegram ?? true,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const currentPrice = prices[formData.symbol]?.price;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = {
        ...formData,
        target_price: parseFloat(formData.target_price),
      };

      if (editAlert) {
        const response = await alertsAPI.update(editAlert.id, data);
        updateAlert(editAlert.id, response.data);
      } else {
        const response = await alertsAPI.create(data);
        addAlert(response.data);
      }
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save alert');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="card w-full max-w-md animate-slide-up">
        <div className="flex items-center justify-between p-4 border-b border-crypto-border">
          <div className="flex items-center gap-2">
            <Bell className="w-5 h-5 text-crypto-accent" />
            <h2 className="font-semibold">{editAlert ? 'Edit Alert' : 'Create Alert'}</h2>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          {error && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 text-red-400 text-sm">
              {error}
            </div>
          )}

          {/* Symbol select */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">Symbol</label>
            <select
              value={formData.symbol}
              onChange={(e) => setFormData({ ...formData, symbol: e.target.value })}
              className="input"
            >
              {SYMBOLS.map((s) => (
                <option key={s} value={s}>
                  {s.replace('USDT', '/USDT')}
                </option>
              ))}
            </select>
            {currentPrice && (
              <p className="text-xs text-gray-500 mt-1">
                Current price: ${currentPrice.toLocaleString()}
              </p>
            )}
          </div>

          {/* Condition */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">Condition</label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setFormData({ ...formData, condition: 'above' })}
                className={`flex items-center justify-center gap-2 p-3 rounded-lg border transition-all
                  ${formData.condition === 'above'
                    ? 'border-green-500 bg-green-500/10 text-green-400'
                    : 'border-crypto-border hover:border-green-500/50'
                  }`}
              >
                <TrendingUp className="w-4 h-4" />
                <span>Price Above</span>
              </button>
              <button
                type="button"
                onClick={() => setFormData({ ...formData, condition: 'below' })}
                className={`flex items-center justify-center gap-2 p-3 rounded-lg border transition-all
                  ${formData.condition === 'below'
                    ? 'border-red-500 bg-red-500/10 text-red-400'
                    : 'border-crypto-border hover:border-red-500/50'
                  }`}
              >
                <TrendingDown className="w-4 h-4" />
                <span>Price Below</span>
              </button>
            </div>
          </div>

          {/* Target price */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">Target Price (USD)</label>
            <input
              type="number"
              step="0.01"
              value={formData.target_price}
              onChange={(e) => setFormData({ ...formData, target_price: e.target.value })}
              placeholder="Enter target price"
              className="input font-mono"
              required
            />
          </div>

          {/* Note */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">Note (optional)</label>
            <input
              type="text"
              value={formData.note}
              onChange={(e) => setFormData({ ...formData, note: e.target.value })}
              placeholder="e.g., Buy opportunity"
              className="input"
              maxLength={200}
            />
          </div>

          {/* Telegram toggle */}
          <div className="flex items-center justify-between p-3 bg-crypto-dark rounded-lg">
            <span className="text-sm">Telegram notification</span>
            <button
              type="button"
              onClick={() => setFormData({ ...formData, notify_telegram: !formData.notify_telegram })}
              className={`w-12 h-6 rounded-full transition-all relative
                ${formData.notify_telegram ? 'bg-crypto-accent' : 'bg-crypto-border'}`}
            >
              <div className={`w-5 h-5 rounded-full bg-white absolute top-0.5 transition-all
                ${formData.notify_telegram ? 'left-6' : 'left-0.5'}`} 
              />
            </button>
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            className="w-full btn-primary py-3 disabled:opacity-50"
          >
            {loading ? 'Saving...' : (editAlert ? 'Update Alert' : 'Create Alert')}
          </button>
        </form>
      </div>
    </div>
  );
}
