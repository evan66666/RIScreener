import React from 'react';
import { X, ExternalLink, FileText } from 'lucide-react';

interface PdfViewerModalProps {
  documentId: number | null;
  targetPage?: number;
  onClose: () => void;
}

export const PdfViewerModal: React.FC<PdfViewerModalProps> = ({
  documentId,
  targetPage = 1,
  onClose,
}) => {
  if (!documentId) return null;

  const pdfUrl = `/api/documents/${documentId}/pdf#page=${targetPage}`;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fade-in">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-5xl h-[85vh] flex flex-col shadow-2xl overflow-hidden">
        
        {/* Modal Header */}
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-slate-800 bg-slate-950/70">
          <div className="flex items-center space-x-2">
            <FileText className="w-5 h-5 text-cyan-400" />
            <div>
              <h3 className="text-sm font-bold text-slate-100">
                Original Disclosure Document PDF
              </h3>
              <p className="text-[11px] text-slate-400">
                Document ID: #{documentId} &bull; Target Page: {targetPage}
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <a
              href={`/api/documents/${documentId}/pdf`}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold cursor-pointer transition-colors"
            >
              <ExternalLink className="w-3.5 h-3.5" />
              <span>Open in New Tab</span>
            </a>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 cursor-pointer transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* PDF Frame */}
        <div className="flex-1 bg-slate-950 p-1 relative">
          <iframe
            src={pdfUrl}
            className="w-full h-full rounded-b-xl border-0"
            title="PDF Document Viewer"
          />
        </div>
      </div>
    </div>
  );
};
