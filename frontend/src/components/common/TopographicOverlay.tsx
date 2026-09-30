import React from 'react';

export const TopographicOverlay: React.FC = () => {
  return (
    <div className="pointer-events-none fixed inset-0 z-0 opacity-[0.03] dark:opacity-[0.02]">
      <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern id="topo" width="200" height="200" patternUnits="userSpaceOnUse">
            <path d="M 0 40 Q 50 10 100 40 T 200 40" fill="none" stroke="currentColor" strokeWidth="1" />
            <path d="M 0 80 Q 50 120 100 80 T 200 80" fill="none" stroke="currentColor" strokeWidth="1" />
            <path d="M 0 120 Q 50 90 100 120 T 200 120" fill="none" stroke="currentColor" strokeWidth="1" />
            <path d="M 0 160 Q 50 180 100 160 T 200 160" fill="none" stroke="currentColor" strokeWidth="1" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#topo)" />
      </svg>
    </div>
  );
};
