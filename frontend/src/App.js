import React, { useState, useCallback, useRef, useEffect } from 'react';
import { 
  Sparkles, Upload, FileCode, Brain, BarChart3, Settings, 
  CheckCircle2, XCircle, AlertCircle, Zap, Download, 
  ArrowRight, Play, RefreshCw, Eye, Code2, Palette, 
  Layout, Type, Layers, TrendingUp, FileText, 
  ChevronRight, Star, Target, Rocket, Filter, Home,
  Shield, Wand2, Globe, Users, Clock, Award
} from 'lucide-react';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [files, setFiles] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [analysisResults, setAnalysisResults] = useState({});
  const [loading, setLoading] = useState(false);
  const [selectedModels, setSelectedModels] = useState(['gpt-4o']);
  const [selectedIssue, setSelectedIssue] = useState(null);
  const [showIssueModal, setShowIssueModal] = useState(false);
  const [issueModalTab, setIssueModalTab] = useState('code');
  const [remediationResults, setRemediationResults] = useState({});
  const [currentPage, setCurrentPage] = useState('welcome'); // 'welcome', 'upload', 'analyze', 'results'
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Enhanced remediation states
  const [remediationPreviews, setRemediationPreviews] = useState({});
  const [showRemediationModal, setShowRemediationModal] = useState(false);
  const [currentRemediation, setCurrentRemediation] = useState(null);
  const [remediationTab, setRemediationTab] = useState('preview');
  const [appliedRemediations, setAppliedRemediations] = useState({});

  const fileInputRef = useRef(null);
  const isRestoringRef = useRef(false);

  // Scroll to top on page load to prevent auto-scroll
  useEffect(() => {
    window.scrollTo(0, 0);
    // Prevent browser from restoring scroll position
    if ('scrollRestoration' in window.history) {
      window.history.scrollRestoration = 'manual';
    }
  }, []);

  // Restore session from localStorage on mount
  useEffect(() => {
    const restoreSession = async () => {
      const savedSessionId = localStorage.getItem('aesthetic_session_id');
      console.log('Checking for saved session:', savedSessionId);
      
      if (!savedSessionId) {
        console.log('No saved session found');
        return;
      }

      isRestoringRef.current = true;

      try {
        console.log('Fetching session data from backend...');
        const response = await fetch(`${API_BASE}/session/${savedSessionId}`);
        
        if (!response.ok) {
          console.warn('Session not found or expired, clearing localStorage');
          localStorage.removeItem('aesthetic_session_id');
          isRestoringRef.current = false;
          return;
        }

        const sessionData = await response.json();
        console.log('Session data retrieved:', sessionData);
        
        // Restore session state
        setSessionId(savedSessionId);
        setFiles(sessionData.files || []);
        setAnalysisResults(sessionData.analysis_results || {});
        setRemediationResults(sessionData.remediation_results || {});
        
        // Determine which page to show based on session state
        if (sessionData.analysis_results && Object.keys(sessionData.analysis_results).length > 0) {
          console.log('Restoring to results page');
          setCurrentPage('results');
        } else if (sessionData.files && sessionData.files.length > 0) {
          console.log('Restoring to analyze page');
          setCurrentPage('analyze');
        } else {
          console.log('Session restored but no files/results, staying on welcome page');
        }
        
        // Scroll to top after restoring
        setTimeout(() => {
          window.scrollTo(0, 0);
          isRestoringRef.current = false;
        }, 100);
      } catch (error) {
        console.error('Failed to restore session:', error);
        localStorage.removeItem('aesthetic_session_id');
        isRestoringRef.current = false;
      }
    };

    restoreSession();
  }, []);

  // Save sessionId to localStorage whenever it changes
  useEffect(() => {
    if (sessionId) {
      localStorage.setItem('aesthetic_session_id', sessionId);
      console.log('SessionId saved to localStorage:', sessionId);
    } else {
      // Only remove if we're not in the middle of restoring (to prevent clearing during initial mount)
      if (!isRestoringRef.current) {
        localStorage.removeItem('aesthetic_session_id');
        console.log('SessionId removed from localStorage');
      }
    }
  }, [sessionId]);

  const availableModels = [
    { id: 'gpt-4o', name: 'GPT-4o', icon: Brain, color: 'from-blue-500 to-cyan-500', description: 'Advanced reasoning' },
    { id: 'claude-opus-4', name: 'Claude Opus 4', icon: Sparkles, color: 'from-purple-500 to-pink-500', description: 'Strong analytics' },
    { id: 'deepseek-v3', name: 'DeepSeek-V3', icon: Code2, color: 'from-green-500 to-emerald-500', description: 'Code-focused' },
    { id: 'llama-maverick', name: 'LLaMA Maverick', icon: Rocket, color: 'from-orange-500 to-red-500', description: 'Alternative view' }
  ];

  const categoryIcons = {
    color: Palette,
    spacing: Layout,
    typography: Type,
    hierarchy: Layers,
    consistency: Target,
    modern_patterns: Star,
    balance: TrendingUp,
    clutter: Filter
  };

  const handleFileUpload = useCallback(async (event) => {
    const uploadedFiles = Array.from(event.target.files);
    if (uploadedFiles.length === 0) return;

    setLoading(true);
    try {
      const formData = new FormData();
      uploadedFiles.forEach(file => {
        formData.append('files', file);
      });

      const response = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Upload failed');

      const result = await response.json();
      const newSessionId = result.session_id;
      console.log('New session created:', newSessionId);
      setSessionId(newSessionId);
      setFiles(result.files);
      // Clear previous analysis results when starting a new session
      setAnalysisResults({});
      setRemediationResults({});
      setCurrentPage('analyze');
      // sessionId will be saved to localStorage via useEffect
    } catch (error) {
      alert(`Upload failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleAnalysis = useCallback(async () => {
    if (!sessionId || selectedModels.length === 0) return;

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          models: selectedModels,
          analysis_type: 'detection'
        }),
      });

      if (!response.ok) throw new Error('Analysis failed');

      const result = await response.json();
      setAnalysisResults(result.results);
      setCurrentPage('results');
    } catch (error) {
      alert(`Analysis failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  }, [sessionId, selectedModels]);

  const handleRemediationPreview = useCallback(async (issueId, model, issue) => {
    if (!sessionId) return;
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/remediate/preview`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          issue_id: issueId,
          model: model
        }),
      });

      if (!response.ok) throw new Error('Remediation preview failed');
      const result = await response.json();

      setRemediationPreviews(prev => ({ ...prev, [issueId]: result }));
      setCurrentRemediation(result);
      setShowRemediationModal(true);
    } catch (error) {
      alert(`Remediation preview failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  const downloadReport = useCallback(async () => {
    if (!sessionId) return;
    window.open(`${API_BASE}/report/${sessionId}`, '_blank');
  }, [sessionId]);

  const downloadFixedCode = useCallback(async () => {
    if (!sessionId) return;
    window.open(`${API_BASE}/fixed-code/${sessionId}`, '_blank');
  }, [sessionId]);

  const getAllIssues = () => {
    const allIssues = [];
    Object.entries(analysisResults).forEach(([model, results]) => {
      if (Array.isArray(results)) {
        results.forEach(fileResult => {
          fileResult.issues?.forEach(issue => {
              allIssues.push({
                ...issue,
                model,
              fileName: fileResult.file_info?.name || 'Unknown'
              });
            });
        });
      }
    });
    return allIssues;
  };

  const getCategoryColor = (category) => {
    const colors = {
      color: 'badge-critical',
      spacing: 'badge-high',
      typography: 'badge-medium',
      hierarchy: 'badge-high',
      consistency: 'badge-medium',
      modern_patterns: 'badge-low',
      balance: 'badge-medium',
      clutter: 'badge-high'
    };
    return colors[category] || 'badge-low';
  };

  const getSeverityColor = (severity) => {
    const colors = {
      critical: 'badge-critical',
      high: 'badge-high',
      medium: 'badge-medium',
      low: 'badge-low'
    };
    return colors[severity] || 'badge-medium';
  };

  const openIssueModal = (issue, model, fileName) => {
    setSelectedIssue({ ...issue, model, fileName });
    setShowIssueModal(true);
  };

  // Start a new analysis - clear everything and reset
  const handleStartNewAnalysis = useCallback(() => {
    // Clear all state
    setSessionId(null);
    setFiles([]);
    setAnalysisResults({});
    setRemediationResults({});
    setSelectedIssue(null);
    setShowIssueModal(false);
    setShowRemediationModal(false);
    setCurrentRemediation(null);
    setAppliedRemediations({});
    
    // Clear localStorage
    localStorage.removeItem('aesthetic_session_id');
    
    // Reset to welcome page
    setCurrentPage('welcome');
    
    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    
    // Scroll to top
    window.scrollTo(0, 0);
    
    console.log('Started new analysis - all data cleared');
  }, []);

  // Sidebar Component
  const Sidebar = () => (
    <div className={`sidebar ${sidebarOpen ? '' : 'translate-x-[-100%]'}`}>
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[hsl(var(--primary))] to-[hsl(var(--secondary))] flex items-center justify-center">
            <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
            <h1 className="text-xl font-bold text-[hsl(var(--text-primary))]">Aesthetics</h1>
            <p className="text-xs text-[hsl(var(--text-secondary))]">Analyzer</p>
                </div>
              </div>
          </div>

      <nav className="space-y-2">
        <div 
          className={`sidebar-item ${currentPage === 'welcome' ? 'active' : ''}`}
          onClick={() => setCurrentPage('welcome')}
        >
          <Home className="w-5 h-5" />
          <span>Home</span>
        </div>
        {(sessionId || files.length > 0) && (
          <div 
            className="sidebar-item"
            onClick={handleStartNewAnalysis}
            style={{ cursor: 'pointer' }}
          >
            <RefreshCw className="w-5 h-5" />
            <span>Start New Analysis</span>
          </div>
        )}
        <div 
          className={`sidebar-item ${currentPage === 'upload' ? 'active' : ''}`}
          onClick={() => setCurrentPage('upload')}
        >
          <Upload className="w-5 h-5" />
          <span>Upload Files</span>
        </div>
        <div 
          className={`sidebar-item ${currentPage === 'analyze' ? 'active' : ''}`}
          onClick={() => sessionId && setCurrentPage('analyze')}
        >
          <Settings className="w-5 h-5" />
          <span>Configure</span>
        </div>
        <div 
          className={`sidebar-item ${currentPage === 'results' ? 'active' : ''}`}
          onClick={() => Object.keys(analysisResults).length > 0 && setCurrentPage('results')}
        >
          <BarChart3 className="w-5 h-5" />
          <span>Results</span>
        </div>
      </nav>

      {files.length > 0 && (
        <div className="mt-8 p-4 glass rounded-xl">
          <div className="text-xs text-[hsl(var(--text-secondary))] mb-2">Uploaded Files</div>
          <div className="text-lg font-bold text-[hsl(var(--text-primary))]">{files.length}</div>
                        </div>
                      )}
      </div>
    );

  // Welcome Page
  const WelcomePage = () => {
    const stats = [
      { icon: FileCode, value: '10,847', label: 'Files Analyzed', color: 'from-blue-400 via-cyan-400 to-blue-500', accent: 'text-blue-400' },
      { icon: Users, value: '5,231', label: 'Active Users', color: 'from-purple-400 via-pink-400 to-purple-500', accent: 'text-purple-400' },
      { icon: Zap, value: '52,109', label: 'Issues Fixed', color: 'from-emerald-400 via-green-400 to-emerald-500', accent: 'text-emerald-400' },
      { icon: Award, value: '99.2%', label: 'Accuracy Rate', color: 'from-amber-400 via-orange-400 to-amber-500', accent: 'text-amber-400' }
    ];

    const features = [
      {
        icon: Brain,
        title: 'Multi-LLM Analysis',
        description: 'Leverage GPT-4o, Claude Opus 4, DeepSeek-V3, and LLaMA Maverick for comprehensive design analysis',
        color: 'from-blue-500 to-cyan-500'
      },
      {
        icon: Palette,
        title: 'Aesthetic Detection',
        description: 'Identify color harmony, spacing issues, typography problems, and visual hierarchy violations',
        color: 'from-purple-500 to-pink-500'
      },
      {
        icon: Wand2,
        title: 'AI-Powered Fixes',
        description: 'Get intelligent remediation suggestions with preview, validation, and rollback capabilities',
        color: 'from-green-500 to-emerald-500'
      },
      {
        icon: Shield,
        title: 'Quality Assurance',
        description: 'Validate fixes with syntax checking, design re-analysis, and confidence scoring',
        color: 'from-orange-500 to-red-500'
      },
      {
        icon: BarChart3,
        title: 'Detailed Reports',
        description: 'Generate comprehensive PDF reports with metrics, charts, and actionable recommendations',
        color: 'from-indigo-500 to-purple-500'
      },
      {
        icon: Globe,
        title: 'Multi-Format Support',
        description: 'Analyze HTML, CSS, JS, JSX, TSX, XML, C++, Java, Swift, and more',
        color: 'from-teal-500 to-cyan-500'
      }
    ];

    return (
      <div className="max-w-7xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-24 animate-fade-in">
          <div className="relative inline-block mb-10">
            <div className="absolute inset-0 blur-2xl bg-gradient-to-br from-[hsl(var(--primary)/0.3)] to-[hsl(var(--secondary)/0.3)] rounded-full"></div>
            <div className="relative inline-flex items-center justify-center w-28 h-28 rounded-2xl bg-gradient-to-br from-[hsl(var(--primary))] via-[hsl(var(--secondary))] to-[hsl(var(--accent))] shadow-2xl animate-float">
              <Sparkles className="w-14 h-14 text-white" strokeWidth={1.5} />
            </div>
          </div>
          <div className="mb-6">
            <span className="inline-block px-4 py-2 rounded-full bg-[hsl(var(--primary)/0.1)] border border-[hsl(var(--primary)/0.2)] text-[hsl(var(--primary))] text-sm font-medium mb-6">
              Premium Design Analysis Platform
            </span>
          </div>
          <h1 className="text-7xl font-light text-[hsl(var(--text-primary))] mb-6 tracking-tight leading-tight">
            Elevate Your Code's
            <br />
            <span className="font-normal bg-gradient-to-r from-[hsl(var(--primary))] via-[hsl(var(--secondary))] to-[hsl(var(--accent))] bg-clip-text text-transparent">
              Aesthetic Excellence
            </span>
          </h1>
          <p className="text-xl text-[hsl(var(--text-secondary))] mb-12 max-w-2xl mx-auto leading-relaxed font-light">
            Professional-grade design analysis powered by advanced AI. Transform your codebase into visually stunning, 
            user-centric interfaces with intelligent detection and remediation.
          </p>
          <div className="flex items-center justify-center gap-4">
            <button
              onClick={() => setCurrentPage('upload')}
              className="btn-primary-modern btn-modern text-base px-10 py-4 font-medium"
            >
              <Upload className="w-4 h-4" />
              Begin Analysis
              <ArrowRight className="w-4 h-4" />
            </button>
            <button
              onClick={() => setCurrentPage('upload')}
              className="btn-secondary-modern btn-modern text-base px-10 py-4 font-medium"
            >
              <Eye className="w-4 h-4" />
              Explore Features
            </button>
          </div>
        </div>

        {/* Statistics Section */}
        <div className="mb-20">
          <div className="text-center mb-12">
            <div className="inline-block w-12 h-px bg-gradient-to-r from-transparent via-[hsl(var(--primary)/0.5)] to-transparent mb-4"></div>
            <h2 className="text-sm uppercase tracking-widest text-[hsl(var(--text-secondary))] font-medium mb-2">
              Trusted by Industry Leaders
            </h2>
            <p className="text-[hsl(var(--text-secondary))] text-sm font-light">
              Proven results across thousands of projects
            </p>
          </div>
          <div className="grid-modern grid-4">
            {stats.map((stat, index) => {
              const Icon = stat.icon;
              return (
                <div
                  key={index}
                  className="stat-card animate-slide-in-up"
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <div className="flex items-center justify-between mb-6">
                    <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${stat.color} flex items-center justify-center shadow-lg`}>
                      <Icon className="w-6 h-6 text-white" strokeWidth={1.5} />
                    </div>
                    <div className={`w-2 h-2 rounded-full ${stat.accent} opacity-60`}></div>
                  </div>
                  <div className="stat-value mb-3">{stat.value}</div>
                  <div className="text-[hsl(var(--text-secondary))] text-sm font-light tracking-wide uppercase text-xs">
                    {stat.label}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Features Section */}
        <div className="mb-20">
          <div className="text-center mb-16">
            <div className="inline-block w-12 h-px bg-gradient-to-r from-transparent via-[hsl(var(--primary)/0.5)] to-transparent mb-6"></div>
            <h2 className="text-5xl font-light text-[hsl(var(--text-primary))] mb-6 tracking-tight">
              Enterprise-Grade
              <br />
              <span className="font-normal">Capabilities</span>
            </h2>
            <p className="text-[hsl(var(--text-secondary))] text-lg max-w-2xl mx-auto font-light leading-relaxed">
              Comprehensive tools designed for professional development teams
            </p>
          </div>
          <div className="grid-modern grid-3">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div
                  key={index}
                  className="modern-card animate-slide-in-up group"
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <div className="flex items-start gap-4 mb-4">
                    <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${feature.color} flex items-center justify-center shadow-lg flex-shrink-0 group-hover:scale-110 transition-transform duration-300`}>
                      <Icon className="w-7 h-7 text-white" strokeWidth={1.5} />
                    </div>
                    <div className="flex-1 pt-1">
                      <h3 className="text-xl font-semibold text-[hsl(var(--text-primary))] mb-3 tracking-tight">{feature.title}</h3>
                      <p className="text-[hsl(var(--text-secondary))] leading-relaxed font-light text-sm">
                        {feature.description}
                      </p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* CTA Section */}
        <div className="modern-card text-center relative overflow-hidden mb-20">
          <div className="absolute inset-0 bg-gradient-to-br from-[hsl(var(--primary)/0.08)] via-[hsl(var(--secondary)/0.06)] to-[hsl(var(--accent)/0.08)]"></div>
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,hsl(var(--primary)/0.05),transparent)]"></div>
          <div className="relative z-10 py-12">
            <div className="inline-block w-16 h-px bg-gradient-to-r from-transparent via-[hsl(var(--primary)/0.4)] to-transparent mb-8"></div>
            <h2 className="text-4xl font-light text-[hsl(var(--text-primary))] mb-6 tracking-tight">
              Ready to Transform
              <br />
              <span className="font-normal">Your Codebase?</span>
            </h2>
            <p className="text-[hsl(var(--text-secondary))] text-lg mb-10 max-w-2xl mx-auto font-light leading-relaxed">
              Experience the power of AI-driven design analysis. Upload your files and receive 
              comprehensive insights with intelligent remediation suggestions.
            </p>
            <button
              onClick={() => setCurrentPage('upload')}
              className="btn-primary-modern btn-modern text-base px-12 py-5 font-medium"
            >
              <Upload className="w-4 h-4" />
              Start Your Analysis
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid-modern grid-3">
          <div className="modern-card text-center group">
            <div className="w-16 h-16 mx-auto mb-6 rounded-xl bg-gradient-to-br from-[hsl(var(--primary)/0.2)] to-[hsl(var(--secondary)/0.2)] flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
              <Clock className="w-8 h-8 text-[hsl(var(--primary))]" strokeWidth={1.5} />
            </div>
            <div className="text-3xl font-light text-[hsl(var(--text-primary))] mb-2 tracking-tight">Fast</div>
            <div className="text-[hsl(var(--text-secondary))] text-sm font-light uppercase tracking-wider">Analysis in seconds</div>
          </div>
          <div className="modern-card text-center group">
            <div className="w-16 h-16 mx-auto mb-6 rounded-xl bg-gradient-to-br from-[hsl(var(--success)/0.2)] to-[hsl(var(--accent)/0.2)] flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
              <Shield className="w-8 h-8 text-[hsl(var(--success))]" strokeWidth={1.5} />
            </div>
            <div className="text-3xl font-light text-[hsl(var(--text-primary))] mb-2 tracking-tight">Secure</div>
            <div className="text-[hsl(var(--text-secondary))] text-sm font-light uppercase tracking-wider">Enterprise-grade security</div>
          </div>
          <div className="modern-card text-center group">
            <div className="w-16 h-16 mx-auto mb-6 rounded-xl bg-gradient-to-br from-[hsl(var(--accent)/0.2)] to-[hsl(var(--primary)/0.2)] flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
              <TrendingUp className="w-8 h-8 text-[hsl(var(--accent))]" strokeWidth={1.5} />
            </div>
            <div className="text-3xl font-light text-[hsl(var(--text-primary))] mb-2 tracking-tight">Precise</div>
            <div className="text-[hsl(var(--text-secondary))] text-sm font-light uppercase tracking-wider">99.2% accuracy rate</div>
          </div>
        </div>
      </div>
    );
  };

  // Upload Page
  const UploadPage = () => (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8 animate-fade-in">
        <h2 className="text-4xl font-bold text-[hsl(var(--text-primary))] mb-3">Upload Your Code</h2>
        <p className="text-[hsl(var(--text-secondary))] text-lg">
          Drop your files or click to browse. We support HTML, CSS, JS, JSX, TSX, XML, and more.
              </p>
            </div>

      <div className="modern-card animate-slide-in-up">
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".html,.htm,.css,.js,.jsx,.ts,.tsx,.xml,.cpp,.c,.h,.java,.kt,.swift,.zip"
                onChange={handleFileUpload}
                className="hidden"
              />
        
        <div
                onClick={() => fileInputRef.current?.click()}
          className="upload-zone"
        >
          <div className="relative z-10">
            <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-[hsl(var(--primary))] to-[hsl(var(--secondary))] flex items-center justify-center animate-float">
              <Upload className="w-10 h-10 text-white" />
                  </div>
            <h3 className="text-2xl font-bold text-[hsl(var(--text-primary))] mb-2">
              {loading ? 'Uploading...' : 'Drop files here or click to browse'}
            </h3>
            <p className="text-[hsl(var(--text-secondary))]">
              Supports HTML, CSS, JS, XML, C++, Java, Swift, ZIP
            </p>
                  </div>
                </div>

              {files.length > 0 && (
          <div className="mt-6 space-y-2">
                    {files.map((file, index) => (
              <div key={index} className="flex items-center gap-3 p-3 glass rounded-xl">
                <FileCode className="w-5 h-5 text-[hsl(var(--primary))]" />
                <div className="flex-1">
                  <div className="text-[hsl(var(--text-primary))] font-medium">{file.name}</div>
                  <div className="text-xs text-[hsl(var(--text-secondary))]">
                    {(file.size / 1024).toFixed(2)} KB
                      </div>
                  </div>
                <CheckCircle2 className="w-5 h-5 text-[hsl(var(--success))]" />
              </div>
            ))}
                </div>
              )}
            </div>
    </div>
  );

  // Analyze Page
  const AnalyzePage = () => (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8 animate-fade-in">
        <h2 className="text-4xl font-bold text-[hsl(var(--text-primary))] mb-3">Configure Analysis</h2>
        <p className="text-[hsl(var(--text-secondary))] text-lg">
          Select AI models and start analyzing your code for aesthetic issues
        </p>
      </div>

      <div className="grid-modern grid-2 mb-8">
        {availableModels.map((model, index) => {
          const Icon = model.icon;
          return (
            <div
              key={model.id}
              className="modern-card animate-slide-in-up"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className="flex items-start gap-4">
                <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${model.color} flex items-center justify-center flex-shrink-0`}>
                  <Icon className="w-7 h-7 text-white" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-xl font-bold text-[hsl(var(--text-primary))]">{model.name}</h3>
                    <input
                      type="checkbox"
                      checked={selectedModels.includes(model.id)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedModels([...selectedModels, model.id]);
                        } else {
                          setSelectedModels(selectedModels.filter(m => m !== model.id));
                        }
                      }}
                      className="w-5 h-5 rounded accent-[hsl(var(--primary))]"
                    />
                    </div>
                  <p className="text-[hsl(var(--text-secondary))] text-sm">{model.description}</p>
              </div>
                </div>
            </div>
          );
        })}
              </div>

      <div className="modern-card">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-2xl font-bold text-[hsl(var(--text-primary))] mb-2">Ready to Analyze</h3>
            <p className="text-[hsl(var(--text-secondary))]">
              {files.length} files • {selectedModels.length} models selected
            </p>
          </div>
              <button
                onClick={handleAnalysis}
                disabled={!sessionId || selectedModels.length === 0 || loading}
            className="btn-primary-modern btn-modern text-lg px-8"
          >
            {loading ? (
              <>
                <RefreshCw className="w-5 h-5 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Play className="w-5 h-5" />
                Start Analysis
              </>
            )}
              </button>
            </div>
          </div>
        </div>
  );

  // Results Page
  const ResultsPage = () => {
    const allIssues = getAllIssues();
    const totalIssues = allIssues.length;
    
    const stats = {
      critical: allIssues.filter(i => i.severity === 'critical').length,
      high: allIssues.filter(i => i.severity === 'high').length,
      medium: allIssues.filter(i => i.severity === 'medium').length,
      low: allIssues.filter(i => i.severity === 'low').length,
    };

    const categoryStats = {};
    allIssues.forEach(issue => {
      categoryStats[issue.category] = (categoryStats[issue.category] || 0) + 1;
    });

    return (
      <div className="space-y-8">
        {/* Stats Overview */}
        <div className="grid-modern grid-4">
          <div className="stat-card animate-slide-in-up">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[hsl(var(--danger))] to-[hsl(var(--warning))] flex items-center justify-center">
                <AlertCircle className="w-6 h-6 text-white" />
      </div>
              <span className="badge-modern badge-critical">{stats.critical}</span>
    </div>
            <div className="stat-value">{stats.critical}</div>
            <div className="text-[hsl(var(--text-secondary))] text-sm mt-1">Critical Issues</div>
          </div>

          <div className="stat-card animate-slide-in-up" style={{ animationDelay: '0.1s' }}>
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[hsl(var(--warning))] to-[hsl(var(--accent))] flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
              <span className="badge-modern badge-high">{stats.high}</span>
            </div>
            <div className="stat-value">{stats.high}</div>
            <div className="text-[hsl(var(--text-secondary))] text-sm mt-1">High Priority</div>
            </div>

          <div className="stat-card animate-slide-in-up" style={{ animationDelay: '0.2s' }}>
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[hsl(var(--accent))] to-[hsl(var(--primary))] flex items-center justify-center">
                <BarChart3 className="w-6 h-6 text-white" />
          </div>
              <span className="badge-modern badge-medium">{stats.medium}</span>
        </div>
            <div className="stat-value">{stats.medium}</div>
            <div className="text-[hsl(var(--text-secondary))] text-sm mt-1">Medium</div>
          </div>

          <div className="stat-card animate-slide-in-up" style={{ animationDelay: '0.3s' }}>
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[hsl(var(--primary))] to-[hsl(var(--secondary))] flex items-center justify-center">
                <Target className="w-6 h-6 text-white" />
              </div>
              <span className="badge-modern badge-low">{stats.low}</span>
            </div>
            <div className="stat-value">{stats.low}</div>
            <div className="text-[hsl(var(--text-secondary))] text-sm mt-1">Low Priority</div>
          </div>
        </div>

        {/* Action Bar */}
        <div className="modern-card">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-2xl font-bold text-[hsl(var(--text-primary))] mb-1">
                {totalIssues} Issues Found
              </h3>
              <p className="text-[hsl(var(--text-secondary))]">
                Review and fix aesthetic issues in your code
              </p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={handleStartNewAnalysis}
                className="btn-secondary-modern btn-modern"
              >
                <RefreshCw className="w-4 h-4" />
                New Analysis
              </button>
              <button onClick={downloadReport} className="btn-secondary-modern btn-modern">
                <FileText className="w-4 h-4" />
                Report
              </button>
              <button onClick={downloadFixedCode} className="btn-success-modern btn-modern">
                <Download className="w-4 h-4" />
                Download
              </button>
                  </div>
            </div>
          </div>

          {/* Issues List */}
        <div className="space-y-4">
          {allIssues.length === 0 ? (
            <div className="modern-card text-center py-16">
              <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-gradient-to-br from-[hsl(var(--success))] to-[hsl(var(--accent))] flex items-center justify-center">
                <CheckCircle2 className="w-10 h-10 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-[hsl(var(--text-primary))] mb-2">Perfect! No Issues Found</h3>
              <p className="text-[hsl(var(--text-secondary))]">
                Your code meets high aesthetic standards
              </p>
            </div>
          ) : (
            allIssues.map((issue, index) => {
              const CategoryIcon = categoryIcons[issue.category] || AlertCircle;
              return (
                <div
                  key={index}
                  className="issue-card animate-slide-in-up"
                  style={{ animationDelay: `${index * 0.05}s` }}
                >
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[hsl(var(--primary))] to-[hsl(var(--secondary))] flex items-center justify-center flex-shrink-0">
                      <CategoryIcon className="w-6 h-6 text-white" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2 flex-wrap">
                        <h4 className="text-lg font-bold text-[hsl(var(--text-primary))]">
                          {issue.principle_id || issue.wcag_guideline || 'Aesthetic Issue'}
                        </h4>
                        <span className={`badge-modern ${getSeverityColor(issue.severity)}`}>
                          {issue.severity || 'medium'}
                        </span>
                        <span className={`badge-modern ${getCategoryColor(issue.category)}`}>
                          {issue.category}
                        </span>
                      </div>
                      <p className="text-[hsl(var(--text-secondary))] mb-3">
                        {issue.description}
                      </p>
                      <div className="flex items-center gap-4 text-sm text-[hsl(var(--text-secondary))] mb-4">
                        <span className="flex items-center gap-1">
                          <FileCode className="w-4 h-4" />
                          {issue.fileName}
                        </span>
                        {issue.line_numbers && (
                          <span className="flex items-center gap-1">
                            <Code2 className="w-4 h-4" />
                            Lines {issue.line_numbers.join(', ')}
                          </span>
                        )}
                      </div>
                      <div className="flex gap-2">
                      <button
                        onClick={() => openIssueModal(issue, issue.model, issue.fileName)}
                          className="btn-secondary-modern btn-modern"
                      >
                          <Eye className="w-4 h-4" />
                          View Details
                      </button>
                              <button
                          onClick={() => handleRemediationPreview(issue.issue_id, issue.model, issue)}
                          className="btn-primary-modern btn-modern"
                              >
                          <Zap className="w-4 h-4" />
                          Smart Fix
                              </button>
                          </div>
                        </div>
                      </div>
                    </div>
              );
            })
          )}
                  </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen relative">
      <div className="animated-bg"></div>
      
      <Sidebar />
      
      <div className="main-content">
        {currentPage === 'welcome' && <WelcomePage />}
        {currentPage === 'upload' && <UploadPage />}
        {currentPage === 'analyze' && <AnalyzePage />}
        {currentPage === 'results' && <ResultsPage />}
      </div>

      {/* Issue Modal */}
      {showIssueModal && selectedIssue && (
        <div className="modal-overlay" onClick={() => setShowIssueModal(false)}>
          <div className="modal-content w-full max-w-4xl" onClick={(e) => e.stopPropagation()}>
            <div className="p-6 border-b border-[hsl(var(--text-primary)/0.1)]">
              <div className="flex items-center justify-between">
                <h3 className="text-2xl font-bold text-[hsl(var(--text-primary))]">
                  {selectedIssue.principle_id || 'Issue Details'}
                </h3>
                        <button
                  onClick={() => setShowIssueModal(false)}
                  className="w-8 h-8 rounded-lg hover:bg-[hsl(var(--bg-tertiary))] flex items-center justify-center"
                        >
                  <XCircle className="w-5 h-5 text-[hsl(var(--text-secondary))]" />
                        </button>
                      </div>
            </div>
            <div className="p-6 overflow-y-auto max-h-[70vh]">
              <div className="space-y-4">
                <div>
                  <div className="text-sm text-[hsl(var(--text-secondary))] mb-1">Description</div>
                  <div className="text-[hsl(var(--text-primary))]">{selectedIssue.description}</div>
                </div>
                {selectedIssue.code_snippet && (
                  <div>
                    <div className="text-sm text-[hsl(var(--text-secondary))] mb-1">Code Snippet</div>
                    <pre className="p-4 glass rounded-xl text-sm text-[hsl(var(--text-primary))] overflow-x-auto bg-[hsl(var(--bg-tertiary))]">
                      {selectedIssue.code_snippet}
                    </pre>
                  </div>
                )}
              </div>
            </div>
          </div>
                    </div>
                  )}

      {/* Remediation Modal */}
      {showRemediationModal && currentRemediation && (
        <div className="modal-overlay" onClick={() => setShowRemediationModal(false)}>
          <div className="modal-content w-full max-w-4xl" onClick={(e) => e.stopPropagation()}>
            <div className="p-6 border-b border-[hsl(var(--text-primary)/0.1)]">
                      <div className="flex items-center justify-between">
                <h3 className="text-2xl font-bold text-[hsl(var(--text-primary))]">Remediation Preview</h3>
                        <button
                  onClick={() => setShowRemediationModal(false)}
                  className="w-8 h-8 rounded-lg hover:bg-[hsl(var(--bg-tertiary))] flex items-center justify-center"
                >
                  <XCircle className="w-5 h-5 text-[hsl(var(--text-secondary))]" />
                        </button>
                      </div>
                    </div>
            <div className="p-6 overflow-y-auto max-h-[70vh]">
              {currentRemediation.changes && (
                <div className="space-y-4">
                  {currentRemediation.changes.map((change, idx) => (
                    <div key={idx} className="glass rounded-xl p-4">
                      <div className="text-sm text-[hsl(var(--text-secondary))] mb-2">Line {change.line_number}</div>
                      <div className="space-y-2">
                        <div>
                          <div className="text-xs text-red-600 mb-1">Original</div>
                          <pre className="p-2 bg-[hsl(var(--bg-tertiary))] rounded text-xs text-[hsl(var(--text-primary))]">{change.original}</pre>
                        </div>
                        <ArrowRight className="w-4 h-4 text-[hsl(var(--primary))] mx-auto" />
                        <div>
                          <div className="text-xs text-green-600 mb-1">Fixed</div>
                          <pre className="p-2 bg-[hsl(var(--bg-tertiary))] rounded text-xs text-[hsl(var(--text-primary))]">{change.fixed}</pre>
                </div>
            </div>
          </div>
                  ))}
        </div>
              )}
      </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
