/**
 * WebSocket hook for real-time price updates.
 */
import { useEffect, useRef, useCallback } from 'react';
import { usePriceStore } from '../store';

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

export function useWebSocket() {
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const { setPrice, setPrices, setConnected } = usePriceStore();

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket(`${WS_URL}/api/prices/ws`);

    ws.onopen = () => {
      console.log('✓ WebSocket connected');
      setConnected(true);
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };

    ws.onclose = () => {
      console.log('✗ WebSocket disconnected');
      setConnected(false);
      // Reconnect after 3 seconds
      reconnectTimeoutRef.current = setTimeout(connect, 3000);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);

        if (message.type === 'snapshot') {
          // Initial snapshot of all prices
          setPrices(message.data);
        } else if (message.type === 'update') {
          // Single price update
          const { symbol } = message.data;
          if (symbol) {
            setPrice(symbol, message.data);
          }
        }
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e);
      }
    };

    wsRef.current = ws;

    // Ping to keep connection alive
    const pingInterval = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send('ping');
      }
    }, 25000);

    return () => {
      clearInterval(pingInterval);
    };
  }, [setPrice, setPrices, setConnected]);

  useEffect(() => {
    connect();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [connect]);

  return {
    connected: usePriceStore((s) => s.connected),
  };
}
