import React, { useState, useEffect } from 'react';
import { AlertCircle, TrendingUp, Users, DollarSign, Clock, MessageSquare, Search, ChevronRight, Loader2, Sparkles, Upload, FileText, X, Zap } from 'lucide-react';
import PatternInsights from './components/PatternInsights';
import ConversationAssistant from './components/ConversationAssistant';
import AnalyticsCharts from './components/AnalyticsCharts';

const API_BASE = 'http://localhost:8000';

interface Message {
  id: string;
  case_id?: string;
  sender: string;
  content: string;
  timestamp: string;
}

interface FinancialSnapshot {
  annual_income: number;
  credit_score: number;
  savings: number;
  total_debt: number;
  dependents: number;
}

interface Case {
  id: string;
  employee_name: string;
  employer: string;
  urgency: 'critical' | 'high' | 'medium' | 'low';
  categories: string[];
  last_contact: string;
  status: string;
  financial_snapshot: FinancialSnapshot;
  open_actions: string[];
  messages: Message[];
  sentiment?: string;
}

interface Resource {
  id: string;
  name: string;
  description: string;
  max_amount?: number;
  typical_approval_time: string;
  application_difficulty: string;
  success_rate: number;
}

interface ResourceRecommendation {
  resource: Resource;
  relevance_score: number;
  reasoning: string;
  estimated_success: number;
}

interface Analytics {
  total_active_cases: number;
  critical_cases: number;
  this_month: {
    cases_resolved: number;
    total_money_saved: number;
    avg_credit_score_improvement: number;
    avg_response_time_hours: number;
  };
  category_breakdown: {
    [key: string]: number;
  };
}

interface Document {
  id: string;
  filename: string;
  file_type: string;
  uploaded_at: string;
  has_text: boolean;
}

interface UrgencyBadgeProps {
  level: 'critical' | 'high' | 'medium' | 'low';
}

const UrgencyBadge: React.FC<UrgencyBadgeProps> = ({ level }) => {
  const colors = {
    critical: 'bg-red-100 text-red-800 border-red-200',
    high: 'bg-orange-100 text-orange-800 border-orange-200',
    medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    low: 'bg-green-100 text-green-800 border-green-200'
  };
  
  const icons = { critical: '🔴', high: '🟠', medium: '🟡', low: '🟢' };
  
  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium border ${colors[level]}`}>
      {icons[level]} {level.toUpperCase()}
    </span>
  );
};

const Dashboard: React.FC = () => {
  const [view, setView] = useState<'overview' | 'case-detail'>('overview');
  const [cases, setCases] = useState<Case[]>([]);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [selectedCase, setSelectedCase] = useState<Case | null>(null);
  const [recommendations, setRecommendations] = useState<ResourceRecommendation[]>([]);
  const [aiTriage, setAiTriage] = useState<any>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [recommendLoading, setRecommendLoading] = useState(false);
  const [triageLoading, setTriageLoading] = useState(false);
  const [responseMessage, setResponseMessage] = useState('');
  const [uploadingFile, setUploadingFile] = useState(false);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [streamingText, setStreamingText] = useState('');
  const [useStreaming, setUseStreaming] = useState(true);
  const [sendingMessage, setSendingMessage] = useState(false);
  const [caseNotes, setCaseNotes] = useState<{[key: string]: string}>({});
  const [savingNotes, setSavingNotes] = useState(false);
  
  // New state for create case
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newCase, setNewCase] = useState({
    employee_name: '',
    employer: '',
    annual_income: '',
    credit_score: '',
    savings: '',
    total_debt: '',
    dependents: ''
  });
  const [creatingCase, setCreatingCase] = useState(false);

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [casesRes, analyticsRes] = await Promise.all([
        fetch(`${API_BASE}/api/cases`),
        fetch(`${API_BASE}/api/analytics`)
      ]);
      setCases(await casesRes.json());
      setAnalytics(await analyticsRes.json());
    } catch (error) {
      console.error('Backend error:', error);
      alert('Backend error - make sure it\'s running on port 8000');
    } finally {
      setLoading(false);
    }
  };

  const createCase = async () => {
    // Validate
    if (!newCase.employee_name || !newCase.employer) {
      alert('Please fill in employee name and employer');
      return;
    }
    
    try {
      setCreatingCase(true);
      
      const res = await fetch(`${API_BASE}/api/cases`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          employee_name: newCase.employee_name,
          employer: newCase.employer,
          financial_snapshot: {
            annual_income: parseInt(newCase.annual_income) || 0,
            credit_score: parseInt(newCase.credit_score) || 0,
            savings: parseInt(newCase.savings) || 0,
            total_debt: parseInt(newCase.total_debt) || 0,
            dependents: parseInt(newCase.dependents) || 0
          }
        })
      });
      
      if (res.ok) {
        const result = await res.json();
        
        // Reload cases
        await loadData();
        
        // Reset form
        setNewCase({
          employee_name: '',
          employer: '',
          annual_income: '',
          credit_score: '',
          savings: '',
          total_debt: '',
          dependents: ''
        });
        
        // Close modal
        setShowCreateModal(false);
        
        alert('✅ Case created successfully!');
        
        // Auto-select the new case
        if (result.case) {
          selectCase(result.case);
        }
      }
    } catch (error) {
      console.error('Create case error:', error);
      alert('Failed to create case');
    } finally {
      setCreatingCase(false);
    }
  };

  const selectCase = async (c: Case) => {
    setSelectedCase(c);
    setView('case-detail');
    setRecommendations([]);
    setAiTriage(null);
    setResponseMessage('');
    setStreamingText('');
    
    // Load documents for this case
    try {
      const res = await fetch(`${API_BASE}/api/case/${c.id}/documents`);
      setDocuments(await res.json());
    } catch (error) {
      console.error('Error loading documents:', error);
    }

    // Load notes for this case
    try {
      const res = await fetch(`${API_BASE}/api/case/${c.id}/notes`);
      const data = await res.json();
      if (data.notes) {
        setCaseNotes({...caseNotes, [c.id]: data.notes});
      }
    } catch (error) {
      console.error('Error loading notes:', error);
    }
  };

  const getRecommendations = async () => {
    if (!selectedCase) return;
    
    if (useStreaming) {
      // STREAMING VERSION
      try {
        setRecommendLoading(true);
        setStreamingText('');
        
        const response = await fetch(`${API_BASE}/api/recommend/stream`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ case_id: selectedCase.id })
        });

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
          const { done, value } = await reader!.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = JSON.parse(line.slice(6));
              if (data.token) {
                setStreamingText(prev => prev + data.token);
              } else if (data.done && data.result) {
                setRecommendations(data.result.map((rec: any) => ({
                  resource: { id: rec.resource_id, ...rec },
                  relevance_score: rec.relevance_score,
                  reasoning: rec.reasoning,
                  estimated_success: rec.estimated_success
                })));
              }
            }
          }
        }
      } catch (error) {
        console.error('Error:', error);
      } finally {
        setRecommendLoading(false);
      }
    } else {
      // NON-STREAMING VERSION
      try {
        setRecommendLoading(true);
        const res = await fetch(`${API_BASE}/api/recommend`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ case_id: selectedCase.id })
        });
        const data = await res.json();
        setRecommendations(Array.isArray(data) ? data : []);
      } catch (error) {
        console.error('Error:', error);
      } finally {
        setRecommendLoading(false);
      }
    }
  };

  const analyzeMessage = async () => {
    if (!selectedCase?.messages?.length) return;
    
    if (useStreaming) {
      // STREAMING VERSION
      try {
        setTriageLoading(true);
        setStreamingText('');
        
        const msg = selectedCase.messages[selectedCase.messages.length - 1];
        const response = await fetch(`${API_BASE}/api/triage/stream`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ case_id: selectedCase.id, message: msg.content })
        });

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
          const { done, value } = await reader!.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = JSON.parse(line.slice(6));
              if (data.token) {
                setStreamingText(prev => prev + data.token);
              } else if (data.done && data.result) {
                setAiTriage(data.result);
              }
            }
          }
        }
      } catch (error) {
        console.error('Error:', error);
      } finally {
        setTriageLoading(false);
      }
    } else {
      // NON-STREAMING
      try {
        setTriageLoading(true);
        const msg = selectedCase.messages[selectedCase.messages.length - 1];
        const res = await fetch(`${API_BASE}/api/triage`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ case_id: selectedCase.id, message: msg.content })
        });
        setAiTriage(await res.json());
      } catch (error) {
        console.error('Error:', error);
      } finally {
        setTriageLoading(false);
      }
    }
  };

  const uploadFile = async (file: File) => {
    if (!selectedCase) return;
    
    try {
      setUploadingFile(true);
      const formData = new FormData();
      formData.append('file', file);
      formData.append('case_id', selectedCase.id);

      const res = await fetch(`${API_BASE}/api/upload?case_id=${selectedCase.id}`, {
        method: 'POST',
        body: formData
      });
      const result = await res.json();
      
      if (result.success) {
        alert(`✅ File uploaded! ${result.extracted_text_preview ? 'Text extracted from document.' : ''}`);
        
        // Reload documents immediately
        const docsRes = await fetch(`${API_BASE}/api/case/${selectedCase.id}/documents`);
        setDocuments(await docsRes.json());
        
        // Reload the entire case to get updated documents_text
        const casesRes = await fetch(`${API_BASE}/api/cases`);
        const updatedCases = await casesRes.json();
        setCases(updatedCases);
        const updatedCase = updatedCases.find((c: Case) => c.id === selectedCase.id);
        if (updatedCase) {
          setSelectedCase(updatedCase);
        }
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert('Failed to upload file');
    } finally {
      setUploadingFile(false);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      uploadFile(file);
    }
    // Reset input so same file can be uploaded again
    e.target.value = '';
  };

  const sendMessage = async () => {
    if (!selectedCase || !responseMessage.trim()) return;
    
    try {
      setSendingMessage(true);
      
      const res = await fetch(`${API_BASE}/api/case/${selectedCase.id}/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sender: 'assistant',
          content: responseMessage
        })
      });
      
      if (res.ok) {
        const casesRes = await fetch(`${API_BASE}/api/cases`);
        const updatedCases = await casesRes.json();
        setCases(updatedCases);
        
        const updatedCase = updatedCases.find((c: Case) => c.id === selectedCase.id);
        if (updatedCase) {
          setSelectedCase(updatedCase);
        }
        
        setResponseMessage('');
        alert('✅ Message sent!');
      }
    } catch (error) {
      console.error('Send message error:', error);
      alert('Failed to send message');
    } finally {
      setSendingMessage(false);
    }
  };

  const saveNotes = async () => {
    if (!selectedCase) return;
    
    try {
      setSavingNotes(true);
      const notes = caseNotes[selectedCase.id] || '';
      
      const res = await fetch(`${API_BASE}/api/case/${selectedCase.id}/notes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ notes })
      });
      
      if (res.ok) {
        alert('✅ Notes saved!');
      }
    } catch (error) {
      console.error('Save notes error:', error);
      alert('Failed to save notes');
    } finally {
      setSavingNotes(false);
    }
  };

  const filtered = cases.filter(c => 
    c.employee_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.employer.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <Loader2 className="w-16 h-16 animate-spin text-blue-600 mb-4" />
        <p className="text-gray-600 font-medium">Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-semibold text-gray-900">Financial Assistant Dashboard</h1>
              <p className="text-sm text-gray-500 mt-0.5">
                Case Management System
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">Sarah Johnson</p>
                <p className="text-xs text-gray-500">Financial Assistant</p>
              </div>
              <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center text-gray-600 font-medium text-sm">
                SJ
              </div>
            </div>
          </div>
        </div>
      </header>

      {view === 'overview' ? (
        <div className="p-6 space-y-6 max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg shadow-sm p-5 border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-gray-500 font-medium uppercase tracking-wide">Active Cases</p>
                  <p className="text-3xl font-semibold text-gray-900 mt-1">{analytics?.total_active_cases || 0}</p>
                </div>
                <div className="w-12 h-12 rounded-lg bg-blue-50 flex items-center justify-center">
                  <Users className="w-6 h-6 text-blue-600" />
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow-sm p-5 border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-gray-500 font-medium uppercase tracking-wide">Critical</p>
                  <p className="text-3xl font-semibold text-red-600 mt-1">{analytics?.critical_cases || 0}</p>
                </div>
                <div className="w-12 h-12 rounded-lg bg-red-50 flex items-center justify-center">
                  <AlertCircle className="w-6 h-6 text-red-600" />
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow-sm p-5 border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-gray-500 font-medium uppercase tracking-wide">Money Saved</p>
                  <p className="text-3xl font-semibold text-green-600 mt-1">
                    ${((analytics?.this_month?.total_money_saved || 0) / 1000).toFixed(0)}k
                  </p>
                </div>
                <div className="w-12 h-12 rounded-lg bg-green-50 flex items-center justify-center">
                  <DollarSign className="w-6 h-6 text-green-600" />
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow-sm p-5 border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-gray-500 font-medium uppercase tracking-wide">Credit +</p>
                  <p className="text-3xl font-semibold text-blue-600 mt-1">
                    +{analytics?.this_month?.avg_credit_score_improvement || 0}
                  </p>
                </div>
                <div className="w-12 h-12 rounded-lg bg-blue-50 flex items-center justify-center">
                  <TrendingUp className="w-6 h-6 text-blue-600" />
                </div>
              </div>
            </div>
          </div>

          {analytics && <AnalyticsCharts analytics={analytics} />}
          <PatternInsights />

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
            <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-base font-semibold text-gray-900">Active Cases</h2>
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => setShowCreateModal(true)}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 transition-colors flex items-center gap-2"
                  >
                    <Users className="w-4 h-4" />
                    Create New Case
                  </button>
                  <div className="relative">
                    <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                    <input
                      type="text"
                      placeholder="Search..."
                      className="pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                  </div>
                </div>
              </div>
            </div>
            
            <div className="divide-y divide-gray-100">
              {filtered.map((c) => (
                <div
                  key={c.id}
                  className="px-6 py-4 hover:bg-gray-50 cursor-pointer transition-colors"
                  onClick={() => selectCase(c)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-1">
                        <h3 className="font-medium text-gray-900">{c.employee_name}</h3>
                        <UrgencyBadge level={c.urgency} />
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{c.employer}</p>
                      <div className="flex items-center gap-4 text-xs text-gray-500">
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {new Date(c.last_contact).toLocaleDateString()}
                        </span>
                        <span className="flex items-center gap-1">
                          <MessageSquare className="w-3 h-3" />
                          {c.messages.length}
                        </span>
                        <span>${(c.financial_snapshot.annual_income / 1000).toFixed(0)}k income</span>
                        <span>Score: {c.financial_snapshot.credit_score}</span>
                      </div>
                    </div>
                    <ChevronRight className="w-5 h-5 text-gray-400" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : selectedCase && (
        <div className="p-6 space-y-6 max-w-7xl mx-auto">
          <button
            onClick={() => setView('overview')}
            className="text-blue-600 hover:text-blue-700 font-medium text-sm flex items-center gap-1"
          >
            ← Back to Cases
          </button>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-6">
              <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h2 className="text-3xl font-bold text-gray-900 mb-2">{selectedCase.employee_name}</h2>
                    <p className="text-gray-600 text-lg">{selectedCase.employer}</p>
                  </div>
                  <UrgencyBadge level={selectedCase.urgency} />
                </div>
                
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t">
                  <div>
                    <p className="text-xs text-gray-500 font-medium mb-1">Annual Income</p>
                    <p className="text-xl font-bold text-gray-900">
                      ${(selectedCase.financial_snapshot.annual_income / 1000).toFixed(0)}k
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 font-medium mb-1">Credit Score</p>
                    <p className="text-xl font-bold text-gray-900">
                      {selectedCase.financial_snapshot.credit_score}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 font-medium mb-1">Savings</p>
                    <p className="text-xl font-bold text-gray-900">
                      ${selectedCase.financial_snapshot.savings}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 font-medium mb-1">Total Debt</p>
                    <p className="text-xl font-bold text-gray-900">
                      ${(selectedCase.financial_snapshot.total_debt / 1000).toFixed(1)}k
                    </p>
                  </div>
                </div>
              </div>

              {/* Documents Section */}
              <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="font-bold text-gray-900 text-lg flex items-center gap-2">
                    <FileText className="w-5 h-5" />
                    Documents ({documents.length})
                  </h3>
                  <label className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors cursor-pointer flex items-center gap-2">
                    {uploadingFile ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
                    Upload Document
                    <input
                      type="file"
                      onChange={handleFileSelect}
                      className="hidden"
                      accept="image/*,.pdf,.txt"
                      disabled={uploadingFile}
                    />
                  </label>
                </div>
                
                {documents.length === 0 ? (
                  <p className="text-sm text-gray-500 text-center py-8">No documents uploaded yet. Upload bills, eviction notices, or other documents.</p>
                ) : (
                  <div className="space-y-2">
                    {documents.map((doc) => (
                      <div key={doc.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center gap-3">
                          <FileText className="w-5 h-5 text-gray-400" />
                          <div>
                            <p className="text-sm font-medium text-gray-900">{doc.filename}</p>
                            <p className="text-xs text-gray-500">
                              Uploaded {new Date(doc.uploaded_at).toLocaleDateString()}
                              {doc.has_text && <span className="ml-2 text-green-600">• Text extracted</span>}
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="font-bold text-gray-900 text-lg">Conversation</h3>
                  <button
                    onClick={analyzeMessage}
                    disabled={triageLoading || !selectedCase.messages?.length}
                    className="px-4 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg text-sm font-medium hover:from-purple-700 hover:to-indigo-700 transition-all shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                  >
                    {triageLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                    {useStreaming ? 'Stream Analysis' : 'Analyze with AI'}
                  </button>
                </div>
                
                {selectedCase.messages?.length === 0 ? (
                  <div className="text-center py-8 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
                    <MessageSquare className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                    <p className="text-sm text-gray-600">No messages yet in this conversation</p>
                    <p className="text-xs text-gray-500 mt-1">Messages will appear here when the employee contacts you</p>
                  </div>
                ) : (
                  <div className="space-y-4 mb-6">
                    {selectedCase.messages?.map((msg) => (
                      <div key={msg.id} className={`flex ${msg.sender === 'employee' ? 'justify-start' : 'justify-end'}`}>
                        <div className={`rounded-2xl p-4 max-w-lg shadow-sm ${
                          msg.sender === 'employee' 
                            ? 'bg-gray-100 text-gray-900' 
                            : 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white'
                        }`}>
                          <p className="text-sm leading-relaxed">{msg.content}</p>
                          <p className={`text-xs mt-2 ${msg.sender === 'employee' ? 'text-gray-500' : 'text-blue-100'}`}>
                            {new Date(msg.timestamp).toLocaleTimeString()}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
                
                {/* Streaming text preview */}
                {triageLoading && streamingText && (
                  <div className="mb-6 p-4 bg-purple-50 border border-purple-200 rounded-lg">
                    <p className="text-sm text-purple-900 font-mono">{streamingText}</p>
                  </div>
                )}
                
                {aiTriage && (
                  <div className="mt-6 p-5 bg-gradient-to-r from-purple-50 to-indigo-50 border border-purple-200 rounded-xl shadow-sm relative">
                    <button
                      onClick={() => setAiTriage(null)}
                      className="absolute top-3 right-3 text-purple-400 hover:text-purple-600"
                    >
                      <X className="w-4 h-4" />
                    </button>
                    <div className="flex items-start gap-3">
                      <Sparkles className="w-5 h-5 text-purple-600 flex-shrink-0 mt-0.5" />
                      <div className="flex-1">
                        <p className="font-bold text-purple-900 mb-3">🤖 AI Analysis (Powered by RAG + Vector Search)</p>
                        <div className="space-y-2 text-sm text-purple-900">
                          <p><strong>Urgency:</strong> {aiTriage.urgency} (Priority: {aiTriage.priority_score}/10)</p>
                          <p><strong>Sentiment:</strong> {aiTriage.sentiment}</p>
                          <p><strong>Categories:</strong> {aiTriage.categories?.join(', ')}</p>
                          {aiTriage.reasoning && <p><strong>Analysis:</strong> {aiTriage.reasoning}</p>}
                          {aiTriage.red_flags?.length > 0 && (
                            <div className="mt-3 p-3 bg-white rounded-lg border border-purple-200">
                              <strong>⚠️ Red Flags:</strong>
                              <ul className="list-disc list-inside mt-1 space-y-1">
                                {aiTriage.red_flags.map((flag: string, i: number) => (
                                  <li key={i}>{flag}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                          {aiTriage.suggested_response && (
                            <div className="mt-3 p-3 bg-white rounded-lg border border-purple-200">
                              <strong>💬 Suggested Response:</strong>
                              <p className="mt-1 italic">"{aiTriage.suggested_response}"</p>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                <div className="mt-6 space-y-3">
                  <textarea
                    value={responseMessage}
                    onChange={(e) => setResponseMessage(e.target.value)}
                    placeholder="Type your response here..."
                    className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                    rows={3}
                  />
                  <div className="flex gap-2">
                    <button
                      onClick={sendMessage}
                      disabled={sendingMessage || !responseMessage.trim()}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                      {sendingMessage ? <Loader2 className="w-4 h-4 animate-spin" /> : <MessageSquare className="w-4 h-4" />}
                      Send Message
                    </button>
                    <button
                      onClick={() => setResponseMessage('')}
                      className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-300 transition-colors"
                    >
                      Clear
                    </button>
                  </div>
                  <ConversationAssistant caseId={selectedCase.id} message={responseMessage} />
                </div>
              </div>

              <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
                <h3 className="font-bold text-gray-900 mb-4">Action Items</h3>
                <div className="space-y-2">
                  {selectedCase.open_actions.map((action, idx) => (
                    <div key={idx} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                      <input type="checkbox" className="mt-1" />
                      <span className="text-sm text-gray-700">{action}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="space-y-6">
              <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="font-bold text-gray-900 text-lg flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-purple-600" />
                    AI Resource Recommendations
                  </h3>
                  <button
                    onClick={getRecommendations}
                    disabled={recommendLoading}
                    className="px-4 py-2 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg text-sm font-medium hover:from-green-700 hover:to-emerald-700 transition-all shadow-md hover:shadow-lg disabled:opacity-50 flex items-center gap-2"
                  >
                    {recommendLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                    {useStreaming ? 'Stream Recommendations' : 'Get Recommendations'}
                  </button>
                </div>

                {/* Streaming text preview for recommendations */}
                {recommendLoading && streamingText && (
                  <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                    <p className="text-sm text-green-900 font-mono whitespace-pre-wrap">{streamingText}</p>
                  </div>
                )}

                {recommendations.length === 0 && !recommendLoading ? (
                  <p className="text-sm text-gray-500 text-center py-8">
                    Click button to find relevant resources
                  </p>
                ) : (
                  <div className="space-y-4">
                    {recommendations.map((rec, idx) => (
                      <div key={idx} className="p-4 bg-white rounded-lg border border-gray-200">
                        <div className="flex items-start justify-between mb-2">
                          <h4 className="font-medium text-gray-900">{rec.resource.name || `Resource ${idx + 1}`}</h4>
                          <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-medium">
                            {Math.round(rec.relevance_score * 100)}% Match
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mb-3">{rec.resource.description}</p>
                        <div className="grid grid-cols-2 gap-2 mb-3 text-xs text-gray-600">
                          {rec.resource.max_amount && (
                            <div className="flex items-center gap-1">
                              <DollarSign className="w-3 h-3" />
                              Up to ${rec.resource.max_amount?.toLocaleString()}
                            </div>
                          )}
                          <div className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {rec.resource.typical_approval_time}
                          </div>
                          <div className="flex items-center gap-1">
                            <TrendingUp className="w-3 h-3" />
                            {Math.round(rec.estimated_success * 100)}% Success
                          </div>
                          <div className="flex items-center gap-1">
                            {rec.resource.application_difficulty}
                          </div>
                        </div>
                        <div className="pt-3 border-t border-gray-200">
                          <p className="text-sm text-gray-700">
                            <strong className="text-gray-900">Why:</strong> {rec.reasoning}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl shadow-md p-6 border border-blue-200">
                <h3 className="font-bold text-gray-900 mb-3 flex items-center gap-2">
                  <AlertCircle className="w-5 h-5 text-blue-600" />
                  Suggested Next Steps
                </h3>
                <div className="space-y-2">
                  <div className="px-4 py-3 bg-white rounded-lg text-sm text-gray-700 border border-blue-100">
                    📞 Schedule a follow-up call to check progress
                  </div>
                  <div className="px-4 py-3 bg-white rounded-lg text-sm text-gray-700 border border-blue-100">
                    📧 Send resource application links via email
                  </div>
                  <div className="px-4 py-3 bg-white rounded-lg text-sm text-gray-700 border border-blue-100">
                    📋 Create a step-by-step action plan document
                  </div>
                  <div className="px-4 py-3 bg-white rounded-lg text-sm text-gray-700 border border-blue-100">
                    🔔 Set reminder for application deadline tracking
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm p-5 border border-gray-200">
                <h3 className="font-medium text-gray-900 mb-3 text-sm">Notes</h3>
                <textarea
                  value={caseNotes[selectedCase.id] || ''}
                  onChange={(e) => setCaseNotes({...caseNotes, [selectedCase.id]: e.target.value})}
                  placeholder="Add private notes about this case..."
                  className="w-full p-3 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 resize-none"
                  rows={4}
                />
                <button
                  onClick={saveNotes}
                  disabled={savingNotes}
                  className="mt-3 px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center gap-2"
                >
                  {savingNotes && <Loader2 className="w-4 h-4 animate-spin" />}
                  Save Notes
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Create Case Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200 flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900">Create New Case</h2>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            
            <div className="p-6 space-y-4">
              {/* Employee Info */}
              <div className="space-y-4">
                <h3 className="font-semibold text-gray-900">Employee Information</h3>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Employee Name *
                  </label>
                  <input
                    type="text"
                    value={newCase.employee_name}
                    onChange={(e) => setNewCase({...newCase, employee_name: e.target.value})}
                    placeholder="John Smith"
                    className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Employer *
                  </label>
                  <input
                    type="text"
                    value={newCase.employer}
                    onChange={(e) => setNewCase({...newCase, employer: e.target.value})}
                    placeholder="Acme Corporation"
                    className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
              
              {/* Financial Snapshot */}
              <div className="space-y-4 pt-4 border-t">
                <h3 className="font-semibold text-gray-900">Financial Snapshot</h3>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Annual Income
                    </label>
                    <input
                      type="number"
                      value={newCase.annual_income}
                      onChange={(e) => setNewCase({...newCase, annual_income: e.target.value})}
                      placeholder="50000"
                      className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Credit Score
                    </label>
                    <input
                      type="number"
                      value={newCase.credit_score}
                      onChange={(e) => setNewCase({...newCase, credit_score: e.target.value})}
                      placeholder="650"
                      className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Savings
                    </label>
                    <input
                      type="number"
                      value={newCase.savings}
                      onChange={(e) => setNewCase({...newCase, savings: e.target.value})}
                      placeholder="1000"
                      className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:
                      ring-blue-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Total Debt
                    </label>
                    <input
                      type="number"
                      value={newCase.total_debt}
                      onChange={(e) => setNewCase({...newCase, total_debt: e.target.value})}
                      placeholder="5000"
                      className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Number of Dependents
                    </label>
                    <input
                      type="number"
                      value={newCase.dependents}
                      onChange={(e) => setNewCase({...newCase, dependents: e.target.value})}
                      placeholder="0"
                      className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
              </div>
            </div>
            
            <div className="p-6 bg-gray-50 border-t border-gray-200 flex justify-end gap-3">
              <button
                onClick={() => setShowCreateModal(false)}
                className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={createCase}
                disabled={creatingCase}
                className="px-6 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors disabled:opacity-50 flex items-center gap-2"
              >
                {creatingCase && <Loader2 className="w-4 h-4 animate-spin" />}
                Create Case
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;