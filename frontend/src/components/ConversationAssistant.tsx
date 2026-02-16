import React, { useState, useEffect } from 'react';
import { Sparkles, Loader2 } from 'lucide-react';

const API_BASE = 'http://localhost:8000';

interface Props {
  caseId: string;
  message: string;
}

const ConversationAssistant: React.FC<Props> = ({ caseId, message }) => {
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Debounce the API call
    const timer = setTimeout(() => {
      if (message.trim().length > 5) {
        getSuggestions();
      } else {
        setSuggestions([]);
      }
    }, 1000);

    return () => clearTimeout(timer);
  }, [message, caseId]);

  const getSuggestions = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API_BASE}/api/conversation/assist`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ case_id: caseId, message })
      });
      const data = await res.json();
      setSuggestions(data.suggestions || []);
    } catch (error) {
      console.error('Failed to get suggestions:', error);
      setSuggestions([]);
    } finally {
      setLoading(false);
    }
  };

  if (!message.trim() || suggestions.length === 0) {
    return null;
  }

  return (
    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-200">
      <div className="flex items-center gap-2 mb-2">
        {loading ? (
          <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
        ) : (
          <Sparkles className="w-4 h-4 text-blue-600" />
        )}
        <h4 className="text-sm font-bold text-blue-900">AI Writing Assistant</h4>
      </div>
      <div className="space-y-2">
        {suggestions.map((suggestion, idx) => (
          <div key={idx} className="text-sm text-blue-800 bg-white rounded p-2 border border-blue-100">
            {suggestion}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ConversationAssistant;