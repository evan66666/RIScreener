import React from 'react';
import { Calendar, FileText, ArrowUpRight } from 'lucide-react';
import type { TimelineItem } from '../types';

interface TimelineViewProps {
  timeline: TimelineItem[];
  onOpenPdf: (docId: number) => void;
}

export const TimelineView: React.FC<TimelineViewProps> = ({ timeline, onOpenPdf }) => {
  if (!timeline || timeline.length === 0) {
    return <div className="text-xs text-slate-500 py-4">No chronological events found.</div>;
  }

  return (
    <div className="relative pl-6 border-l-2 border-slate-800 space-y-6 my-4">
      {timeline.map((item, idx) => {
        const d = new Date(item.event_date);
        const formattedDate = d.toLocaleDateString('id-ID', {
          day: '2-digit',
          month: 'short',
          year: 'numeric',
        });

        const isExplicit = item.signal_type === 'EXPLICIT';
        const isAdvancement = item.contribution === 'STATE_ADVANCEMENT';

        return (
          <div key={item.event_id || idx} className="relative group">
            {/* Timeline bullet */}
            <div
              className={`absolute -left-[31px] top-1 w-4 h-4 rounded-full border-2 flex items-center justify-center transition-all ${
                isExplicit
                  ? 'bg-emerald-950 border-emerald-400 text-emerald-400 shadow-sm shadow-emerald-500/20'
                  : isAdvancement
                  ? 'bg-amber-950 border-amber-400 text-amber-400'
                  : 'bg-slate-900 border-cyan-500 text-cyan-400'
              }`}
            >
              <div className="w-1.5 h-1.5 rounded-full bg-current"></div>
            </div>

            {/* Event box */}
            <div className="bg-slate-900/90 border border-slate-800/90 rounded-xl p-3.5 hover:border-slate-700 transition-all">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-1.5">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
                    <Calendar className="w-3.5 h-3.5 text-cyan-400" />
                    {formattedDate}
                  </span>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                      isExplicit
                        ? 'bg-emerald-950/80 text-emerald-300 border border-emerald-800/60'
                        : isAdvancement
                        ? 'bg-amber-950/80 text-amber-300 border border-amber-800/60'
                        : 'bg-slate-800 text-slate-300'
                    }`}
                  >
                    {(item.lifecycle_stage || item.stage || 'EVENT').replace('_', ' ')}
                  </span>
                  {item.contribution && (
                    <span className="text-[10px] text-slate-500 font-medium">
                      ({item.contribution.replace('_', ' ')})
                    </span>
                  )}
                </div>

                {item.document_id && (
                  <button
                    onClick={() => onOpenPdf(item.document_id)}
                    className="flex items-center gap-1 text-[11px] text-cyan-400 hover:text-cyan-300 hover:underline cursor-pointer font-medium"
                  >
                    <FileText className="w-3.5 h-3.5" />
                    <span>View Filing PDF</span>
                    <ArrowUpRight className="w-3 h-3" />
                  </button>
                )}
              </div>

              <p className="text-xs text-slate-300 font-medium leading-normal">
                {item.announcement_title || item.title}
              </p>

              {(item.announcement_category || item.category) && (
                <div className="text-[11px] text-slate-500 mt-1">
                  Category: {item.announcement_category || item.category}
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};
