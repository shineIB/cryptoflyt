/**
 * Settings page - user profile and notification settings.
 */
import React, { useState } from 'react';
import { User, Bell, MessageCircle, Save } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

export function Settings() {
  const { user, updateProfile } = useAuth();
  const [formData, setFormData] = useState({
    username: user?.username || '',
    telegram_chat_id: user?.telegram_chat_id || '',
    telegram_notifications: user?.telegram_notifications || false,
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage({ type: '', text: '' });

    const result = await updateProfile(formData);
    
    if (result.success) {
      setMessage({ type: 'success', text: 'Settings saved successfully!' });
    } else {
      setMessage({ type: 'error', text: result.error });
    }
    
    setLoading(false);
  };

  return (
    <div className="p-6 space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-gray-400">Manage your profile and notifications</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {message.text && (
          <div className={`p-4 rounded-lg ${
            message.type === 'success' 
              ? 'bg-green-500/10 border border-green-500/30 text-green-400' 
              : 'bg-red-500/10 border border-red-500/30 text-red-400'
          }`}>
            {message.text}
          </div>
        )}

        <div className="card p-6 space-y-4">
          <div className="flex items-center gap-3 mb-2">
            <User className="w-5 h-5 text-crypto-accent" />
            <h2 className="font-semibold">Profile</h2>
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-2">Email</label>
            <input
              type="email"
              value={user?.email || ''}
              className="input bg-crypto-darker text-gray-500"
              disabled
            />
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-2">Username</label>
            <input
              type="text"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              className="input"
              required
            />
          </div>
        </div>

        <div className="card p-6 space-y-4">
          <div className="flex items-center gap-3 mb-2">
            <MessageCircle className="w-5 h-5 text-blue-400" />
            <h2 className="font-semibold">Telegram Notifications</h2>
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-2">Telegram Chat ID</label>
            <input
              type="text"
              value={formData.telegram_chat_id}
              onChange={(e) => setFormData({ ...formData, telegram_chat_id: e.target.value })}
              placeholder="e.g., 123456789"
              className="input font-mono"
            />
            <p className="text-xs text-gray-500 mt-1">
              Get your Chat ID from @userinfobot on Telegram
            </p>
          </div>

          <div className="flex items-center justify-between p-3 bg-crypto-dark rounded-lg">
            <span className="text-sm">Enable Telegram alerts</span>
            <button
              type="button"
              onClick={() => setFormData({ ...formData, telegram_notifications: !formData.telegram_notifications })}
              className={`w-12 h-6 rounded-full transition-all relative
                ${formData.telegram_notifications ? 'bg-crypto-accent' : 'bg-crypto-border'}`}
            >
              <div className={`w-5 h-5 rounded-full bg-white absolute top-0.5 transition-all
                ${formData.telegram_notifications ? 'left-6' : 'left-0.5'}`} 
              />
            </button>
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="btn-primary flex items-center gap-2 disabled:opacity-50"
        >
          <Save className="w-4 h-4" />
          {loading ? 'Saving...' : 'Save Settings'}
        </button>
      </form>
    </div>
  );
}
