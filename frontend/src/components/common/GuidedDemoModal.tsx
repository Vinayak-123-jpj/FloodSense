import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Play, ArrowRight, ArrowLeft, X, Shield, Activity, Sliders, Bell, Cpu } from 'lucide-react';

interface GuidedDemoModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const GuidedDemoModal: React.FC<GuidedDemoModalProps> = ({ isOpen, onClose }) => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState<number>(0);

  if (!isOpen) return null;

  const steps = [
    {
      title: '1. Active River Gauging Atlas',
      subtitle: 'Real-time telemetry from 10 virtual ESP32 gauging nodes',
      description: 'Explore live station telemetry across Kerala (Periyar, Pamba) and Assam (Brahmaputra). Tiles use keyless OpenTopoMap in Light mode and desaturated Night Watch filters in Dark mode with automatic 4-second vector GeoJSON fallback.',
      icon: Activity,
      actionText: 'Go to Live Monitor',
      path: '/live'
    },
    {
      title: '2. Kerala August 2018 Historical Replay',
      subtitle: 'Genuinely out-of-sample event scrubber',
      description: 'Replay the catastrophic August 2018 Kerala flood event evaluated using heldout_2018_model.joblib (trained strictly on non-2018 daily data). Starts playback instantly within 2 seconds.',
      icon: Play,
      actionText: 'Open Replay Scrubber',
      path: '/replay'
    },
    {
      title: '3. What-If Rainfall Stress Simulator',
      subtitle: 'Interactive digital twin rain multiplier slider',
      description: 'Test hydrological catchment response by adjusting rainfall intensity multipliers (0.5x to 3.0x). Watch water level gauges and risk thresholds adjust in real time.',
      icon: Sliders,
      actionText: 'Test What-If Slider',
      path: '/replay'
    },
    {
      title: '4. Hysteresis Alert Engine & Outbox',
      subtitle: 'Multilingual alerts (English & Hindi) & OSM routing',
      description: 'State transition hysteresis prevents duplicate alarm fatigue. View queued emergency outbox notifications in English and Hindi alongside nearest safe elevation evacuation routes.',
      icon: Bell,
      actionText: 'View Alert Outbox',
      path: '/alerts'
    },
    {
      title: '5. Model & Science Audit Report',
      subtitle: '1990–2025 Multi-Horizon Benchmarks & Baseline Comparisons',
      description: 'Complete transparency model card detailing 131,490 daily samples, 3-horizon predictions (t+1d, t+2d, t+3d), per-station 2018 lead times, and side-by-side comparisons vs Linear (Logistic Regression), Persistence, and Threshold Rule baselines.',
      icon: Cpu,
      actionText: 'Inspect Science Audit',
      path: '/model'
    }
  ];

  const step = steps[currentStep];
  const Icon = step.icon;

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(prev => prev + 1);
    } else {
      onClose();
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const handleNavigate = () => {
    navigate(step.path);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-[1000] flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
      <div className="relative w-full max-w-lg rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card p-6 shadow-xl space-y-5">
        
        {/* Modal Header */}
        <div className="flex items-center justify-between border-b border-survey-border/60 dark:border-night-border/60 pb-3">
          <div className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-survey-teal dark:text-night-teal" />
            <span className="font-mono text-xs font-bold text-survey-teal dark:text-night-teal uppercase tracking-wider">
              FLOODSENSE GUIDED DEMO ({currentStep + 1} / {steps.length})
            </span>
          </div>
          <button
            onClick={onClose}
            className="text-survey-slate dark:text-night-slate hover:text-survey-ink dark:hover:text-night-text p-1 rounded transition-all cursor-pointer"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-survey-paper dark:bg-night-bg h-1.5 rounded overflow-hidden">
          <div
            className="bg-survey-teal dark:bg-night-teal h-full transition-all duration-300"
            style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
          />
        </div>

        {/* Step Content */}
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded bg-survey-paper dark:bg-night-bg border border-survey-border dark:border-night-border text-survey-teal dark:text-night-teal">
              <Icon className="h-6 w-6" />
            </div>
            <div>
              <h2 className="font-serif text-lg font-bold text-survey-ink dark:text-night-text">{step.title}</h2>
              <p className="font-mono text-xs text-survey-teal dark:text-night-teal">{step.subtitle}</p>
            </div>
          </div>

          <p className="font-sans text-xs text-survey-slate dark:text-night-slate leading-relaxed">
            {step.description}
          </p>
        </div>

        {/* Action Button for Step */}
        <button
          onClick={handleNavigate}
          className="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded bg-survey-teal hover:bg-survey-teal/90 text-white font-sans text-xs font-semibold transition-all cursor-pointer"
        >
          {step.actionText} <ArrowRight className="h-3.5 w-3.5" />
        </button>

        {/* Footer Navigation */}
        <div className="flex items-center justify-between border-t border-survey-border/60 dark:border-night-border/60 pt-3">
          <button
            onClick={handleBack}
            disabled={currentStep === 0}
            className={`inline-flex items-center gap-1 font-mono text-xs ${
              currentStep === 0
                ? 'opacity-40 cursor-not-allowed text-survey-slate dark:text-night-slate'
                : 'text-survey-ink dark:text-night-text hover:text-survey-teal dark:hover:text-night-teal cursor-pointer'
            }`}
          >
            <ArrowLeft className="h-3.5 w-3.5" /> Back
          </button>

          <button
            onClick={onClose}
            className="font-mono text-xs text-survey-slate dark:text-night-slate hover:text-survey-ink dark:hover:text-night-text cursor-pointer"
          >
            Skip Tour
          </button>

          <button
            onClick={handleNext}
            className="inline-flex items-center gap-1 font-mono text-xs text-survey-teal dark:text-night-teal font-semibold hover:underline cursor-pointer"
          >
            {currentStep === steps.length - 1 ? 'Finish' : 'Next'} <ArrowRight className="h-3.5 w-3.5" />
          </button>
        </div>

      </div>
    </div>
  );
};
