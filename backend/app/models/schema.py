from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class Company(SQLModel, table=True):
    __tablename__ = "companies"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    ticker: str = Field(index=True, unique=True)
    name: str = Field(default="")
    sector: Optional[str] = Field(default=None)
    status: str = Field(default="ACTIVE")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    announcements: List["Announcement"] = Relationship(back_populates="company")
    action_states: List["IssuerActionState"] = Relationship(back_populates="company")
    ownership_events: List["OwnershipEvent"] = Relationship(back_populates="company")
    ownership_snapshots: List["OwnershipSnapshot"] = Relationship(back_populates="company")
    behavior_states: List["ActorBehaviorState"] = Relationship(back_populates="company")
    intelligence_states: List["IssuerIntelligenceState"] = Relationship(back_populates="company")
    market_structure_snapshots: List["MarketStructureSnapshot"] = Relationship(back_populates="company")
    ca_assessments: List["CorporateActionAssessment"] = Relationship(back_populates="company")


class Actor(SQLModel, table=True):
    __tablename__ = "actors"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    canonical_name: str = Field(index=True)
    raw_name: Optional[str] = Field(default=None)
    actor_type: str = Field(default="OTHER", index=True)  # CONTROLLER, SIGNIFICANT_HOLDER, DIRECTOR, COMMISSIONER, STRATEGIC_INVESTOR, INSTITUTION, CORPORATE, PUBLIC, OTHER
    domicile: Optional[str] = Field(default=None)  # DOMESTIC, FOREIGN, or specific country
    beneficial_owner_id: Optional[int] = Field(default=None, foreign_key="actors.id")
    controller_id: Optional[int] = Field(default=None, foreign_key="actors.id")
    normalized_key: str = Field(index=True, unique=True)
    confidence: str = Field(default="HIGH")  # EXACT, HIGH, MEDIUM, LOW, UNRESOLVED
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    aliases: List["ActorAlias"] = Relationship(back_populates="actor")
    ownership_events: List["OwnershipEvent"] = Relationship(back_populates="actor")
    ownership_snapshots: List["OwnershipSnapshot"] = Relationship(back_populates="actor")
    transaction_events: List["TransactionEvent"] = Relationship(back_populates="actor")
    behavior_states: List["ActorBehaviorState"] = Relationship(back_populates="actor")
    investor_classifications: List["InvestorClassification"] = Relationship(back_populates="actor")


class ActorAlias(SQLModel, table=True):
    __tablename__ = "actor_aliases"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    actor_id: int = Field(foreign_key="actors.id", index=True)
    alias: str = Field(index=True)
    source: str = Field(default="DISCLOSURE")
    confidence: str = Field(default="HIGH")

    actor: Optional[Actor] = Relationship(back_populates="aliases")


class ActorRelationship(SQLModel, table=True):
    __tablename__ = "actor_relationships"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    actor_id: int = Field(foreign_key="actors.id", index=True)
    related_actor_id: int = Field(foreign_key="actors.id", index=True)
    relationship_type: str = Field(default="AFFILIATED")  # CONTROLS, AFFILIATED, ULTIMATE_BENEFICIARY, PARENT, SUBSIDIARY
    beneficial_owner_id: Optional[int] = Field(default=None, foreign_key="actors.id")
    controller_id: Optional[int] = Field(default=None, foreign_key="actors.id")
    source_document_id: Optional[int] = Field(default=None)
    valid_from: Optional[datetime] = Field(default=None)
    valid_to: Optional[datetime] = Field(default=None)
    confidence: str = Field(default="HIGH")


class Announcement(SQLModel, table=True):
    __tablename__ = "announcements"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="companies.id", index=True)
    source_announcement_id: Optional[str] = Field(default=None, index=True)
    title: str
    category: Optional[str] = Field(default=None)
    published_at: datetime = Field(index=True)
    source_url: Optional[str] = Field(default=None)
    normalized_url: Optional[str] = Field(default=None)
    status: str = Field(default="PENDING", index=True)
    processing_state: str = Field(default="UNPROCESSED")  # UNPROCESSED, TIER_A_DEEP, TIER_B_DEEP, TIER_C_META, TIER_D_ARCHIVED
    is_historical_context: bool = Field(default=False)

    company: Optional[Company] = Relationship(back_populates="announcements")
    documents: List["Document"] = Relationship(back_populates="announcement")


class Document(SQLModel, table=True):
    __tablename__ = "documents"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    announcement_id: int = Field(foreign_key="announcements.id", index=True)
    pdf_url: Optional[str] = Field(default=None)
    local_path: Optional[str] = Field(default=None)
    sha256: Optional[str] = Field(default=None, index=True)
    document_priority: str = Field(default="TIER_C", index=True)  # TIER_A, TIER_B, TIER_C, TIER_D
    acquisition_status: str = Field(default="PENDING")  # PENDING, DOWNLOADED, SKIPPED, FAILED
    extraction_status: str = Field(default="PENDING")  # PENDING, EXTRACTED, OCR_REQUIRED, EXTRACTION_FAILED, SKIPPED
    processed_at: Optional[datetime] = Field(default=None)
    page_count: int = Field(default=0)

    announcement: Optional[Announcement] = Relationship(back_populates="documents")
    pages: List["DocumentPage"] = Relationship(back_populates="document")
    signals: List["DocumentSignal"] = Relationship(back_populates="document")


class DocumentPage(SQLModel, table=True):
    __tablename__ = "document_pages"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    document_id: int = Field(foreign_key="documents.id", index=True)
    page_number: int
    extracted_text: str = Field(default="")

    document: Optional[Document] = Relationship(back_populates="pages")


class OwnershipSnapshot(SQLModel, table=True):
    __tablename__ = "ownership_snapshots"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="companies.id", index=True)
    actor_id: int = Field(foreign_key="actors.id", index=True)
    snapshot_date: datetime = Field(index=True)
    shares: float = Field(default=0.0)
    ownership_pct: float = Field(default=0.0)
    voting_pct: Optional[float] = Field(default=None)
    investor_class: Optional[str] = Field(default=None)
    source_type: str = Field(default="DISCLOSURE")  # DISCLOSURE, KSEI_MONTHLY, BEI_PUBLIC
    source_document_id: Optional[int] = Field(default=None)
    evidence_quality: str = Field(default="HIGH")

    company: Optional[Company] = Relationship(back_populates="ownership_snapshots")
    actor: Optional[Actor] = Relationship(back_populates="ownership_snapshots")


class OwnershipEvent(SQLModel, table=True):
    __tablename__ = "ownership_events"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="companies.id", index=True)
    actor_id: int = Field(foreign_key="actors.id", index=True)
    event_date: datetime = Field(index=True)
    transaction_date: Optional[datetime] = Field(default=None, index=True)
    reporting_date: Optional[datetime] = Field(default=None)
    publication_date: Optional[datetime] = Field(default=None, index=True)
    event_type: str = Field(default="ACQUIRE", index=True)  # ACQUIRE, DISPOSE, SUBSCRIBE, EXERCISE, CONVERT, TRANSFER, PLEDGE, RELEASE_PLEDGE, ADMINISTRATIVE_CHANGE
    shares_before: float = Field(default=0.0)
    shares_after: float = Field(default=0.0)
    delta_shares: float = Field(default=0.0)
    pct_before: float = Field(default=0.0)
    pct_after: float = Field(default=0.0)
    delta_pct: float = Field(default=0.0)
    transaction_price: Optional[float] = Field(default=None)
    estimated_value: Optional[float] = Field(default=None)
    transaction_type: Optional[str] = Field(default=None)  # OPEN_MARKET, NEGOTIATED, PLEDGE, ADMINISTRATIVE, OFF_MARKET
    administrative_flag: bool = Field(default=False)
    related_party_flag: bool = Field(default=False)
    pledge_flag: bool = Field(default=False)
    source_document_id: Optional[int] = Field(default=None, index=True)
    context_classification: str = Field(default="MARKET_ACQUISITION_CANDIDATE")  # MARKET_ACQUISITION_CANDIDATE, MARKET_DISPOSAL_CANDIDATE, CORPORATE_ACTION_EFFECT, ADMINISTRATIVE_TRANSFER, CONTROL_RESTRUCTURE, UNCLEAR
    confidence: str = Field(default="HIGH")

    company: Optional[Company] = Relationship(back_populates="ownership_events")
    actor: Optional[Actor] = Relationship(back_populates="ownership_events")


class TransactionEvent(SQLModel, table=True):
    __tablename__ = "transaction_events"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="companies.id", index=True)
    actor_id: int = Field(foreign_key="actors.id", index=True)
    event_date: datetime = Field(index=True)
    direction: str = Field(default="ACQUIRE")  # ACQUIRE, DISPOSE, SUBSCRIBE, EXERCISE, CONVERT, TRANSFER
    transaction_type: str = Field(default="OPEN_MARKET")
    quantity: float = Field(default=0.0)
    price: Optional[float] = Field(default=None)
    estimated_value: Optional[float] = Field(default=None)
    source_document_id: Optional[int] = Field(default=None)
    evidence_id: Optional[int] = Field(default=None)

    actor: Optional[Actor] = Relationship(back_populates="transaction_events")


class CorporateActionEvent(SQLModel, table=True):
    __tablename__ = "corporate_action_events"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="companies.id", index=True)
    action_type: str = Field(index=True)
    event_date: datetime = Field(index=True)
    lifecycle_stage: str = Field(default="EARLY")  # EARLY, DEVELOPING, EXPLICIT, EXECUTING, COMPLETED, CANCELLED, CONTRADICTED
    impact: str = Field(default="UNCLEAR")
    confidence: str = Field(default="HIGH")
    source_document_id: Optional[int] = Field(default=None)


class DocumentSignal(SQLModel, table=True):
    __tablename__ = "document_signals"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    document_id: int = Field(foreign_key="documents.id", index=True)
    action_type: str = Field(index=True)
    information_importance: str = Field(default="LOW", index=True)
    novelty_type: str = Field(default="NEW")
    impact: str = Field(default="UNCLEAR", index=True)
    stage: str = Field(default="EARLY", index=True)
    strength: str = Field(default="MEDIUM")
    confidence: str = Field(default="MEDIUM")
    lifecycle_stage: Optional[str] = Field(default=None)
    reason: str = Field(default="")
    is_negated: bool = Field(default=False)
    is_cancelled: bool = Field(default=False)
    is_distress: bool = Field(default=False)

    document: Optional[Document] = Relationship(back_populates="signals")
    evidence_items: List["Evidence"] = Relationship(back_populates="signal")


class Evidence(SQLModel, table=True):
    __tablename__ = "evidence"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    document_signal_id: Optional[int] = Field(default=None, foreign_key="document_signals.id", index=True)
    source_document_id: Optional[int] = Field(default=None, index=True)
    page_number: int = Field(default=1)
    excerpt: str = Field(default="")
    evidence_type: str = Field(default="TRIGGER")  # TRIGGER, CONTEXT, PRECURSOR, NEGATION, DISTRESS, LIFECYCLE, OWNERSHIP, PRICE
    extraction_confidence: str = Field(default="HIGH")

    signal: Optional[DocumentSignal] = Relationship(back_populates="evidence_items")


class ActorBehaviorState(SQLModel, table=True):
    __tablename__ = "actor_behavior_states"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="companies.id", index=True)
    actor_id: int = Field(foreign_key="actors.id", index=True)
    behavior_type: str = Field(default="ACCUMULATION_CANDIDATE", index=True)  # NEW_POSITION, ACCUMULATION_CANDIDATE, DISTRIBUTION_CANDIDATE, POSITION_REDUCTION, STABLE_LARGE_HOLDER, THRESHOLD_CROSSING, CONTROL_BUILDING, ADMINISTRATIVE_CHANGE
    current_stage: str = Field(default="DEVELOPING")
    priority: str = Field(default="MEDIUM", index=True)  # VERY_HIGH, HIGH, MEDIUM, LOW, WATCH
    confidence: str = Field(default="HIGH")
    total_shares_delta: float = Field(default=0.0)
    pct_before: float = Field(default=0.0)
    pct_after: float = Field(default=0.0)
    delta_pct: float = Field(default=0.0)
    avg_price: Optional[float] = Field(default=None)
    transaction_count: int = Field(default=1)
    first_signal_at: datetime = Field(default_factory=datetime.utcnow)
    last_signal_at: datetime = Field(default_factory=datetime.utcnow)
    state_status: str = Field(default="ACTIVE", index=True)

    company: Optional[Company] = Relationship(back_populates="behavior_states")
    actor: Optional[Actor] = Relationship(back_populates="behavior_states")


class IssuerIntelligenceState(SQLModel, table=True):
    __tablename__ = "issuer_intelligence_states"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="companies.id", index=True)
    smart_money_score: int = Field(default=0, index=True)
    strategic_positioning_score: int = Field(default=0)
    corporate_transformation_score: int = Field(default=0)
    corporate_action_score: int = Field(default=0)
    alignment_score: int = Field(default=0)
    strategic_actor_score: int = Field(default=0)
    ownership_behavior_score: int = Field(default=0)
    concentration_score: int = Field(default=0)
    evidence_quality_score: int = Field(default=0)
    lead_time_quality_score: int = Field(default=0)
    hsc_flag: bool = Field(default=False, index=True)
    free_float_pct: Optional[float] = Field(default=None)
    overall_priority: str = Field(default="MEDIUM", index=True)  # VERY_HIGH, HIGH, MEDIUM, LOW, WATCH
    primary_actor_id: Optional[int] = Field(default=None, foreign_key="actors.id")
    primary_behavior: Optional[str] = Field(default=None)
    primary_action_type: Optional[str] = Field(default=None)
    lead_time_days: Optional[int] = Field(default=None)
    transaction_to_public_lag_days: Optional[int] = Field(default=None)
    first_public_lead_days: Optional[int] = Field(default=None)
    first_alignment_lead_days: Optional[int] = Field(default=None)
    first_positioning_lead_days: Optional[int] = Field(default=None)
    first_signal_at: Optional[datetime] = Field(default=None)
    explicit_action_at: Optional[datetime] = Field(default=None)
    current_summary: Optional[str] = Field(default=None)
    why_flagged_summary: Optional[str] = Field(default=None)
    what_changed_summary: Optional[str] = Field(default=None)
    corroborating_docs_count: int = Field(default=1)
    # v7.3 Corporate Action Quality & Opportunity State
    quality_score: Optional[float] = Field(default=None)
    quality_label: Optional[str] = Field(default=None, index=True)
    opportunity_state: Optional[str] = Field(default=None, index=True)
    shareholder_value_score: Optional[float] = Field(default=None)
    positive_drivers_count: int = Field(default=0)
    red_flags_count: int = Field(default=0)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    company: Optional[Company] = Relationship(back_populates="intelligence_states")


class InvestorClassification(SQLModel, table=True):
    __tablename__ = "investor_classifications"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    actor_id: int = Field(foreign_key="actors.id", index=True)
    raw_class: str = Field(default="")
    normalized_class: str = Field(default="OTHER", index=True)
    source: str = Field(default="DISCLOSURE")
    observed_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    confidence: str = Field(default="HIGH")

    actor: Optional[Actor] = Relationship(back_populates="investor_classifications")


class MarketStructureSnapshot(SQLModel, table=True):
    __tablename__ = "market_structure_snapshots"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="companies.id", index=True)
    observation_date: datetime = Field(index=True)
    hsc_flag: bool = Field(default=False, index=True)
    concentration_metric: Optional[float] = Field(default=None)
    free_float_pct: Optional[float] = Field(default=None)
    free_float_shares: Optional[float] = Field(default=None)
    relevant_holder_count: Optional[int] = Field(default=None)
    source_document_id: Optional[int] = Field(default=None)

    company: Optional[Company] = Relationship(back_populates="market_structure_snapshots")


class IssuerActionState(SQLModel, table=True):
    __tablename__ = "issuer_action_states"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="companies.id", index=True)
    action_type: str = Field(index=True)
    current_stage: str = Field(default="EARLY", index=True)
    current_impact: str = Field(default="UNCLEAR", index=True)
    current_strength: str = Field(default="MEDIUM")
    current_confidence: str = Field(default="MEDIUM")
    priority: str = Field(default="MEDIUM", index=True)
    first_signal_at: datetime
    last_signal_at: datetime
    state_status: str = Field(default="ACTIVE", index=True)
    what_changed_summary: Optional[str] = Field(default=None)
    why_flagged_summary: Optional[str] = Field(default=None)
    corroborating_docs_count: int = Field(default=1)

    company: Optional[Company] = Relationship(back_populates="action_states")
    events: List["SignalEvent"] = Relationship(back_populates="action_state")
    assessments: List["CorporateActionAssessment"] = Relationship(back_populates="action_state")


class SignalEvent(SQLModel, table=True):
    __tablename__ = "signal_events"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    issuer_action_state_id: Optional[int] = Field(default=None, foreign_key="issuer_action_states.id", index=True)
    company_id: Optional[int] = Field(default=None, index=True)
    actor_id: Optional[int] = Field(default=None, index=True)
    document_id: Optional[int] = Field(default=None, foreign_key="documents.id", index=True)
    event_date: datetime
    lifecycle_stage: str
    signal_type: str
    contribution: str = Field(default="ADVANCEMENT")
    status: str = Field(default="ACTIVE")

    action_state: Optional[IssuerActionState] = Relationship(back_populates="events")


class CorporateActionAssessment(SQLModel, table=True):
    __tablename__ = "corporate_action_assessments"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    issuer_action_state_id: Optional[int] = Field(default=None, foreign_key="issuer_action_states.id", index=True)
    company_id: Optional[int] = Field(default=None, foreign_key="companies.id", index=True)
    action_type: str = Field(index=True)
    
    # 3-Way Independent Dimensions (PRD v7.3 Section 1, 3, 4)
    likelihood_score: float = Field(default=0.0)
    likelihood_stage: str = Field(default="DEVELOPING", index=True)  # EARLY, DEVELOPING, LIKELY, EXPLICIT, CONTRADICTED, CANCELLED
    quality_score: float = Field(default=50.0, index=True)
    quality_label: str = Field(default="QUALITY_UNCLEAR", index=True)  # VERY_ATTRACTIVE, ATTRACTIVE, NEUTRAL_MIXED, RISKY_DILUTIVE, UNATTRACTIVE_DISTRESS, QUALITY_UNCLEAR
    shareholder_value_score: float = Field(default=50.0)
    risk_score: float = Field(default=30.0)
    confidence: str = Field(default="MEDIUM")  # LOW, MEDIUM, MEDIUM_HIGH, HIGH
    opportunity_state: str = Field(default="DEVELOPING_UNCLEAR", index=True)
    
    # Decomposed Quality Components (0 - 100) (PRD v7.3 Section 6 & 17)
    strategic_rationale_score: float = Field(default=50.0)
    capital_efficiency_score: float = Field(default=50.0)
    funding_quality_score: float = Field(default=50.0)
    asset_quality_score: float = Field(default=50.0)
    control_alignment_score: float = Field(default=50.0)
    pricing_attractiveness_score: float = Field(default=50.0)
    execution_risk_score: float = Field(default=30.0)
    related_party_risk_score: float = Field(default=10.0)
    distress_risk_score: float = Field(default=0.0)
    dilution_score: float = Field(default=50.0)
    
    # Structural Attributes & Extracted Metrics
    dilution_pct: Optional[float] = Field(default=None)
    new_share_ratio: Optional[str] = Field(default=None)
    subscription_price: Optional[float] = Field(default=None)
    use_of_proceeds_json: Optional[str] = Field(default=None)
    recipients_json: Optional[str] = Field(default=None)
    positive_drivers_json: Optional[str] = Field(default=None)
    red_flags_json: Optional[str] = Field(default=None)
    why_attractive: Optional[str] = Field(default=None)
    why_risky: Optional[str] = Field(default=None)
    source_document_id: Optional[int] = Field(default=None, foreign_key="documents.id")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    action_state: Optional[IssuerActionState] = Relationship(back_populates="assessments")
    company: Optional[Company] = Relationship(back_populates="ca_assessments")


class Scan(SQLModel, table=True):
    __tablename__ = "scans"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)
    scan_from: datetime
    scan_to: datetime
    lookback_days: int = Field(default=60)
    scan_mode: str = Field(default="smart", index=True)  # smart, full_audit
    status: str = Field(default="RUNNING", index=True)  # RUNNING, COMPLETED, FAILED, PARTIAL
    announcements_found: int = Field(default=0)
    announcements_new: int = Field(default=0)
    announcements_known: int = Field(default=0)
    tier_a_documents: int = Field(default=0)
    tier_b_documents: int = Field(default=0)
    tier_c_metadata_only: int = Field(default=0)
    documents_processed: int = Field(default=0)
    pdfs_downloaded: int = Field(default=0)
    pdfs_extracted: int = Field(default=0)
    ocr_required_or_failed: int = Field(default=0)
    processed_no_pdf: int = Field(default=0)
    ownership_events_found: int = Field(default=0)
    strategic_positioning_candidates: int = Field(default=0)
    important_signals_found: int = Field(default=0)
    early_signals_count: int = Field(default=0)
    developing_signals_count: int = Field(default=0)
    explicit_signals_count: int = Field(default=0)
    bootstrap_performed: bool = Field(default=False)
    summary_json: Optional[str] = Field(default=None)


class RuleVersion(SQLModel, table=True):
    __tablename__ = "rule_versions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    rule_family: str = Field(index=True)
    version: str = Field(default="7.0.0")
    config_hash: Optional[str] = Field(default=None)
    effective_from: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
