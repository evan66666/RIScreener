import React, { useState, useEffect } from 'react';
import { Play, RotateCw, Calendar, Clock, Radar, ArrowRight } from 'lucide-react';

interface HeaderProps {
  scanRange: string;
  setScanRange: (val: string) => void;
  lookbackDays: number;
  setLookbackDays: (val: number) => void;
  scanMode: string;
  setScanMode: (val: string) => void;
  customFrom: string;
  setCustomFrom: (val: string) => void;
  customTo: string;
  setCustomTo: (val: string) => void;
  onRunScreening: () => void;
  isLoading: boolean;
  lastScanTime?: string;
}

interface DataSource {
  source_mode: string;
  source_label: string;
  playwright_installed: boolean;
  cloudflare_cookies_cached: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  scanRange,
  setScanRange,
  lookbackDays,
  setLookbackDays,
  scanMode,
  setScanMode,
  customFrom,
  setCustomFrom,
  customTo,
  setCustomTo,
  onRunScreening,
  isLoading,
}) => {
  const [dataSource, setDataSource] = useState<DataSource | null>(null);

  useEffect(() => {
    fetch('/api/data-source')
      .then(r => r.json())
      .then(setDataSource)
      .catch(() => {});
  }, []);

  const isLiveMode = dataSource?.source_mode?.startsWith('IDX_LIVE');

  return (
    <header className="border-b border-slate-800 bg-slate-950/90 backdrop-blur-md sticky top-0 z-30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
        <div className="flex items-center justify-between gap-4">
          
          {/* Left: Clean Logo & Title */}
          <div className="flex items-center space-x-3 shrink-0">
            <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
              <Radar className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-bold tracking-tight text-slate-100">RIScreener</span>
                <span className="text-[10px] font-semibold px-1.5 py-0.2 rounded bg-slate-800 text-slate-400 border border-slate-700 font-mono">
                  v7.3
                </span>
              </div>
              <p className="text-[11px] text-slate-400 hidden sm:block">
                Intelijen Aksi Korporasi & Kepemilikan IDX
              </p>
            </div>
          </div>

          {/* Right: All Controls Aligned Right */}
          <div className="ml-auto flex items-center gap-2.5 flex-wrap sm:flex-nowrap justify-end">
            
            {/* Live Connection Badge */}
            {dataSource && (
              <span
                className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-[11px] font-medium text-slate-300"
                title={dataSource.source_label}
              >
                <span className={`w-1.5 h-1.5 rounded-full ${isLiveMode ? 'bg-emerald-400' : 'bg-amber-400'}`} />
                <span>{isLiveMode ? 'Live IDX' : 'Sample'}</span>
              </span>
            )}

            {/* Mode Switcher (Smart / Audit) */}
            <div className="flex items-center bg-slate-900 border border-slate-800 rounded-lg p-0.5 text-xs">
              <button
                type="button"
                onClick={() => setScanMode('smart')}
                className={`px-2.5 py-1 rounded font-semibold transition-colors cursor-pointer ${
                  scanMode === 'smart'
                    ? 'bg-slate-800 text-cyan-300 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
                title="Smart Scan: Tier A priority + triggered Tier B"
              >
                Smart
              </button>
              <button
                type="button"
                onClick={() => setScanMode('full_audit')}
                className={`px-2.5 py-1 rounded font-semibold transition-colors cursor-pointer ${
                  scanMode === 'full_audit'
                    ? 'bg-slate-800 text-indigo-300 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
                title="Full Audit: Deep process all filings"
              >
                Audit
              </button>
            </div>

            {/* Scan Range Dropdown */}
            <div className="flex items-center bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1 text-xs text-slate-300">
              <Calendar className="w-3.5 h-3.5 text-slate-400 mr-1.5 shrink-0" />
              <select
                value={scanRange}
                onChange={(e) => {
                  const val = e.target.value;
                  setScanRange(val);
                  if (val === 'custom') {
                    const todayStr = new Date().toISOString().split('T')[0];
                    const past30 = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
                    if (!customFrom) setCustomFrom(past30);
                    if (!customTo) setCustomTo(todayStr);
                  }
                }}
                className="bg-transparent text-slate-200 font-medium focus:outline-none cursor-pointer pr-1"
              >
                <option value="today" className="bg-slate-900 text-slate-200">Hari Ini</option>
                <option value="3days" className="bg-slate-900 text-slate-200">3 Hari Terakhir</option>
                <option value="7days" className="bg-slate-900 text-slate-200">7 Hari Terakhir</option>
                <option value="1month" className="bg-slate-900 text-slate-200">30 Hari Terakhir</option>
                <option value="custom" className="bg-slate-900 text-slate-200">Kustom Tanggal</option>
              </select>
            </div>

            {/* Custom Range Picker */}
            {scanRange === 'custom' && (
              <div className="flex items-center gap-1.5 bg-slate-900 border border-slate-700 rounded-lg px-2 py-1 text-xs">
                <input
                  type="date"
                  value={customFrom}
                  onChange={(e) => setCustomFrom(e.target.value)}
                  className="bg-slate-800 text-slate-200 text-xs px-1.5 py-0.5 rounded border border-slate-700 font-mono"
                />
                <ArrowRight className="w-3 h-3 text-slate-500" />
                <input
                  type="date"
                  value={customTo}
                  onChange={(e) => setCustomTo(e.target.value)}
                  className="bg-slate-800 text-slate-200 text-xs px-1.5 py-0.5 rounded border border-slate-700 font-mono"
                />
              </div>
            )}

            {/* Lookback Selector */}
            <div className="hidden lg:flex items-center bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1 text-xs text-slate-300">
              <Clock className="w-3.5 h-3.5 text-slate-400 mr-1.5 shrink-0" />
              <select
                value={lookbackDays}
                onChange={(e) => setLookbackDays(Number(e.target.value))}
                className="bg-transparent text-slate-200 font-medium focus:outline-none cursor-pointer pr-1"
              >
                <option value={60} className="bg-slate-900 text-slate-200">Lookback 60 Hari</option>
                <option value={120} className="bg-slate-900 text-slate-200">Lookback 120 Hari</option>
              </select>
            </div>

            {/* Run Button */}
            <button
              onClick={onRunScreening}
              disabled={isLoading}
              className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg font-semibold text-xs transition-all cursor-pointer ${
                isLoading
                  ? 'bg-slate-800 text-slate-400 cursor-not-allowed'
                  : 'bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold active:scale-95'
              }`}
            >
              {isLoading ? (
                <>
                  <RotateCw className="w-3.5 h-3.5 animate-spin" />
                  <span>Scanning...</span>
                </>
              ) : (
                <>
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>Screening IDX</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};
