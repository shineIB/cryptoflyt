/**
 * Alerts page - manage price alerts.
 */
import React, { useState, useEffect } from 'react';
import { Bell, Plus, Filter } from 'lucide-react';
import { AlertForm, AlertList } from '../components';
import { useAlertStore } from '../store';
import { alertsAPI } from '../services/api';

export function Alerts() {
  const { alerts, setAlerts, setLoading } = useAlertStore();
  const [showForm, setShowForm] = useState(false);
  const [editAlert, setEditAlert] = useState(null);
  const [filter, setFilter] = useState('all'); // 'all', 'active', 'triggered'

  // Fetch alerts on mount
  useEffect(() => {
    const fetchAlerts = async () => {
      setLoading(true);
      try {
        const response = await alertsAPI.getAll();
        setAlerts(response.data);
      } catch (error) {
        console.error('Failed to fetch alerts:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchAlerts();
  }, [setAlerts, setLoading]);

  const handleEdit = (alert) => {
    setEditAlert(alert);
    setShowForm(true);
  };

  const handleCloseForm = () => {
    setShowForm(false);
    setEditAlert(null);
  };

  // Filter alerts
  const filteredAlerts = alerts.filter((alert) => {
    if (filter === 'active') return alert.is_active && !alert.is_triggered;
    if (filter === 'triggered') return alert.is_triggered;
    return true;
  });

  // Stats
  const activeCount = alerts.filter(a => a.is_active && !a.is_triggered).length;
  const triggeredCount = alerts.filter(a => a.is_triggered).length;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Price Alerts</h1>
          <p className="text-gray-400">Get notified when prices hit your targets</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          New Alert
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="card p-4">
          <p className="text-sm text-gray-400">Total Alerts</p>
          <p className="text-2xl font-bold">{alerts.length}</p>
        </div>
        <div className="card p-4">
          <p className="text-sm text-gray-400">Active</p>
          <p className="text-2xl font-bold text-green-400">{activeCount}</p>
        </div>
        <div className="card p-4">
          <p className="text-sm text-gray-400">Triggered</p>
          <p className="text-2xl font-bold text-yellow-400">{triggeredCount}</p>
        </div>
      </div>

      {/* Filter */}
      <div className="flex items-center gap-2">
        <Filter className="w-4 h-4 text-gray-500" />
        <div className="flex gap-1 bg-crypto-dark rounded-lg p-1">
          {[
            { value: 'all', label: 'All' },
            { value: 'active', label: 'Active' },
            { value: 'triggered', label: 'Triggered' },
          ].map((f) => (
            <button
              key={f.value}
              onClick={() => setFilter(f.value)}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all
                ${filter === f.value 
                  ? 'bg-crypto-accent text-white' 
                  : 'text-gray-400 hover:text-white'
                }`}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {/* Alert list */}
      <AlertList alerts={filteredAlerts} onEdit={handleEdit} />

      {/* Alert form modal */}
      {showForm && (
        <AlertForm onClose={handleCloseForm} editAlert={editAlert} />
      )}
    </div>
  );
}
