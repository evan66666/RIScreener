import React from 'react';
import {
  ArrowRight,
  User,
  Zap,
  Clock,
  ShieldAlert,
  Globe
} from 'lucide-react';
import type { SmartMoneySignal } from '../types';

interface SignalCardProps {
  signal: SmartMoneySignal;
  onSelect: (signalId: number) => void;
}

export const SignalCard: React.FC<SignalCardProps> = ({ signal, onSelect }) => {
  // Priority styles
  const priorityStyles: Record<string, { border: string; badge: string }> = {
    VERY_HIGH: {
      border: 'border-l-4 border-l-cyan-400',
      badge: 'bg-cyan-500/15 text-cyan-300 border-cyan-500/40',
    },
    HIGH: {
      border: 'border-l-4 border-l-sky-400',
      badge: 'bg-sky-500/15 text-sky-300 border-sky-500/40',
    },
    MEDIUM: {
      border: 'border-l-4 border-l-indigo-500',
      badge: 'bg-indigo-500/15 text-indigo-300 border-indigo-500/40',
    },
    LOW: {
      border: 'border-l-4 border-l-slate-700',
      badge: 'bg-slate-800 text-slate-400 border-slate-700',
    },
    WATCH: {
      border: 'border-l-4 border-l-slate-800',
      badge: 'bg-slate-900 text-slate-500 border-slate-800',
    },
  };

  const priorityLabels: Record<string, string> = {
    VERY_HIGH: 'Sangat Tinggi',
    HIGH: 'Tinggi',
    MEDIUM: 'Menengah',
    LOW: 'Rendah',
    WATCH: 'Pantau',
  };

  const behaviorLabels: Record<string, string> = {
    ACCUMULATION_CANDIDATE: 'Kandidat Akumulasi',
    STRATEGIC_POSITIONING_CANDIDATE: 'Posisi Strategis',
    NEW_POSITION: 'Posisi Baru',
    THRESHOLD_CROSSING: 'Perlintasan Batas (>5%)',
    SHARE_PLEDGE_FINANCING: 'Gadai Saham',
    SHARE_PLEDGE_RELEASE: 'Pelepasan Gadai',
    DISTRIBUTION_CANDIDATE: 'Kandidat Distribusi',
    POSITION_REDUCTION: 'Pengurangan Posisi',
    ADMINISTRATIVE_CHANGE: 'Perubahan Administratif',
  };

  const stageLabels: Record<string, string> = {
    DEVELOPING: 'Tahap Awal',
    EARLY: 'Rencana',
    EXPLICIT: 'Eksplisit',
  };

  const qualityLabels: Record<string, string> = {
    VERY_ATTRACTIVE: 'Sangat Menarik',
    ATTRACTIVE: 'Menarik',
    NEUTRAL_MIXED: 'Netral',
    UNATTRACTIVE_DILUTIVE: 'Dilutif',
    HIGH_RISK_DILUTIVE: 'Risiko Tinggi',
  };

  // Behavior badge color classes
  const behaviorBadges: Record<string, string> = {
    ACCUMULATION_CANDIDATE: 'bg-emerald-950/80 text-emerald-300 border-emerald-700/50',
    STRATEGIC_POSITIONING_CANDIDATE: 'bg-cyan-950/80 text-cyan-300 border-cyan-700/50',
    NEW_POSITION: 'bg-indigo-950/80 text-indigo-300 border-indigo-700/50',
    THRESHOLD_CROSSING: 'bg-purple-950/80 text-purple-300 border-purple-700/50',
    SHARE_PLEDGE_FINANCING: 'bg-amber-950/80 text-amber-300 border-amber-700/50',
    SHARE_PLEDGE_RELEASE: 'bg-teal-950/80 text-teal-300 border-teal-700/50',
    DISTRIBUTION_CANDIDATE: 'bg-rose-950/80 text-rose-300 border-rose-700/50',
    POSITION_REDUCTION: 'bg-amber-950/80 text-amber-300 border-amber-700/50',
    ADMINISTRATIVE_CHANGE: 'bg-slate-800 text-slate-400 border-slate-700',
  };

  const stageBadges: Record<string, string> = {
    DEVELOPING: 'bg-amber-950/70 text-amber-300 border-amber-700/50',
    EARLY: 'bg-indigo-950/70 text-indigo-300 border-indigo-700/50',
    EXPLICIT: 'bg-emerald-950/70 text-emerald-300 border-emerald-700/50',
  };

  const roleBadges: Record<string, { label: string; badge: string }> = {
    CONTROLLER: { label: 'Pengendali (PSP)', badge: 'bg-amber-950/80 text-amber-300 border-amber-700/60' },
    DIRECTOR: { label: 'Direksi', badge: 'bg-blue-950/80 text-blue-300 border-blue-700/60' },
    COMMISSIONER: { label: 'Komisaris', badge: 'bg-indigo-950/80 text-indigo-300 border-indigo-700/60' },
    STRATEGIC_INVESTOR: { label: 'Inv. Strategis', badge: 'bg-cyan-950/80 text-cyan-300 border-cyan-700/60' },
    INSTITUTION: { label: 'Institusi', badge: 'bg-purple-950/80 text-purple-300 border-purple-700/60' },
    SIGNIFICANT_HOLDER: { label: 'Pemegang >5%', badge: 'bg-slate-800 text-slate-300 border-slate-700' },
  };

  const pStyle = priorityStyles[signal.priority] || priorityStyles.MEDIUM;
  const bBadge = behaviorBadges[signal.behavior_type] || 'bg-slate-800 text-slate-300 border-slate-700';

  const formattedDate = signal.last_signal_at
    ? new Date(signal.last_signal_at).toLocaleDateString('id-ID', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
      })
    : '';

  const rawActor = signal.actor_name || 'Pihak Terlapor';
  const cleanActor = rawActor.length > 40 ? `${rawActor.substring(0, 38)}...` : rawActor;

  return (
    <div
      onClick={() => onSelect(signal.id)}
      className={`glass-panel rounded-xl p-4 sm:p-5 transition-all duration-150 cursor-pointer ${pStyle.border} border border-slate-800/90 hover:border-slate-700 group hover:bg-slate-900/50`}
    >
      {/* Row 1: Ticker & Company Name (Left), Priority & Score (Right) */}
      <div className="flex items-center justify-between gap-3 mb-1.5">
        <div className="flex items-center space-x-2.5 min-w-0">
          <span className="px-2 py-0.5 bg-slate-900 border border-slate-700 rounded-md text-sm font-bold text-cyan-300 font-mono shrink-0">
            {signal.ticker}
          </span>
          <div className="min-w-0">
            <h3 className="text-sm font-bold text-slate-100 group-hover:text-cyan-300 transition-colors truncate" title={signal.company_name || signal.ticker}>
              {signal.company_name || signal.ticker}
            </h3>
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${pStyle.badge}`}>
            {priorityLabels[signal.priority] || signal.priority}
          </span>

          {/* Smart Money Score Meter */}
          <div className="flex items-center gap-1 px-2 py-0.5 rounded-md bg-slate-900 border border-slate-800">
            <Zap className="w-3 h-3 text-cyan-400 fill-current" />
            <span className="text-xs font-bold text-cyan-300 font-mono">
              {signal.smart_money_score}
            </span>
            <span className="text-[10px] text-slate-500 font-mono">/100</span>
          </div>
        </div>
      </div>

      {/* Row 2: Sector, Date & Badges */}
      <div className="flex items-center justify-between gap-2 flex-wrap mb-3 text-xs text-slate-400">
        <div className="flex items-center gap-1.5 flex-wrap">
          {signal.sector && (
            <span className="text-slate-400 font-medium">{signal.sector}</span>
          )}
          {formattedDate && (
            <span className="text-[11px] text-slate-500 font-mono">&bull; {formattedDate}</span>
          )}
        </div>

        <div className="flex items-center gap-1.5 flex-wrap">
          {signal.quality_label && signal.quality_label !== 'QUALITY_UNCLEAR' && (
            <span className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${
              signal.quality_label === 'VERY_ATTRACTIVE' || signal.quality_label === 'ATTRACTIVE'
                ? 'bg-emerald-950/80 text-emerald-300 border-emerald-700/50'
                : signal.quality_label === 'NEUTRAL_MIXED'
                ? 'bg-amber-950/80 text-amber-300 border-amber-700/50'
                : 'bg-rose-950/80 text-rose-300 border-rose-700/50'
            }`}>
              {qualityLabels[signal.quality_label] || signal.quality_label} ({signal.quality_score})
            </span>
          )}

          {signal.hsc_flag && (
            <span className="flex items-center gap-1 text-[10px] font-bold px-1.5 py-0.5 rounded bg-purple-950/80 text-purple-300 border border-purple-700/50" title="Konsentrasi Kepemilikan Tinggi">
              <ShieldAlert className="w-2.5 h-2.5" />
              HSC
            </span>
          )}

          {signal.free_float_pct !== undefined && signal.free_float_pct !== null && (
            <span className="text-[10px] font-mono font-medium px-1.5 py-0.5 rounded bg-slate-900 text-slate-300 border border-slate-800" title="Free Float Publik">
              Float: {signal.free_float_pct.toFixed(1)}%
            </span>
          )}
        </div>
      </div>

      {/* Row 3: Actor, Behavior State, Ownership Delta */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 p-3 rounded-lg bg-slate-900/60 border border-slate-800/80 mb-3">
        {/* Left: Actor info */}
        <div className="space-y-1.5 min-w-0">
          <div className="flex items-center gap-1.5 flex-wrap">
            <User className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
            <span className="text-xs font-semibold text-slate-100 truncate max-w-[200px]" title={rawActor}>
              {cleanActor}
            </span>
            {signal.actor_type && roleBadges[signal.actor_type] && (
              <span className={`text-[9px] font-bold px-1.5 py-0.2 rounded border ${roleBadges[signal.actor_type].badge}`}>
                {roleBadges[signal.actor_type].label}
              </span>
            )}
            {signal.domicile === 'FOREIGN' && (
              <span className="flex items-center gap-1 text-[9px] font-bold px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                <Globe className="w-2.5 h-2.5" />
                Asing
              </span>
            )}
          </div>

          <div className="flex items-center gap-1.5 flex-wrap">
            <span className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${bBadge}`}>
              {behaviorLabels[signal.behavior_type] || signal.behavior_type.replace(/_/g, ' ')}
            </span>
            {signal.transaction_count > 1 && (
              <span className="text-[10px] font-medium text-slate-400 bg-slate-800 px-1.5 py-0.5 rounded border border-slate-700">
                {signal.transaction_count}x Transaksi
              </span>
            )}
          </div>
        </div>

        {/* Right: Ownership change */}
        <div className="space-y-1 sm:text-right">
          <div className="flex items-center sm:justify-end gap-1.5 text-xs">
            <span className="text-slate-400">Perubahan:</span>
            <span className={`font-mono font-bold ${signal.total_shares_delta >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
              {signal.total_shares_delta >= 0 ? `+${signal.total_shares_delta.toLocaleString('id-ID')}` : signal.total_shares_delta.toLocaleString('id-ID')} lembar
            </span>
          </div>

          <div className="flex items-center sm:justify-end gap-2 text-xs flex-wrap">
            {signal.pct_before !== undefined && signal.pct_after !== undefined && (
              <span className="text-slate-300 font-mono text-[11px]">
                {signal.pct_before.toFixed(2)}% &rarr; <strong className="text-cyan-300">{signal.pct_after.toFixed(2)}%</strong> ({signal.delta_pct >= 0 ? `+${signal.delta_pct.toFixed(2)}%` : `${signal.delta_pct.toFixed(2)}%`})
              </span>
            )}
            {signal.avg_price && (
              <span className="text-amber-300 font-mono text-[11px] bg-slate-800 px-1.5 py-0.2 rounded border border-slate-700">
                @ Rp {signal.avg_price.toLocaleString('id-ID')}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Row 4: Action Name, Stage, Lead time, and Clean "Lihat Detail" Link */}
      <div className="flex items-center justify-between gap-2 text-xs pt-0.5">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-slate-400 font-medium">Aksi:</span>
          <span className="font-semibold text-slate-200">
            {signal.action_name}
          </span>
          <span className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${stageBadges[signal.stage] || stageBadges.EARLY}`}>
            {stageLabels[signal.stage] || signal.stage}
          </span>
          {signal.lead_time_days !== undefined && signal.lead_time_days !== null && (
            <span className="flex items-center gap-1 text-[10px] font-mono font-medium text-cyan-300 bg-slate-900 border border-slate-800 px-1.5 py-0.5 rounded">
              <Clock className="w-3 h-3 text-cyan-400" />
              T-{signal.lead_time_days}h
            </span>
          )}
        </div>

        {/* Clean Detail Action */}
        <div className="flex items-center gap-1 text-xs font-semibold text-cyan-400 group-hover:text-cyan-300 transition-colors shrink-0">
          <span>Lihat Detail</span>
          <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
        </div>
      </div>
    </div>
  );
};
