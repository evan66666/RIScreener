# PRD PATCH — IDX Strategic Ownership & Smart Money Intelligence

**Patch Version:** 7.2  
**Base Version:** v7.1  
**Patch Type:** Incremental implementation update only  
**Status:** Required addition to existing v7.1 implementation  
**Scope:** Ownership intelligence accuracy, structural ownership context, investor classification, beneficial-owner relationships, HSC, free-float context, share pledge/release, and lead-time integrity

> **Important:** This is a patch, not a replacement PRD. Do not rewrite v7.0/v7.1 modules already implemented. Only add/modify the requirements below.

---

## 1. Purpose

v7.1 correctly introduced the IDX discovery routes:

- `5%`
- `1%`
- `Kepemilikan`
- issuer ticker
- `Volatilitas`

and separated discovery evidence from actual ownership events.

v7.2 strengthens the system so that it can behave more like a disciplined smart-money researcher by distinguishing:

1. **event-level ownership evidence**;
2. **structural ownership context**;
3. **investor identity/classification**;
4. **beneficial-owner / controller relationships**;
5. **ownership concentration and free-float context**;
6. **share pledge / release events**;
7. **publication latency versus actual transaction timing**.

The goal is to reduce false conclusions such as:

> “Holder owns >1%, therefore accumulation is happening now.”

or:

> “Ownership disclosure appeared, therefore the investor knew a future corporate action.”

The system must instead answer:

> **What is directly observed, what changed, who is involved, how timely is the evidence, how concentrated is ownership, what strategic relationship exists, and what independent evidence confirms the behavior?**

---

# 2. Critical Architecture Rule

Ownership intelligence must now be split into four independent layers:

```text
LAYER 1 — DISCOVERY
Why did we find the document?

LAYER 2 — FACT / EVENT
What ownership or pledge event is explicitly disclosed?

LAYER 3 — STRUCTURAL CONTEXT
Who owns the shares, how concentrated is ownership, what investor type is involved?

LAYER 4 — INTERPRETATION
Does the combined evidence suggest accumulation, distribution,
strategic positioning, financing pressure, control activity, or an unknown state?
```

No layer may be substituted for another.

---

# 3. Fix — `1%` Route Must Be Deep-Process Eligible

The v7.1 `1%` discovery route is retained but must be corrected.

### New rule

`OWN-01` must be included in deep-processing eligibility when the route returns a title/category consistent with ownership data or when the underlying search result is a dedicated public ownership dataset.

```text
Deep-process eligibility includes:

OWN-05
OR OWN-01
OR OWN-KP
OR ownership-related title/category
OR control-related title/category
OR MKT-VOL
OR high-priority issuer promotion
OR Tier-A/B corporate-action match
OR required timeline completion
```

### Important interpretation rule

`1%` remains a **discovery/structural ownership route**, not evidence of an exact transaction threshold crossing.

The system must store the actual observed percentage from the source.

---

# 4. Ownership Evidence Taxonomy

The system shall distinguish the following ownership information classes.

## 4.1 Ownership Snapshot

Answers:

> Who owns shares at an observed date?

Examples:

- public ownership data above 1%;
- KSEI ownership snapshots;
- significant-holder tables;
- HSC disclosures.

This is **structural context**, not transaction proof.

---

## 4.2 Ownership Acquisition Event

Answers:

> Who acquired shares, how many, when, and at what disclosed price?

Possible values:

- BUY / ACQUIRE
- SUBSCRIBE
- EXERCISE / CONVERSION where applicable
- RECEIVE / TRANSFER-IN if explicitly disclosed

---

## 4.3 Ownership Disposal Event

Possible values:

- SELL / DISPOSE
- TRANSFER-OUT
- REDUCE POSITION

The system must preserve the disclosed reason when available.

---

## 4.4 Ownership Threshold / State Change

Examples:

- crossing above 1%;
- crossing above 5%;
- falling below 5%;
- change in controller status;
- material change in voting ownership.

A threshold event is not necessarily a transaction itself. The actual transaction evidence must remain separately stored when available.

---

## 4.5 Share Pledge Event

Add a dedicated ownership-financing event family:

- pledge initiated;
- pledge increased;
- pledge decreased;
- pledge released;
- pledge reaches a reportable threshold;
- accumulated pledge change.

POJK 4/2024 explicitly regulates reporting of activities involving pledging listed-company shares, including staged pledges that cumulatively reach the applicable threshold. citeturn205910search24turn205910search26

These events must never automatically be classified as bullish or bearish.

Interpretation depends on context such as financing, repayment, control, liquidity pressure, and subsequent disclosures.

---

## 4.6 Administrative / Non-Market Ownership Change

Add explicit classification for changes that may not represent discretionary market positioning:

- internal group transfer;
- affiliated transfer;
- inheritance / succession where disclosed;
- corporate restructuring transfer;
- nominee/custodian movement where explicitly identified;
- conversion or corporate-action-driven change;
- other administrative transfer.

These events must receive an **administrative-change penalty** in strategic-positioning scoring unless independent evidence shows genuine market positioning.

---

# 5. Investor / Holder Classification Layer

The existing `holder_role / holder_type` must be upgraded from a generic field into a normalized taxonomy.

At minimum support:

```text
INDIVIDUAL
INSTITUTION
CORPORATE
FUND
INSURANCE
PENSION
BANK / FINANCIAL INSTITUTION
GOVERNMENT-RELATED
STRATEGIC INVESTOR
CONTROLLER-RELATED
DIRECTOR
COMMISSIONER
AFFILIATE / RELATED PARTY
FOREIGN INVESTOR
DOMESTIC INVESTOR
CUSTODIAN / NOMINEE
OTHER / UNKNOWN
```

The implementation must remain extensible because current KSEI investor ownership data has a much more granular classification structure. OJK/BEI/KSEI reported in April 2026 that public ownership data now uses **39 investor classifications and types**. citeturn205910search2

### Rule

Do not compress all institutional investors into one generic `institution` value when the source provides a more precise classification.

Store:

```text
raw_investor_class
normalized_investor_class
source
observed_at
confidence
```

---

# 6. Beneficial Owner / Controller Relationship Layer

Add a relationship layer linking:

```text
Holder
  ↓
Parent / Related Entity
  ↓
Beneficial Owner
  ↓
Controller / Control Group
```

OJK/BEI/KSEI reported strengthened availability of beneficial-owner information for holders at or above 10%, subject to the applicable framework. citeturn205910search2

### Required fields

```text
holder_id
related_entity_id
beneficial_owner_id
controller_id
relationship_type
source_document_id
valid_from
valid_to
confidence
```

### Critical interpretation rule

Different legal holders must not automatically be treated as independent actors if the source evidence indicates a common controller / beneficial owner / affiliate relationship.

Conversely, the system must not infer a common beneficial owner without source evidence.

---

# 7. Actor Identity Resolution

Ownership intelligence requires stable actor identities across documents.

Add / strengthen:

```text
actor_canonical_id
raw_holder_name
normalized_holder_name
aliases
entity_type
country / domicile when disclosed
related_actor_ids
beneficial_owner_id when disclosed
controller_id when disclosed
```

### Normalization examples

The system should tolerate:

- PT ABC Tbk
- PT ABC Tbk.
- ABC
- ABC HOLDINGS LTD
- abbreviated issuer/entity names
- punctuation and capitalization differences

But normalization must never merge two entities solely because their names are similar.

A merge must be supported by:

- exact identifiers;
- source relationships;
- legal entity metadata;
- or manually verified alias mapping.

---

# 8. High Shareholding Concentration (HSC) Layer

Add **HSC** as a structural market-context event family.

OJK/BEI/KSEI announced implementation of public HSC disclosure in 2026 and described related transparency reforms as part of the market-structure transparency program. citeturn205910search2

### HSC must answer

> How concentrated is the listed company's ownership structure at the observed date?

Store, where available:

```text
issuer
observation_date
hsc_flag
concentration_metric
relevant_holder_count
source_document_id
```

### Interpretation

HSC is **not** an accumulation signal.

It is a **supply / ownership-structure context signal**.

Potential interpretation combinations:

```text
HSC only
→ structural context

HSC + increasing strategic ownership
→ stronger concentration / positioning watch

HSC + low free float + volatility
→ elevated market-structure risk / opportunity watch

HSC + ownership reduction
→ possible distribution / supply change candidate
```

The system must not claim that HSC alone predicts price performance.

---

# 9. Free-Float Context Layer

Add free-float context to ownership analysis.

OJK/BEI/KSEI announced an increase in the minimum free-float requirement to 15% through an adjustment to BEI Regulation I-A as part of the 2026 transparency reforms. citeturn205910search2

Store where available:

```text
free_float_pct
free_float_shares
observation_date
source
```

### Purpose

Free float must be used only to contextualize:

- ownership concentration;
- potential supply availability;
- effect of strategic accumulation/distribution;
- HSC;
- volatility risk.

Do not transform low free float automatically into a bullish signal.

---

# 10. Ownership Event Timing Integrity

The system must distinguish three dates for every ownership event:

```text
transaction_date
reporting_date
publication_date
```

v7.1 already introduced this distinction; v7.2 makes it mandatory for **lead-time calculations**. fileciteturn4file0L595-L621

### New Lead-Time Rule

Lead time must be measured from the **earliest observable public evidence**, not from the date the system happened to ingest the document.

Example:

```text
Transaction:        2026-08-10
Report submitted:   2026-08-12
Public disclosure:  2026-08-13
Scan ingestion:     2026-08-15
```

The system may not claim:

> “Signal detected 5 days before transaction.”

if the public disclosure only became available after the transaction.

It should instead say:

> “Public ownership evidence became observable 3 days after transaction and 17 days before the later corporate-action disclosure.”

This prevents false claims of predictive ability.

POJK 4/2024 states that required ownership changes are to be reported as soon as possible and no later than 5 working days in the covered cases. citeturn205910search25turn205910search1

---

# 11. Lead-Time Engine Update

The existing v7.0 lead-time engine remains, but it must now calculate separate measurements:

### A. Transaction-to-public lag

```text
publication_date - transaction_date
```

### B. First-public-evidence lead

```text
corporate_action_explicit_date
- earliest_public_evidence_date
```

### C. First-alignment lead

```text
corporate_action_explicit_date
- first_date_when_multiple_independent_evidence_layers_aligned
```

### D. First-positioning lead

```text
corporate_action_explicit_date
- earliest_public_strategic_positioning_evidence
```

Only B/C/D are relevant to genuine early-warning research.

---

# 12. Smart Money Positioning Score Update

The existing Smart Money Score must incorporate the following dimensions:

```text
Actor Significance
+ Ownership Change
+ Repetition
+ Size / Materiality
+ Timing
+ Transaction Price Evidence
+ Investor Classification
+ Beneficial-Owner / Controller Relevance
+ Administrative-vs-Market Classification
+ Ownership Concentration Context
+ Corporate-Action Alignment
+ Transformation Alignment
+ Volatility Alignment
- Administrative Transfer Penalty
- Contradiction Penalty
- Staleness Penalty
```

### Critical rule

No single field may dominate the score.

In particular:

```text
5% crossing ≠ high Smart Money Score
>1% holder ≠ accumulation
HSC ≠ accumulation
Volatilitas ≠ accumulation
Large transaction ≠ smart money
```

The score must reward **convergence** rather than isolated size.

---

# 13. New Signal: Ownership Convergence

Add a distinct intermediate signal:

> **OWNERSHIP_CONVERGENCE**

Triggered when multiple independent ownership facts point in the same direction.

Example:

```text
Holder A appears
+
Holder A increases position
+
Same actor repeats acquisition
+
Actor is strategically relevant
+
Ownership concentration rises
```

This is stronger than any single ownership event.

---

# 14. New Signal: Strategic Positioning + Corporate Action Alignment

The highest-priority early signal remains the intersection of:

```text
Strategic Actor Positioning
        +
Corporate-Action Preparation
        +
Transformation / Asset Catalyst
        +
Temporal Alignment
```

The system should label this:

```text
VERY_HIGH_PRIORITY_ALIGNMENT
```

It is still a research priority, **not a buy recommendation**.

---

# 15. Anti-False-Positive Rules — Expanded

The system must not classify the following as strategic positioning without corroboration:

- public >1% snapshot alone;
- KSEI snapshot alone;
- HSC alone;
- low free float alone;
- a 5% threshold alone;
- a 1% threshold alone;
- a single large ownership transaction with no actor context;
- a pledge alone;
- a pledge release alone;
- intercompany transfer;
- affiliate transfer;
- administrative transfer;
- corporate-action-driven dilution or issuance;
- nominee/custodian movement without independent evidence;
- a repeated duplicate filing;
- volatility disclosure without independent ownership/action evidence.

### Required classification

These must remain:

```text
STRUCTURAL CONTEXT
or
OWNERSHIP EVENT
or
MARKET ANOMALY
```

until corroborating evidence supports a behavior hypothesis.

---

# 16. Cross-Layer Correlation Matrix

The scoring engine should explicitly model the following combinations:

| Evidence | Interpretation |
|---|---|
| >1% ownership snapshot | Structural context |
| HSC | Concentration context |
| Low free float | Supply context |
| Ownership increase | Event-level positioning evidence |
| Repeated ownership increase | Behavioral evidence |
| Strategic actor + increase | Stronger positioning evidence |
| Ownership + Volatilitas | Market-behavior investigation |
| Ownership + corporate-action preparation | High-value alignment |
| Ownership + transformation + asset injection | Very strong strategic-research candidate |
| Pledge + liquidity pressure | Financing-risk investigation |
| Pledge release + strategic ownership increase | Financing/positioning transition candidate |

The table is not a deterministic trading rule. It is a prioritization framework.

---

# 17. Corporate-Action Early Detection Must Remain Independent

Do not let ownership intelligence replace the existing corporate-action precursor engine.

The existing lifecycle remains:

```text
Early
→ Developing
→ Explicit
```

Corporate-action evidence must be able to trigger a candidate even when no ownership signal exists.

Likewise, ownership evidence must be able to trigger a candidate even when no corporate action is visible yet.

The highest priority occurs when the two layers align.

---

# 18. Smart Scan Search Order Update

The v7.1 order is retained but expanded:

```text
A. OWNERSHIP RADAR
   5%
   1%
   Kepemilikan
   >1% public ownership
   HSC
   Investor classification

B. MARKET STRUCTURE RADAR
   Volatilitas
   Free float
   ownership concentration

C. ISSUER DEEP DIVE
   Ticker route

D. EVENT / FINANCING RADAR
   Share pledge / release
   capital raising
   strategic investor
   control
   acquisition / divestment

E. EXISTING v7.0 TRANSFORMATION + CORPORATE-ACTION RADAR
```

The execution may be parallelized, but route identity must be preserved.

---

# 19. Data Model Additions

Add or extend the following entities without replacing existing v7.0/v7.1 entities.

### ownership_snapshots

```text
id
issuer_id
holder_id
observation_date
share_count
ownership_pct
investor_class
source_document_id
source_type
```

### ownership_events

```text
id
issuer_id
holder_id
event_type
transaction_date
reporting_date
publication_date
previous_shares
current_shares
delta_shares
previous_pct
current_pct
delta_pct
transaction_price
transaction_value
transaction_type
administrative_flag
related_party_flag
pledge_flag
source_document_id
```

### actor_relationships

```text
id
actor_id
related_actor_id
relationship_type
beneficial_owner_id
controller_id
source_document_id
valid_from
valid_to
confidence
```

### market_structure_snapshots

```text
id
issuer_id
observation_date
hsc_flag
concentration_metric
free_float_pct
free_float_shares
source_document_id
```

### investor_classifications

```text
id
actor_id
raw_class
normalized_class
source
observed_at
confidence
```

---

# 20. Ownership Timeline UI Update

For an ownership candidate, the detail view should now show:

```text
ACTOR
↓
INVESTOR TYPE
↓
BENEFICIAL OWNER / CONTROLLER (if disclosed)
↓
PREVIOUS OWNERSHIP
↓
TRANSACTION / EVENT
↓
CURRENT OWNERSHIP
↓
TRANSACTION PRICE / VALUE
↓
PLEDGE / RELEASE STATUS
↓
OWNERSHIP CONCENTRATION / FREE FLOAT
↓
RELATED CORPORATE-ACTION EVIDENCE
↓
LEAD-TIME / PUBLIC OBSERVABILITY
```

The UI must visually separate:

- **Observed Fact**
- **Derived Metric**
- **Behavior Candidate**
- **Strategic Hypothesis**

---

# 21. Scoring Output Update

Do not show one opaque “Smart Money Score” without decomposition.

Minimum visible components:

```text
Strategic Actor Score
Ownership Behavior Score
Ownership Concentration Context
Corporate-Action Alignment
Transformation Alignment
Market-Anomaly Alignment
Evidence Quality
Lead-Time Quality
```

Then calculate:

```text
Overall Priority
```

This makes it possible to see whether a candidate is strong because of actual behavior or merely because of structural ownership concentration.

---

# 22. Validation / Backtesting Update

Backtesting must now evaluate ownership evidence separately from structural context.

Required measurements:

### Ownership event quality

- precision of true ownership-event extraction;
- false-positive rate from `1%` / `5%` search routes;
- administrative-transfer classification accuracy;
- actor identity resolution accuracy;
- investor classification accuracy;
- pledge / release extraction accuracy.

### Smart-money research quality

- lead time from earliest public evidence;
- lead time from first multi-layer alignment;
- false-positive rate of strategic-positioning candidates;
- rate of candidates later associated with explicit corporate action;
- rate of candidates where no later confirmation appears;
- contribution of HSC/free-float context;
- contribution of beneficial-owner relationships.

### Important

Do not call the system predictive merely because historical examples show co-occurrence.

The output is an **evidence-based early-warning / research prioritization system**.

---

# 23. Acceptance Criteria

v7.2 is complete when:

### Ownership

- `OWN-01` is deep-process eligible when relevant.
- Ownership snapshot and ownership event remain separate.
- Acquisition, disposal, threshold change, pledge, release, and administrative changes are distinguishable.
- Transaction/reporting/publication dates are stored separately.

### Structural context

- Public >1% ownership data is stored as structural context.
- HSC can be stored as structural context.
- Free float can be stored as structural context.
- Investor classifications can preserve source granularity.
- Beneficial-owner/controller relationships can be stored when disclosed.

### Actor intelligence

- Holder aliases can be normalized safely.
- Different holders can be linked when source evidence supports a relationship.
- No unsupported entity merge occurs.

### Scoring

- Structural context cannot alone create a strategic-positioning confirmation.
- Pledge/release cannot alone create a bullish/bearish classification.
- Volatility cannot alone create accumulation confirmation.
- Multi-layer convergence increases priority.
- Administrative transfers receive a penalty or neutral treatment.

### Lead time

- Lead time uses the earliest observable public evidence.
- Transaction-to-publication lag is shown separately.
- No signal is described as “predictive” when it was only disclosed after the underlying event.

### Efficiency

- Existing v7.1 discovery routes remain functional.
- Multiple routes still deduplicate to one canonical document.
- Existing v7.0/v7.1 engines remain intact.

---

# 24. Developer Test Corpus — Additional Cases

Add at least:

1. >1% monthly ownership snapshot only.
2. HSC disclosure only.
3. low free-float issuer without ownership change.
4. 5% ownership change event.
5. 1% ownership snapshot.
6. repeated acquisition by the same actor.
7. administrative affiliate transfer.
8. share pledge initiation.
9. staged share pledge reaching reportable threshold.
10. share pledge release.
11. holder + beneficial-owner relationship.
12. holder + controller relationship.
13. two legal entities with same/similar names but no evidence of relationship.
14. two entities with explicit common controller.
15. ownership event disclosed several days after transaction.
16. ownership + volatility + corporate-action preparation.
17. HSC + low free float + volatility without ownership change.
18. strategic ownership + transformation + asset injection.

Expected outputs must preserve the separation between:

```text
fact
→ structure
→ behavior
→ strategic hypothesis
```

---

# 25. Final Smart-Money Principle

The enhanced project must follow this rule:

> **Do not ask only “Who owns the stock?” Ask “Who changed their position, what relationship do they have to the issuer, what financing or control activity surrounds the change, how concentrated is the ownership, when did the public learn about it, and what independent evidence is moving in the same direction?”**

The highest-value candidate is not simply a stock with:

```text
large holder
or
>1%
ownership
or
HSC
or
volatility
```

It is a situation where **multiple independent evidence layers converge before the corporate action becomes explicit**:

```text
Strategic Actor
      +
Observed Positioning
      +
Repeated / Persistent Behavior
      +
Corporate-Action Preparation
      +
Transformation / Asset Catalyst
      +
Market-Structure Context
      +
Temporal Alignment
      +
High Evidence Quality
```

That is the project’s intended **highest-priority research state**.

It remains an information and research-prioritization system, not proof of insider knowledge, not a literal “bandar detector,” and not a buy/sell recommendation engine.
