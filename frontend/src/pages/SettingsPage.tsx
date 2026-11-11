import { useAuth } from '../context/AuthContext';

export function SettingsPage() {
  const { user, token, logout } = useAuth();

  return (
    <div className="max-w-2xl space-y-8">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Settings</h1>

      {/* Account Section */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Account</h2>
        <div className="space-y-4">
          <div className="flex items-center gap-4 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
            <div className="w-12 h-12 bg-violet-100 dark:bg-violet-900/30 rounded-full flex items-center justify-center">
              <svg className="w-6 h-6 text-violet-700 dark:text-violet-300" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
              </svg>
            </div>
            <div>
              <p className="font-medium text-gray-900 dark:text-white">{user?.name || 'Demo User'}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">{user?.email || 'demo@planbright.ai'}</p>
            </div>
          </div>

          <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
            <h3 className="font-medium text-gray-900 dark:text-white mb-3">Authentication Token</h3>
            <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                Your token is stored locally and sent with each API request.
              </p>
              <div className="flex items-center gap-2">
                <code className="flex-1 text-xs bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded font-mono break-all">
                  {token ? `${token.slice(0, 20)}...${token.slice(-10)}` : 'No token set'}
                </code>
                {token && (
                  <button
                    onClick={() => navigator.clipboard.writeText(token)}
                    className="px-3 py-1.5 text-sm bg-violet-100 dark:bg-violet-900/30 text-violet-700 dark:text-violet-300 rounded hover:bg-violet-200 dark:hover:bg-violet-900/50 transition-colors"
                  >
                    Copy
                  </button>
                )}
              </div>
            </div>
          </div>

          <button
            onClick={logout}
            className="w-full py-2.5 px-4 bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-300 font-medium rounded-lg hover:bg-red-100 dark:hover:bg-red-900/50 border border-red-200 dark:border-red-800 transition-colors"
          >
            Sign Out
          </button>
        </div>
      </div>

      {/* API Configuration */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">API Configuration</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Backend API URL
            </label>
            <input
              type="text"
              value={import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}
              readOnly
              className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700/50 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white text-sm font-mono"
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Set via VITE_API_BASE_URL environment variable
            </p>
          </div>

          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <h4 className="font-medium text-blue-900 dark:text-blue-300 mb-2">Environment Variables</h4>
            <p className="text-sm text-blue-800 dark:text-blue-400">
              Create a <code className="bg-blue-100 dark:bg-blue-900/30 px-1.5 py-0.5 rounded">.env</code> file in the frontend root with:
            </p>
            <pre className="mt-2 text-xs bg-blue-900/90 text-blue-100 p-3 rounded overflow-x-auto">
{`VITE_API_BASE_URL=http://localhost:8000`}
            </pre>
          </div>
        </div>
      </div>

      {/* About */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">About</h2>
        <div className="space-y-3 text-sm text-gray-600 dark:text-gray-400">
          <p><strong>PlanBright AI Frontend</strong> - React + TypeScript + Vite + Tailwind CSS</p>
          <p>Version: 0.1.0</p>
          <p>Backend: FastAPI + Supabase + OpenAI</p>
          <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
            <p className="font-medium text-gray-900 dark:text-white mb-2">Available Agents:</p>
            <ul className="space-y-1 text-sm">
              <li className="flex items-center gap-2">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                Lesson Planner (Functional)
              </li>
              <li className="flex items-center gap-2">
                <span className="w-2 h-2 bg-gray-400 rounded-full"></span>
                Assessment Generator (Coming Soon)
              </li>
              <li className="flex items-center gap-2">
                <span className="w-2 h-2 bg-gray-400 rounded-full"></span>
                Rubrik Generator (Coming Soon)
              </li>
              <li className="flex items-center gap-2">
                <span className="w-2 h-2 bg-gray-400 rounded-full"></span>
                Differentiation Suggestor (Coming Soon)
              </li>
              <li className="flex items-center gap-2">
                <span className="w-2 h-2 bg-gray-400 rounded-full"></span>
                IEP Generator (Coming Soon)
              </li>
              <li className="flex items-center gap-2">
                <span className="w-2 h-2 bg-gray-400 rounded-full"></span>
                Feedback Generator (Coming Soon)
              </li>
              <li className="flex items-center gap-2">
                <span className="w-2 h-2 bg-gray-400 rounded-full"></span>
                Unit Planner (Coming Soon)
              </li>
              <li className="flex items-center gap-2">
                <span className="w-2 h-2 bg-gray-400 rounded-full"></span>
                AI Coach (Coming Soon)
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
