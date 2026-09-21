export interface EvidenceItem {
  event_date?: string;
  document_id?: number;
  announcement_title?: string;
  page_number: number;
  excerpt: string;
  evidence_type: string;
  stage?: string;
  impact?: string;
}

export interface LifecycleStageDef {
  stage: string;
  name: string;
  patterns?: string[];
}

export interface TimelineItem {
  document_id: number;
  event_date: string;
  title: string;
  category?: string;
  priority?: string;
  pdf_url?: string;
  has_local_pdf: boolean;
  event_id?: number;
  stage?: string;
  lifecycle_stage?: string;
  signal_type?: string;
  contribution?: string;
  announcement_title?: string;
  announcement_category?: string;
}

export interface OwnershipHistoryItem {
  id: number;
  actor_id: number;
  actor_name: string;
  event_date: string;
  transaction_date?: string | null;
  reporting_date?: string | null;
  publication_date?: string | null;
  event_type: string;
  shares_before: number;
  shares_after: number;
  delta_shares: number;
  pct_before: number;
  pct_after: number;
  delta_pct: number;
  transaction_price?: number | null;
  estimated_value?: number | null;
  transaction_type?: string | null;
  administrative_flag?: boolean;
  related_party_flag?: boolean;
  pledge_flag?: boolean;
  context_classification: string;
  source_document_id?: number;
}

export interface InvestorClassificationRecord {
  raw_class: string;
  normalized_class: string;
  source?: string;
  observed_at?: string;
}

export interface ActorProfile {
  id: number | null;
  canonical_name: string;
  actor_type: string;
  domicile?: string;
  aliases: string[];
  relationships: Array<{
    relationship_type: string;
    related_actor: string;
  }>;
  investor_classes?: InvestorClassificationRecord[];
  beneficial_owner?: { id: number; name: string; actor_type: string } | null;
  controller?: { id: number; name: string; actor_type: string } | null;
}

export interface CompositeScores {
  smart_money_score: number;
  strategic_positioning_score: number;
  corporate_transformation_score: number;
  corporate_action_score: number;
  alignment_score: number;
  strategic_actor_score?: number;
  ownership_behavior_score?: number;
  concentration_score?: number;
  evidence_quality_score?: number;
  lead_time_quality_score?: number;
  overall_priority: "VERY_HIGH" | "HIGH" | "MEDIUM" | "LOW" | "WATCH";
  lead_time_days?: number | null;
}

export interface StructuralContext {
  hsc_flag: boolean;
  free_float_pct?: number | null;
  concentration_score?: number;
}

export interface TimingIntegrity {
  transaction_to_public_lag_days?: number | null;
  first_public_lead_days?: number | null;
  first_alignment_lead_days?: number | null;
  first_positioning_lead_days?: number | null;
  first_signal_at?: string | null;
  explicit_action_at?: string | null;
}

export interface CorporateActionMeta {
  action_type: string;
  action_name: string;
  category: string;
  lifecycle_stages?: Array<{
    stage: string;
    name: string;
    patterns: string[];
  }>;
}

export interface ProceedsAllocation {
  category: string;
  percentage?: number | null;
  amount?: number | null;
  description: string;
}

export interface CorporateActionAssessment {
  id: number;
  issuer_action_state_id?: number | null;
  company_id?: number | null;
  action_type: string;
  likelihood_score: number;
  likelihood_stage: string;
  quality_score: number;
  quality_label: string;
  shareholder_value_score: number;
  risk_score: number;
  confidence: string;
  opportunity_state: string;
  scores_decomposition?: {
    strategic_rationale_score?: number;
    capital_efficiency_score?: number;
    funding_quality_score?: number;
    asset_quality_score?: number;
    control_alignment_score?: number;
    pricing_attractiveness_score?: number;
    execution_risk_score?: number;
    related_party_risk_score?: number;
    distress_risk_score?: number;
    dilution_score?: number;
  };
  dilution_pct?: number | null;
  new_share_ratio?: string | null;
  subscription_price?: number | null;
  use_of_proceeds?: ProceedsAllocation[];
  recipients?: {
    has_standby_buyer?: boolean;
    has_strategic_investor?: boolean;
    has_related_party_recipient?: boolean;
    standby_buyer_names?: string[];
    strategic_investor_names?: string[];
  };
  positive_drivers?: string[];
  red_flags?: string[];
  why_attractive?: string;
  why_risky?: string;
  updated_at?: string;
}

export interface SmartMoneySignal {
  id: number;
  company_id: number;
  ticker: string;
  company_name: string;
  sector?: string;
  primary_actor_id?: number | null;
  actor_name: string;
  actor_type: string;
  domicile?: string;
  behavior_type: string;
  total_shares_delta: number;
  pct_before: number;
  pct_after: number;
  delta_pct: number;
  avg_price?: number | null;
  transaction_count: number;
  action_type: string;
  action_name: string;
  category: string;
  stage: "EARLY" | "DEVELOPING" | "EXPLICIT";
  impact: "POSITIVE" | "NEUTRAL" | "NEGATIVE" | "MIXED" | "UNCLEAR" | "NO_SIGNAL";
  priority: "VERY_HIGH" | "HIGH" | "MEDIUM" | "LOW" | "WATCH";
  smart_money_score: number;
  strategic_positioning_score: number;
  corporate_transformation_score: number;
  corporate_action_score: number;
  alignment_score: number;
  strategic_actor_score?: number;
  ownership_behavior_score?: number;
  concentration_score?: number;
  evidence_quality_score?: number;
  lead_time_quality_score?: number;
  hsc_flag?: boolean;
  free_float_pct?: number | null;
  transaction_to_public_lag_days?: number | null;
  first_public_lead_days?: number | null;
  first_alignment_lead_days?: number | null;
  first_positioning_lead_days?: number | null;
  lead_time_days?: number | null;
  quality_score?: number | null;
  quality_label?: string | null;
  opportunity_state?: string | null;
  shareholder_value_score?: number | null;
  positive_drivers_count?: number;
  red_flags_count?: number;
  corroborating_docs_count: number;
  why_flagged?: string;
  what_changed?: string;
  last_signal_at: string;
  latest_document_id?: number;
  evidence?: EvidenceItem[];
}

export interface SignalDetail extends SmartMoneySignal {
  actor: ActorProfile;
  behavior: {
    behavior_type: string;
    total_shares_delta: number;
    pct_before: number;
    pct_after: number;
    delta_pct: number;
    avg_price?: number | null;
    transaction_count: number;
  };
  structural_context?: StructuralContext;
  timing_integrity?: TimingIntegrity;
  scores: CompositeScores;
  corporate_action: CorporateActionMeta;
  corporate_action_assessment?: CorporateActionAssessment | null;
  ownership_history: OwnershipHistoryItem[];
  timeline: TimelineItem[];
  evidence: EvidenceItem[];
}

export interface ScanRecord {
  id: number;
  scan_date: string;
  date_from: string;
  date_to: string;
  lookback_days: number;
  status: string;
  summary_json?: string;
  created_at: string;
  completed_at?: string | null;
}

export interface ScanSummary {
  stage_message?: string;
  progress_percent?: number;
  error?: string;
  scan_mode?: string;
  announcements_retrieved: number;
  tier_a_documents?: number;
  tier_b_documents?: number;
  tier_c_metadata_only?: number;
  documents_processed: number;
  pdfs_downloaded: number;
  pdfs_extracted: number;
  ocr_or_failed: number;
  ownership_events?: number;
  strategic_candidates?: number;
  signals_total: number;
  early: number;
  developing: number;
  explicit: number;
}

