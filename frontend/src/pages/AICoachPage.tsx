import { ComingSoonPage } from './ComingSoonPage';

export function AICoachPage() {
  return (
    <ComingSoonPage
      agentName="AI Coach"
      description="Interactive chat with an AI teaching coach for real-time guidance and document analysis."
      icon={
        <svg className="w-12 h-12" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" d="M9.594 3.94c.06-.613.558-1.072 1.172-.954 1.257.25 2.28 1.37 2.576 2.618.146.624-.008 1.249-.44 1.729L21 14l-2.476 1.58c-.95.606-1.808 1.58-2.31 2.658-.1.212-.224.422-.347.629a6.026 6.026 0 01-2.54 1.906 3 3 0 11-3.597-5.404c0-.47.122-.912.333-1.306.461-.856 1.172-1.61 2.074-2.18.366-.232.507-.587.44-1.003l-.844-3.146Z" />
          <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0Z" />
        </svg>
      }
      color="pink"
    />
  );
}
