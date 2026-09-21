import React from 'react';
import { BookOpen, FileText, ExternalLink } from 'lucide-react';
import type { EvidenceItem } from '../types';

interface EvidenceCardProps {
  evidence: EvidenceItem;
  onOpenPdf?: (docId: number, page: number) => void;
}

export const EvidenceCard: React.FC<EvidenceCardProps> = ({ evidence, onOpenPdf }) => {
  return (
    <div className="bg-slate-900/80 border border-slate-800/90 rounded-xl p-3.5 my-2 hover:border-slate-700 transition-all">
      <div className="flex items-center justify-between gap-2 mb-2">
        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 rounded bg-cyan-950/80 border border-cyan-800/60 text-cyan-400 text-[10px] font-bold">
            Page {evidence.page_number}
          </span>
          <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px] font-semibold">
            {evidence.evidence_type.replace('_', ' ')}
          </span>
        </div>

        {evidence.document_id && onOpenPdf && (
          <button
            onClick={() => onOpenPdf(evidence.document_id!, evidence.page_number)}
            className="flex items-center gap-1 text-[11px] text-cyan-400 hover:text-cyan-300 hover:underline cursor-pointer font-medium"
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Inspect PDF (Page {evidence.page_number})</span>
            <ExternalLink className="w-3 h-3 ml-0.5" />
          </button>
        )}
      </div>

      {evidence.announcement_title && (
        <div className="text-xs text-slate-400 font-medium mb-1.5 line-clamp-1">
          Source: <strong className="text-slate-300">{evidence.announcement_title}</strong>
        </div>
      )}

      <div className="bg-slate-950/90 rounded-lg p-3 border border-slate-800/80 text-xs text-slate-300 leading-relaxed font-mono relative">
        <BookOpen className="w-3.5 h-3.5 text-slate-600 absolute right-2.5 top-2.5" />
        <p className="pr-4">{evidence.excerpt}</p>
      </div>
    </div>
  );
};
