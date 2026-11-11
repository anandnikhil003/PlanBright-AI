import { Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/Layout';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { LessonPlannerPage } from './pages/LessonPlannerPage';
import { AssessmentGeneratorPage } from './pages/AssessmentGeneratorPage';
import { RubrikGeneratorPage } from './pages/RubrikGeneratorPage';
import { DifferentiationPage } from './pages/DifferentiationPage';
import { IEPGeneratorPage } from './pages/IEPGeneratorPage';
import { FeedbackGeneratorPage } from './pages/FeedbackGeneratorPage';
import { UnitPlannerPage } from './pages/UnitPlannerPage';
import { AICoachPage } from './pages/AICoachPage';
import { HistoryPage } from './pages/HistoryPage';
import { SettingsPage } from './pages/SettingsPage';
import { useAuth } from './context/AuthContext';

// Protected route wrapper
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
}

// Public route wrapper (redirects authenticated users)
function PublicRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  return !isAuthenticated ? <>{children}</> : <Navigate to="/" replace />;
}

function App() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />

      {/* Protected routes with layout */}
      <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        
        {/* Resources - Lesson Planner (functional) */}
        <Route path="/resources/lesson-planner" element={<LessonPlannerPage />} />
        
        {/* Resources - Coming soon pages */}
        <Route path="/resources/assessment-generator" element={<AssessmentGeneratorPage />} />
        <Route path="/resources/rubrik-generator" element={<RubrikGeneratorPage />} />
        <Route path="/resources/differentiation" element={<DifferentiationPage />} />
        <Route path="/resources/iep-generator" element={<IEPGeneratorPage />} />
        <Route path="/resources/feedback-generator" element={<FeedbackGeneratorPage />} />
        <Route path="/resources/unit-planner" element={<UnitPlannerPage />} />
        <Route path="/resources/ai-coach" element={<AICoachPage />} />
      </Route>

      {/* Catch-all redirect */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
