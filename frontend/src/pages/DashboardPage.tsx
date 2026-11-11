import { Link } from 'react-router-dom';

const agentCards = [
  {
    name: 'Lesson Planner',
    description: 'Create comprehensive lesson plans with standards alignment, differentiation strategies, and expandable sections.',
    icon: DocumentTextIcon,
    href: '/resources/lesson-planner',
    color: 'blue',
    available: true,
  },
  {
    name: 'Assessment Generator',
    description: 'Generate formative and summative assessments aligned to learning objectives and standards.',
    icon: ClipboardDocumentCheckIcon,
    href: '/resources/assessment-generator',
    color: 'green',
    available: false,
  },
  {
    name: 'Rubrik Generator',
    description: 'Create detailed rubrics with multiple criteria levels and standards alignment.',
    icon: ClipboardDocumentListIcon,
    href: '/resources/rubrik-generator',
    color: 'purple',
    available: false,
  },
  {
    name: 'Differentiation Suggestor',
    description: 'Get tailored differentiation strategies for diverse learning profiles and proficiency levels.',
    icon: LightBulbIcon,
    href: '/resources/differentiation',
    color: 'orange',
    available: false,
  },
  {
    name: 'IEP Generator',
    description: 'Generate Individualized Education Programs with goals, services, and accommodations.',
    icon: UserGroupIcon,
    href: '/resources/iep-generator',
    color: 'red',
    available: false,
  },
  {
    name: 'Feedback Generator',
    description: 'Create personalized, constructive feedback for student assignments and projects.',
    icon: ChatBubbleLeftRightIcon,
    href: '/resources/feedback-generator',
    color: 'teal',
    available: false,
  },
  {
    name: 'Unit Planner',
    description: 'Plan comprehensive instructional units with pacing, assessments, and interdisciplinary links.',
    icon: CalendarDaysIcon,
    href: '/resources/unit-planner',
    color: 'indigo',
    available: false,
  },
  {
    name: 'AI Coach',
    description: 'Interactive chat with an AI teaching coach for real-time guidance and document analysis.',
    icon: SparklesIcon,
    href: '/resources/ai-coach',
    color: 'pink',
    available: false,
  },
];

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

export function DashboardPage() {
  return (
    <div className="space-y-8">
      {/* Welcome header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Welcome back</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Choose a tool to start creating amazing educational content
          </p>
        </div>
        <Link
          to="/resources/lesson-planner"
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-violet-600 text-white font-medium rounded-lg hover:bg-violet-700 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800 transition-colors"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
          </svg>
          New Lesson Plan
        </Link>
      </div>

      {/* Quick stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Lesson Plans" value="0" icon="📝" color="blue" />
        <StatCard title="Assessments" value="0" icon="📋" color="green" />
        <StatCard title="Rubriks" value="0" icon="📊" color="purple" />
        <StatCard title="Total Uses" value="0" icon="⚡" color="orange" />
      </div>

      {/* Resources grid */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Available Tools</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {agentCards.map((agent) => (
            <Link
              key={agent.name}
              to={agent.href}
              className={`group relative block p-5 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-violet-300 dark:hover:border-violet-700 transition-all duration-200 ${!agent.available ? 'opacity-60 pointer-events-none' : ''}`}
            >
              <div className={`w-12 h-12 rounded-xl flex items-center justify-center bg-${agent.color}-100 dark:bg-${agent.color}-900/30 text-${agent.color}-600 dark:text-${agent.color}-400 group-hover:scale-110 transition-transform`}>
                <agent.icon className="w-6 h-6" />
              </div>
              <h3 className="mt-4 font-semibold text-gray-900 dark:text-white group-hover:text-violet-600 dark:group-hover:text-violet-400 transition-colors">
                {agent.name}
              </h3>
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                {agent.description}
              </p>
              {!agent.available && (
                <div className="absolute inset-0 bg-white/80 dark:bg-gray-800/80 rounded-xl flex items-center justify-center">
                  <span className="text-sm font-medium text-gray-500 dark:text-gray-400">Coming Soon</span>
                </div>
              )}
            </Link>
          ))}
        </div>
      </div>

      {/* Getting started */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Getting Started</h2>
        <div className="space-y-3 text-gray-600 dark:text-gray-400">
          <Step number={1} title="Enter your details" description="Fill in grade level, topic, standards, and any additional criteria for your lesson." />
          <Step number={2} title="Generate" description="Click Generate and watch your lesson plan stream in real-time via SSE." />
          <Step number={3} title="Refine" description="Expand sections, translate, summarize, or adjust tone with quick actions." />
          <Step number={4} title="Export" description="Download as PDF, DOCX, Markdown, or save to Google Docs." />
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, icon, color }: { title: string; value: string; icon: string; color: string }) {
  const colorClasses = {
    blue: 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400',
    green: 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400',
    purple: 'bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400',
    orange: 'bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400',
  };
  
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{title}</p>
          <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{value}</p>
        </div>
        <span className={`w-12 h-12 rounded-xl flex items-center justify-center text-2xl ${colorClasses[color as keyof typeof colorClasses]}`}>
          {icon}
        </span>
      </div>
    </div>
  );
}

function Step({ number, title, description }: { number: number; title: string; description: string }) {
  return (
    <div className="flex items-start gap-4">
      <span className="flex-shrink-0 w-8 h-8 rounded-full bg-violet-100 dark:bg-violet-900/30 text-violet-700 dark:text-violet-300 flex items-center justify-center font-bold text-sm">
        {number}
      </span>
      <div>
        <h3 className="font-medium text-gray-900 dark:text-white">{title}</h3>
        <p className="text-sm mt-0.5">{description}</p>
      </div>
    </div>
  );
}
