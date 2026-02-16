import React, { useState, useEffect } from 'react';
import { TrendingUp, Loader2, RefreshCw } from 'lucide-react';

const API_BASE = 'http://localhost:8000';

const PatternInsights: React.FC = () => {
  const [insights, setInsights] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadInsights = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('Fetching insights from:', `${API_BASE}/api/insights/patterns`);
      const res = await fetch(`${API_BASE}/api/insights/patterns`);
      
      console.log('Response status:', res.status);
      
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      
      const data = await res.json();
      console.log('Insights data received:', data);
      
      if (data && Array.isArray(data.insights)) {
        setInsights(data.insights);
      } else {
        console.error('Invalid data format:', data);
        setError('Invalid data format received from server');
        setInsights([]);
      }
    } catch (error) {
      console.error('Failed to load insights:', error);
      setError(error instanceof Error ? error.message : 'Failed to load insights');
      setInsights([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadInsights();
  }, []);

  return (
    <div className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-xl shadow-md p-6 border border-purple-200">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-purple-600" />
          <h2 className="text-lg font-bold text-gray-900">AI Pattern Analysis</h2>
        </div>
        <button
          onClick={loadInsights}
          disabled={loading}
          className="px-3 py-1 bg-purple-600 text-white rounded-lg text-sm font-medium hover:bg-purple-700 transition-colors disabled:opacity-50 flex items-center gap-2"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
          Refresh
        </button>
      </div>
      
      {loading ? (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="w-8 h-8 animate-spin text-purple-600" />
        </div>
      ) : error ? (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-700 font-semibold mb-2">Error loading insights</p>
          <p className="text-xs text-red-600">{error}</p>
          <p className="text-xs text-gray-500 mt-2">Check browser console for details</p>
        </div>
      ) : insights.length === 0 ? (
        <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-sm text-yellow-700">No insights available yet</p>
        </div>
      ) : (
        <div className="space-y-3">
          {insights.map((insight, idx) => (
            <div key={idx} className="flex items-start gap-3 p-3 bg-white rounded-lg border border-purple-100 hover:border-purple-300 transition-colors">
              <span className="text-2xl">🤖</span>
              <p className="text-sm text-gray-700 leading-relaxed">{insight}</p>
            </div>
          ))}
        </div>
      )}
      
      <div className="mt-4 pt-4 border-t border-purple-200">
        <p className="text-xs text-purple-600 italic">
          💡 Insights powered by real-time analysis of your caseload using AI pattern recognition
        </p>
      </div>
    </div>
  );
};

export default PatternInsights;