import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { lessonPlannerApi, type LessonPlanHistoryItem } from '../api/lessonPlanner';

export function HistoryPage() {
  const { token, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [history, setHistory] = useState<LessonPlanHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'favorites'>('all');

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    loadHistory();
  }, [token]);

  const loadHistory = async () => {
    if (!token) return;
    setLoading(true);
    try {
      const data = await lessonPlannerApi.getHistory(token);
      setHistory(data);
    } catch (err) {
      console.error('Failed to load history:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredHistory = filter === 'favorites' 
    ? history.filter(item => item.is_favorite)
    : history;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">History</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            All your generated lesson plans
          </p>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as 'all' | 'favorites')}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-violet-500"
          >
            <option value="all">All ({history.length})</option>
            <option value="favorites">Favorites ({history.filter(f => f.is_favorite).length})</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="w-8 h-8 border-3 border-violet-600 border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : filteredHistory.length === 0 ? (
        <div className="text-center py-16">
          <svg className="w-16 h-16 mx-auto mb-4 text-gray-300 dark:text-gray-600" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
          </svg>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            {filter === 'favorites' ? 'No favorites yet' : 'No lesson plans yet'}
          </h3>
          <p className="text-gray-500 dark:text-gray-400 mb-6">
            {filter === 'favorites' 
              ? 'Mark lesson plans as favorites to see them here'
              : 'Create your first lesson plan to get started'}
          </p>
          <button
            onClick={() => navigate('/resources/lesson-planner')}
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-violet-600 text-white font-medium rounded-lg hover:bg-violet-700"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
            </svg>
            Create Lesson Plan
          </button>
        </div>
      ) : (
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
          <ul className="divide-y divide-gray-200 dark:divide-gray-700" role="list">
            {filteredHistory.map((item) => (
              <li key={item.lesson_plan_id}>
                <button
                  onClick={() => navigate(`/resources/lesson-planner?load=${item.lesson_plan_id}`)}
                  className="w-full p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors flex items-start gap-4 text-left"
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-medium text-gray-900 dark:text-white truncate flex-1">
                        {item.user_query_title}
                      </h3>
                      {item.is_favorite && (
                        <svg className="w-4 h-4 text-yellow-500 flex-shrink-0" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
                        </svg>
                      )}
                    </div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {new Date(item.created_at).toLocaleString()}
                    </p>
                  </div>
                  <svg className="w-5 h-5 text-gray-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757a1.5 1.5 0 012.121 2.121l-3 3a6 6 0 108.485 8.485l3-3a1.5 1.5 0 012.121 2.121l-1.757 1.757a4.5 4.5 0 01-6.364-6.364l4.5-4.5a4.5 4.5 0 01-1.242-7.244z" />
                  </svg>
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
