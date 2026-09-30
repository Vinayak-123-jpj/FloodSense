import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { ThemeProvider } from './theme/ThemeContext';
import { Header } from './components/common/Header';
import { TopographicOverlay } from './components/common/TopographicOverlay';

import { LandingPage } from './pages/LandingPage';
import { LiveMonitorPage } from './pages/LiveMonitorPage';
import { ScenarioReplayPage } from './pages/ScenarioReplayPage';
import { AlertsPage } from './pages/AlertsPage';
import { ModelMethodPage } from './pages/ModelMethodPage';
import { OpenHardwarePage } from './pages/OpenHardwarePage';

const NotFoundPage: React.FC = () => (
  <div className="text-center py-20 space-y-4">
    <div className="font-mono text-4xl font-bold text-survey-teal dark:text-night-teal">404</div>
    <h1 className="font-serif text-2xl font-bold text-survey-ink dark:text-night-text">Page Not Found</h1>
    <p className="font-sans text-xs text-survey-slate dark:text-night-slate">The requested survey route does not exist in the FloodSense grid.</p>
    <Link to="/" className="inline-block px-4 py-2 rounded bg-survey-teal text-white font-mono text-xs">Return to Overview →</Link>
  </div>
);

export const App: React.FC = () => {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <div className="relative min-h-screen bg-survey-paper dark:bg-night-bg text-survey-ink dark:text-night-text transition-colors duration-200 font-sans">
          <TopographicOverlay />
          <Header />
          <main className="relative z-10 mx-auto max-w-7xl px-4 sm:px-6 pt-6">
            <Routes>
              <Route path="/" element={<LandingPage />} />
              <Route path="/live" element={<LiveMonitorPage />} />
              <Route path="/replay" element={<ScenarioReplayPage />} />
              <Route path="/alerts" element={<AlertsPage />} />
              <Route path="/model-method" element={<ModelMethodPage />} />
              <Route path="/hardware" element={<OpenHardwarePage />} />
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </ThemeProvider>
  );
};
