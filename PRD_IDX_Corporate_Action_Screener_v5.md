# Product Requirements Document (PRD)
# IDX Corporate Action Early Detection Screener

**Version:** 5.1 - Early Detection & Information Intelligence  
**Date:** 1 September 2026  
**Status:** Ready for implementation  
**Deployment:** Local-only  
**Primary interaction:** Manual one-click screening

---

## 1. Executive Summary

IDX Corporate Action Early Detection Screener is a focused local web application for investors who want to reduce the time required to screen IDX company disclosures and identify information that may precede a positive corporate action.

The application uses `nichsedge/idx-bei` as the IDX data acquisition layer. Based on the repository documentation reviewed for this PRD, `GetAllAnnouncement` exposes company disclosures and PDF filings, and the repository also provides a FastAPI service and Python-based tooling.

The MVP is intentionally narrow. The user opens the local web application, selects a scan range, and clicks **Run Screening** once. That single action runs the entire pipeline:

1. Retrieve announcements for the selected scan range through `idx-bei`.
2. Detect announcements/documents that are new or not yet processed locally.
3. Resolve and download attached PDF filings when available.
4. Extract page-aware text from each PDF.
5. Screen every newly ingested disclosure for important information.
6. Detect explicit corporate actions and early/indirect precursor signals.
7. Compare the new disclosure with relevant issuer history.
8. Detect novelty and changes in wording/state versus prior disclosures.
9. Corroborate related signals across multiple disclosures.
10. Detect contradiction, cancellation, or supersession.
11. Determine action stage: Early, Developing, or Explicit.
12. Determine potential information impact: Positive, Neutral, Negative, Mixed, or Unclear.
13. Rank the most important signals for review.
14. Show the reason, evidence excerpt, page number, supporting documents, timeline, and original PDF.

The product does **not** predict stock prices, generate buy/sell recommendations, trade securities, or require an LLM in the MVP.

### Core product question

> Which IDX issuers are showing new, meaningful evidence of a potentially positive corporate action, including early clues before the action is formally announced?

---

## 2. Product Vision

Convert the manual research workflow:

**Open IDX -> inspect many announcements -> open PDFs -> read -> search -> compare with old disclosures -> decide relevance**

to:

**Open local app -> choose range -> click Run Screening -> review ranked signals -> inspect evidence -> open source PDF.**

The product is successful when the user can focus attention on a small number of high-value disclosures instead of manually reading every filing.

---

## 3. Problem Statement

Disclosure titles are not sufficient to detect meaningful events. Material information can appear inside a filing without a title that explicitly names a corporate action.

Examples of potential leading information:

- funding requirements;
- capital structure discussions;
- RUPSLB linked to capital matters;
- increase in authorized capital;
- discussion of issuing new shares;
- acquisition exploration or negotiation;
- strategic investor discussions;
- major expansion plans;
- major contracts;
- new financing arrangements;
- changes in controlling shareholders;
- buyback plans;
- special dividend intentions.

The application therefore performs **document-content screening plus cross-document early detection**, not title-only keyword matching.

---

## 4. Goals

### 4.1 Primary goals

- Retrieve newly published IDX disclosures through `idx-bei`.
- Download the attached PDF whenever available.
- Extract searchable, page-aware text.
- Screen all newly ingested disclosure content for important information.
- Detect explicit corporate-action signals.
- Detect early and indirect leading indicators.
- Detect material changes versus previous disclosure language when possible.
- Connect related disclosures for the same issuer across a rolling lookback period.
- Detect signal progression from Early -> Developing -> Explicit.
- Separate event likelihood from economic impact.
- Classify impact as Positive, Neutral, Negative, Mixed, Unclear, or No Signal.
- Rank information so the user sees the most useful signals first.
- Preserve explainable evidence and source traceability.
- Keep the system local, lightweight, deterministic, and maintainable.

### 4.2 Core early-detection objective

For the Right Issue/HMETD use case, the system should surface meaningful precursor evidence **before** waiting for an explicit HMETD announcement.

Early signals must never be presented as confirmed corporate actions.

### 4.3 Information-intelligence objective

Every newly processed disclosure should receive an information relevance result, even if it is not a corporate action.

The result should distinguish:

- **High importance** - materially new or potentially market-relevant information.
- **Medium importance** - relevant change/event but limited or uncertain impact.
- **Low importance** - routine or low-value information.
- **No material signal** - no meaningful signal detected by the rules.

---

## 5. Non-Goals / Out of Scope

The MVP will not include:

- stock price prediction;
- buy/sell recommendations;
- automatic trading;
- portfolio management;
- broker integration;
- news aggregation;
- social sentiment;
- public multi-user SaaS features;
- mandatory LLM/AI document interpretation;
- complex quantitative alpha models;
- trading-strategy backtesting;
- Redis;
- Celery/RabbitMQ;
- PostgreSQL;
- Neo4j/UBO graph features;
- notification services;
- mobile applications;
- real-time market terminal features;
- automatic scheduled scanning in MVP.

---

## 6. Target User

### Primary user

A self-directed IDX investor/trader who wants a fast, explainable first-pass screen of newly published issuer disclosures and early corporate-action indicators.

### User need

The user wants to answer, with minimal manual work:

1. What new information appeared?
2. Which issuers have meaningful information?
3. Which issuers show early signs of a corporate action?
4. Why was an issuer flagged?
5. What evidence supports the signal?
6. Is the action confirmed or still only an early indication?

---

## 7. Operating Model: Local + Manual One-Click

### 7.1 Local-only

The application runs on the user's local machine.

- React frontend is local.
- FastAPI backend is local.
- SQLite database is local.
- PDF files are stored locally.
- Screening rules run locally.
- No cloud database is required.

### 7.2 One-click screening

The MVP has one primary action:

**Run Screening**

After the user clicks it, no additional manual action is required for the selected scan to complete.

```text
Open local app
    -> Select Scan Range
    -> Click Run Screening
    -> Fetch IDX announcements
    -> Detect new documents
    -> Download PDFs
    -> Extract text
    -> Screen information
    -> Build early signals
    -> Rank results
    -> Display results
```

### 7.3 No scheduler in MVP

There is no automatic daily/background scan in MVP.

The codebase should keep the screening pipeline callable as one reusable service so a scheduler can be added later without changing the detection engine.

---

## 8. Scan Range vs Historical Lookback

These are separate concepts and must not be conflated.

### 8.1 Scan Range

Determines which disclosure announcements are retrieved for the current screening session.

Default:

- Today

Available:

- Today
- Last 3 days
- Last 7 days
- Custom date range

### 8.2 Historical Lookback

Determines how much prior issuer history is included when evaluating early signals.

Default:

- 60 calendar days

Optional extension:

- up to 120 calendar days for selected slow-moving action families.

Example:

```text
Scan Range: Today
        |
        +--> ingest today's new disclosures
        |
        +--> evaluate against issuer history
              from the prior 60-120 days
```

The system should not re-download already processed historical PDFs solely because they are used in the lookback. Existing local evidence should be reused.

### 8.3 First-run historical bootstrap (mandatory)

When the local database does not contain enough historical issuer evidence for early detection, the first screening run shall automatically bootstrap the configured historical lookback before final signal evaluation.

Default bootstrap behavior:

- Scan Range remains Today unless the user chooses another range.
- Historical Lookback is the previous 60 calendar days.
- Selected slow-moving action families may use up to 120 calendar days.

The bootstrap shall:

1. Retrieve historical announcements needed for context.
2. Detect historical documents not yet stored locally.
3. Download every supported PDF attachment needed for the configured lookback.
4. Extract and store page-aware text.
5. Run the same rule library against historical documents.
6. Mark those records as `HISTORICAL_CONTEXT` so they are not mistaken for newly published information.

If bootstrap is incomplete, the system must show the missing-context status and reduce confidence rather than silently treating the issuer as having no history.

---

## 9. Core User Journey

### 9.1 Screening

1. User opens local dashboard.
2. User selects scan range; default is Today.
3. User clicks Run Screening once.
4. If this is the first run or local history is insufficient, the system performs the mandatory historical bootstrap before final early-detection evaluation.
4. Backend retrieves announcement data through `idx-bei`.
5. System identifies new/unprocessed disclosures.
6. System resolves the attached PDF URL where available.
7. System downloads the PDF.
8. System hashes the PDF and deduplicates it.
9. System extracts page-aware text using PyMuPDF.
10. System performs text normalization.
11. System runs importance screening.
12. System runs corporate-action and precursor detection.
13. System checks context, negation, uncertainty, cancellation, and contradictions.
14. System compares the new content with relevant issuer/action history.
15. System performs novelty/change detection where prior text exists.
16. System updates issuer/action timelines.
17. System ranks results.
18. Frontend displays the completed screening result.

### 9.2 Scan completion summary

After each run, the dashboard shall show processing completeness before the signal list, including:

- announcements retrieved;
- announcements newly processed;
- announcements already known;
- PDF attachments found;
- PDFs downloaded;
- PDFs extracted;
- PDFs requiring OCR or with extraction failure;
- announcements processed without a PDF;
- important disclosures detected;
- Early / Developing / Explicit signals detected.

This summary prevents missing files or failed extraction from being mistaken for a clean `No Signal` result.

### 9.3 Review

1. User sees High-priority results first.
2. User opens an issuer or signal.
3. User sees what changed, why it matters, action stage, impact, confidence, and evidence.
4. User sees supporting disclosures in timeline order.
5. User opens the original PDF if further verification is needed.

---

## 10. Functional Requirements

### FR-01 Announcement ingestion

The system shall retrieve IDX company announcements using `idx-bei`.

Minimum normalized fields:

- announcement ID, when available;
- issuer/ticker;
- company name, when available;
- title;
- publication date/time;
- announcement type/category, when available;
- attachment metadata;
- PDF URL, when available.

Source references:

- https://github.com/nichsedge/idx-bei
- https://github.com/nichsedge/idx-bei/blob/main/python/API_VERIFICATION_SPEC.md

### FR-01A All-disclosure ingestion (mandatory)

The selected Scan Range shall retrieve and process **all announcements returned by `idx-bei`**, regardless of title or whether an obvious corporate-action keyword is present.

Every announcement must end in an explicit processing state:

- `PROCESSED_PDF`
- `PROCESSED_METADATA_ONLY`
- `PDF_UNAVAILABLE`
- `DOWNLOAD_FAILED`
- `EXTRACTION_FAILED`
- `DUPLICATE_ALREADY_PROCESSED`

Announcements must not be filtered out merely because they appear routine at the title level. The information-importance layer is responsible for determining whether the content is important.

### FR-01B Multiple-attachment processing (mandatory)

If one announcement contains multiple supported PDF attachments, the system shall process **every supported PDF attachment**, not only the first attachment.

Each attachment shall have its own document record, checksum, download status, extraction status, and evidence. The announcement remains the parent entity linking all attachments.

Unsupported non-PDF attachments may be skipped with an explicit `UNSUPPORTED_ATTACHMENT` status and must not fail the entire announcement.

### FR-02 Scan range

The scanner shall support Today, Last 3 Days, Last 7 Days, and Custom range.

### FR-03 New-document detection

A document is new when it has not previously been processed using, in priority order:

1. stable announcement/document ID;
2. normalized source URL;
3. SHA-256 content hash.

### FR-04 PDF acquisition

For announcements with available filing attachments, the backend shall download the PDF locally.

Requirements:

- timeout;
- transient retry;
- maximum file-size guard;
- content-type validation;
- safe filename handling;
- SHA-256 checksum;
- status tracking.

### FR-05 PDF extraction

PyMuPDF is the primary extractor.

Extraction output:

- page number;
- page text;
- document metadata where available.

### FR-06 OCR readiness

OCR is not mandatory for MVP, but the architecture shall permit it as fallback.

Unreadable/scanned documents must not silently become No Signal.

Possible statuses:

- EXTRACTED
- OCR_REQUIRED
- EXTRACTION_FAILED

### FR-07 Text normalization

Normalize safely for:

- case differences;
- repeated whitespace;
- line-break artifacts;
- common hyphenation;
- Unicode normalization where safe.

Original text must remain available for evidence reproduction.

---

## 11. Information Importance Screening

This layer sits **before** corporate-action classification.

### 11.1 Objective

Determine whether the new disclosure contains material or potentially market-relevant information, even if it does not directly mention a corporate action.

### 11.2 Importance classes

**HIGH**

Potentially material change, strategic event, funding event, major contract, ownership change, acquisition/divestment, capital action, or other high-value disclosure.

**MEDIUM**

Meaningful event with limited scope, incomplete context, or moderate potential impact.

**LOW**

Relevant but routine or low novelty information.

**NO MATERIAL SIGNAL**

No important change detected by the rules.

### 11.3 Importance evidence

Importance must be explainable by one or more evidence items:

- event type;
- novelty/change;
- financial/strategic magnitude when explicitly stated;
- lifecycle transition;
- corroboration;
- source quality;
- issuer context.

The system must not invent materiality metrics that are absent from the disclosure.

---

## 12. Corporate-Action Taxonomy

The MVP shall screen:

1. Right Issue / HMETD
2. Private Placement
3. Acquisition
4. Divestment
5. Merger
6. Spin-off / Separation
7. Share Buyback
8. Special Dividend
9. Stock Split / Reverse Split
10. Warrant
11. Convertible Securities
12. Major Expansion
13. Major Contract
14. Strategic Investor
15. Change of Control

Each action family must have a rule set containing:

- explicit terms;
- early/indirect terms;
- lifecycle states;
- positive-impact contexts;
- negative/distress contexts;
- negation patterns;
- uncertainty patterns;
- cancellation/supersession patterns.

### Mandatory rule-library completeness

Before MVP release, every action family must have a versioned rule definition for all of the items above. Rules shall be stored separately from frontend code and be independently testable.

The test suite shall include, for every action family, representative examples of:

- positive/valid signal;
- negative/distress signal;
- negated statement;
- hypothetical/exploratory statement;
- cancelled/superseded statement.

An action family is not considered MVP-complete until its rules and representative tests exist.

---

## 13. Early-Signal Detection

### 13.1 Two-layer engine

**Document level**

```text
PDF text
 -> trigger matching
 -> context
 -> negation/uncertainty
 -> evidence
 -> document signal
```

**Issuer level**

```text
document signals
 -> temporal grouping
 -> novelty/change detection
 -> corroboration
 -> contradiction
 -> lifecycle/state transition
 -> issuer/action signal
```

### 13.2 Leading-indicator principle

The system must actively look for information that may precede an explicit action.

Example: potential capital raising

```text
Funding need
 + RUPSLB related to capital
 + capital-structure change
 + new-share discussion
 + strategic investor subscription
 ----------------------------------
 Developing capital-raising signal
```

A single weak clue should not be treated as confirmation.

### 13.3 Signal stage

**EARLY**

Meaningful precursor evidence exists, but no formal action is apparent.

**DEVELOPING**

Multiple related signals, or a highly informative planned/approved step, indicate that the suspected action is becoming more concrete.

**EXPLICIT**

The corporate action is formally/directly disclosed.

### 13.4 State progression

```text
NO SIGNAL
   -> EARLY
   -> DEVELOPING
   -> EXPLICIT
```

Additional states:

```text
EARLY/DEVELOPING
   -> CONTRADICTED
   -> EXPIRED
   -> SUPERSEDED
```

Historical evidence must remain visible even after a signal is superseded.

---

## 14. Event Lifecycle Detection

The system shall model action-family progression rather than treating every disclosure as isolated.

Examples:

### Right Issue / Capital Raising

```text
Funding Need
 -> Capital Discussion
 -> RUPSLB / Capital Agenda
 -> Capital Structure Change
 -> New Share Discussion
 -> HMETD / Rights Offering
 -> Execution
```

### Acquisition

```text
Exploration
 -> Evaluation / Due Diligence
 -> Negotiation
 -> Agreement
 -> Approval
 -> Completion
```

### Change of Control

```text
Ownership Discussion
 -> Share Acquisition
 -> Prospective Controller
 -> Approval / Closing
 -> Completed Control Change
```

Lifecycle stage must be based on actual disclosure wording and evidence.

---

## 15. Novelty and Change Detection

A key part of early detection is identifying what changed versus prior issuer disclosures.

### 15.1 Novelty classes

- ROUTINE
- NEW
- MATERIAL_CHANGE
- STATE_ADVANCEMENT
- REVERSAL
- CONFIRMATION

### 15.2 Example

Previous disclosure:

> "The company is considering expansion funding."

New disclosure:

> "The company has secured financing for expansion."

The second document should be recognized as a **STATE_ADVANCEMENT** even if both documents relate to the same broad topic.

### 15.3 Required output

For relevant signals, the UI should show:

**What changed?**

Example:

```text
15 Aug - Funding requirement mentioned
21 Aug - RUPSLB with capital agenda
28 Aug - Capital structure change disclosed
01 Sep - New share issuance stated
```

---

## 16. Cross-Document Corroboration

Related disclosures for the same issuer/action family shall be grouped over the lookback window.

### Corroboration rules

Confidence can increase when:

- evidence comes from multiple separate disclosures;
- disclosures are temporally consistent;
- lifecycle stages advance rather than repeat;
- different evidence types support the same action family.

Example:

```text
RUPSLB
 + capital change
 + funding requirement
 + new investor
 = stronger developing signal
```

A repeated copy of the same statement should not receive the same corroboration bonus as independent evidence.

---

## 17. Contradiction, Cancellation, and Expiry

### Contradiction

A later authoritative disclosure that rejects the suspected action must reduce the active signal.

### Cancellation

A statement such as a cancelled plan must suppress the active positive signal for that action.

### Supersession

A later document may replace an earlier state. Historical evidence remains preserved.

### Expiry

If no supporting evidence appears during a configurable observation period, an old early signal can move to EXPIRED.

The UI must distinguish:

- active;
- contradicted;
- cancelled/superseded;
- expired.

---

## 18. Context, Negation, and Uncertainty

The engine shall distinguish:

- completed;
- approved;
- planned;
- proposed;
- preliminary;
- exploratory;
- hypothetical;
- denied;
- cancelled.

Negations such as:

- tidak berencana;
- tidak akan melakukan;
- belum memiliki rencana;
- dibatalkan;
- tidak dilanjutkan;

and their English equivalents must suppress or reduce the relevant signal.

The engine must not treat a PDF merely mentioning a corporate-action term as an actual corporate-action event.

---

## 19. Impact Classification

The system separates **what is happening** from **whether it appears economically positive**.

### Positive

Potentially favorable based on disclosed business/economic rationale.

Examples:

- strategic acquisition with stated benefits;
- major expansion with credible growth objective;
- major contract with material commercial impact;
- strategic investor;
- buyback;
- special dividend;
- right issue used for productive expansion/acquisition/deleveraging with clear rationale.

### Neutral

The event is real but economic impact is unclear.

### Negative

The disclosure indicates potential distress or value destruction.

Examples:

- capital raising mainly to address immediate liquidity stress;
- forced asset disposal to meet obligations;
- restructuring explicitly tied to financial distress.

### Mixed

Material positive and negative effects coexist.

Example:

```text
+ Acquisition of a strategic business
- Large shareholder dilution
```

### Unclear

Evidence is too incomplete or ambiguous to classify the impact.

### No Signal

No meaningful action or material information detected.

**Important:** Positive means potentially favorable information, not a prediction that the stock price will rise.

---

## 20. Special Treatment of Right Issue / HMETD

Right Issue/HMETD is the primary early-detection use case.

### 20.1 Early precursor signals

The engine should watch for combinations of:

- funding requirement;
- RUPSLB related to capital;
- increase in authorized capital;
- changes to issued/paid-up capital;
- new-share discussion;
- strategic investor subscription;
- expansion/acquisition requiring new funding;
- financing pressure paired with capital discussion.

### 20.2 Positive context

Potentially positive uses of proceeds include:

- capacity expansion;
- acquisition;
- productive capital expenditure;
- strategic transformation;
- meaningful deleveraging with strategic benefit.

### 20.3 Negative context

Potentially negative context includes:

- emergency liquidity needs;
- funding losses;
- debt distress;
- covering immediate obligations without a clear value-creation plan.

### 20.4 Early-development rule

A sequence of two or more materially related precursor signals inside the lookback window should be eligible to reach **DEVELOPING**, even before HMETD is explicitly named, provided context and contradiction checks support it.

---

## 21. Ranking and Priority

The dashboard ranking should optimize for **research usefulness**, not pseudo-precision.

### 21.1 Priority factors

- information importance;
- early-stage relevance;
- signal strength;
- corroboration;
- recency;
- novelty/state advancement;
- positive-impact evidence;
- contradiction penalty;
- distress penalty;
- evidence quality.

### 21.2 Priority hierarchy

For the user's early-detection objective:

```text
Developing + Positive
        >
Early + Positive
        >
Explicit + Positive
        >
Developing + Mixed/Unclear
        >
Neutral / Low-priority items
```

An explicit event may be highly important but is not necessarily the most valuable **early** opportunity.

### 21.3 No pseudo-probability

The MVP should display categories such as:

- High Priority
- Medium Priority
- Low Priority

and confidence:

- High
- Medium
- Low

It must not display made-up probabilities such as `87.43%` unless a later validated statistical model supports them.

---

## 22. Evidence and Explainability

Every actionable signal must include evidence.

Minimum evidence fields:

- source document;
- publication date;
- page number;
- relevant sentence/paragraph;
- matched signal/action type;
- context classification;
- stage;
- impact;
- confidence.

### Example

```text
ABCD
DEVELOPING - Positive
Potential Capital Raising / HMETD

What changed?
- 21 Aug: RUPSLB with capital agenda
- 28 Aug: authorized capital change
- 01 Sep: new-share issuance discussed

Why flagged?
Three related disclosures advanced the capital-raising lifecycle.

Evidence
Document: RUPSLB filing
Page: 7
Excerpt: "..."

[Open Original PDF]
```

The system should never ask the user to trust a signal without allowing them to trace it back to the filing.

---

## 23. Dashboard Requirements

### 23.1 Main dashboard

```text
IDX CORPORATE ACTION EARLY DETECTION

Scan Range: [Today v]
Historical Lookback: 60 days

[ RUN SCREENING ]

Last Scan: 01 Sep 2026 22:30

HIGH PRIORITY

ABCD   Developing   Positive   Potential Capital Raising
XYZ    Early        Positive   Strategic Acquisition
QWER   Explicit     Positive   Buyback

OTHER IMPORTANT INFORMATION

LMNO   High   Major Contract
PQRS   Medium Ownership Change
```

### 23.2 Result categories

The dashboard should provide simple filters:

- All important information;
- Positive;
- Early;
- Developing;
- Explicit;
- Negative/Mixed;
- No Signal / routine.

### 23.3 Detail page

Show:

- ticker/company;
- information importance;
- action family;
- stage;
- impact;
- strength;
- confidence;
- what changed;
- current lifecycle state;
- evidence;
- supporting disclosures;
- timeline;
- original PDF link.

---

## 24. Data Model

### `companies`

- id
- ticker
- name

### `announcements`

- id
- company_id
- source_announcement_id
- title
- category
- published_at
- source_url
- normalized_url
- status

### `documents`

- id
- announcement_id
- pdf_url
- local_path
- sha256
- extraction_status
- processed_at

### `document_pages`

- id
- document_id
- page_number
- extracted_text

### `document_signals`

- id
- document_id
- action_type
- information_importance
- novelty_type
- impact
- stage
- strength
- confidence
- reason

### `evidence`

- id
- document_signal_id
- page_number
- excerpt
- evidence_type

### `issuer_action_states`

- id
- company_id
- action_type
- current_stage
- current_impact
- current_strength
- current_confidence
- priority
- first_signal_at
- last_signal_at
- state_status

### `signal_events`

- id
- issuer_action_state_id
- document_id
- event_date
- lifecycle_stage
- signal_type
- contribution
- status

### `scans`

- id
- started_at
- completed_at
- scan_from
- scan_to
- status
- announcements_found
- documents_processed
- signals_found

---

## 25. Screening Engine Architecture

```text
                     IDX
                      |
                      v
                 idx-bei layer
                      |
                      v
             Announcement Ingestion
                      |
                      v
              New Document Detection
                      |
                      v
                 PDF Downloader
                      |
                      v
                 PyMuPDF Parser
                      |
                      v
                Text Normalizer
                      |
          +-----------+-----------+
          |                       |
          v                       v
   Importance Engine      Action Signal Engine
          |                       |
          +-----------+-----------+
                      |
                      v
             Context / Negation
                      |
                      v
            Novelty / Change Check
                      |
                      v
          Cross-Document Correlation
                      |
             +--------+--------+
             |        |        |
             v        v        v
          Recency  Contradiction  Distress
             \        |        /
              \       |       /
               v      v      v
                State Transition
                      |
                      v
                  Ranking
                      |
                      v
                FastAPI API
                      |
                      v
             React Dashboard
```

---

## 26. Technology Stack

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- TanStack Query

### Backend

- Python
- FastAPI
- Uvicorn
- Pydantic
- SQLModel
- httpx

### IDX data acquisition

- `nichsedge/idx-bei`

### PDF processing

- PyMuPDF

### Database

- SQLite

### Python tooling

- `uv`
- Ruff
- Pytest

### Packaging

- Docker optional for local reproducibility, not required for normal local development.

### Explicitly excluded from MVP

- Redis
- Celery/RabbitMQ
- PostgreSQL
- Neo4j
- LLM API dependency

---

## 27. Core API Contract

### POST `/api/screen`

Starts one manual screening run.

Request:

```json
{
  "date_from": "2026-09-01",
  "date_to": "2026-09-01",
  "lookback_days": 60
}
```

Response:

```json
{
  "scan_id": "...",
  "status": "completed",
  "announcements_found": 123,
  "documents_processed": 42,
  "important_signals": 9
}
```

### GET `/api/signals`

Returns ranked screening results.

Supported filters:

- stage;
- impact;
- importance;
- action type;
- ticker;
- priority.

### GET `/api/signals/{id}`

Returns full signal detail, evidence, and timeline.

### GET `/api/scans/{id}`

Returns scan progress/result metadata.

### GET `/api/documents/{id}`

Returns document metadata and local/source references.

---

## 28. Screening Algorithm - MVP

The algorithm must be deterministic and explainable.

### Step 1 - Ingest

Retrieve announcements for the selected scan range.

### Step 2 - Deduplicate

Skip previously processed documents.

### Step 3 - Acquire

Download available PDFs.

### Step 4 - Extract

Extract page-aware text.

### Step 5 - Importance screen

Identify whether the disclosure contains potentially important information.

### Step 6 - Action screen

Detect explicit and precursor action signals.

### Step 7 - Context

Apply negation, uncertainty, cancellation, and distress rules.

### Step 8 - Novelty/change

Compare with prior related issuer disclosures.

### Step 9 - Corroboration

Combine related signals across the lookback window.

### Step 10 - State transition

Move the issuer/action state between Early, Developing, Explicit, Contradicted, Expired, or Superseded.

### Step 11 - Impact

Classify Positive, Neutral, Negative, Mixed, Unclear, or No Signal.

### Step 12 - Rank

Rank by information importance and early-opportunity value.

### Step 13 - Evidence

Persist supporting paragraphs and page numbers.

---

## 29. Example: Early Right Issue Detection

### Document A - 14 Aug

> Funding need for capacity expansion.

Result:

```text
Information Importance: Medium
Action Family: Capital Raising
Stage: Early
Impact: Unclear
```

### Document B - 21 Aug

> RUPSLB includes capital-related agenda.

Result:

```text
Stage: Early
Corroboration: Increased
```

### Document C - 28 Aug

> Authorized capital changes are approved.

Result:

```text
Stage: Developing
Impact: Positive potential
```

### Document D - 01 Sep

> Company discloses HMETD.

Result:

```text
Stage: Explicit
Impact: Positive/Neutral/Mixed
```

The system's value is not merely detecting Document D. It should have surfaced the issuer during Documents B/C as an **early developing signal**.

---

## 30. Backtesting and Validation (Development Only)

Backtesting is not exposed as a user-facing MVP feature, but it is required as an engineering validation activity before declaring the detector effective.

### Purpose

Determine whether the rules actually identify precursor patterns before known corporate-action events.

### Test corpus

Use historical disclosures associated with known corporate actions.

For each event, inspect windows such as:

- T-90
- T-60
- T-30
- T-14
- T-7
- T-1
- T+1

### Metrics

At minimum measure:

- early lead time;
- precision of Early/Developing signals;
- false-positive rate;
- corroboration effectiveness;
- frequency of contradictory/cancelled signals;
- rate of unreadable documents;
- document-processing success rate.

The product must not claim statistical effectiveness until these metrics have been measured on a defined historical sample.

---

## 31. Error Handling

The system must clearly distinguish:

- IDX retrieval failure;
- missing PDF attachment;
- PDF download failure;
- invalid PDF;
- extraction failure;
- OCR required;
- screening completed with limited evidence.

A failed PDF extraction must not be classified as No Signal.

The dashboard should show a processing summary after each scan.

---

## 32. Performance Expectations

MVP is intended for local personal use.

Priority is:

1. correctness;
2. traceability;
3. reasonable scan speed;
4. low local resource usage.

The scanner should process documents independently so one broken PDF does not abort the entire scan.

The scan result should be progressively persisted so a partial failure does not destroy previously completed work.

---

## 33. Security / Local Data Handling

- Store downloaded PDFs locally.
- Do not require user authentication.
- Do not expose the local application publicly by default.
- Sanitize downloaded filenames and paths.
- Validate remote document URLs before download.
- Avoid executing content from downloaded PDFs.
- Keep source URLs for traceability.

---

## 34. MVP Acceptance Criteria

The MVP is complete when all of the following are true:

### Manual operation

- User can choose a scan range.
- User clicks Run Screening once.
- The full screening pipeline runs without additional actions.
- No scheduled/background scan is required.

### Data acquisition

- New IDX announcements can be retrieved through `idx-bei`.
- **All announcements in the selected Scan Range are ingested**, not only keyword-matching announcements.
- New/unprocessed documents can be detected.
- **All supported PDF attachments for each announcement are processed.**
- Available PDF attachments can be downloaded.
- **First-run historical bootstrap populates the configured lookback when local history is insufficient.**
- Partial bootstrap failures are visible and affect confidence.

### PDF intelligence

- PDF text can be extracted page-by-page.
- Evidence includes page number.
- Extraction failures are visible.

### Importance detection

- Every newly processed disclosure receives an information relevance outcome.
- Important disclosures can be ranked.

### Corporate-action detection

- All 15 target action families have explicit and precursor rules.
- **All 15 action families have the mandatory versioned rule-library components and representative tests.**
- Negation and uncertainty handling works for defined patterns.

### Early detection

- Related disclosures for an issuer can be linked over 60 days.
- Up to 120 days can be configured for selected signals.
- Multiple clues can move a signal from Early to Developing.
- State progression can reach Explicit when the action becomes direct.
- Contradiction/cancellation can reduce or supersede an earlier signal.

### Explainability

- Each actionable signal shows reason and evidence.
- User can open the original PDF.
- User can inspect the issuer/action timeline.
- User can see what changed.

### Scope discipline

- No trading execution.
- No stock-price prediction.
- No required LLM.
- No heavy infrastructure services.

---

## 35. Definition of Success

The product should make this task materially easier:

> **"Find which issuers have important new disclosure information today, and identify which of them are developing potentially positive corporate actions before the action becomes explicit."**

A successful scan should not merely produce a long list of keywords. It should produce a concise, prioritized, evidence-backed set of issuers that deserve human review.

---

## 36. Final Product Principle

> **Find the information early, connect the evidence, show what changed, and never hide the source.**

The system is an information-screening and early-warning tool. It is not a trading oracle and must not present uncertain early signals as confirmed facts.
