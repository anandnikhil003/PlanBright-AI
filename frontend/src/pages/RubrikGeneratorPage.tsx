import { ComingSoonPage } from './ComingSoonPage';

export function RubrikGeneratorPage() {
  return (
    <ComingSoonPage
      agentName="Rubrik Generator"
      description="Create detailed rubrics with multiple criteria levels and standards alignment."
      icon={
        <svg className="w-12 h-12" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0118 16.5h-2.25m-3.75 0l-1.5 1.5m0 0l-1.5-1.5m1.5 1.5v3.75" />
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h.008v.008H9V12Zm0 3h.008v.008H9V15Zm0 3h.008v.008H9V18Zm3-9h.008v.008H12V9Zm0 3h.008v.008H12V12Zm0 3h.008v.008H12V15Zm3-9h.008v.008H15V9Zm0 3h.008v.008H15V12Zm0 3h.008v.008H15V15Z" />
        </svg>
      }
      color="purple"
    />
  );
}
