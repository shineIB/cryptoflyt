/**
 * Alert list component.
 */
import React from 'react';
import { Bell, BellOff, Trash2, Edit2, TrendingUp, TrendingDown, CheckCircle } from 'lucide-react';
import { alertsAPI } from '../services/api';
import { useAlertStore, usePriceStore } from '../store';

export function AlertList({ alerts, onEdit }) {
  const { updateAlert, removeAlert } = useAlertStore();
  const prices = usePriceStore((s) => s.prices);

  const handleToggle = async (alert) => {
    try {
      const response = await alertsAPI.update(alert.id, { is_active: !alert.is_active });
      updateAlert(alert.id, response.data);
    } catch (error) {
      console.error('Failed to toggle alert:', error);
    }
  };

  const handleDelete = async (alert) => {
    if (!confirm('Delete this alert?')) return;
    
    try {
      await alertsAPI.delete(alert.id);
      removeAlert(alert.id);
    } catch (error) {
      console.error('Failed to delete alert:', error);
    }
  };

  if (alerts.length === 0) {
    return (
      <div className="card p-12 text-center">
        <Bell className="w-12 h-12 text-gray-600 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-400 mb-2">No alerts yet</h3>
        <p className="text-sm text-gray-500">Create your first price alert to get started.</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {alerts.map((alert) => {
        const currentPrice = prices[alert.symbol]?.price;
        const isAbove = alert.condition === 'above';
        const distance = currentPrice 
          ? ((alert.target_price - currentPrice) / currentPrice * 100).toFixed(2)
          : null;

        return (
          <div 
            key={alert.id}
            className={`card p-4 transition-all ${!alert.is_active ? 'opacity-50' : ''}`}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center
                  ${alert.is_triggered 
                    ? 'bg-green-500/20' 
                    : isAbove 
                      ? 'bg-green-500/10' 
                      : 'bg-red-500/10'
                  }`}>
                  {alert.is_triggered ? (
                    <CheckCircle className="w-5 h-5 text-green-400" />
                  ) : isAbove ? (
                    <TrendingUp className="w-5 h-5 text-green-400" />
                  ) : (
                    <TrendingDown className="w-5 h-5 text-red-400" />
                  )}
                </div>
                
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold">{alert.symbol.replace('USDT', '')}</span>
                    <span className={`badge ${isAbove ? 'badge-green' : 'badge-red'}`}>
                      {isAbove ? 'Above' : 'Below'}
                    </span>
                    {alert.is_triggered && (
                      <span className="badge badge-green">Triggered</span>
                    )}
                  </div>
                  
                  <p className="text-lg font-mono font-bold mt-1">
                    ${alert.target_price.toLocaleString()}
                  </p>
                  
                  {currentPrice && !alert.is_triggered && (
                    <p className="text-xs text-gray-500 mt-1">
                      {Math.abs(distance)}% {parseFloat(distance) > 0 ? 'above' : 'below'} current price
                    </p>
                  )}
                  
                  {alert.note && (
                    <p className="text-sm text-gray-400 mt-2">📝 {alert.note}</p>
                  )}
                  
                  {alert.is_triggered && alert.triggered_at && (
                    <p className="text-xs text-green-400 mt-2">
                      Triggered at ${alert.triggered_price?.toLocaleString()} on{' '}
                      {new Date(alert.triggered_at).toLocaleString()}
                    </p>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-1">
                {!alert.is_triggered && (
                  <>
                    <button
                      onClick={() => onEdit(alert)}
                      className="p-2 text-gray-400 hover:text-white hover:bg-crypto-card rounded-lg transition-all"
                      title="Edit"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleToggle(alert)}
                      className="p-2 text-gray-400 hover:text-white hover:bg-crypto-card rounded-lg transition-all"
                      title={alert.is_active ? 'Disable' : 'Enable'}
                    >
                      {alert.is_active ? (
                        <Bell className="w-4 h-4" />
                      ) : (
                        <BellOff className="w-4 h-4" />
                      )}
                    </button>
                  </>
                )}
                <button
                  onClick={() => handleDelete(alert)}
                  className="p-2 text-gray-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-all"
                  title="Delete"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
