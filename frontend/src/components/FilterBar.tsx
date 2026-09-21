import React from 'react';
import { Search, X, Calendar, ArrowRight } from 'lucide-react';

interface FilterBarProps {
  selectedPriority: string;
  setSelectedPriority: (val: string) => void;
  selectedBehavior: string;
  setSelectedBehavior: (val: string) => void;
  selectedStage: string;
  setSelectedStage: (val: string) => void;
  selectedAction: string;
  setSelectedAction: (val: string) => void;
  searchTicker: string;
  setSearchTicker: (val: string) => void;
  filterDateRange: string;
  setFilterDateRange: (val: string) => void;
  filterCustomFrom: string;
  setFilterCustomFrom: (val: string) => void;
  filterCustomTo: string;
  setFilterCustomTo: (val: string) => void;
  actionFamilies: Array<{ key: string; name: string }>;
  transformationFamilies: Array<{ key: string; name: string }>;
  totalCount: number;
}

export const FilterBar: React.FC<FilterBarProps> = ({
  selectedPriority,
  setSelectedPriority,
  selectedBehavior,
  setSelectedBehavior,
  selectedStage,
  setSelectedStage,
  selectedAction,
  setSelectedAction,
  searchTicker,
  setSearchTicker,
  filterDateRange,
  setFilterDateRange,
  filterCustomFrom,
  setFilterCustomFrom,
  filterCustomTo,
  setFilterCustomTo,
  actionFamilies,
  transformationFamilies,
  totalCount,
}) => {
  const priorityTabs = [
    { label: 'Semua Prioritas', value: '' },
    { label: 'Sangat Tinggi', value: 'VERY_HIGH' },
    { label: 'Tinggi', value: 'HIGH' },
    { label: 'Menengah', value: 'MEDIUM' },
    { label: 'Rendah / Pantau', value: 'LOW' },
  ];

  const behaviorOptions = [
    { label: 'Semua Perilaku', value: '' },
    { label: 'Kandidat Akumulasi', value: 'ACCUMULATION_CANDIDATE' },
    { label: 'Posisi Strategis', value: 'STRATEGIC_POSITIONING_CANDIDATE' },
    { label: 'Posisi Baru', value: 'NEW_POSITION' },
    { label: 'Perlintasan Batas (>5%)', value: 'THRESHOLD_CROSSING' },
    { label: 'Kandidat Distribusi', value: 'DISTRIBUTION_CANDIDATE' },
    { label: 'Perubahan Administratif', value: 'ADMINISTRATIVE_CHANGE' },
  ];

  const stageOptions = [
    { label: 'Semua Tahap', value: '' },
    { label: 'Tahap Awal', value: 'DEVELOPING' },
    { label: 'Rencana', value: 'EARLY' },
    { label: 'Eksplisit / Terjadwal', value: 'EXPLICIT' },
  ];

  const dateOptions = [
    { label: 'Semua Data', value: 'all' },
    { label: 'Hari Ini', value: 'today' },
    { label: '3 Hari Terakhir', value: '3days' },
    { label: '7 Hari Terakhir', value: '7days' },
    { label: '30 Hari Terakhir', value: '30days' },
    { label: 'Kustom Tanggal...', value: 'custom' },
  ];

  const clearFilters = () => {
    setSelectedPriority('');
    setSelectedBehavior('');
    setSelectedStage('');
    setSelectedAction('');
    setSearchTicker('');
    setFilterDateRange('all');
    setFilterCustomFrom('');
    setFilterCustomTo('');
  };

  const hasActiveFilters =
    selectedPriority ||
    selectedBehavior ||
    selectedStage ||
    selectedAction ||
    searchTicker ||
    filterDateRange !== 'all' ||
    filterCustomFrom ||
    filterCustomTo;

  return (
    <div className="glass-panel rounded-xl p-4 mb-6 border border-slate-800 shadow-md space-y-3">
      {/* Top Filter Row: Priority Tabs + Search */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
        {/* Priority Tabs */}
        <div className="flex flex-wrap items-center bg-slate-900/90 border border-slate-800 rounded-lg p-1 gap-1">
          {priorityTabs.map((tab) => {
            const isActive = selectedPriority === tab.value;
            return (
              <button
                key={tab.value}
                onClick={() => setSelectedPriority(tab.value)}
                className={`px-3 py-1 text-xs font-semibold rounded-md transition-all cursor-pointer ${
                  isActive
                    ? 'bg-slate-800 text-cyan-300 shadow-sm border border-slate-700/80'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                }`}
              >
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Search Input */}
        <div className="relative w-full lg:w-80">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Cari emiten, ticker, atau pihak..."
            value={searchTicker}
            onChange={(e) => setSearchTicker(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-9 pr-8 py-1.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500/60 focus:ring-1 focus:ring-cyan-500/30 transition-all font-medium"
          />
          {searchTicker && (
            <button
              onClick={() => setSearchTicker('')}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200 p-0.5 rounded cursor-pointer"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Secondary Dropdown Filter Row */}
      <div className="flex flex-wrap items-center gap-2 pt-2.5 border-t border-slate-800/70 text-xs">
        {/* Behavior Dropdown */}
        <div className="flex items-center bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1 text-slate-300">
          <span className="text-[11px] font-medium text-slate-400 mr-1.5">Perilaku:</span>
          <select
            value={selectedBehavior}
            onChange={(e) => setSelectedBehavior(e.target.value)}
            className="bg-transparent text-slate-200 text-xs font-semibold focus:outline-none cursor-pointer"
          >
            {behaviorOptions.map((opt) => (
              <option key={opt.value} value={opt.value} className="bg-slate-900 text-slate-200">
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        {/* Corporate Action & Transformation Family Dropdown */}
        <div className="flex items-center bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1 text-slate-300">
          <span className="text-[11px] font-medium text-slate-400 mr-1.5">Aksi:</span>
          <select
            value={selectedAction}
            onChange={(e) => setSelectedAction(e.target.value)}
            className="bg-transparent text-slate-200 text-xs font-semibold focus:outline-none max-w-[210px] truncate cursor-pointer"
          >
            <option value="" className="bg-slate-900 text-slate-200">Semua Aksi & Katalis</option>
            <optgroup label="Aksi Korporasi" className="bg-slate-900 text-cyan-400 font-bold">
              {actionFamilies.map((fam) => (
                <option key={fam.key} value={fam.key} className="bg-slate-900 text-slate-200 font-normal">
                  {fam.name}
                </option>
              ))}
            </optgroup>
            {transformationFamilies && transformationFamilies.length > 0 && (
              <optgroup label="Katalis Transformasi" className="bg-slate-900 text-indigo-400 font-bold">
                {transformationFamilies.map((fam) => (
                  <option key={fam.key} value={fam.key} className="bg-slate-900 text-slate-200 font-normal">
                    {fam.name}
                  </option>
                ))}
              </optgroup>
            )}
          </select>
        </div>

        {/* Stage Dropdown */}
        <div className="flex items-center bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1 text-slate-300">
          <span className="text-[11px] font-medium text-slate-400 mr-1.5">Tahap:</span>
          <select
            value={selectedStage}
            onChange={(e) => setSelectedStage(e.target.value)}
            className="bg-transparent text-slate-200 text-xs font-semibold focus:outline-none cursor-pointer"
          >
            {stageOptions.map((opt) => (
              <option key={opt.value} value={opt.value} className="bg-slate-900 text-slate-200">
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        {/* Date Filter Dropdown */}
        <div className="flex items-center bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1 text-xs text-slate-300">
          <Calendar className="w-3.5 h-3.5 text-slate-400 mr-1.5 shrink-0" />
          <span className="text-[11px] font-medium text-slate-400 mr-1.5">Tanggal:</span>
          <select
            value={filterDateRange}
            onChange={(e) => {
              const val = e.target.value;
              setFilterDateRange(val);
              if (val === 'custom') {
                const todayStr = new Date().toISOString().split('T')[0];
                const past7 = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
                if (!filterCustomFrom) setFilterCustomFrom(past7);
                if (!filterCustomTo) setFilterCustomTo(todayStr);
              }
            }}
            className="bg-transparent text-slate-200 text-xs font-semibold focus:outline-none cursor-pointer"
          >
            {dateOptions.map((opt) => (
              <option key={opt.value} value={opt.value} className="bg-slate-900 text-slate-200">
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        {/* Custom date range inputs */}
        {filterDateRange === 'custom' && (
          <div className="flex items-center gap-1.5 bg-slate-900 border border-slate-700 rounded-lg px-2 py-1 text-xs">
            <input
              type="date"
              value={filterCustomFrom}
              onChange={(e) => setFilterCustomFrom(e.target.value)}
              className="bg-slate-800 text-slate-200 text-xs font-mono px-1.5 py-0.5 rounded border border-slate-700"
            />
            <ArrowRight className="w-3 h-3 text-slate-500" />
            <input
              type="date"
              value={filterCustomTo}
              onChange={(e) => setFilterCustomTo(e.target.value)}
              className="bg-slate-800 text-slate-200 text-xs font-mono px-1.5 py-0.5 rounded border border-slate-700"
            />
          </div>
        )}

        {/* Active Filters Clear */}
        {hasActiveFilters && (
          <button
            onClick={clearFilters}
            className="flex items-center gap-1 text-xs text-rose-400 hover:text-rose-200 bg-rose-950/40 hover:bg-rose-900/50 border border-rose-800/40 rounded-lg px-2.5 py-1 transition-colors cursor-pointer font-medium"
          >
            <X className="w-3.5 h-3.5" />
            <span>Reset Filter</span>
          </button>
        )}

        <div className="text-xs text-slate-400 ml-auto flex items-center gap-2 font-medium bg-slate-900 border border-slate-800 px-3 py-1 rounded-lg">
          <span className="w-2 h-2 rounded-full bg-emerald-400" />
          <span>Sinyal:</span>
          <strong className="text-cyan-300 font-mono font-bold">{totalCount}</strong>
        </div>
      </div>
    </div>
  );
};
