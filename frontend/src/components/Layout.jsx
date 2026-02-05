/**
 * Main layout component with sidebar navigation.
 */
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Bell, 
  Wallet, 
  Settings, 
  LogOut,
  TrendingUp,
  Zap
} from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { usePriceStore } from '../store';

const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/alerts', icon: Bell, label: 'Alerts' },
  { path: '/portfolio', icon: Wallet, label: 'Portfolio' },
  { path: '/settings', icon: Settings, label: 'Settings' },
];

export function Layout({ children }) {
  const location = useLocation();
  const { user, logout } = useAuth();
  const connected = usePriceStore((s) => s.connected);

  return (
    <div className="min-h-screen bg-crypto-darker flex">
      {/* Sidebar */}
      <aside className="w-64 bg-crypto-dark border-r border-crypto-border flex flex-col">
        {/* Logo */}
        <div className="p-6 border-b border-crypto-border">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-crypto-accent to-purple-600 
                          flex items-center justify-center">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="font-bold text-lg">CryptoFlyt</h1>
              <div className="flex items-center gap-1.5">
                <div className={`w-1.5 h-1.5 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-xs text-gray-500">
                  {connected ? 'Live' : 'Offline'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4">
          <ul className="space-y-1">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <li key={item.path}>
                  <Link
                    to={item.path}
                    className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200
                      ${isActive 
                        ? 'bg-crypto-accent/20 text-crypto-accent' 
                        : 'text-gray-400 hover:bg-crypto-card hover:text-white'
                      }`}
                  >
                    <item.icon className="w-5 h-5" />
                    <span className="font-medium">{item.label}</span>
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* User section */}
        <div className="p-4 border-t border-crypto-border">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-full bg-crypto-accent/20 flex items-center justify-center">
              <span className="text-crypto-accent font-bold">
                {user?.username?.[0]?.toUpperCase() || 'U'}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-medium text-sm truncate">{user?.username}</p>
              <p className="text-xs text-gray-500 truncate">{user?.email}</p>
            </div>
          </div>
          <button
            onClick={logout}
            className="w-full flex items-center gap-3 px-4 py-2 rounded-lg text-gray-400 
                     hover:bg-red-500/10 hover:text-red-400 transition-all duration-200"
          >
            <LogOut className="w-4 h-4" />
            <span className="text-sm">Logout</span>
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        {children}
      </main>
    </div>
  );
}
