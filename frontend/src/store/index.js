/**
 * Zustand stores for application state management.
 */
import { create } from 'zustand';

// Price store - real-time price data
export const usePriceStore = create((set, get) => ({
  prices: {},
  lastUpdated: null,
  connected: false,
  
  setPrice: (symbol, priceData) => set((state) => ({
    prices: { ...state.prices, [symbol]: priceData },
    lastUpdated: new Date(),
  })),
  
  setPrices: (prices) => set({
    prices,
    lastUpdated: new Date(),
  }),
  
  setConnected: (connected) => set({ connected }),
  
  getPrice: (symbol) => get().prices[symbol],
}));

// Auth store - user authentication state
export const useAuthStore = create((set, get) => ({
  user: JSON.parse(localStorage.getItem('user') || 'null'),
  token: localStorage.getItem('token'),
  isAuthenticated: !!localStorage.getItem('token'),
  
  login: (user, token) => {
    localStorage.setItem('user', JSON.stringify(user));
    localStorage.setItem('token', token);
    set({ user, token, isAuthenticated: true });
  },
  
  logout: () => {
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    set({ user: null, token: null, isAuthenticated: false });
  },
  
  updateUser: (userData) => {
    const user = { ...get().user, ...userData };
    localStorage.setItem('user', JSON.stringify(user));
    set({ user });
  },
}));

// Alert store - user alerts
export const useAlertStore = create((set, get) => ({
  alerts: [],
  loading: false,
  
  setAlerts: (alerts) => set({ alerts }),
  setLoading: (loading) => set({ loading }),
  
  addAlert: (alert) => set((state) => ({
    alerts: [alert, ...state.alerts],
  })),
  
  updateAlert: (id, data) => set((state) => ({
    alerts: state.alerts.map((a) => (a.id === id ? { ...a, ...data } : a)),
  })),
  
  removeAlert: (id) => set((state) => ({
    alerts: state.alerts.filter((a) => a.id !== id),
  })),
}));

// Portfolio store
export const usePortfolioStore = create((set) => ({
  holdings: [],
  totalValue: 0,
  totalPnl: 0,
  totalPnlPercent: 0,
  loading: false,
  
  setPortfolio: (data) => set({
    holdings: data.holdings,
    totalValue: data.total_value,
    totalPnl: data.total_pnl,
    totalPnlPercent: data.total_pnl_percent,
  }),
  
  setLoading: (loading) => set({ loading }),
}));

// UI store - notifications, modals, etc.
export const useUIStore = create((set) => ({
  notifications: [],
  
  addNotification: (notification) => set((state) => ({
    notifications: [
      ...state.notifications,
      { id: Date.now(), ...notification },
    ],
  })),
  
  removeNotification: (id) => set((state) => ({
    notifications: state.notifications.filter((n) => n.id !== id),
  })),
}));
