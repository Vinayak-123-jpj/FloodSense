import React, { useState } from 'react';
import { AlertItem } from '../../types';
import { RiskBadge } from '../common/Badge';
import { ExternalLink, Trash2, Send, Languages } from 'lucide-react';

interface OutboxProps {
  alerts: AlertItem[];
  onClear: () => void;
}

export const OutboxList: React.FC<OutboxProps> = ({ alerts, onClear }) => {
  const [activeLang, setActiveLang] = useState<'en' | 'hi'>('en');

  const filteredAlerts = alerts.filter(a => a.language === activeLang);

  return (
    <div className="rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card p-4 shadow-xs">
      
      {/* Header Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-4 border-b border-survey-border/60 dark:border-night-border/60 pb-3">
        <div>
          <span className="font-mono text-xs text-survey-teal dark:text-night-teal uppercase tracking-wider block">EMERGENCY ALERT OUTBOX</span>
          <span className="font-serif text-base font-bold text-survey-ink dark:text-night-text">Dispatched Notifications & Telegram Logs</span>
        </div>

        <div className="flex items-center gap-3">
          {/* Language Toggle Preview */}
          <div className="flex items-center gap-1 border border-survey-border dark:border-night-border rounded p-1 bg-survey-paper dark:bg-night-bg">
            <Languages className="h-4 w-4 text-survey-teal dark:text-night-teal ml-1" />
            <button
              onClick={() => setActiveLang('en')}
              className={`px-2.5 py-0.5 font-mono text-xs rounded transition-all cursor-pointer ${
                activeLang === 'en' ? 'bg-survey-teal text-white font-bold' : 'text-survey-slate dark:text-night-slate'
              }`}
            >
              English
            </button>
            <button
              onClick={() => setActiveLang('hi')}
              className={`px-2.5 py-0.5 font-mono text-xs rounded transition-all cursor-pointer ${
                activeLang === 'hi' ? 'bg-survey-teal text-white font-bold' : 'text-survey-slate dark:text-night-slate'
              }`}
            >
              हिंदी (Hindi)
            </button>
          </div>

          {/* Clear Outbox */}
          <button
            onClick={onClear}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded border border-red-200 dark:border-red-900/50 bg-red-50 dark:bg-red-950/30 text-xs font-mono text-red-700 dark:text-red-300 hover:bg-red-100 transition-all cursor-pointer"
          >
            <Trash2 className="h-3.5 w-3.5" /> Clear Outbox
          </button>
        </div>
      </div>

      {/* Outbox Items */}
      {filteredAlerts.length === 0 ? (
        <div className="text-center py-12 text-survey-slate dark:text-night-slate font-mono text-xs">
          No alert outbox logs recorded for the selected language.
        </div>
      ) : (
        <div className="space-y-3">
          {filteredAlerts.map(alert => (
            <div
              key={alert.id}
              className="rounded border border-survey-border dark:border-night-border bg-survey-paper dark:bg-night-bg p-3.5 transition-all hover:border-survey-teal"
            >
              <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                <div className="flex items-center gap-2">
                  <RiskBadge level={alert.risk_level} size="sm" />
                  <span className="font-serif text-sm font-bold text-survey-ink dark:text-night-text">
                    {alert.station_name || alert.station_id}
                  </span>
                </div>
                <div className="flex items-center gap-2 font-mono text-xs">
                  <span className="text-survey-slate dark:text-night-slate">
                    {new Date(alert.timestamp).toLocaleString()}
                  </span>
                  {alert.sent_to_telegram ? (
                    <span className="inline-flex items-center gap-1 text-[10px] bg-sky-100 dark:bg-sky-950/40 text-sky-800 dark:text-sky-300 px-2 py-0.5 rounded border border-sky-300">
                      <Send className="h-3 w-3" /> TELEGRAM DELIVERED
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-[10px] bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 px-2 py-0.5 rounded border border-slate-300">
                      LOGGED TO OUTBOX
                    </span>
                  )}
                </div>
              </div>

              {/* Alert Driver & Action Details */}
              <div className="text-xs font-sans text-survey-ink dark:text-night-text mb-2 space-y-1">
                <div><strong>Primary Driver:</strong> {alert.reason}</div>
                <div><strong>Recommended Action:</strong> {alert.action_recommended}</div>
              </div>

              {/* Evacuation Link */}
              {alert.evacuation_route_url && (
                <div className="pt-2 border-t border-survey-border/40 dark:border-night-border/40">
                  <a
                    href={alert.evacuation_route_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 font-mono text-xs text-survey-teal dark:text-night-teal hover:underline font-medium"
                  >
                    <ExternalLink className="h-3.5 w-3.5" /> View OpenStreetMap Evacuation Directions →
                  </a>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
