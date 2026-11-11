import { useState } from 'react';
import { Outlet, NavLink, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

interface NavItem {
  name: string;
  href: string;
  icon: ({ className }: { className?: string }) => React.ReactElement;
  children?: NavItem[];
  comingSoon?: boolean;
}

const navigation: NavItem[] = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { 
    name: 'Resources', 
    href: '/resources', 
    icon: BookOpenIcon, 
    children: [
      { name: 'Lesson Planner', href: '/resources/lesson-planner', icon: DocumentTextIcon },
      { name: 'Assessment Generator', href: '/resources/assessment-generator', icon: ClipboardDocumentCheckIcon, comingSoon: true },
      { name: 'Rubrik Generator', href: '/resources/rubrik-generator', icon: ClipboardDocumentListIcon, comingSoon: true },
      { name: 'Differentiation Suggestor', href: '/resources/differentiation', icon: LightBulbIcon, comingSoon: true },
      { name: 'IEP Generator', href: '/resources/iep-generator', icon: UserGroupIcon, comingSoon: true },
      { name: 'Feedback Generator', href: '/resources/feedback-generator', icon: ChatBubbleLeftRightIcon, comingSoon: true },
      { name: 'Unit Planner', href: '/resources/unit-planner', icon: CalendarDaysIcon, comingSoon: true },
      { name: 'AI Coach', href: '/resources/ai-coach', icon: SparklesIcon, comingSoon: true },
    ]
  },
  { name: 'History', href: '/history', icon: ClockArrowCounterclockwiseIcon },
  { name: 'Settings', href: '/settings', icon: Cog6ToothIcon },
];

// Icons
function HomeIcon({ className }: { className?: string }) {
  return <svg className={className} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M2.25 12l8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" /></svg>;
}
function BookOpenIcon({ className }: { className?: string }) {
  return <svg className={className} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" /></svg>;
}
function DocumentTextIcon({ className }: { className?: string }) {
  return <svg className={className} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" /><path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" d="M16.5 12.75H18a1.125 1.125 0 001.125-1.125v-3.75c0-.621-.504-1.125-1.125-1.125H18" /></svg>;
}
function ClipboardDocumentCheckIcon({ className }: { className?: string }) {
  return <svg className={className} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285Z" /></svg>;
}
function ClipboardDocumentListIcon({ className }: { className?: string }) {
  return <svg className={className} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0118 16.5h-2.25m-3.75 0l-1.5 1.5m0 0l-1.5-1.5m1.5 1.5v3.75" /><path strokeLinecap="round" strokeLinejoin="round" d="M9 12h.008v.008H9V12Zm0 3h.008v.008H9V15Zm0 3h.008v.008H9V18Zm3-9h.008v.008H12V9Zm0 3h.008v.008H12V12Zm0 3h.008v.008H12V15Zm3-9h.008v.008H15V9Zm0 3h.008v.008H15V12Zm0 3h.008v.008H15V15Z" /></svg>;
}
function LightBulbIcon({ className }: { className?: string }) {
  return <svg className={className} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>;
}
function UserGroupIcon({ className }: { className?: string }) {
  return <svg className={className} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m.94 3.198l.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0112 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 016 18.719m12 0a5.971 5.971 0 00-.941-3.197m0 0A5.995 5.995 0 0012 12.75a5.995 5.995 0 00-5.058 2.772m0 0a3 3 0 00-4.681 2.72 8.986 8.986 0 003.74.477m.94-3.197a5.971 5.971 0 00-.94 3.197M15 6.75a3 3 0 11-6 0 3 3 0 016 0zm-3 0a3 3 0 11-6 0 3 3 0 016 0zm12 0a3 3 0 11-6 0 3 3 0 016 0z" /></svg>;
}
function ChatBubbleLeftRightIcon({ className }: { className?: string }) {
  return <svg className={className} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09ZM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456ZM16.894 20.567A9.98 9.98 0 0112 21c-2.593 0-5.017-.722-6.894-1.951.074-.056.14-.113.198-.173a4.5 4.5 0 011.665-5.097A4.5 4.5 0 017.958 2.25a4.5 4.5 0 015.097 1.665c.06.058.117.125.173.198.523.475 1.072.911 1.652 1.307a3.375 3.375 0 004.746 4.746c.396.58.832 1.129 1.307 1.651Z" /></svg>;
}
function CalendarDaysIcon({ className }: { className?: string }) {
  return <svg className={className} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 18.75ZM9 11.25h.008v.008H9V11.25ZM12.75 11.25h.008v.008H12.75V11.25ZM16.5 11.25h.008v.008H16.5V11.25ZM9 15h.008v.008H9V15ZM12.75 15h.008v.008H12.75V15ZM16.5 15h.008v.008H16.5V15Z" /></svg>;
}
function SparklesIcon({ className }: { className?: string }) {
  return <svg className={className} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M9.594 3.94c.06-.613.558-1.072 1.172-.954 1.257.25 2.28 1.37 2.576 2.618.146.624-.008 1.249-.44 1.729L21 14l-2.476 1.58c-.95.606-1.808 1.58-2.31 2.658-.1.212-.224.422-.347.629a6.026 6.026 0 01-2.54 1.906 3 3 0 11-3.597-5.404c0-.47.122-.912.333-1.306.461-.856 1.172-1.61 2.074-2.18.366-.232.507-.587.44-1.003l-.844-3.146Z" /><path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0Z" /></svg>;
}
function Cog6ToothIcon({ className }: { className?: string }) {
  return <svg className={className} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" /></svg>;
}
function ClockArrowCounterclockwiseIcon({ className }: { className?: string }) {
  return <svg className={className} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M12.75 15a.75.75 0 01.75-.75h2.25a.75.75 0 010 1.5h-2.25a.75.75 0 01-.75-.75zM19.59 4.74a9.013 9.013 0 00-12.14 0c-.839.84-.839 2.198 0 3.037l.09.09A4.503 4.503 0 008.73 12a4.5 4.5 0 003.894 4.124l.091.09c.84.84 2.197.84 3.037 0l5.407-5.407a4.502 4.502 0 000-6.364z" /><path strokeLinecap="round" strokeLinejoin="round" d="M15.75 9a.75.75 0 11-1.5 0 .75.75 0 011.5 0z" /></svg>;
}
function ChevronDownIcon({ className }: { className?: string }) {
  return <svg className={className} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" /></svg>;
}
function UserIcon({ className }: { className?: string }) {
  return <svg className={className} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" /></svg>;
}
function LogoutIcon({ className }: { className?: string }) {
  return <svg className={className} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75" /></svg>;
}

export function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [expandedGroups, setExpandedGroups] = useState<string[]>(['Resources']);
  const location = useLocation();
  const { user, logout } = useAuth();

  const toggleGroup = (groupName: string) => {
    setExpandedGroups(prev => 
      prev.includes(groupName) 
        ? prev.filter(g => g !== groupName) 
        : [...prev, groupName]
    );
  };

  const isActive = (href: string) => location.pathname === href || location.pathname.startsWith(href + '/');

  // Inject animation styles
  useState(() => {
    const style = document.createElement('style');
    style.textContent = `
      @keyframes slide-down {
        from { opacity: 0; transform: translateY(-8px); }
        to { opacity: 1; transform: translateY(0); }
      }
      .animate-slide-down { animation: slide-down 0.2s ease-out; }
    `;
    document.head.appendChild(style);
    return () => document.head.removeChild(style);
  });

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex">
      {/* Mobile sidebar overlay */}
      <div 
        className={`fixed inset-0 z-40 bg-black/50 lg:hidden transition-opacity ${sidebarOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}
        onClick={() => setSidebarOpen(false)}
        aria-hidden="true"
      />

      {/* Sidebar */}
      <aside className={`fixed lg:static inset-y-0 left-0 z-50 w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transform transition-transform duration-300 lg:translate-x-0 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <h1 className="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
              <span className="w-8 h-8 bg-violet-600 rounded-lg flex items-center justify-center text-white text-sm font-bold">P</span>
              PlanBright AI
            </h1>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-1 overflow-y-auto" role="navigation" aria-label="Main navigation">
            {navigation.map((item) => {
              const hasChildren = item.children && item.children.length > 0;
              const isExpanded = expandedGroups.includes(item.name);
              const isGroupActive = hasChildren && item.children!.some(child => isActive(child.href));
              
              return (
                <div key={item.name}>
                  {hasChildren ? (
                    <button
                      onClick={() => toggleGroup(item.name)}
                      className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                        isGroupActive || isActive(item.href)
                          ? 'bg-violet-50 dark:bg-violet-900/30 text-violet-700 dark:text-violet-300'
                          : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                      }`}
                      aria-expanded={isExpanded}
                    >
                      <span className="flex items-center gap-3">
                        <item.icon className="w-5 h-5" />
                        {item.name}
                      </span>
                      <ChevronDownIcon className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
                    </button>
                  ) : (
                    <NavLink
                      to={item.href}
                      className={({ isActive: active }) => `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                        active
                          ? 'bg-violet-50 dark:bg-violet-900/30 text-violet-700 dark:text-violet-300'
                          : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                      }`}
                    >
                      <item.icon className="w-5 h-5" />
                      {item.name}
                      {item.comingSoon && <span className="ml-auto text-xs bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 px-2 py-0.5 rounded-full">Soon</span>}
                    </NavLink>
                  )}
                  
                  {hasChildren && isExpanded && (
                    <div className="ml-6 mt-1 space-y-0.5 animate-slide-down" role="group" aria-label={`${item.name} submenu`}>
                      {item.children!.map((child) => (
                        <NavLink
                          key={child.href}
                          to={child.href}
                          className={({ isActive: active }) => `flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                            active
                              ? 'bg-violet-50 dark:bg-violet-900/30 text-violet-700 dark:text-violet-300 font-medium'
                              : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white'
                          }`}
                        >
                          <child.icon className="w-4 h-4" />
                          {child.name}
                          {child.comingSoon && <span className="ml-auto text-xs bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 px-2 py-0.5 rounded-full">Soon</span>}
                        </NavLink>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </nav>

          {/* User menu */}
          <div className="p-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-3 px-3 py-2">
              <div className="w-8 h-8 bg-violet-100 dark:bg-violet-900/30 rounded-full flex items-center justify-center">
                <UserIcon className="w-5 h-5 text-violet-700 dark:text-violet-300" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                  {user?.name || 'Demo User'}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                  {user?.email || 'demo@planbright.ai'}
                </p>
              </div>
              <button
                onClick={logout}
                className="p-2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                aria-label="Logout"
              >
                <LogoutIcon className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0 lg:ml-0">
        {/* Top bar */}
        <header className="sticky top-0 z-30 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 lg:hidden">
          <div className="flex items-center justify-between h-16 px-4">
            <button
              onClick={() => setSidebarOpen(true)}
              className="p-2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
              aria-label="Open menu"
            >
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
              </svg>
            </button>
            <h1 className="text-lg font-semibold text-gray-900 dark:text-white">PlanBright AI</h1>
            <div className="w-10" />
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 p-4 lg:p-8 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
