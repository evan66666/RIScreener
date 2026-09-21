import React, { useState } from 'react';
import {
  X,
  Calendar,
  FileText,
  ExternalLink,
  ShieldCheck,
  User,
  Zap,
  TrendingUp,
  Clock,
  Layers,
  AlertTriangle,
  Building2,
  Lock,
  Scale,
  Info,
  CheckCircle,
  AlertOctagon,
  Sparkles,
} from 'lucide-react';
import type { SignalDetail } from '../types';

interface SignalDetailModalProps {
  signal: SignalDetail | null;
  onClose: () => void;
  onOpenPdf: (docId: number, page?: number) => void;
}

// Translation & Formatting Helpers for Professional Financial Terminal UI
const formatActorType = (type?: string): string => {
  if (!type) return 'Pemegang Saham Strategis';
  switch (type.toUpperCase().replace(/\s+/g, '_')) {
    case 'CONTROLLER':
      return 'Pemegang Saham Pengendali';
    case 'STRATEGIC_HOLDER':
      return 'Pemegang Saham Strategis';
    case 'FINANCIAL_INSTITUTION':
      return 'Institusi Keuangan';
    case 'MANAGEMENT':
      return 'Direksi / Komisaris';
    case 'INDIVIDUAL':
      return 'Individu / Perorangan';
    case 'FOUNDATION':
      return 'Yayasan / Lembaga';
    case 'CORPORATE':
      return 'Korporasi / Badan Usaha';
    case 'BENEFICIAL_OWNER':
      return 'Pemilik Manfaat Akhir';
    default:
      return type.replace(/_/g, ' ');
  }
};

const formatDomicile = (dom?: string): string => {
  if (!dom) return 'Domestik';
  switch (dom.toUpperCase()) {
    case 'ID':
    case 'LOCAL':
    case 'DOMESTIC':
      return 'Indonesia (Domestik)';
    case 'FOREIGN':
      return 'Asing';
    case 'SG':
      return 'Singapura';
    case 'MY':
      return 'Malaysia';
    case 'HK':
      return 'Hong Kong';
    case 'US':
      return 'Amerika Serikat';
    default:
      return dom;
  }
};

const formatBehavior = (type?: string): string => {
  if (!type) return 'Posisi Strategis';
  switch (type.toUpperCase().replace(/\s+/g, '_')) {
    case 'ACCUMULATION_CANDIDATE':
      return 'Kandidat Akumulasi';
    case 'STRATEGIC_POSITIONING_CANDIDATE':
      return 'Posisi Strategis';
    case 'EXPANSION_CANDIDATE':
      return 'Ekspansi Kepemilikan';
    case 'STABLE_LARGE_HOLDER':
      return 'Pemegang Saham Mayoritas Stabil';
    case 'STRATEGIC_HOLDER':
      return 'Pemegang Saham Strategis';
    case 'DIVESTMENT':
      return 'Divestasi / Penjualan';
    case 'INSIDER_BUY':
      return 'Pembelian Orang Dalam (Insider)';
    case 'INSIDER_SELL':
      return 'Penjualan Orang Dalam (Insider)';
    case 'PLEDGE_INCREASE':
      return 'Penambahan Jaminan Saham';
    case 'PLEDGE_RELEASE':
      return 'Pelepasan Jaminan Saham';
    default:
      return type.replace(/_/g, ' ');
  }
};

const formatStage = (stage?: string): string => {
  if (!stage) return 'Tahap Awal';
  switch (stage.toUpperCase()) {
    case 'CONFIRMED':
    case 'EXPLICIT':
      return 'Terkonfirmasi';
    case 'DEVELOPING':
      return 'Tahap Awal';
    case 'EARLY':
      return 'Rencana';
    case 'EXPLORATORY':
      return 'Eksplorasi';
    default:
      return stage.replace(/_/g, ' ');
  }
};

const formatQualityLabel = (label?: string): string => {
  if (!label) return 'Belum Dianalisis';
  switch (label.toUpperCase()) {
    case 'VERY_ATTRACTIVE':
      return 'Sangat Menarik';
    case 'ATTRACTIVE':
      return 'Menarik';
    case 'NEUTRAL_MIXED':
      return 'Netral / Campuran';
    case 'DILUTIVE_HIGH_RISK':
      return 'Berisiko Tinggi / Dilutif';
    case 'VALUE_DESTRUCTIVE':
      return 'Destruktif Nilai';
    case 'QUALITY_UNCLEAR':
      return 'Data Terbatas';
    default:
      return label.replace(/_/g, ' ');
  }
};

const formatOpportunityState = (state?: string): string => {
  if (!state) return 'Dalam Pemantauan';
  switch (state.toUpperCase().replace(/\s+/g, '_')) {
    case 'HIGH_CONVICTION_OPPORTUNITY':
      return 'Peluang Kuat Terarah';
    case 'CONFIRMED_OPPORTUNITY':
      return 'Peluang Terkonfirmasi';
    case 'SPECULATIVE_CATALYST':
      return 'Katalis Spekulatif';
    case 'DEVELOPING_UNCLEAR':
      return 'Dalam Pemantauan';
    case 'EXPLICIT_UNCLEAR':
      return 'Eksplisit (Perlu Telaah Lanjutan)';
    case 'HIGH_RISK_DILUTIVE':
      return 'Risiko Dilusi Tinggi';
    case 'LOW_ALIGNMENT':
      return 'Korelasi Rendah';
    default:
      return state.replace(/_/g, ' ');
  }
};

const formatConfidence = (conf?: string): string => {
  if (!conf) return 'Sedang';
  switch (conf.toUpperCase().replace(/\s+/g, '_')) {
    case 'HIGH':
      return 'Tinggi';
    case 'MEDIUM_HIGH':
      return 'Menengah ke Tinggi';
    case 'MEDIUM':
      return 'Sedang';
    case 'MEDIUM_LOW':
      return 'Menengah ke Rendah';
    case 'LOW':
      return 'Rendah';
    default:
      return conf;
  }
};

const formatProceedsCategory = (cat?: string): string => {
  if (!cat) return 'Operasional';
  switch (cat.toUpperCase().replace(/\s+/g, '_')) {
    case 'CAPEX':
      return 'Belanja Modal (Capex)';
    case 'WORKING_CAPITAL':
      return 'Modal Kerja (Working Capital)';
    case 'DELEVERAGING':
    case 'DEBT_REPAYMENT':
      return 'Pelunasan Utang (Deleveraging)';
    case 'INVESTMENT':
      return 'Investasi / Akuisisi';
    case 'SUBSIDIARY_EQUITY':
      return 'Penyertaan Modal Anak Usaha';
    default:
      return cat.replace(/_/g, ' ');
  }
};

const formatDriver = (driver: string): string => {
  switch (driver.toUpperCase().replace(/\s+/g, '_')) {
    case 'ORGANIC_GROWTH_EXPANSION':
      return 'Ekspansi pertumbuhan usaha organik';
    case 'STRONG_STANDBY_BUYER':
      return 'Tersedia komitmen pembeli siaga kredibel';
    case 'LOW_DILUTION':
      return 'Tingkat dilusi relatif rendah (<15%)';
    case 'STRATEGIC_MNA':
      return 'Akuisisi strategis operasional & sinergi';
    case 'ATTRACTIVE_DISCOUNT':
      return 'Harga pelaksanaan berada di valuasi menarik';
    case 'CLEAR_USE_OF_PROCEEDS':
      return 'Rincian alokasi modal kerja terukur';
    case 'DELEVERAGING_BENEFIT':
      return 'Penurunan beban bunga pinjaman (Deleveraging)';
    case 'SHAREHOLDER_VALUE_ACCRETIVE':
      return 'Berpotensi meningkatkan nilai per saham';
    case 'PRICING_DISCOUNT_ATTRACTIVE':
      return 'Harga pelaksanaan memberikan diskon wajar';
    case 'PROCEEDS_EXPANSION_FOCUSED':
      return 'Mayoritas dana diarahkan untuk ekspansi produktif';
    default:
      return driver.replace(/_/g, ' ');
  }
};

const formatRedFlag = (flag: string): string => {
  switch (flag.toUpperCase().replace(/\s+/g, '_')) {
    case 'DEBT_SETTLEMENT_RISK':
      return 'Alokasi dominan untuk pelunasan utang afiliasi';
    case 'RELATED_PARTY_RISK':
    case 'RELATED_PARTY_ACQUISITION':
      return 'Risiko transaksi pihak terafiliasi pengendali';
    case 'HEAVY_DILUTION_RISK':
      return 'Potensi dilusi pemegang saham signifikan (>20%)';
    case 'UNCLEAR_USE_OF_PROCEEDS':
      return 'Rincian alokasi dana belum diuraikan spesifik';
    case 'BELOW_MARKET_STANDBY':
      return 'Harga tebus diskon dalam terhadap harga pasar';
    case 'NO_COMMITTED_STANDBY':
      return 'Belum terdapat pembeli siaga yang mengikat';
    case 'DISTRESS_RESCUE':
      return 'Indikasi penambahan modal darurat (turnaround)';
    case 'EXECUTION_UNCERTAINTY':
      return 'Tingkat ketidakpastian persetujuan regulator / RUPS';
    default:
      return flag.replace(/_/g, ' ');
  }
};

const formatEvidenceType = (type?: string): string => {
  if (!type) return 'Dokumen Keterbukaan';
  switch (type.toUpperCase()) {
    case 'OWNERSHIP_REPORT':
      return 'Laporan Kepemilikan Saham (X.M.1)';
    case 'RIGHTS_ISSUE_PROSPECTUS':
      return 'Prospektus / Info HMETD';
    case 'RUPS_NOTICE':
      return 'Panggilan / Hasil RUPS';
    case 'DISCLOSURE_OF_INFORMATION':
      return 'Keterbukaan Informasi Emiten';
    case 'SHARE_PLEDGE':
      return 'Laporan Penjaminan / Gadai';
    default:
      return type.replace(/_/g, ' ');
  }
};

const formatContextClass = (ctx?: string): string => {
  if (!ctx) return 'Keterbukaan Publik';
  switch (ctx.toUpperCase().replace(/\s+/g, '_')) {
    case 'MATERIAL_EXPANSION':
      return 'Ekspansi Material';
    case 'MANDATORY_DISCLOSURE':
      return 'Kewajiban Lapor';
    case 'CONTROLLER_CONSOLIDATION':
      return 'Konsolidasi Pengendali';
    case 'COLLATERAL_MANAGEMENT':
      return 'Pengelolaan Jaminan';
    case 'MARKET_ACQUISITION_CANDIDATE':
      return 'Akumulasi Pasar Reguler';
    case 'DIVESTMENT':
      return 'Divestasi Saham';
    default:
      return ctx.replace(/_/g, ' ');
  }
};

export const SignalDetailModal: React.FC<SignalDetailModalProps> = ({
  signal,
  onClose,
  onOpenPdf,
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'quality' | 'ownership' | 'structure' | 'timing' | 'evidence' | 'timeline'>('overview');

  if (!signal) return null;

  const priorityStr = signal.priority || signal.scores?.overall_priority || 'MEDIUM';
  const behaviorStr = signal.behavior_type || signal.behavior?.behavior_type || 'STRATEGIC_POSITIONING_CANDIDATE';
  const actorName = signal.actor?.canonical_name || signal.actor_name || 'Strategic Actor';
  const actorType = signal.actor?.actor_type || signal.actor_type || 'STRATEGIC_HOLDER';
  const actorDomicile = signal.actor?.domicile || signal.domicile || 'ID';
  const actionName = signal.action_name || signal.corporate_action?.action_name || 'Corporate Action';
  const stageStr = signal.stage || 'DEVELOPING';
  const sharesDelta = signal.total_shares_delta ?? signal.behavior?.total_shares_delta ?? 0;
  const pctBefore = signal.pct_before ?? signal.behavior?.pct_before ?? 0;
  const pctAfter = signal.pct_after ?? signal.behavior?.pct_after ?? 0;
  const deltaPct = signal.delta_pct ?? signal.behavior?.delta_pct ?? 0;
  const avgPrice = signal.avg_price ?? signal.behavior?.avg_price;

  // Structural Context
  const isHsc = signal.structural_context?.hsc_flag ?? signal.hsc_flag ?? false;
  const freeFloatPct = signal.structural_context?.free_float_pct ?? signal.free_float_pct;

  // Timing Metrics
  const timing = signal.timing_integrity;
  const lagDays = timing?.transaction_to_public_lag_days ?? signal.transaction_to_public_lag_days;
  const firstPublicLead = timing?.first_public_lead_days ?? signal.first_public_lead_days;
  const firstAlignmentLead = timing?.first_alignment_lead_days ?? signal.first_alignment_lead_days;
  const firstPositioningLead = timing?.first_positioning_lead_days ?? signal.first_positioning_lead_days;
  const explicitLeadDays = signal.lead_time_days ?? signal.scores?.lead_time_days;

  // Smart Money Decomposed Scores
  const scores = signal.scores;
  const smartMoneyScore = scores?.smart_money_score ?? signal.smart_money_score ?? 0;
  const actorScore = scores?.strategic_actor_score ?? signal.strategic_actor_score ?? scores?.strategic_positioning_score ?? 0;
  const behScore = scores?.ownership_behavior_score ?? signal.ownership_behavior_score ?? scores?.strategic_positioning_score ?? 0;
  const concScore = scores?.concentration_score ?? signal.concentration_score ?? 0;
  const caScore = scores?.corporate_action_score ?? signal.corporate_action_score ?? 0;
  const transScore = scores?.corporate_transformation_score ?? signal.corporate_transformation_score ?? 0;
  const evScore = scores?.evidence_quality_score ?? signal.evidence_quality_score ?? 70;
  const leadScore = scores?.lead_time_quality_score ?? signal.lead_time_quality_score ?? 70;
  const alignmentScore = scores?.alignment_score ?? signal.alignment_score ?? 0;

  // Corporate Action Quality Assessment
  const caAssessment = signal.corporate_action_assessment;
  const qualityScore = caAssessment?.quality_score ?? signal.quality_score;
  const qualityLabel = caAssessment?.quality_label ?? signal.quality_label ?? 'QUALITY_UNCLEAR';
  const svScore = caAssessment?.shareholder_value_score ?? signal.shareholder_value_score;
  const oppState = caAssessment?.opportunity_state ?? signal.opportunity_state ?? 'DEVELOPING_UNCLEAR';
  const positiveDrivers = caAssessment?.positive_drivers ?? [];
  const redFlags = caAssessment?.red_flags ?? [];
  const whyAttractive = caAssessment?.why_attractive;
  const whyRisky = caAssessment?.why_risky;
  const useOfProceeds = caAssessment?.use_of_proceeds ?? [];
  const dilutionPct = caAssessment?.dilution_pct ?? null;
  const newShareRatio = caAssessment?.new_share_ratio ?? null;
  const subPrice = caAssessment?.subscription_price ?? null;
  const caDecomp = caAssessment?.scores_decomposition;

  // Investor Classifications
  const investorClasses = signal.actor?.investor_classes || [];

  // Hierarchy
  const beneficialOwner = signal.actor?.beneficial_owner;
  const controller = signal.actor?.controller;

  // Pledge Check
  const hasPledges = (signal.ownership_history || []).some(
    (h) => h.pledge_flag || h.transaction_type?.includes('PLEDGE')
  );

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center p-2 sm:p-4 md:p-6 bg-slate-950/85 backdrop-blur-md animate-fade-in overflow-y-auto">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-5xl max-h-[92vh] flex flex-col shadow-2xl overflow-hidden my-auto">
        
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-800 bg-slate-950/95 flex items-start justify-between gap-4">
          <div className="space-y-2 min-w-0 flex-1">
            {/* Row 1: Ticker, Company Name, Sector */}
            <div className="flex flex-wrap items-center gap-2.5">
              <span className="px-2 py-0.5 bg-slate-900 border border-slate-700 rounded-md text-sm font-bold text-cyan-300 font-mono">
                {signal.ticker}
              </span>
              <h2 className="text-base font-bold text-slate-100 truncate" title={signal.company_name || signal.ticker}>
                {signal.company_name || signal.ticker}
              </h2>
              {signal.sector && (
                <span className="text-xs text-slate-400 font-medium">&bull; {signal.sector}</span>
              )}
            </div>

            {/* Row 2: Key Indicators */}
            <div className="flex flex-wrap items-center gap-2 text-xs">
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                priorityStr === 'VERY_HIGH'
                  ? 'bg-cyan-950/80 text-cyan-300 border-cyan-700/60'
                  : priorityStr === 'HIGH'
                  ? 'bg-sky-950/80 text-sky-300 border-sky-700/60'
                  : 'bg-slate-800 text-slate-300 border-slate-700'
              }`}>
                {priorityStr === 'VERY_HIGH' ? 'Sangat Tinggi' : priorityStr === 'HIGH' ? 'Tinggi' : 'Menengah'}
              </span>

              <div className="flex items-center gap-1 px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-[11px]">
                <Zap className="w-3 h-3 text-cyan-400 fill-current" />
                <span className="text-slate-400">Skor:</span>
                <strong className="text-cyan-300 font-mono font-bold">{smartMoneyScore}</strong>
                <span className="text-slate-500 text-[10px]">/100</span>
              </div>

              <span className="text-slate-600">&bull;</span>

              <span className="text-xs text-slate-300 flex items-center gap-1.5 truncate max-w-[260px]" title={actorName}>
                <User className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                <span className="truncate">{actorName}</span>
              </span>

              <span className="text-slate-600">&bull;</span>

              <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-900 text-slate-300 border border-slate-800">
                Aksi: <strong className="text-slate-100">{actionName}</strong> ({formatStage(stageStr)})
              </span>

              {freeFloatPct !== undefined && freeFloatPct !== null && (
                <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-medium border ${
                  freeFloatPct < 15.0
                    ? 'bg-amber-950/60 text-amber-300 border-amber-800/50'
                    : 'bg-slate-900 text-slate-300 border-slate-800'
                }`}>
                  Float: {freeFloatPct.toFixed(1)}% {freeFloatPct < 15.0 ? '(<15% Ketentuan IDX)' : ''}
                </span>
              )}

              {isHsc && (
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-purple-950/70 text-purple-300 border border-purple-700/50">
                  Konsentrasi Tinggi (HSC)
                </span>
              )}
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white cursor-pointer transition-colors border border-slate-700 shrink-0"
            title="Tutup modal (Esc)"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Navigation Tabs */}
        <div className="flex items-center px-4 sm:px-6 border-b border-slate-800 bg-slate-950/60 gap-1 overflow-x-auto">
          <button
            onClick={() => setActiveTab('overview')}
            className={`flex items-center gap-1.5 py-2.5 px-3 text-xs font-semibold border-b-2 transition-all cursor-pointer whitespace-nowrap shrink-0 ${
              activeTab === 'overview'
                ? 'border-cyan-400 text-cyan-300 bg-cyan-950/20'
                : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/40'
            }`}
          >
            <Layers className="w-3.5 h-3.5 text-cyan-400" />
            <span>Ringkasan & Skor</span>
          </button>
          <button
            onClick={() => setActiveTab('quality')}
            className={`flex items-center gap-1.5 py-2.5 px-3 text-xs font-semibold border-b-2 transition-all cursor-pointer whitespace-nowrap shrink-0 ${
              activeTab === 'quality'
                ? 'border-emerald-400 text-emerald-300 bg-emerald-950/20'
                : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/40'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
            <span>Kualitas & Valuasi Aksi</span>
          </button>
          <button
            onClick={() => setActiveTab('ownership')}
            className={`flex items-center gap-1.5 py-2.5 px-3 text-xs font-semibold border-b-2 transition-all cursor-pointer whitespace-nowrap shrink-0 ${
              activeTab === 'ownership'
                ? 'border-sky-400 text-sky-300 bg-sky-950/20'
                : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/40'
            }`}
          >
            <TrendingUp className="w-3.5 h-3.5 text-sky-400" />
            <span>Kepemilikan & Transaksi ({signal.ownership_history?.length || 0})</span>
          </button>
          <button
            onClick={() => setActiveTab('structure')}
            className={`flex items-center gap-1.5 py-2.5 px-3 text-xs font-semibold border-b-2 transition-all cursor-pointer whitespace-nowrap shrink-0 ${
              activeTab === 'structure'
                ? 'border-indigo-400 text-indigo-300 bg-indigo-950/20'
                : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/40'
            }`}
          >
            <Building2 className="w-3.5 h-3.5 text-indigo-400" />
            <span>Struktur Pemegang Saham</span>
          </button>
          <button
            onClick={() => setActiveTab('timing')}
            className={`flex items-center gap-1.5 py-2.5 px-3 text-xs font-semibold border-b-2 transition-all cursor-pointer whitespace-nowrap shrink-0 ${
              activeTab === 'timing'
                ? 'border-amber-400 text-amber-300 bg-amber-950/20'
                : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/40'
            }`}
          >
            <Clock className="w-3.5 h-3.5 text-amber-400" />
            <span>Timing & Lead Time</span>
          </button>
          <button
            onClick={() => setActiveTab('evidence')}
            className={`flex items-center gap-1.5 py-2.5 px-3 text-xs font-semibold border-b-2 transition-all cursor-pointer whitespace-nowrap shrink-0 ${
              activeTab === 'evidence'
                ? 'border-violet-400 text-violet-300 bg-violet-950/20'
                : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/40'
            }`}
          >
            <FileText className="w-3.5 h-3.5 text-violet-400" />
            <span>Bukti Pengumuman ({signal.evidence?.length || 0})</span>
          </button>
          <button
            onClick={() => setActiveTab('timeline')}
            className={`flex items-center gap-1.5 py-2.5 px-3 text-xs font-semibold border-b-2 transition-all cursor-pointer whitespace-nowrap shrink-0 ${
              activeTab === 'timeline'
                ? 'border-cyan-400 text-cyan-300 bg-cyan-950/20'
                : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/40'
            }`}
          >
            <Calendar className="w-3.5 h-3.5 text-cyan-400" />
            <span>Kronologi ({signal.timeline?.length || 0})</span>
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          
          {/* TAB 1: OVERVIEW */}
          {activeTab === 'overview' && (
            <div className="space-y-4">
              
              {/* Executive Summary Card */}
              <div className="bg-slate-950/90 border border-slate-800 rounded-xl p-4 shadow-md">
                <div className="flex items-center justify-between mb-2">
                  <div className="text-xs font-bold text-cyan-400 uppercase tracking-wider flex items-center gap-1.5">
                    <ShieldCheck className="w-4 h-4" />
                    Ringkasan Eksekutif
                  </div>
                  <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-800 text-amber-300 border border-slate-700">
                    Indikasi Strategis
                  </span>
                </div>
                <p className="text-sm text-slate-200 leading-relaxed font-medium">
                  {signal.what_changed || signal.why_flagged}
                </p>
                {signal.why_flagged && signal.what_changed && (
                  <div className="mt-2 pt-2 border-t border-slate-800/80 text-xs text-slate-400">
                    <strong className="text-slate-300">Catatan Analisis:</strong> {signal.why_flagged}
                  </div>
                )}
              </div>

              {/* Smart Money Score Breakdown */}
              <div className="bg-slate-950/70 rounded-xl p-4 border border-slate-800 space-y-3.5">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800/80 pb-2.5">
                  <div>
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
                      <Zap className="w-3.5 h-3.5 text-cyan-400" />
                      Rincian Skor Smart Money
                    </h3>
                    <p className="text-[11px] text-slate-400 mt-0.5">
                      Bobot atribusi faktor pihak, transaksi akumulasi, dan aksi korporasi.
                    </p>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="text-xs text-slate-400">Skor Total:</span>
                    <span className="text-xl font-bold text-cyan-300 font-mono">
                      {smartMoneyScore}
                      <span className="text-xs text-slate-500 font-normal">/100</span>
                    </span>
                  </div>
                </div>

                {/* Score Components Grid */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                  
                  {/* Strategic Actor */}
                  <div className="bg-slate-900/90 rounded-lg p-2.5 border border-slate-800">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold uppercase text-slate-400">Pihak Strategis</span>
                      <span className="text-[9px] px-1 bg-slate-800 rounded text-slate-400">15% wt</span>
                    </div>
                    <div className="text-lg font-black text-cyan-300 font-mono mt-1">{actorScore}</div>
                    <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mt-1.5">
                      <div className="bg-cyan-400 h-full rounded-full" style={{ width: `${Math.min(actorScore, 100)}%` }}></div>
                    </div>
                    <span className="text-[9px] text-slate-500 mt-1 block">Institusi / Pengendali</span>
                  </div>

                  {/* Ownership Behavior */}
                  <div className="bg-slate-900/90 rounded-lg p-2.5 border border-slate-800">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold uppercase text-slate-400">Perilaku Akumulasi</span>
                      <span className="text-[9px] px-1 bg-slate-800 rounded text-slate-400">20% wt</span>
                    </div>
                    <div className="text-lg font-black text-emerald-400 font-mono mt-1">{behScore}</div>
                    <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mt-1.5">
                      <div className="bg-emerald-400 h-full rounded-full" style={{ width: `${Math.min(behScore, 100)}%` }}></div>
                    </div>
                    <span className="text-[9px] text-slate-500 mt-1 block">Ekspansi Kepemilikan</span>
                  </div>

                  {/* Concentration Context */}
                  <div className="bg-slate-900/90 rounded-lg p-2.5 border border-slate-800">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold uppercase text-slate-400">Konsentrasi Saham</span>
                      <span className="text-[9px] px-1 bg-slate-800 rounded text-slate-400">10% wt</span>
                    </div>
                    <div className="text-lg font-black text-purple-400 font-mono mt-1">{concScore}</div>
                    <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mt-1.5">
                      <div className="bg-purple-400 h-full rounded-full" style={{ width: `${Math.min(concScore, 100)}%` }}></div>
                    </div>
                    <span className="text-[9px] text-slate-500 mt-1 block">{isHsc ? 'Konsentrasi Tinggi (HSC)' : 'Struktur Normal'}</span>
                  </div>

                  {/* Corporate Action Prep */}
                  <div className="bg-slate-900/90 rounded-lg p-2.5 border border-slate-800">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold uppercase text-slate-400">Katalis Korporasi</span>
                      <span className="text-[9px] px-1 bg-slate-800 rounded text-slate-400">20% wt</span>
                    </div>
                    <div className="text-lg font-black text-amber-400 font-mono mt-1">{caScore}</div>
                    <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mt-1.5">
                      <div className="bg-amber-400 h-full rounded-full" style={{ width: `${Math.min(caScore, 100)}%` }}></div>
                    </div>
                    <span className="text-[9px] text-slate-500 mt-1 block">RUPS / Rights Issue / Split</span>
                  </div>

                  {/* Corporate Transformation */}
                  <div className="bg-slate-900/90 rounded-lg p-2.5 border border-slate-800">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold uppercase text-slate-400">Transformasi</span>
                      <span className="text-[9px] px-1 bg-slate-800 rounded text-slate-400">15% wt</span>
                    </div>
                    <div className="text-lg font-black text-indigo-400 font-mono mt-1">{transScore}</div>
                    <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mt-1.5">
                      <div className="bg-indigo-400 h-full rounded-full" style={{ width: `${Math.min(transScore, 100)}%` }}></div>
                    </div>
                    <span className="text-[9px] text-slate-500 mt-1 block">M&A / Backdoor / Direksi</span>
                  </div>

                  {/* Cross-Layer Alignment */}
                  <div className="bg-slate-900/90 rounded-lg p-2.5 border border-slate-800">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold uppercase text-slate-400">Konvergensi Sinyal</span>
                      <span className="text-[9px] px-1 bg-slate-800 rounded text-slate-400">10% wt</span>
                    </div>
                    <div className="text-lg font-black text-rose-400 font-mono mt-1">{alignmentScore}</div>
                    <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mt-1.5">
                      <div className="bg-rose-400 h-full rounded-full" style={{ width: `${Math.min(alignmentScore, 100)}%` }}></div>
                    </div>
                    <span className="text-[9px] text-slate-500 mt-1 block">Korelasi Silang Dokumen</span>
                  </div>

                  {/* Evidence Quality */}
                  <div className="bg-slate-900/90 rounded-lg p-2.5 border border-slate-800">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold uppercase text-slate-400">Kualitas Bukti</span>
                      <span className="text-[9px] px-1 bg-slate-800 rounded text-slate-400">5% wt</span>
                    </div>
                    <div className="text-lg font-black text-teal-400 font-mono mt-1">{evScore}</div>
                    <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mt-1.5">
                      <div className="bg-teal-400 h-full rounded-full" style={{ width: `${Math.min(evScore, 100)}%` }}></div>
                    </div>
                    <span className="text-[9px] text-slate-500 mt-1 block">Kutipan Faktual & OCR</span>
                  </div>

                  {/* Lead Time Quality */}
                  <div className="bg-slate-900/90 rounded-lg p-2.5 border border-slate-800">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold uppercase text-slate-400">Lead Time Sinyal</span>
                      <span className="text-[9px] px-1 bg-slate-800 rounded text-slate-400">5% wt</span>
                    </div>
                    <div className="text-lg font-black text-yellow-400 font-mono mt-1">{leadScore}</div>
                    <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mt-1.5">
                      <div className="bg-yellow-400 h-full rounded-full" style={{ width: `${Math.min(leadScore, 100)}%` }}></div>
                    </div>
                    <span className="text-[9px] text-slate-500 mt-1 block">{explicitLeadDays ? `${explicitLeadDays} hari sebelum` : 'Sinyal Awal'}</span>
                  </div>

                </div>
              </div>

              {/* Actor Profile & Disclosed Facts */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                
                {/* Actor Profile Card */}
                <div className="bg-slate-950/60 rounded-xl p-4 border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                      <User className="w-3.5 h-3.5 text-cyan-400" />
                      Profil Pihak Terlapor
                    </h4>
                    <span className="px-1.5 py-0.5 rounded text-[9px] font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                      Data Resmi IDX
                    </span>
                  </div>
                  <div className="space-y-2 text-xs">
                    <div className="flex justify-between py-1 border-b border-slate-800/80">
                      <span className="text-slate-500">Nama Pihak:</span>
                      <strong className="text-slate-200">{actorName}</strong>
                    </div>
                    <div className="flex justify-between py-1 border-b border-slate-800/80">
                      <span className="text-slate-500">Klasifikasi Pihak:</span>
                      <span className="font-semibold text-cyan-400">{formatActorType(actorType)}</span>
                    </div>
                    <div className="flex justify-between py-1 border-b border-slate-800/80">
                      <span className="text-slate-500">Domisili / Yurisdiksi:</span>
                      <span className="font-semibold text-slate-200">{formatDomicile(actorDomicile)}</span>
                    </div>
                    {beneficialOwner && (
                      <div className="flex justify-between py-1 border-b border-slate-800/80">
                        <span className="text-slate-500">Beneficial Owner Akhir:</span>
                        <span className="font-bold text-amber-300">{beneficialOwner.name}</span>
                      </div>
                    )}
                    {controller && (
                      <div className="flex justify-between py-1 border-b border-slate-800/80">
                        <span className="text-slate-500">Pengendali Akhir:</span>
                        <span className="font-bold text-amber-300">{controller.name}</span>
                      </div>
                    )}
                    {signal.actor?.aliases && signal.actor.aliases.length > 0 && (
                      <div className="py-1 border-b border-slate-800/80">
                        <span className="text-slate-500 block mb-1">Alias Terdata:</span>
                        <div className="flex flex-wrap gap-1">
                          {signal.actor.aliases.map((al, idx) => (
                            <span key={idx} className="bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded text-[10px]">
                              {al}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Normalized Facts & Cost Basis */}
                <div className="bg-slate-950/60 rounded-xl p-4 border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                      <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
                      Posisi Kepemilikan & Estimasi Biaya
                    </h4>
                    <span className="px-1.5 py-0.5 rounded text-[9px] font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                      Kalkulasi
                    </span>
                  </div>
                  <div className="space-y-2 text-xs">
                    <div className="flex justify-between py-1 border-b border-slate-800/80">
                      <span className="text-slate-500">Klasifikasi Perilaku:</span>
                      <strong className="text-cyan-300">{formatBehavior(behaviorStr)}</strong>
                    </div>
                    <div className="flex justify-between py-1 border-b border-slate-800/80">
                      <span className="text-slate-500">Perubahan Saham:</span>
                      <span className="font-mono font-bold text-emerald-400">
                        {sharesDelta >= 0 ? `+${sharesDelta.toLocaleString('id-ID')}` : sharesDelta.toLocaleString('id-ID')} lembar
                      </span>
                    </div>
                    <div className="flex justify-between py-1 border-b border-slate-800/80">
                      <span className="text-slate-500">Porsi Kepemilikan:</span>
                      <span className="font-mono text-slate-200">
                        {pctBefore.toFixed(2)}% &rarr; <strong className="text-cyan-400">{pctAfter.toFixed(2)}%</strong> ({deltaPct >= 0 ? `+${deltaPct.toFixed(2)}%` : `${deltaPct.toFixed(2)}%`})
                      </span>
                    </div>
                    <div className="flex justify-between py-1 border-b border-slate-800/80">
                      <span className="text-slate-500">Rata-rata Harga Pembelian:</span>
                      <span className="font-mono font-bold text-amber-300">
                        {avgPrice ? `Rp ${avgPrice.toLocaleString('id-ID')}` : 'Tidak Dicantumkan'}
                      </span>
                    </div>
                    {lagDays !== undefined && lagDays !== null && (
                      <div className="flex justify-between py-1">
                        <span className="text-slate-500">Jeda Publikasi Dokumen:</span>
                        <span className="font-semibold text-yellow-400">{lagDays} hari sejak tanggal transaksi</span>
                      </div>
                    )}
                  </div>
                </div>

              </div>

            </div>
          )}

          {/* TAB 2: CORPORATE ACTION QUALITY & VALUE ASSESSMENT */}
          {activeTab === 'quality' && (
            <div className="space-y-4">
              
              {/* 4-Metric Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                
                {/* Likelihood */}
                <div className="bg-slate-950/70 rounded-xl p-3.5 border border-slate-800">
                  <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
                    Kepastian Tahap Aksi
                  </span>
                  <div className="text-base font-bold text-cyan-300 font-mono mt-1 tracking-tight">
                    {formatStage(caAssessment?.likelihood_stage || stageStr)}
                  </div>
                  <div className="text-xs text-slate-400 mt-1">
                    Skor: <strong className="text-cyan-300 font-mono">{caAssessment?.likelihood_score ?? 70}/100</strong>
                  </div>
                  <span className="text-[10px] text-slate-500 mt-0.5 block">Kematangan dokumen resmi</span>
                </div>

                {/* Quality Score */}
                <div className="bg-slate-950/70 rounded-xl p-3.5 border border-slate-800">
                  <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
                    Kualitas Aksi Korporasi
                  </span>
                  <div className="text-base font-bold text-emerald-300 font-mono mt-1 tracking-tight">
                    {formatQualityLabel(qualityLabel)}
                  </div>
                  <div className="text-xs text-slate-400 mt-1">
                    Skor: <strong className="text-emerald-400 font-mono">{qualityScore ?? '-'}/100</strong>
                  </div>
                  <span className="text-[10px] text-slate-500 mt-0.5 block">Daya tarik ekonomi & valuasi</span>
                </div>

                {/* Shareholder Value Score */}
                <div className="bg-slate-950/70 rounded-xl p-3.5 border border-slate-800">
                  <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
                    Nilai Pemegang Saham
                  </span>
                  <div className="text-xl font-bold text-indigo-300 font-mono mt-1 tracking-tight">
                    {svScore ?? '-'}
                    <span className="text-xs text-slate-500 font-normal">/100</span>
                  </div>
                  <span className="text-[10px] text-slate-500 mt-1 block">Dampak bagi pemegang minoritas</span>
                </div>

                {/* Opportunity State */}
                <div className="bg-slate-950/70 rounded-xl p-3.5 border border-slate-800">
                  <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
                    Status Peluang
                  </span>
                  <div className="text-sm font-bold text-amber-300 font-mono mt-1 tracking-tight">
                    {formatOpportunityState(oppState)}
                  </div>
                  <div className="text-xs text-slate-400 mt-1">
                    Tingkat Keyakinan: <span className="text-cyan-300 font-semibold">{formatConfidence(caAssessment?.confidence)}</span>
                  </div>
                  <span className="text-[10px] text-slate-500 mt-0.5 block">Sintesis akumulasi vs katalis</span>
                </div>

              </div>

              {/* Positive Drivers & Red Flags */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
                
                {/* Positive Drivers Card */}
                <div className="bg-emerald-950/20 rounded-xl p-3.5 border border-emerald-500/25 space-y-2">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-bold text-emerald-300 flex items-center gap-1.5">
                      <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
                      Faktor Pendorong Positif ({positiveDrivers.length})
                    </h4>
                  </div>
                  {positiveDrivers.length > 0 ? (
                    <div className="space-y-1.5 pt-1">
                      {positiveDrivers.map((driver, idx) => (
                        <div key={idx} className="flex items-start gap-2 text-xs text-slate-200">
                          <span className="text-emerald-400 font-bold mt-0.5">&bull;</span>
                          <span className="font-medium text-emerald-200">{formatDriver(driver)}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-xs text-slate-400 italic">
                      Tidak ada faktor pendorong positif spesifik yang terisolasi dari dokumen keterbukaan.
                    </div>
                  )}
                </div>

                {/* Red Flags Card */}
                <div className="bg-rose-950/20 rounded-xl p-3.5 border border-rose-500/25 space-y-2">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-bold text-rose-300 flex items-center gap-1.5">
                      <AlertOctagon className="w-3.5 h-3.5 text-rose-400" />
                      Catatan Risiko Struktural ({redFlags.length})
                    </h4>
                  </div>
                  {redFlags.length > 0 ? (
                    <div className="space-y-1.5 pt-1">
                      {redFlags.map((flag, idx) => (
                        <div key={idx} className="flex items-start gap-2 text-xs text-slate-200">
                          <span className="text-rose-400 font-bold mt-0.5">&bull;</span>
                          <span className="font-medium text-rose-200">{formatRedFlag(flag)}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-xs text-slate-400 italic">
                      Tidak teridentifikasi risiko struktural kritis pada pengumuman ini.
                    </div>
                  )}
                </div>

              </div>

              {/* Explanations: Why Potentially Attractive vs Why It May Fail */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
                
                {/* Why Attractive */}
                <div className="bg-slate-950/60 rounded-xl p-3.5 border border-slate-800 space-y-1.5">
                  <h4 className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                    Alasan Berpotensi Menarik
                  </h4>
                  <div className="text-xs text-slate-300 leading-relaxed whitespace-pre-line font-medium bg-slate-900/40 p-2.5 rounded-lg border border-slate-800/80">
                    {whyAttractive || "Informasi faktor penarik strategis belum terungkap secara spesifik dalam dokumen awal."}
                  </div>
                </div>

                {/* Why Risky */}
                <div className="bg-slate-950/60 rounded-xl p-3.5 border border-slate-800 space-y-1.5">
                  <h4 className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                    Potensi Risiko & Tantangan
                  </h4>
                  <div className="text-xs text-slate-300 leading-relaxed whitespace-pre-line font-medium bg-slate-900/40 p-2.5 rounded-lg border border-slate-800/80">
                    {whyRisky || "Risiko struktural material belum teridentifikasi dari keterbukaan awal."}
                  </div>
                </div>

              </div>

              {/* Use of Proceeds Breakdown & Dilution Terms */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
                
                {/* Use of Proceeds Table */}
                <div className="bg-slate-950/60 rounded-xl p-3.5 border border-slate-800 space-y-2">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
                      <Building2 className="w-3.5 h-3.5 text-cyan-400" />
                      Rencana Penggunaan Dana
                    </h4>
                  </div>
                  {useOfProceeds.length > 0 ? (
                    <div className="overflow-x-auto rounded-lg border border-slate-800">
                      <table className="w-full text-left text-xs">
                        <thead className="bg-slate-900 text-slate-400">
                          <tr>
                            <th className="p-2">Kategori</th>
                            <th className="p-2 text-right">Alokasi</th>
                            <th className="p-2">Deskripsi</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800/80 font-mono">
                          {useOfProceeds.map((p, idx) => (
                            <tr key={idx} className="hover:bg-slate-900/50">
                              <td className="p-2 font-sans font-semibold text-cyan-300">{formatProceedsCategory(p.category)}</td>
                              <td className="p-2 text-right text-emerald-400 font-bold">
                                {p.percentage !== null && p.percentage !== undefined ? `${p.percentage}%` : '-'}
                              </td>
                              <td className="p-2 font-sans text-slate-400 text-[11px] truncate max-w-[150px]">{p.description}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <div className="text-xs text-slate-500 italic p-3 text-center bg-slate-900/40 rounded-lg">
                      Rincian alokasi penggunaan dana belum diuraikan secara numerik dalam dokumen keterbukaan ini.
                    </div>
                  )}
                </div>

                {/* Dilution & Pricing Economics */}
                <div className="bg-slate-950/60 rounded-xl p-3.5 border border-slate-800 space-y-2">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
                      <Scale className="w-3.5 h-3.5 text-cyan-400" />
                      Ekonomi Harga & Potensi Dilusi
                    </h4>
                  </div>
                  <div className="space-y-1.5 text-xs">
                    <div className="flex justify-between py-1 border-b border-slate-800/80">
                      <span className="text-slate-500">Rasio Hak Memesan / Saham:</span>
                      <span className="font-mono font-bold text-slate-200">{newShareRatio || 'Belum Diumumkan'}</span>
                    </div>
                    <div className="flex justify-between py-1 border-b border-slate-800/80">
                      <span className="text-slate-500">Potensi Dilusi (Non-Partisipasi):</span>
                      <span className={`font-mono font-bold ${dilutionPct && dilutionPct > 20 ? 'text-rose-400' : 'text-slate-200'}`}>
                        {dilutionPct !== null && dilutionPct !== undefined ? `${dilutionPct.toFixed(1)}%` : 'Belum Ditentukan'}
                      </span>
                    </div>
                    <div className="flex justify-between py-1 border-b border-slate-800/80">
                      <span className="text-slate-500">Harga Pelaksanaan (Exercise Price):</span>
                      <span className="font-mono font-bold text-amber-300">
                        {subPrice ? `Rp ${subPrice.toLocaleString('id-ID')}` : 'Belum Ditetapkan'}
                      </span>
                    </div>
                    <div className="flex justify-between py-1">
                      <span className="text-slate-500">Status Pembeli Siaga:</span>
                      <span className="font-semibold text-emerald-400">
                        {caAssessment?.recipients?.has_standby_buyer ? 'Tersedia Komitmen' : 'Belum Diungkapkan'}
                      </span>
                    </div>
                  </div>
                </div>

              </div>

              {/* 10 Quality Dimensions Decomposition Grid */}
              {caDecomp && (
                <div className="bg-slate-950/60 rounded-xl p-3.5 border border-slate-800 space-y-2.5">
                  <h4 className="text-xs font-bold text-slate-300">
                    Evaluasi 10 Dimensi Kualitas Aksi Korporasi
                  </h4>
                  <div className="grid grid-cols-2 sm:grid-cols-5 gap-2.5 pt-1 text-xs">
                    
                    <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                      <div className="flex justify-between text-[10px] text-slate-400 font-medium">
                        <span>Rasional Strategis</span>
                        <span>20%</span>
                      </div>
                      <div className="font-mono font-bold text-cyan-300 mt-1 text-sm">{caDecomp.strategic_rationale_score ?? 50}</div>
                    </div>

                    <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                      <div className="flex justify-between text-[10px] text-slate-400 font-medium">
                        <span>Efisiensi Modal</span>
                        <span>20%</span>
                      </div>
                      <div className="font-mono font-bold text-emerald-300 mt-1 text-sm">{caDecomp.capital_efficiency_score ?? 50}</div>
                    </div>

                    <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                      <div className="flex justify-between text-[10px] text-slate-400 font-medium">
                        <span>Dampak Dilusi</span>
                        <span>15%</span>
                      </div>
                      <div className="font-mono font-bold text-purple-300 mt-1 text-sm">{caDecomp.dilution_score ?? 50}</div>
                    </div>

                    <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                      <div className="flex justify-between text-[10px] text-slate-400 font-medium">
                        <span>Kualitas Aset</span>
                        <span>15%</span>
                      </div>
                      <div className="font-mono font-bold text-amber-300 mt-1 text-sm">{caDecomp.asset_quality_score ?? 50}</div>
                    </div>

                    <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                      <div className="flex justify-between text-[10px] text-slate-400 font-medium">
                        <span>Kualitas Dana</span>
                        <span>10%</span>
                      </div>
                      <div className="font-mono font-bold text-teal-300 mt-1 text-sm">{caDecomp.funding_quality_score ?? 50}</div>
                    </div>

                    <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                      <div className="flex justify-between text-[10px] text-slate-400 font-medium">
                        <span>Kesesuaian Kendali</span>
                        <span>Multi</span>
                      </div>
                      <div className="font-mono font-bold text-indigo-300 mt-1 text-sm">{caDecomp.control_alignment_score ?? 50}</div>
                    </div>

                    <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                      <div className="flex justify-between text-[10px] text-slate-400 font-medium">
                        <span>Daya Tarik Harga</span>
                        <span>Multi</span>
                      </div>
                      <div className="font-mono font-bold text-sky-300 mt-1 text-sm">{caDecomp.pricing_attractiveness_score ?? 50}</div>
                    </div>

                    <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                      <div className="flex justify-between text-[10px] text-slate-400 font-medium">
                        <span>Risiko Eksekusi</span>
                        <span>Multi</span>
                      </div>
                      <div className="font-mono font-bold text-rose-300 mt-1 text-sm">{caDecomp.execution_risk_score ?? 50}</div>
                    </div>

                    <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                      <div className="flex justify-between text-[10px] text-slate-400 font-medium">
                        <span>Risiko Afiliasi</span>
                        <span>Multi</span>
                      </div>
                      <div className="font-mono font-bold text-orange-300 mt-1 text-sm">{caDecomp.related_party_risk_score ?? 50}</div>
                    </div>

                    <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                      <div className="flex justify-between text-[10px] text-slate-400 font-medium">
                        <span>Risiko Finansial</span>
                        <span>Multi</span>
                      </div>
                      <div className="font-mono font-bold text-yellow-300 mt-1 text-sm">{caDecomp.distress_risk_score ?? 50}</div>
                    </div>

                  </div>
                </div>
              )}

            </div>
          )}

          {/* TAB 3: OWNERSHIP & TRANSACTIONS TABLE */}
          {activeTab === 'ownership' && (
            <div className="space-y-3.5">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                <h3 className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
                  <Layers className="w-3.5 h-3.5 text-cyan-400" />
                  Riwayat Perubahan Kepemilikan & Gadai Saham
                </h3>
                <span className="text-xs text-slate-500">
                  Perbandingan tanggal transaksi efektif dengan tanggal publikasi IDX
                </span>
              </div>

              {signal.ownership_history && signal.ownership_history.length > 0 ? (
                <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-950/60">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="border-b border-slate-800 bg-slate-900/80 text-slate-400 font-semibold">
                        <th className="p-3">Tgl Transaksi</th>
                        <th className="p-3">Tgl Publikasi</th>
                        <th className="p-3">Pihak Terlapor</th>
                        <th className="p-3">Jenis</th>
                        <th className="p-3 text-right">Perubahan Saham</th>
                        <th className="p-3 text-right">Sebelum</th>
                        <th className="p-3 text-right">Sesudah</th>
                        <th className="p-3 text-right">Harga</th>
                        <th className="p-3">Keterangan</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 font-mono">
                      {signal.ownership_history.map((ow) => {
                        const isPledge = ow.pledge_flag || ow.transaction_type?.includes('PLEDGE');
                        const isRelease = ow.transaction_type?.includes('RELEASE');
                        const isAcq = ow.event_type === 'ACQUIRE' || ow.transaction_type?.includes('ACQUISITION');
                        const isDisposal = ow.event_type === 'DISPOSE' || ow.transaction_type?.includes('DISPOSAL');
                        
                        return (
                          <tr key={ow.id} className="hover:bg-slate-800/30 transition-colors">
                            <td className="p-3 text-slate-300 whitespace-nowrap">
                              {ow.transaction_date 
                                ? new Date(ow.transaction_date).toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' })
                                : ow.event_date 
                                ? new Date(ow.event_date).toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' })
                                : '-'}
                            </td>
                            <td className="p-3 text-slate-500 whitespace-nowrap">
                              {ow.publication_date 
                                ? new Date(ow.publication_date).toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' })
                                : '-'}
                            </td>
                            <td className="p-3 font-sans font-medium text-slate-200 truncate max-w-[150px]">
                              {ow.actor_name}
                            </td>
                            <td className="p-3">
                              {isPledge ? (
                                <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-amber-950 text-amber-300 border border-amber-700/60 flex items-center gap-1 w-fit">
                                  <Lock className="w-2.5 h-2.5" />
                                  GADAI
                                </span>
                              ) : isRelease ? (
                                <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-indigo-950 text-indigo-300 border border-indigo-700/60 w-fit">
                                  LEPAS GADAI
                                </span>
                              ) : isAcq ? (
                                <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-emerald-950 text-emerald-300 border border-emerald-800 w-fit">
                                  BELI
                                </span>
                              ) : isDisposal ? (
                                <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-rose-950 text-rose-300 border border-rose-800 w-fit">
                                  JUAL
                                </span>
                              ) : (
                                <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-slate-800 text-slate-300 border border-slate-700 w-fit">
                                  {ow.event_type}
                                </span>
                              )}
                            </td>
                            <td className={`p-3 text-right font-bold ${ow.delta_shares >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                              {ow.delta_shares >= 0 ? `+${ow.delta_shares.toLocaleString('id-ID')}` : ow.delta_shares.toLocaleString('id-ID')}
                            </td>
                            <td className="p-3 text-right text-slate-400">{ow.pct_before.toFixed(2)}%</td>
                            <td className="p-3 text-right text-cyan-300 font-bold">{ow.pct_after.toFixed(2)}%</td>
                            <td className="p-3 text-right text-amber-300 font-bold">
                              {ow.transaction_price ? `Rp ${ow.transaction_price.toLocaleString('id-ID')}` : '-'}
                            </td>
                            <td className="p-3 font-sans text-[11px] text-slate-400">
                              <div className="flex flex-wrap items-center gap-1">
                                {ow.administrative_flag && (
                                  <span className="px-1 py-0.2 rounded bg-slate-800 text-[9px] text-slate-300">
                                    ADMIN
                                  </span>
                                )}
                                {ow.related_party_flag && (
                                  <span className="px-1 py-0.2 rounded bg-indigo-950 text-[9px] text-indigo-300">
                                    AFILIASI
                                  </span>
                                )}
                                <span className="text-[10px] text-slate-500">
                                  {formatContextClass(ow.context_classification)}
                                </span>
                              </div>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-8 text-slate-500 text-xs bg-slate-950/40 rounded-xl border border-slate-800">
                  Belum ada data transaksi kepemilikan yang tercatat untuk emiten ini.
                </div>
              )}
            </div>
          )}

          {/* TAB 4: MARKET STRUCTURE & CONTROLLER HIERARCHY */}
          {activeTab === 'structure' && (
            <div className="space-y-3.5">
              
              {/* Top Context Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
                
                {/* High Shareholding Concentration (HSC) Card */}
                <div className={`rounded-xl p-3.5 border ${
                  isHsc 
                    ? 'bg-red-950/20 border-red-500/35' 
                    : 'bg-slate-950/60 border-slate-800'
                }`}>
                  <div className="flex items-center justify-between mb-1.5">
                    <h4 className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
                      <Scale className="w-3.5 h-3.5 text-cyan-400" />
                      Konsentrasi Kepemilikan (HSC)
                    </h4>
                    {isHsc ? (
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-red-900/60 text-red-300 border border-red-700">
                        KONSENTRASI TINGGI
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-800 text-slate-400">
                        NORMAL
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {isHsc 
                      ? 'Emiten memiliki konsentrasi kepemilikan saham sangat tinggi. Porsi saham likuid di pasar publik relatif tipis, sehingga setiap aksi korporasi memiliki sensitivitas tinggi terhadap struktur kepemilikan.'
                      : 'Porsi kepemilikan publik dan institusional berada dalam rentang wajar tanpa konsentrasi ekstrem pada pemegang tunggal.'}
                  </p>
                  <div className="mt-2.5 pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs">
                    <span className="text-slate-500">Skor Kontribusi Konsentrasi:</span>
                    <span className="font-mono font-bold text-purple-400">{concScore} / 100</span>
                  </div>
                </div>

                {/* 15% Free Float Compliance Card */}
                <div className={`rounded-xl p-3.5 border ${
                  freeFloatPct !== undefined && freeFloatPct !== null && freeFloatPct < 15.0
                    ? 'bg-amber-950/20 border-amber-500/35'
                    : 'bg-slate-950/60 border-slate-800'
                }`}>
                  <div className="flex items-center justify-between mb-1.5">
                    <h4 className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
                      <Building2 className="w-3.5 h-3.5 text-cyan-400" />
                      Kepatuhan Free Float 15% (Ketentuan IDX)
                    </h4>
                    {freeFloatPct !== undefined && freeFloatPct !== null ? (
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                        freeFloatPct < 15.0 
                          ? 'bg-amber-900/60 text-amber-300 border-amber-700' 
                          : 'bg-emerald-900/60 text-emerald-300 border-emerald-700'
                      }`}>
                        {freeFloatPct < 15.0 ? 'BELUM MEMENUHI (<15%)' : 'MEMENUHI KETENTUAN'}
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-800 text-slate-400">
                        DIPANTAU
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {freeFloatPct !== undefined && freeFloatPct !== null && freeFloatPct < 15.0
                      ? `Porsi saham publik tercatat ${freeFloatPct.toFixed(1)}%, berada di bawah ketentuan minimum 15% Bursa Efek Indonesia. Emiten berpotensi melaksanakan penambahan modal publik (Right Issue / Private Placement) untuk memenuhi kepatuhan regulasi.`
                      : freeFloatPct !== undefined && freeFloatPct !== null
                      ? `Porsi saham publik tercatat ${freeFloatPct.toFixed(1)}%, telah memenuhi ketentuan minimal 15% Free Float IDX.`
                      : 'Informasi kuantitatif free-float belum dilaporkan secara terpisah dalam keterbukaan terbaru.'}
                  </p>
                  <div className="mt-2.5 pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs">
                    <span className="text-slate-500">Free Float Publik:</span>
                    <span className="font-mono font-bold text-cyan-400">
                      {freeFloatPct !== undefined && freeFloatPct !== null ? `${freeFloatPct.toFixed(2)}%` : 'Belum Terdata'}
                    </span>
                  </div>
                </div>

              </div>

              {/* Controller & Beneficial Owner Hierarchy */}
              <div className="bg-slate-950/60 rounded-xl p-3.5 border border-slate-800 space-y-2.5">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
                    <User className="w-3.5 h-3.5 text-cyan-400" />
                    Struktur Pengendali & Pemilik Manfaat (UBO)
                  </h4>
                  <span className="px-1.5 py-0.5 rounded text-[9px] font-medium bg-slate-800 text-slate-300 border border-slate-700">
                    Struktur Legal Terlapor
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-2.5">
                  
                  {/* Direct Actor */}
                  <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
                    <span className="text-[10px] text-slate-400 font-semibold uppercase block">Pemegang Saham Langsung</span>
                    <div className="text-xs font-bold text-slate-100 mt-1">{actorName}</div>
                    <span className="text-[10px] text-cyan-400 mt-0.5 block">{formatActorType(actorType)} &bull; {formatDomicile(actorDomicile)}</span>
                  </div>

                  {/* Ultimate Controller */}
                  <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
                    <span className="text-[10px] text-slate-400 font-semibold uppercase block">Pengendali Akhir</span>
                    <div className="text-xs font-bold text-amber-300 mt-1">
                      {controller?.name || 'Sama dengan Pemegang Saham Langsung'}
                    </div>
                    <span className="text-[10px] text-slate-400 mt-0.5 block">
                      {formatActorType(controller?.actor_type)}
                    </span>
                  </div>

                  {/* Beneficial Owner */}
                  <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
                    <span className="text-[10px] text-slate-400 font-semibold uppercase block">Pemilik Manfaat (Beneficial Owner)</span>
                    <div className="text-xs font-bold text-emerald-300 mt-1">
                      {beneficialOwner?.name || 'Terdaftar melalui Pengendali Akhir'}
                    </div>
                    <span className="text-[10px] text-slate-400 mt-0.5 block">
                      {formatActorType(beneficialOwner?.actor_type)}
                    </span>
                  </div>

                </div>

                {/* KSEI Investor Classifications Table */}
                {investorClasses.length > 0 && (
                  <div className="mt-2.5 pt-2.5 border-t border-slate-800">
                    <h5 className="text-[11px] font-semibold text-slate-400 mb-1.5">
                      Klasifikasi Taksonomi Investor (KSEI)
                    </h5>
                    <div className="flex flex-wrap gap-1.5">
                      {investorClasses.map((ic, idx) => (
                        <div key={idx} className="bg-slate-900 px-2 py-1 rounded border border-slate-800 text-xs flex items-center gap-1.5">
                          <span className="font-mono font-bold text-cyan-400">{ic.normalized_class}</span>
                          <span className="text-slate-500">&bull;</span>
                          <span className="text-slate-300 text-[11px]">{ic.raw_class}</span>
                          {ic.source && (
                            <span className="text-[9px] bg-slate-800 text-slate-400 px-1 rounded">{ic.source}</span>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Share Pledge & Collateral Status */}
              <div className="bg-slate-950/60 rounded-xl p-3.5 border border-slate-800 space-y-1.5">
                <h4 className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
                  <Lock className="w-3.5 h-3.5 text-amber-400" />
                  Status Gadai Saham (Share Pledge)
                </h4>
                <p className="text-xs text-slate-300">
                  {hasPledges 
                    ? 'Terdeteksi transaksi gadai / pelepasan gadai saham (Share Pledge). Transaksi ini dicatat sebagai konteks penjaminan fasilitas kredit terpisah dari akumulasi saham murni.'
                    : 'Tidak ada catatan transaksi gadai saham aktif yang dilaporkan dalam keterbukaan pemegang saham mayoritas.'}
                </p>
              </div>

            </div>
          )}

          {/* TAB 5: TIMING INTEGRITY & LEAD LAGS */}
          {activeTab === 'timing' && (
            <div className="space-y-3.5">
              
              <div className="bg-slate-950/70 rounded-xl p-4 border border-slate-800 space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
                      <Clock className="w-3.5 h-3.5 text-cyan-400" />
                      Integritas Waktu & Lead Time Pengumuman
                    </h3>
                    <p className="text-[11px] text-slate-400 mt-0.5">
                      Perhitungan jeda waktu (lag) dan jarak hari dari dokumen resmi keterbukaan IDX.
                    </p>
                  </div>
                </div>

                {/* 4 Lead Metrics Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2.5 pt-1">
                  
                  {/* Transaction-to-Public Lag */}
                  <div className="bg-slate-900/90 rounded-lg p-3 border border-slate-800">
                    <span className="text-[10px] font-semibold text-slate-400 uppercase block">Jeda Transaksi ke Publik</span>
                    <div className="text-lg font-mono font-bold text-amber-300 mt-1">
                      {lagDays !== undefined && lagDays !== null ? `${lagDays} Hari` : 'Hari yang sama'}
                    </div>
                    <span className="text-[10px] text-slate-500 mt-0.5 block">Dari eksekusi transaksi ke rilis IDX</span>
                  </div>

                  {/* First Public Lead */}
                  <div className="bg-slate-900/90 rounded-lg p-3 border border-slate-800">
                    <span className="text-[10px] font-semibold text-slate-400 uppercase block">Lead Time Dokumen Pertama</span>
                    <div className="text-lg font-mono font-bold text-cyan-300 mt-1">
                      {firstPublicLead !== undefined && firstPublicLead !== null ? `${firstPublicLead} Hari` : '-'}
                    </div>
                    <span className="text-[10px] text-slate-500 mt-0.5 block">Dari dokumen awal ke aksi eksplisit</span>
                  </div>

                  {/* First Alignment Lead */}
                  <div className="bg-slate-900/90 rounded-lg p-3 border border-slate-800">
                    <span className="text-[10px] font-semibold text-slate-400 uppercase block">Lead Time Konvergensi</span>
                    <div className="text-lg font-mono font-bold text-purple-300 mt-1">
                      {firstAlignmentLead !== undefined && firstAlignmentLead !== null ? `${firstAlignmentLead} Hari` : '-'}
                    </div>
                    <span className="text-[10px] text-slate-500 mt-0.5 block">Titik temu akumulasi & pengumuman</span>
                  </div>

                  {/* First Positioning Lead */}
                  <div className="bg-slate-900/90 rounded-lg p-3 border border-slate-800">
                    <span className="text-[10px] font-semibold text-slate-400 uppercase block">Lead Time Posisi Pertama</span>
                    <div className="text-lg font-mono font-bold text-emerald-300 mt-1">
                      {firstPositioningLead !== undefined && firstPositioningLead !== null ? `${firstPositioningLead} Hari` : '-'}
                    </div>
                    <span className="text-[10px] text-slate-500 mt-0.5 block">Jarak awal transaksi pertama pihak</span>
                  </div>

                </div>
              </div>

              {/* Public Observability Principle Note */}
              <div className="bg-slate-950/40 rounded-xl p-3.5 border border-slate-800 flex items-start gap-2.5">
                <Info className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                <div className="text-xs text-slate-300 leading-relaxed">
                  <strong className="text-slate-200">Prinsip Observabilitas Faktual Publik:</strong> Seluruh lead-time dihitung secara deterministik dari tanggal dokumen pertama kali dipublikasikan oleh Bursa Efek Indonesia (IDX) hingga tanggal keterbukaan aksi korporasi eksplisit (RUPS / Prospektus).
                </div>
              </div>

            </div>
          )}

          {/* TAB 6: SOURCE EVIDENCE EXCERPTS */}
          {activeTab === 'evidence' && (
            <div className="space-y-3.5">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-bold text-slate-300">
                  Kutipan Bukti Dokumen & Halaman PDF
                </h3>
                <span className="text-xs text-slate-500">Kutipan teks pendukung analisis</span>
              </div>

              {signal.evidence && signal.evidence.length > 0 ? (
                <div className="space-y-2.5">
                  {signal.evidence.map((ev, idx) => (
                    <div key={idx} className="bg-slate-950/70 rounded-xl p-3.5 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                      <div className="space-y-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="px-2 py-0.2 rounded text-[10px] font-bold bg-slate-800 text-cyan-300 border border-slate-700">
                            Hal {ev.page_number}
                          </span>
                          <span className="text-xs font-medium text-slate-400">
                            {formatEvidenceType(ev.evidence_type)}
                          </span>
                          {ev.announcement_title && (
                            <span className="text-xs text-slate-300 truncate max-w-md font-medium">
                              &bull; {ev.announcement_title}
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-slate-200 italic bg-slate-900/50 p-2 rounded-lg border border-slate-800 font-mono">
                          "{ev.excerpt}"
                        </p>
                      </div>

                      {ev.document_id && (
                        <button
                          onClick={() => onOpenPdf(ev.document_id!, ev.page_number)}
                          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-cyan-400 text-xs font-semibold transition-colors shrink-0 cursor-pointer"
                        >
                          <FileText className="w-3.5 h-3.5" />
                          <span>Buka PDF</span>
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-slate-500 text-xs bg-slate-950/40 rounded-xl border border-slate-800">
                  Belum ada kutipan teks bukti langsung yang tercatat.
                </div>
              )}
            </div>
          )}

          {/* TAB 7: TEMPORAL TIMELINE */}
          {activeTab === 'timeline' && (
            <div className="space-y-3.5">
              <h3 className="text-xs font-bold text-slate-300">
                Kronologi Keterbukaan Informasi
              </h3>
              
              {signal.timeline && signal.timeline.length > 0 ? (
                <div className="relative border-l border-slate-800 ml-4 space-y-4 py-1">
                  {signal.timeline.map((item, idx) => (
                    <div key={idx} className="relative pl-5">
                      <div className="absolute -left-1.5 top-1.5 w-2.5 h-2.5 rounded-full bg-cyan-400 border-2 border-slate-900"></div>
                      
                      <div className="bg-slate-950/70 rounded-xl p-3 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
                        <div>
                          <div className="flex items-center gap-2 text-xs text-slate-400 mb-0.5">
                            <Calendar className="w-3 h-3 text-cyan-400" />
                            <span>{new Date(item.event_date).toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' })}</span>
                            {item.priority && (
                              <span className="px-1.5 py-0.2 rounded text-[10px] font-semibold bg-slate-800 text-cyan-400">
                                {item.priority === 'VERY_HIGH' ? 'Sangat Tinggi' : item.priority === 'HIGH' ? 'Tinggi' : item.priority}
                              </span>
                            )}
                          </div>
                          <h4 className="text-xs font-bold text-slate-100">
                            {item.title}
                          </h4>
                          {item.category && (
                            <span className="text-[11px] text-slate-400">{item.category}</span>
                          )}
                        </div>

                        {item.document_id && item.has_local_pdf && (
                          <button
                            onClick={() => onOpenPdf(item.document_id, 1)}
                            className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-cyan-400 text-xs font-semibold shrink-0 cursor-pointer"
                          >
                            <ExternalLink className="w-3 h-3" />
                            <span>Buka PDF</span>
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-slate-500 text-xs bg-slate-950/40 rounded-xl border border-slate-800">
                  Belum ada kronologi pengumuman yang tercatat.
                </div>
              )}
            </div>
          )}

        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3 border-t border-slate-800 bg-slate-950 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-400">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-cyan-400 shrink-0" />
            <span className="text-slate-400">Sumber data: Dokumen keterbukaan informasi resmi Bursa Efek Indonesia (IDX).</span>
          </div>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold cursor-pointer transition-colors border border-slate-700 shrink-0"
          >
            Tutup
          </button>
        </div>
      </div>
    </div>
  );
};
