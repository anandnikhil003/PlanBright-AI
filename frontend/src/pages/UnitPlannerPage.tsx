import { ComingSoonPage } from './ComingSoonPage';

export function UnitPlannerPage() {
  return (
    <ComingSoonPage
      agentName="Unit Planner"
      description="Plan comprehensive instructional units with pacing, assessments, and interdisciplinary links."
      icon={
        <svg className="w-12 h-12" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 18.75ZM9 11.25h.008v.008H9V11.25ZM12.75 11.25h.008v.008H12.75V11.25ZM16.5 11.25h.008v.008H16.5V11.25ZM9 15h.008v.008H9V15ZM12.75 15h.008v.008H12.75V15ZM16.5 15h.008v.008H16.5V15Z" />
        </svg>
      }
      color="indigo"
    />
  );
}
