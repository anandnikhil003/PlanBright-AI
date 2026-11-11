import { ComingSoonPage } from './ComingSoonPage';

export function FeedbackGeneratorPage() {
  return (
    <ComingSoonPage
      agentName="Feedback Generator"
      description="Create personalized, constructive feedback for student assignments and projects."
      icon={
        <svg className="w-12 h-12" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09ZM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456ZM16.894 20.567A9.98 9.98 0 0112 21c-2.593 0-5.017-.722-6.894-1.951.074-.056.14-.113.198-.173a4.5 4.5 0 011.665-5.097A4.5 4.5 0 017.958 2.25a4.5 4.5 0 015.097 1.665c.06.058.117.125.173.198.523.475 1.072.911 1.652 1.307a3.375 3.375 0 004.746 4.746c.396.58.832 1.129 1.307 1.651Z" />
        </svg>
      }
      color="teal"
    />
  );
}
