import React from 'react';
import { CheckCircle2, Circle, ArrowRight, Zap } from 'lucide-react';
import type { LifecycleStageDef, TimelineItem } from '../types';

interface LifecycleVisualizerProps {
  stages: LifecycleStageDef[];
  timeline: TimelineItem[];
  currentStage: string;
}

export const LifecycleVisualizer: React.FC<LifecycleVisualizerProps> = ({
  stages,
  timeline,
  currentStage,
}) => {
  if (!stages || stages.length === 0) return null;

  // Find completed stages from timeline events
  const completedStageKeys = new Set(timeline.map((t) => t.lifecycle_stage || t.stage || ''));

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 my-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
          <Zap className="w-3.5 h-3.5 text-cyan-400" />
          Action Lifecycle Progression
        </h3>
        <span className="text-[11px] text-slate-400">
          Current State: <strong className="text-cyan-400">{currentStage}</strong>
        </span>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        {stages.map((st, idx) => {
          const isPassed = completedStageKeys.has(st.stage);
          const isLast = idx === stages.length - 1;

          return (
            <React.Fragment key={st.stage}>
              <div
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs transition-all ${
                  isPassed
                    ? 'bg-cyan-950/60 border-cyan-500/50 text-cyan-300 font-semibold shadow-sm shadow-cyan-500/10'
                    : 'bg-slate-950/50 border-slate-800 text-slate-500'
                }`}
              >
                {isPassed ? (
                  <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                ) : (
                  <Circle className="w-3.5 h-3.5 text-slate-600 shrink-0" />
                )}
                <span>{st.name}</span>
              </div>

              {!isLast && (
                <ArrowRight className={`w-3.5 h-3.5 ${isPassed ? 'text-cyan-500' : 'text-slate-700'}`} />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};
