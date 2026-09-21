import React, { useState, useEffect, useRef, useMemo } from 'react';
import { FileSearch, RotateCw, AlertCircle, X, Sparkles, TrendingUp, Layers } from 'lucide-react';
import {
  triggerScreening,
  fetchLatestScan,
  fetchSignals,
  fetchSignalDetail,
  fetchActionFamilies,
} from './api/client';
import type { SmartMoneySignal, SignalDetail, ScanRecord, ScanSummary } from './types';
import { Header } from './components/Header';
import { ScanSummaryBanner } from './components/ScanSummary';
import { FilterBar } from './components/FilterBar';
import { SignalCard } from './components/SignalCard';
import { SignalDetailModal } from './components/SignalDetailModal';
import { PdfViewerModal } from './components/PdfViewerModal';

export const App: React.FC = () => {
  // Screening parameters
  const [scanRange, setScanRange] = useState<string>('7days');
  const [lookbackDays, setLookbackDays] = useState<number>(60);
  const [scanMode, setScanMode] = useState<string>('smart');
  const [customFrom, setCustomFrom] = useState<string>('');
  const [customTo, setCustomTo] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const pollTimerRef = useRef<any>(null);

  // Data states
  const [scan, setScan] = useState<ScanRecord | null>(null);
  const [summary, setSummary] = useState<ScanSummary | null>(null);
  const [signals, setSignals] = useState<SmartMoneySignal[]>([]);
  const [actionFamilies, setActionFamilies] = useState<Array<{ key: string; name: string }>>([]);
  const [transformationFamilies, setTransformationFamilies] = useState<Array<{ key: string; name: string }>>([]);

  // Filter states
  const [selectedPriority, setSelectedPriority] = useState<string>('');
  const [selectedBehavior, setSelectedBehavior] = useState<string>('');
  const [selectedStage, setSelectedStage] = useState<string>('');
  const [selectedAction, setSelectedAction] = useState<string>('');
  const [searchTicker, setSearchTicker] = useState<string>('');
  const [filterDateRange, setFilterDateRange] = useState<string>('all');
  const [filterCustomFrom, setFilterCustomFrom] = useState<string>('');
  const [filterCustomTo, setFilterCustomTo] = useState<string>('');

  // Modal states
  const [selectedSignalId, setSelectedSignalId] = useState<number | null>(null);
  const [signalDetail, setSignalDetail] = useState<SignalDetail | null>(null);
  const [pdfModalDocId, setPdfModalDocId] = useState<number | null>(null);
  const [pdfModalPage, setPdfModalPage] = useState<number>(1);

  // Load initial data
  useEffect(() => {
    loadInitialData();
    return () => {
      if (pollTimerRef.current) clearInterval(pollTimerRef.current);
    };
  }, []);

  const loadInitialData = async () => {
    try {
      setErrorMessage(null);
      const [scanData, famData] = await Promise.all([
        fetchLatestScan(),
        fetchActionFamilies(),
      ]);

      if (famData) {
        setActionFamilies(famData.corporate_actions || []);
        setTransformationFamilies(famData.corporate_transformations || []);
      }

      if (scanData.scan) {
        setScan(scanData.scan);
        setSummary(scanData.summary);
        if (scanData.scan.status === 'RUNNING') {
          setIsLoading(true);
          startPolling();
        } else {
          await loadSignals();
        }
      } else {
        setSignals([]);
      }
    } catch (e: any) {
      console.error('Error loading initial data:', e);
      setErrorMessage('Tidak dapat menghubungkan ke backend API. Pastikan server backend sedang berjalan.');
    }
  };

  const startPolling = () => {
    if (pollTimerRef.current) clearInterval(pollTimerRef.current);
    
    pollTimerRef.current = setInterval(async () => {
      try {
        const latest = await fetchLatestScan();
        if (latest.scan) {
          setScan(latest.scan);
          setSummary(latest.summary);

          if (latest.scan.status === 'COMPLETED' || latest.scan.status === 'FAILED') {
            if (pollTimerRef.current) {
              clearInterval(pollTimerRef.current);
              pollTimerRef.current = null;
            }
            setIsLoading(false);
            if (latest.scan.status === 'COMPLETED') {
              await loadSignals();
            } else if (latest.scan.status === 'FAILED') {
              setErrorMessage(latest.summary?.stage_message || 'Proses screening gagal diselesaikan.');
            }
          }
        }
      } catch (err) {
        console.error('Polling error:', err);
      }
    }, 1500);
  };

  const loadSignals = async () => {
    try {
      let dFrom: string | undefined;
      let dTo: string | undefined;
      const now = new Date();

      if (filterDateRange === 'today') {
        dFrom = now.toISOString().split('T')[0];
        dTo = dFrom;
      } else if (filterDateRange === '3days') {
        const past = new Date(now.getTime() - 3 * 24 * 60 * 60 * 1000);
        dFrom = past.toISOString().split('T')[0];
        dTo = now.toISOString().split('T')[0];
      } else if (filterDateRange === '7days') {
        const past = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        dFrom = past.toISOString().split('T')[0];
        dTo = now.toISOString().split('T')[0];
      } else if (filterDateRange === '30days') {
        const past = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
        dFrom = past.toISOString().split('T')[0];
        dTo = now.toISOString().split('T')[0];
      } else if (filterDateRange === 'custom') {
        dFrom = filterCustomFrom || undefined;
        dTo = filterCustomTo || undefined;
      }

      const data = await fetchSignals({
        priority: selectedPriority || undefined,
        behavior: selectedBehavior || undefined,
        action_type: selectedAction || undefined,
        stage: selectedStage || undefined,
        q: searchTicker.trim() || undefined,
        date_from: dFrom,
        date_to: dTo,
      });
      setSignals(data);
    } catch (e) {
      console.error('Error loading signals:', e);
    }
  };

  // Reload signals when filters or date filter change
  useEffect(() => {
    loadSignals();
  }, [
    selectedPriority,
    selectedBehavior,
    selectedStage,
    selectedAction,
    searchTicker,
    filterDateRange,
    filterCustomFrom,
    filterCustomTo,
  ]);

  // Handle Run Screening
  const handleRunScreening = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      let dFrom: string | undefined;
      let dTo: string | undefined;
      const now = new Date();

      if (scanRange === 'today') {
        dFrom = now.toISOString().split('T')[0];
        dTo = dFrom;
      } else if (scanRange === '3days') {
        const past = new Date(now.getTime() - 3 * 24 * 60 * 60 * 1000);
        dFrom = past.toISOString().split('T')[0];
        dTo = now.toISOString().split('T')[0];
      } else if (scanRange === '7days') {
        const past = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        dFrom = past.toISOString().split('T')[0];
        dTo = now.toISOString().split('T')[0];
      } else if (scanRange === '1month') {
        const past = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
        dFrom = past.toISOString().split('T')[0];
        dTo = now.toISOString().split('T')[0];
      } else if (scanRange === 'custom') {
        dFrom = customFrom || new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
        dTo = customTo || now.toISOString().split('T')[0];
      }

      const startRes = await triggerScreening({
        date_from: dFrom,
        date_to: dTo,
        lookback_days: lookbackDays,
        mode: scanMode,
      });

      // Update initial scan state
      if (startRes.summary) {
        setSummary(startRes.summary);
      }

      // Start background polling
      startPolling();

    } catch (e: any) {
      console.error('Screening trigger failed:', e);
      setErrorMessage(e?.message || 'Gagal memulai screening. Pastikan backend server aktif.');
      setIsLoading(false);
    }
  };

  // Open detail modal
  const handleSelectSignal = async (id: number) => {
    setSelectedSignalId(id);
    try {
      const detail = await fetchSignalDetail(id);
      setSignalDetail(detail);
    } catch (e) {
      console.error('Failed to load detail:', e);
    }
  };

  const handleOpenPdf = (docId: number, page: number = 1) => {
    setPdfModalDocId(docId);
    setPdfModalPage(page);
  };

  // Instant search filtering for zero-latency UI responsiveness
  const displaySignals = useMemo(() => {
    if (!searchTicker.trim()) return signals;
    const term = searchTicker.toLowerCase().trim();
    return signals.filter((s) => {
      const tickerMatch = s.ticker.toLowerCase().includes(term);
      const nameMatch = s.company_name.toLowerCase().includes(term);
      const actorMatch = s.actor_name ? s.actor_name.toLowerCase().includes(term) : false;
      const actionMatch = s.action_name ? s.action_name.toLowerCase().includes(term) : false;
      const catMatch = s.category ? s.category.toLowerCase().includes(term) : false;
      const whyMatch = s.why_flagged ? s.why_flagged.toLowerCase().includes(term) : false;
      const whatMatch = s.what_changed ? s.what_changed.toLowerCase().includes(term) : false;
      return tickerMatch || nameMatch || actorMatch || actionMatch || catMatch || whyMatch || whatMatch;
    });
  }, [signals, searchTicker]);

  // Categorize signals by priority from displaySignals
  const highPrioritySignals = displaySignals.filter(
    (s) => s.priority === 'VERY_HIGH' || s.priority === 'HIGH'
  );
  const mediumPrioritySignals = displaySignals.filter(
    (s) => s.priority === 'MEDIUM'
  );
  const otherSignals = displaySignals.filter(
    (s) => s.priority === 'LOW' || s.priority === 'WATCH' || (!['VERY_HIGH', 'HIGH', 'MEDIUM'].includes(s.priority))
  );

  const lastScanFormatted = scan?.completed_at
    ? new Date(scan.completed_at).toLocaleString('id-ID', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    : undefined;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      
      {/* Header with Scan Controls & Mode Selector */}
      <Header
        scanRange={scanRange}
        setScanRange={setScanRange}
        lookbackDays={lookbackDays}
        setLookbackDays={setLookbackDays}
        scanMode={scanMode}
        setScanMode={setScanMode}
        customFrom={customFrom}
        setCustomFrom={setCustomFrom}
        customTo={customTo}
        setCustomTo={setCustomTo}
        onRunScreening={handleRunScreening}
        isLoading={isLoading}
        lastScanTime={lastScanFormatted}
      />

      {/* Error notification banner */}
      {errorMessage && (
        <div className="max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 mt-4">
          <div className="flex items-center justify-between p-4 rounded-xl bg-rose-950/80 border border-rose-600/50 text-rose-200 text-sm shadow-lg shadow-rose-950/40">
            <div className="flex items-center space-x-3">
              <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />
              <div>
                <span className="font-semibold text-rose-300">Pemberitahuan: </span>
                <span>{errorMessage}</span>
              </div>
            </div>
            <button
              onClick={() => setErrorMessage(null)}
              className="p-1 hover:bg-rose-900/60 rounded-md text-rose-400 hover:text-rose-200 transition-colors cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        
        {/* Live Progress Banner during active screening */}
        {(isLoading || scan?.status === 'RUNNING') && (
          <div className="glass-panel rounded-xl p-4 sm:p-5 mb-6 border border-cyan-500/30 shadow-lg bg-slate-900/90">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3">
              <div className="flex items-center space-x-3">
                <div className="p-2 rounded-lg bg-cyan-950/60 border border-cyan-700/40 text-cyan-400">
                  <RotateCw className="w-4 h-4 animate-spin" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                    Screening Keterbukaan Informasi IDX Berjalan
                    <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-cyan-300 border border-slate-700 font-mono font-medium">
                      Mode: {scanMode.toUpperCase()}
                    </span>
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    {summary?.stage_message || 'Memproses pengumuman dan ekstraksi dokumen keterbukaan informasi...'}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="text-right">
                  <span className="text-xs text-slate-400 mr-2">Progress:</span>
                  <span className="text-base font-bold text-cyan-400 font-mono">
                    {summary?.progress_percent || 15}%
                  </span>
                </div>
              </div>
            </div>
            {/* Progress bar line */}
            <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden border border-slate-700/50">
              <div
                className="bg-cyan-500 h-1.5 rounded-full transition-all duration-300"
                style={{ width: `${Math.max(5, summary?.progress_percent || 15)}%` }}
              />
            </div>
          </div>
        )}

        {/* Completeness Summary Banner */}
        <ScanSummaryBanner summary={summary} lookbackDays={lookbackDays} scan={scan} />

        {/* Filters */}
        <FilterBar
          selectedPriority={selectedPriority}
          setSelectedPriority={setSelectedPriority}
          selectedBehavior={selectedBehavior}
          setSelectedBehavior={setSelectedBehavior}
          selectedStage={selectedStage}
          setSelectedStage={setSelectedStage}
          selectedAction={selectedAction}
          setSelectedAction={setSelectedAction}
          searchTicker={searchTicker}
          setSearchTicker={setSearchTicker}
          filterDateRange={filterDateRange}
          setFilterDateRange={setFilterDateRange}
          filterCustomFrom={filterCustomFrom}
          setFilterCustomFrom={setFilterCustomFrom}
          filterCustomTo={filterCustomTo}
          setFilterCustomTo={setFilterCustomTo}
          actionFamilies={actionFamilies}
          transformationFamilies={transformationFamilies}
          totalCount={displaySignals.length}
        />

        {/* Signals Section */}
        {displaySignals.length === 0 ? (
          <div className="glass-panel rounded-xl p-12 text-center border border-slate-800 shadow-md bg-slate-900/30">
            <FileSearch className="w-10 h-10 text-slate-500 mx-auto mb-3" />
            {searchTicker.trim() ? (
              <>
                <h3 className="text-sm font-bold text-slate-200">
                  Tidak Ditemukan Sinyal untuk "{searchTicker.trim()}"
                </h3>
                <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto leading-relaxed">
                  Tidak ada emiten, ticker, pihak terafiliasi, atau jenis aksi korporasi yang cocok dengan kata kunci tersebut.
                </p>
                <button
                  onClick={() => setSearchTicker('')}
                  className="mt-4 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-cyan-400 text-xs font-semibold rounded-lg border border-slate-700 transition-all cursor-pointer"
                >
                  Reset Pencarian
                </button>
              </>
            ) : (
              <>
                <h3 className="text-sm font-bold text-slate-200">Belum Ada Sinyal Ditampilkan</h3>
                <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto leading-relaxed">
                  Pilih rentang tanggal di header lalu klik <span className="text-cyan-400 font-semibold">Screening IDX</span> untuk memulai pencarian dan analisis keterbukaan informasi.
                </p>
              </>
            )}
          </div>
        ) : (
          <div className="space-y-7">
            
            {/* 1. Very High & High Priority Strategic Positioning */}
            {highPrioritySignals.length > 0 && (
              <div>
                <div className="flex items-center space-x-2 mb-3">
                  <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
                  <h2 className="text-xs font-bold uppercase tracking-wider text-slate-100 flex items-center gap-2">
                    <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                    Prioritas Tinggi & Sangat Tinggi
                  </h2>
                  <span className="px-2 py-0.2 rounded text-[10px] font-semibold bg-slate-800 text-cyan-400 border border-slate-700">
                    {highPrioritySignals.length} Sinyal
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
                  {highPrioritySignals.map((sig) => (
                    <SignalCard
                      key={sig.id}
                      signal={sig}
                      onSelect={(id) => handleSelectSignal(id)}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* 2. Medium Priority Signals */}
            {mediumPrioritySignals.length > 0 && (
              <div>
                <div className="flex items-center space-x-2 mb-3 pt-3 border-t border-slate-800/80">
                  <span className="w-2 h-2 rounded-full bg-sky-400"></span>
                  <h2 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                    <TrendingUp className="w-3.5 h-3.5 text-sky-400" />
                    Prioritas Menengah
                  </h2>
                  <span className="px-2 py-0.2 rounded text-[10px] font-semibold bg-slate-800 text-sky-300 border border-slate-700">
                    {mediumPrioritySignals.length} Sinyal
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
                  {mediumPrioritySignals.map((sig) => (
                    <SignalCard
                      key={sig.id}
                      signal={sig}
                      onSelect={(id) => handleSelectSignal(id)}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* 3. Low Priority, Watchlist & Administrative Disclosures */}
            {otherSignals.length > 0 && (
              <div>
                <div className="flex items-center space-x-2 mb-3 pt-3 border-t border-slate-800/80">
                  <span className="w-2 h-2 rounded-full bg-slate-500"></span>
                  <h2 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                    <Layers className="w-3.5 h-3.5 text-slate-400" />
                    Prioritas Rendah & Pemantauan
                  </h2>
                  <span className="px-2 py-0.2 rounded text-[10px] font-semibold bg-slate-800 text-slate-400 border border-slate-700">
                    {otherSignals.length} Sinyal
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
                  {otherSignals.map((sig) => (
                    <SignalCard
                      key={sig.id}
                      signal={sig}
                      onSelect={(id) => handleSelectSignal(id)}
                    />
                  ))}
                </div>
              </div>
            )}

          </div>
        )}

      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-4 text-center text-xs text-slate-500">
        RIScreener v7.3 &bull; Intelijen Aksi Korporasi & Kepemilikan IDX
      </footer>

      {/* Detail Modal */}
      {selectedSignalId && signalDetail && (
        <SignalDetailModal
          signal={signalDetail}
          onClose={() => {
            setSelectedSignalId(null);
            setSignalDetail(null);
          }}
          onOpenPdf={(docId, page) => handleOpenPdf(docId, page)}
        />
      )}

      {/* PDF Viewer Modal */}
      {pdfModalDocId && (
        <PdfViewerModal
          documentId={pdfModalDocId}
          targetPage={pdfModalPage}
          onClose={() => setPdfModalDocId(null)}
        />
      )}

    </div>
  );
};

export default App;
