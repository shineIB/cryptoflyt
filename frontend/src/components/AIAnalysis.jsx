/**
 * AI Market Analysis component.
 */
import React, { useState } from 'react';
import { Brain, RefreshCw, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { pricesAPI } from '../services/api';

const SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'XRPUSDT', 'DOGEUSDT'];

export function AIAnalysis() {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchAnalysis = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await pricesAPI.analyze(SYMBOLS);
      setAnalysis(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to get analysis');
    } finally {
      setLoading(false);
    }
  };

  const getSentimentIcon = (sentiment) => {
    switch (sentiment) {
      case 'bullish':
        return <TrendingUp className="w-5 h-5 text-green-400" />;
      case 'bearish':
        return <TrendingDown className="w-5 h-5 text-red-400" />;
      default:
        return <Minus className="w-5 h-5 text-yellow-400" />;
    }
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'bullish':
        return 'text-green-400 bg-green-500/10 border-green-500/30';
      case 'bearish':
        return 'text-red-400 bg-red-500/10 border-red-500/30';
      default:
        return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30';
    }
  };

  // Simple markdown-like parsing
  const formatAnalysis = (text) => {
    if (!text) return null;
    
    return text.split('\n').map((line, i) => {
      if (line.startsWith('## ')) {
        return <h2 key={i} className="text-lg font-bold mt-4 mb-2">{line.replace('## ', '')}</h2>;
      }
      if (line.startsWith('### ')) {
        return <h3 key={i} className="text-md font-semibold mt-3 mb-1">{line.replace('### ', '')}</h3>;
      }
      if (line.startsWith('- ')) {
        return <li key={i} className="ml-4 text-gray-300">{line.replace('- ', '')}</li>;
      }
      if (line.match(/^\d+\./)) {
        return <li key={i} className="ml-4 text-gray-300">{line}</li>;
      }
      if (line.startsWith('**') && line.endsWith('**')) {
        return <p key={i} className="font-bold text-white">{line.replace(/\*\*/g, '')}</p>;
      }
      if (line.trim()) {
        // Handle inline bold
        const parts = line.split(/(\*\*.*?\*\*)/g);
        return (
          <p key={i} className="text-gray-300 my-1">
            {parts.map((part, j) => 
              part.startsWith('**') && part.endsWith('**')
                ? <strong key={j} className="text-white">{part.replace(/\*\*/g, '')}</strong>
                : part
            )}
          </p>
        );
      }
      return null;
    });
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between p-4 border-b border-crypto-border">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center">
            <Brain className="w-5 h-5 text-purple-400" />
          </div>
          <div>
            <h3 className="font-semibold">AI Market Analysis</h3>
            <p className="text-xs text-gray-500">Powered by Google Gemini</p>
          </div>
        </div>
        <button
          onClick={fetchAnalysis}
          disabled={loading}
          className="btn-secondary flex items-center gap-2"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          {loading ? 'Analyzing...' : 'Analyze'}
        </button>
      </div>

      <div className="p-4">
        {error && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 text-red-400 text-sm">
            {error}
          </div>
        )}

        {!analysis && !loading && !error && (
          <div className="text-center py-8">
            <Brain className="w-12 h-12 text-gray-600 mx-auto mb-3" />
            <p className="text-gray-400">Click "Analyze" to get AI-powered market insights</p>
          </div>
        )}

        {loading && (
          <div className="flex flex-col items-center py-12">
            <div className="w-10 h-10 border-2 border-purple-500 border-t-transparent rounded-full animate-spin mb-4" />
            <p className="text-gray-400">Analyzing market conditions...</p>
          </div>
        )}

        {analysis && !loading && (
          <div className="space-y-4">
            {/* Sentiment badge */}
            <div className={`inline-flex items-center gap-2 px-3 py-2 rounded-lg border ${getSentimentColor(analysis.sentiment)}`}>
              {getSentimentIcon(analysis.sentiment)}
              <span className="font-medium capitalize">{analysis.sentiment}</span>
            </div>

            {/* Analysis content */}
            <div className="prose prose-invert max-w-none text-sm">
              {formatAnalysis(analysis.analysis)}
            </div>

            {/* Timestamp */}
            <p className="text-xs text-gray-500 pt-4 border-t border-crypto-border">
              Generated at {new Date(analysis.timestamp).toLocaleString()}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
