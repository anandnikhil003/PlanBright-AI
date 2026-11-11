import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { lessonPlannerApi, downloadBlob, type GenerateLessonPlanRequest, type LessonPlanHistoryItem, type LessonPlanDetail, type SSEEvent } from '../api/lessonPlanner';

export function LessonPlannerPage() {
  const { token, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  // Redirect if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);

  // Form state
  const [formData, setFormData] = useState<GenerateLessonPlanRequest>({
    grade_level: '',
    topic: '',
    additional_criteria: '',
    standards: '',
  });

  // Generation state
  const [generating, setGenerating] = useState(false);
  const [currentLessonPlanId, setCurrentLessonPlanId] = useState<string | null>(null);
  const [streamingContent, setStreamingContent] = useState('');
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  // History state
  const [history, setHistory] = useState<LessonPlanHistoryItem[]>([]);
  const [selectedLessonPlan, setSelectedLessonPlan] = useState<LessonPlanDetail | null>(null);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [showHistory, setShowHistory] = useState(true);

  // Expanded sections state
  const [expandingSection, setExpandingSection] = useState<string | null>(null);
  const [expandQuery, setExpandQuery] = useState('');

  // Quick actions state
  const [quickActionLoading, setQuickActionLoading] = useState<string | null>(null);
  const [quickActionContent, setQuickActionContent] = useState<{ id: string; content: string; action: string } | null>(null);

  // Refs
  const streamingContentRef = useRef<HTMLDivElement>(null);

  // Load history on mount
  useEffect(() => {
    loadHistory();
  }, []);

  // Auto-scroll streaming content
  useEffect(() => {
    if (streamingContentRef.current && generating) {
      streamingContentRef.current.scrollTop = streamingContentRef.current.scrollHeight;
    }
  }, [streamingContent, generating]);

  const loadHistory = async () => {
    if (!token) return;
    setHistoryLoading(true);
    try {
      const data = await lessonPlannerApi.getHistory(token);
      setHistory(data);
    } catch (err) {
      console.error('Failed to load history:', err);
    } finally {
      setHistoryLoading(false);
    }
  };

  const handleGenerate = async () => {
    if (!token) return;
    
    // Validate form
    if (!formData.grade_level || !formData.topic) {
      setError('Grade level and topic are required');
      return;
    }

    setGenerating(true);
    setError('');
    setSuccessMessage('');
    setStreamingContent('');
    setCurrentLessonPlanId(null);

    try {
      await lessonPlannerApi.generateLessonPlan(
        formData,
        token,
        (event: SSEEvent) => {
          if (event.type === 'id') {
            setCurrentLessonPlanId(event.id);
          } else if (event.type === 'chunk') {
            setStreamingContent(prev => prev + event.chunk);
          } else if (event.type === 'suggested_prompts') {
            // Could show suggested prompts
            console.log('Suggested prompts:', event.suggested_prompts);
          } else if (event.type === 'error') {
            setError(event.error);
          }
        }
      );

      setSuccessMessage('Lesson plan generated successfully!');
      loadHistory(); // Refresh history
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate lesson plan');
    } finally {
      setGenerating(false);
    }
  };

  const handleLoadLessonPlan = async (id: string) => {
    if (!token) return;
    try {
      const data = await lessonPlannerApi.getLessonPlan(id, token);
      setSelectedLessonPlan(data);
    } catch (err) {
      console.error('Failed to load lesson plan:', err);
      setError('Failed to load lesson plan');
    }
  };

  const handleExpandSection = async (lessonPlanId: string) => {
    if (!token || !expandQuery.trim()) return;
    
    setExpandingSection(lessonPlanId);
    try {
      await lessonPlannerApi.expandSection({ id: lessonPlanId, query: expandQuery }, token);
      // Refresh the lesson plan to show expanded section
      await handleLoadLessonPlan(lessonPlanId);
      setExpandQuery('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to expand section');
    } finally {
      setExpandingSection(null);
    }
  };

  const handleQuickAction = async (action: string, lessonPlanId: string) => {
    if (!token) return;
    
    setQuickActionLoading(action);
    setQuickActionContent({ id: lessonPlanId, content: '', action });
    
    try {
      await lessonPlannerApi.quickAction(lessonPlanId, action, token, (event: SSEEvent) => {
        if (event.type === 'chunk') {
          setQuickActionContent(prev => prev ? { ...prev, content: prev.content + event.chunk } : null);
        } else if (event.type === 'id') {
          // New ID for the quick action result
        }
      });
      // Refresh the lesson plan
      await handleLoadLessonPlan(lessonPlanId);
    } catch (err) {
      setError(err instanceof Error ? err.message : `Failed to ${action}`);
    } finally {
      setQuickActionLoading(null);
      setQuickActionContent(null);
    }
  };

  const handleTranslate = async (lessonPlanId: string, language: string) => {
    if (!token) return;
    
    setQuickActionLoading(`translate-${language}`);
    setQuickActionContent({ id: lessonPlanId, content: '', action: `translate to ${language}` });
    
    try {
      await lessonPlannerApi.translate(lessonPlanId, { target_language: language }, token, (event: SSEEvent) => {
        if (event.type === 'chunk') {
          setQuickActionContent(prev => prev ? { ...prev, content: prev.content + event.chunk } : null);
        }
      });
      await handleLoadLessonPlan(lessonPlanId);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Translation failed');
    } finally {
      setQuickActionLoading(null);
      setQuickActionContent(null);
    }
  };

  const handleDownload = async (type: 'markdown' | 'pdf' | 'docx', lessonPlanId: string) => {
    if (!token) return;
    try {
      let blob: Blob;
      if (type === 'markdown') blob = await lessonPlannerApi.downloadMarkdown(lessonPlanId, token);
      else if (type === 'pdf') blob = await lessonPlannerApi.downloadPdf(lessonPlanId, token);
      else blob = await lessonPlannerApi.downloadDocx(lessonPlanId, token);
      
      const ext = type === 'markdown' ? 'md' : type;
      downloadBlob(blob, `lesson-plan-${lessonPlanId.slice(0, 8)}.${ext}`);
      setSuccessMessage(`Downloaded as ${type.toUpperCase()}`);
    } catch (err) {
      setError('Download failed');
    }
  };

  const handleFavorite = async (id: string, currentlyFavorite: boolean) => {
    if (!token) return;
    try {
      if (currentlyFavorite) {
        await lessonPlannerApi.unfavorite(id, token);
      } else {
        await lessonPlannerApi.favorite(id, token);
      }
      loadHistory();
      if (selectedLessonPlan?.lesson_plan_id === id) {
        handleLoadLessonPlan(id);
      }
    } catch (err) {
      setError('Failed to update favorite');
    }
  };

  const handleDelete = async (id: string) => {
    if (!token) return;
    if (!confirm('Are you sure you want to delete this lesson plan?')) return;
    
    try {
      await lessonPlannerApi.deleteHistory(id, token);
      loadHistory();
      if (selectedLessonPlan?.lesson_plan_id === id) {
        setSelectedLessonPlan(null);
      }
    } catch (err) {
      setError('Failed to delete lesson plan');
    }
  };

  const clearError = () => setError('');
  const clearSuccess = () => setSuccessMessage('');

  const quickActions = [
    { id: 'summarize_bulletpoints', label: 'Summarize (Bullets)', icon: '•••' },
    { id: 'summarize_paragraphs', label: 'Summarize (Paragraphs)', icon: '¶' },
    { id: 'make_simpler', label: 'Make Simpler', icon: '✎' },
    { id: 'make_shorter', label: 'Make Shorter', icon: '⋯' },
    { id: 'make_longer', label: 'Make Longer', icon: '≡' },
    { id: 'make_more_professional', label: 'More Professional', icon: '★' },
  ];

  const languages = [
    { code: 'Spanish', name: 'Spanish' },
    { code: 'French', name: 'French' },
    { code: 'German', name: 'German' },
    { code: 'Chinese', name: 'Chinese' },
    { code: 'Japanese', name: 'Japanese' },
    { code: 'Korean', name: 'Korean' },
    { code: 'Arabic', name: 'Arabic' },
    { code: 'Hindi', name: 'Hindi' },
    { code: 'Portuguese', name: 'Portuguese' },
    { code: 'Russian', name: 'Russian' },
  ];

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6 pb-4 border-b border-gray-200 dark:border-gray-700">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Lesson Planner</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Create comprehensive lesson plans with AI assistance
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="p-2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            aria-label={showHistory ? 'Hide history' : 'Show history'}
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 5.25a3 3 0 013 3m3 0a6 6 0 01-7.029 5.912c-.563-.097-1.159.026-1.563.43L10.5 17.25H8.25v2.25H6v2.25H2.25v-2.818c0-.597.237-1.17.659-1.591l6.499-6.499c.404-.404.527-1 .43-1.563A6 6 0 1121.75 8.25z" />
            </svg>
          </button>
        </div>
      </div>

      {/* Messages */}
      {(error || successMessage) && (
        <div className="mb-4 flex items-center justify-between gap-4">
          {error && (
            <div className="flex-1 p-3 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-300 text-sm flex items-center justify-between">
              <span>{error}</span>
              <button onClick={clearError} className="ml-4 text-red-500 hover:text-red-700">×</button>
            </div>
          )}
          {successMessage && (
            <div className="flex-1 p-3 bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-800 rounded-lg text-green-700 dark:text-green-300 text-sm flex items-center justify-between">
              <span>{successMessage}</span>
              <button onClick={clearSuccess} className="ml-4 text-green-500 hover:text-green-700">×</button>
            </div>
          )}
        </div>
      )}

      {/* Main content area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left panel - Form or Streaming Output */}
        <div className={`flex-1 flex flex-col min-w-0 ${showHistory ? 'lg:w-2/3' : ''}`}>
          {generating || streamingContent ? (
            // Streaming output panel
            <div className="flex-1 flex flex-col bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
              <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
                <h2 className="font-semibold text-gray-900 dark:text-white">
                  {generating ? 'Generating Lesson Plan...' : 'Lesson Plan Generated'}
                </h2>
                <div className="flex items-center gap-2">
                  {currentLessonPlanId && (
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleDownload('markdown', currentLessonPlanId)}
                        className="p-2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-sm"
                        title="Download Markdown"
                      >
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
                        </svg>
                      </button>
                      <button
                        onClick={() => handleDownload('pdf', currentLessonPlanId)}
                        className="p-2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-sm"
                        title="Download PDF"
                      >
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                        </svg>
                      </button>
                      <button
                        onClick={() => handleDownload('docx', currentLessonPlanId)}
                        className="p-2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-sm"
                        title="Download DOCX"
                      >
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                        </svg>
                      </button>
                    </div>
                  )}
                </div>
              </div>
              <div 
                ref={streamingContentRef}
                className="flex-1 overflow-y-auto p-4 markdown-content prose prose-sm max-w-none"
              >
                {streamingContent || (
                  <div className="text-center text-gray-500 dark:text-gray-400 py-12">
                    {generating ? (
                      <div className="flex flex-col items-center gap-3">
                        <div className="w-8 h-8 border-3 border-violet-600 border-t-transparent rounded-full animate-spin"></div>
                        <span>Generating your lesson plan...</span>
                      </div>
                    ) : (
                      <span>No content generated yet</span>
                    )}
                  </div>
                )}
              </div>
              {generating && (
                <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
                  <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                    <span className="w-2 h-2 bg-violet-600 rounded-full animate-pulse"></span>
                    <span>Streaming response...</span>
                  </div>
                </div>
              )}
            </div>
          ) : (
            // Form panel
            <div className="flex-1 flex flex-col bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
              <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                <h2 className="font-semibold text-gray-900 dark:text-white">Create New Lesson Plan</h2>
              </div>
              <div className="flex-1 overflow-y-auto p-4 space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Grade Level <span className="text-red-500">*</span>
                  </label>
                  <select
                    value={formData.grade_level}
                    onChange={(e) => setFormData(prev => ({ ...prev, grade_level: e.target.value }))}
                    className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent"
                    required
                  >
                    <option value="">Select grade level</option>
                    {['Pre-K', 'Kindergarten', '1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', '10th', '11th', '12th'].map(grade => (
                      <option key={grade} value={grade}>{grade}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Topic / Standard <span className="text-red-500">*</span>
                  </label>
                  <textarea
                    value={formData.topic}
                    onChange={(e) => setFormData(prev => ({ ...prev, topic: e.target.value }))}
                    rows={3}
                    placeholder="e.g., Photosynthesis, Quadratic Equations, The American Revolution..."
                    className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent resize-none"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Standards Alignment
                  </label>
                  <textarea
                    value={formData.standards}
                    onChange={(e) => setFormData(prev => ({ ...prev, standards: e.target.value }))}
                    rows={2}
                    placeholder="e.g., NGSS MS-LS1-6, CCSS.MATH.CONTENT.HSA.REI.B.4..."
                    className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent resize-none"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Additional Criteria
                  </label>
                  <textarea
                    value={formData.additional_criteria}
                    onChange={(e) => setFormData(prev => ({ ...prev, additional_criteria: e.target.value }))}
                    rows={3}
                    placeholder="e.g., Include hands-on activity, 45-minute class period, differentiation for ELL students..."
                    className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent resize-none"
                  />
                </div>

                <button
                  onClick={handleGenerate}
                  disabled={generating || !formData.grade_level || !formData.topic}
                  className="w-full py-3 px-4 bg-violet-600 text-white font-medium rounded-lg hover:bg-violet-700 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
                >
                  {generating ? (
                    <>
                      <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.977v4.977m0 0h-4.977m4.977 0l-3.181 3.181a8.25 8.25 0 01-13.806-3.744 8.25 8.25 0 011.745-12.88" />
                      </svg>
                      Generating...
                    </>
                  ) : (
                    <>
                      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                      </svg>
                      Generate Lesson Plan
                    </>
                  )}
                </button>

                <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
                  Uses SSE streaming for real-time generation • Powered by GPT-4
                </p>
              </div>
            </div>
          )}

          {/* Quick Action Result Modal */}
          {quickActionContent && (
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50" onClick={() => setQuickActionContent(null)}>
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-3xl w-full max-h-[80vh] flex flex-col" onClick={e => e.stopPropagation()}>
                <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
                  <h3 className="font-semibold text-gray-900 dark:text-white capitalize">
                    {quickActionContent.action.replace(/_/g, ' ')}
                  </h3>
                  <button onClick={() => setQuickActionContent(null)} className="p-1 text-gray-500 hover:text-gray-700">
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                <div className="flex-1 overflow-y-auto p-4 markdown-content prose prose-sm max-w-none">
                  {quickActionContent.content || <div className="animate-pulse">Generating...</div>}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Right panel - History */}
        {showHistory && (
          <div className="hidden lg:block w-80 lg:w-72 flex flex-col bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 ml-4">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
              <h2 className="font-semibold text-gray-900 dark:text-white">History</h2>
              <button
                onClick={loadHistory}
                disabled={historyLoading}
                className="p-1 text-gray-500 hover:text-gray-700 dark:hover:text-gray-200 rounded"
                title="Refresh"
              >
                <svg className={`w-5 h-5 ${historyLoading ? 'animate-spin' : ''}`} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.977v4.977m0 0h-4.977m4.977 0l-3.181 3.181a8.25 8.25 0 01-13.806-3.744 8.25 8.25 0 011.745-12.88" />
                </svg>
              </button>
            </div>
            <div className="flex-1 overflow-y-auto">
              {historyLoading ? (
                <div className="p-4 text-center text-gray-500 dark:text-gray-400">
                  <div className="w-8 h-8 border-3 border-violet-600 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                  Loading history...
                </div>
              ) : history.length === 0 ? (
                <div className="p-8 text-center text-gray-500 dark:text-gray-400">
                  <svg className="w-12 h-12 mx-auto mb-3 text-gray-300 dark:text-gray-600" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                  </svg>
                  <p>No lesson plans yet</p>
                  <p className="text-sm mt-1">Create your first lesson plan to get started</p>
                </div>
              ) : (
                <ul className="divide-y divide-gray-200 dark:divide-gray-700" role="list">
                  {history.map((item) => (
                    <li key={item.lesson_plan_id}>
                      <button
                        onClick={() => handleLoadLessonPlan(item.lesson_plan_id)}
                        className={`w-full p-4 text-left hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors flex items-start gap-3 ${
                          selectedLessonPlan?.lesson_plan_id === item.lesson_plan_id
                            ? 'bg-violet-50 dark:bg-violet-900/20 border-l-2 border-violet-500'
                            : ''
                        }`}
                      >
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-gray-900 dark:text-white truncate">
                            {item.user_query_title}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            {new Date(item.created_at).toLocaleDateString()}
                          </p>
                        </div>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleFavorite(item.lesson_plan_id, item.is_favorite);
                          }}
                          className={`p-1 rounded ${item.is_favorite ? 'text-yellow-500' : 'text-gray-400 hover:text-yellow-500'}`}
                          aria-label={item.is_favorite ? 'Remove from favorites' : 'Add to favorites'}
                        >
                          <svg className="w-5 h-5" fill={item.is_favorite ? 'currentColor' : 'none'} viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
                          </svg>
                        </button>
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        )}

        {/* Selected Lesson Plan Detail Panel */}
        {selectedLessonPlan && !generating && !streamingContent && (
          <div className="hidden lg:block w-96 flex flex-col bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 ml-4">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex items-start justify-between gap-4">
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-gray-900 dark:text-white truncate">
                  {selectedLessonPlan.user_query}
                </h3>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {new Date(selectedLessonPlan.created_at).toLocaleString()}
                </p>
              </div>
              <div className="flex items-center gap-1">
                <button
                  onClick={() => handleFavorite(selectedLessonPlan.lesson_plan_id, selectedLessonPlan.is_favorite)}
                  className={`p-2 rounded ${selectedLessonPlan.is_favorite ? 'text-yellow-500 bg-yellow-50 dark:bg-yellow-900/20' : 'text-gray-400 hover:text-yellow-500'}`}
                  aria-label={selectedLessonPlan.is_favorite ? 'Unfavorite' : 'Favorite'}
                >
                  <svg className="w-5 h-5" fill={selectedLessonPlan.is_favorite ? 'currentColor' : 'none'} viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
                  </svg>
                </button>
                <button
                  onClick={() => handleDownload('markdown', selectedLessonPlan.lesson_plan_id)}
                  className="p-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-200 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
                  title="Download Markdown"
                >
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
                  </svg>
                </button>
                <button
                  onClick={() => handleDownload('pdf', selectedLessonPlan.lesson_plan_id)}
                  className="p-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-200 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
                  title="Download PDF"
                >
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                  </svg>
                </button>
                <button
                  onClick={() => handleDownload('docx', selectedLessonPlan.lesson_plan_id)}
                  className="p-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-200 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
                  title="Download DOCX"
                >
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                  </svg>
                </button>
                <button
                  onClick={() => handleDelete(selectedLessonPlan.lesson_plan_id)}
                  className="p-2 text-gray-500 hover:text-red-600 dark:hover:text-red-400 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
                  title="Delete"
                >
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
                  </svg>
                </button>
              </div>
            </div>
            
            <div className="flex-1 overflow-y-auto p-4 markdown-content prose prose-sm max-w-none">
              {selectedLessonPlan.lesson_plan}
            </div>

            {/* Expand Section */}
            <div className="p-4 border-t border-gray-200 dark:border-gray-700 space-y-3">
              <h4 className="font-medium text-gray-900 dark:text-white">Expand Section</h4>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={expandQuery}
                  onChange={(e) => setExpandQuery(e.target.value)}
                  placeholder="What would you like to expand? (e.g., 'Add more hands-on activities')"
                  className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent text-sm"
                />
                <button
                  onClick={() => handleExpandSection(selectedLessonPlan.lesson_plan_id)}
                  disabled={expandingSection === selectedLessonPlan.lesson_plan_id || !expandQuery.trim()}
                  className="px-4 py-2 bg-violet-600 text-white text-sm font-medium rounded-lg hover:bg-violet-700 disabled:opacity-50 transition-colors"
                >
                  {expandingSection === selectedLessonPlan.lesson_plan_id ? 'Expanding...' : 'Expand'}
                </button>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="p-4 border-t border-gray-200 dark:border-gray-700 space-y-3">
              <h4 className="font-medium text-gray-900 dark:text-white">Quick Actions</h4>
              <div className="grid grid-cols-2 gap-2">
                {quickActions.map((action) => (
                  <button
                    key={action.id}
                    onClick={() => handleQuickAction(action.id, selectedLessonPlan.lesson_plan_id)}
                    disabled={quickActionLoading === action.id}
                    className="p-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 transition-colors disabled:opacity-50"
                  >
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{action.icon}</span>
                      <span>{action.label}</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Translate */}
            <div className="p-4 border-t border-gray-200 dark:border-gray-700 space-y-3">
              <h4 className="font-medium text-gray-900 dark:text-white">Translate</h4>
              <div className="grid grid-cols-2 gap-2">
                {languages.map((lang) => (
                  <button
                    key={lang.code}
                    onClick={() => handleTranslate(selectedLessonPlan.lesson_plan_id, lang.code)}
                    disabled={quickActionLoading === `translate-${lang.code}`}
                    className="p-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 transition-colors disabled:opacity-50"
                  >
                    {lang.name}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
