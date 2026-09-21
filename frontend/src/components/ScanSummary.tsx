import React from 'react';
import { FileText, Download, TrendingUp, Zap } from 'lucide-react';
import type { ScanSummary, ScanRecord } from '../types';

interface ScanSummaryProps {
  summary: ScanSummary | null;
  lookbackDays: number;
  scan?: ScanRecord | null;
}

export const ScanSummaryBanner: React.FC<ScanSummaryProps> = ({ summary, lookbackDays, scan }) => {
  if (!summary) return null;

  const modeLabel = (summary.scan_mode || 'smart').toLowerCase() === 'full_audit' ? 'Full Audit' : 'Smart Scan';

  return (
    <div className="glass-panel rounded-xl p-5 mb-6 border border-slate-800 shadow-lg">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-800/80">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-sm font-bold text-slate-100">
              Ringkasan Screening Intelijen
            </h2>
            <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-800 text-cyan-300 border border-slate-700 font-mono">
              {modeLabel}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1 flex items-center gap-2 flex-wrap">
            <span>Data keterbukaan informasi Bursa Efek Indonesia &bull; Lookback {lookbackDays} hari</span>
            {scan?.id && (
              <span className="px-1.5 py-0.5 rounded bg-cyan-950/60 border border-cyan-700/40 text-cyan-300 font-mono text-[10px] font-semibold">
                Scan #{scan.id}
              </span>
            )}
            {scan?.completed_at && (
              <span className="text-emerald-400/90 font-medium">
                &bull; Diperbarui: {new Date(scan.completed_at).toLocaleString('id-ID', {
                  day: '2-digit',
                  month: 'short',
                  hour: '2-digit',
                  minute: '2-digit',
                })} WIB
              </span>
            )}
          </p>
        </div>

        {/* Status badges */}
        <div className="flex items-center gap-2 text-xs">
          <span className="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 font-medium">
            Terkonfirmasi: <strong className="text-emerald-400 font-mono">{summary.explicit ?? 0}</strong>
          </span>
          <span className="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 font-medium">
            Tahap Awal: <strong className="text-amber-400 font-mono">{summary.developing ?? 0}</strong>
          </span>
        </div>
      </div>

      {/* 4 Clean Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3.5 mt-4">
        {/* 1. Announcements */}
        <div className="bg-slate-900/70 rounded-xl p-3.5 border border-slate-800/90 hover:border-slate-700 transition-colors">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Pengumuman IDX</span>
            <FileText className="w-3.5 h-3.5 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100 font-mono mt-1.5 tracking-tight">
            {summary.announcements_retrieved}
          </div>
          <div className="text-[11px] text-slate-500 mt-0.5">
            Total keterbukaan informasi
          </div>
        </div>

        {/* 2. PDFs Parsed */}
        <div className="bg-slate-900/70 rounded-xl p-3.5 border border-slate-800/90 hover:border-slate-700 transition-colors">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Dokumen Diproses</span>
            <Download className="w-3.5 h-3.5 text-sky-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100 font-mono mt-1.5 tracking-tight">
            {summary.pdfs_extracted}{' '}
            <span className="text-xs font-normal text-slate-400">/ {summary.pdfs_downloaded} PDF</span>
          </div>
          <div className="text-[11px] text-slate-500 mt-0.5">
            Lampiran diunduh & dianalisis
          </div>
        </div>

        {/* 3. Ownership Events */}
        <div className="bg-slate-900/70 rounded-xl p-3.5 border border-slate-800/90 hover:border-slate-700 transition-colors">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Perubahan Kepemilikan</span>
            <TrendingUp className="w-3.5 h-3.5 text-indigo-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100 font-mono mt-1.5 tracking-tight">
            {summary.ownership_events ?? 0}
          </div>
          <div className="text-[11px] text-slate-500 mt-0.5">
            Transaksi kepemilikan saham &gt;5%
          </div>
        </div>

        {/* 4. Signals Detected */}
        <div className="bg-slate-900/70 rounded-xl p-3.5 border border-slate-800/90 hover:border-slate-700 transition-colors">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Sinyal Terdeteksi</span>
            <Zap className="w-3.5 h-3.5 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold text-cyan-300 font-mono mt-1.5 tracking-tight">
            {summary.signals_total}
          </div>
          <div className="text-[11px] text-slate-500 mt-0.5">
            Aksi korporasi aktif teridentifikasi
          </div>
        </div>
      </div>
    </div>
  );
};
