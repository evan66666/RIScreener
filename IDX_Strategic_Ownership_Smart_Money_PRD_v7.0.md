# Product Requirements Document (PRD)
# IDX Strategic Ownership, Smart Money & Corporate Transformation Intelligence Engine

**Version:** 7.0 — Strategic Positioning + Corporate Transformation + Early Corporate Action Intelligence  
**Date:** 15 September 2026  
**Status:** Ready for implementation / architecture reset  
**Deployment:** Local-only  
**Primary interaction:** Manual one-click screening  
**Primary frontend:** React + TypeScript  
**Primary backend:** Python + FastAPI  
**Primary database:** SQLite  
**Primary IDX acquisition layer:** `nichsedge/idx-bei` (subject to runtime verification)  
**Primary document source:** IDX/BEI official disclosure documents  
**Ownership support source:** KSEI / BEI public ownership data  

---

## 0. Executive Decision — V7 Architecture Reset

Version 7.0 is a **strategic re-architecture**, not a feature patch.

The previous v6 architecture correctly moved the system from a pure Corporate Action Screener toward Smart Money / Ownership Intelligence. V7 goes one step further:

> **The real target is not “find the corporate action.” The target is to detect an observable strategic-positioning sequence early enough to investigate whether a corporate action, control change, business transformation, asset injection, or capital event may materially change the issuer's future value.**

The intelligence hierarchy is therefore:

```text
ACTOR / OWNER
      ↓
OWNERSHIP / CONTROL CHANGE
      ↓
CAPITAL / TRANSACTION BEHAVIOR
      ↓
BUSINESS TRANSFORMATION
      ↓
ASSET / PROJECT / VALUE INJECTION
      ↓
CORPORATE ACTION PREPARATION
      ↓
CROSS-SIGNAL ALIGNMENT
      ↓
LEAD-TIME / STAGE
      ↓
RESEARCH PRIORITY
```

Corporate action remains a major signal family, but it is no longer the product's brain.

The product must explicitly separate:

1. **Observed facts** — directly supported by source documents.
2. **Normalized events** — structured representation of observed facts.
3. **Behavior classifications** — deterministic interpretation such as accumulation candidate.
4. **Strategic hypotheses** — possible positioning / transformation thesis requiring human verification.

The product must never claim to identify an actual “bandar” from incomplete public data. It should instead use neutral terms such as:

- strategic holder;
- disclosed significant holder;
- controller;
- strategic positioning candidate;
- accumulation candidate;
- distribution candidate.

### V7 core architecture

```text
                 IDX / BEI / KSEI PUBLIC DATA
                              |
             +----------------+----------------+
             |                                 |
             v                                 v
       OWNERSHIP / ACTOR               CORPORATE ACTION
          EVIDENCE                         EVIDENCE
             |                                 |
             +----------------+----------------+
                              |
                              v
                    ISSUER / ACTOR TIMELINE
                              |
          +-------------------+-------------------+
          |                   |                   |
          v                   v                   v
     POSITIONING        TRANSFORMATION       CAPITAL / ACTION
       ENGINE              ENGINE               ENGINE
          |                   |                   |
          +-------------------+-------------------+
                              |
                              v
                     VALUE / CONTEXT ENGINE
                              |
                              v
                    ALIGNMENT + LEAD TIME
                              |
                              v
                 SMART MONEY PRIORITY QUEUE
                              |
                              v
                 HUMAN VERIFICATION / PDF
```

### Critical design principle

Ownership disclosures are often **lagging or periodic evidence**, not guaranteed “before-the-event” evidence. The engine must therefore treat ownership evidence as one side of the thesis and combine it with **corporate-action preparation, control change, transformation, asset/project injection, and lifecycle evidence**.

The objective is not to predict the future. It is to surface **the earliest observable public evidence of a potentially important strategic sequence**.

# 1. Product Vision

Build a local intelligence engine that answers:

> **Which IDX issuers are showing fresh, evidence-backed signs of strategic ownership or capital positioning, who appears to be moving, what exactly changed, and how does that behavior connect to corporate actions and other disclosures?**

The product is successful when the user can replace a large amount of manual disclosure reading with a short, ranked list of issuers that deserve deeper human investigation.

The core workflow becomes:

```text
Open local app
    -> choose scan range
    -> click Run Screening
    -> ingest IDX metadata
    -> identify high-value document candidates
    -> targeted PDF acquisition
    -> extract ownership / transaction / corporate-action evidence
    -> compare against issuer history
    -> reconstruct actor behavior
    -> cross-correlate ownership + action + timeline
    -> rank Smart Money signals
    -> inspect source evidence
```

---

# 2. Strategic Change From Previous PRD

## 2.1 Previous mental model

The former product was centered on:

> “Which newly published disclosures contain a potentially positive corporate action?”

It already contained valuable capabilities such as early detection, action lifecycle, novelty/change detection, corroboration, contradiction handling, and source evidence.

Those capabilities are **retained**, but their position in the architecture changes.

## 2.2 New mental model

The new product asks:

> “Who is doing what to the capital/ownership structure of the issuer?”

The primary unit of intelligence is therefore no longer the document. It is the **observable actor-behavior event** derived from one or more documents.

## 2.3 What is retained

The following concepts from v5.x remain mandatory foundations:

- local-only deployment;
- manual one-click screening;
- scheduler-ready backend without scheduler in MVP;
- IDX disclosure ingestion;
- PDF traceability;
- page-aware extraction;
- deterministic rules;
- early/developing/explicit lifecycle;
- novelty/change detection;
- corroboration;
- contradiction/cancellation/supersession;
- evidence excerpts;
- historical lookback;
- explainability;
- deterministic database persistence;
- backtesting as engineering validation rather than an MVP user feature.

## 2.4 What changes

The following concepts become first-class:

- actor identity;
- holder identity;
- beneficial-owner / control relationship where disclosed;
- ownership change;
- transaction direction;
- shares before/after;
- percentage before/after;
- delta shares;
- delta percentage;
- transaction price where disclosed;
- estimated transaction value where calculable;
- acquisition/disposal cost basis;
- repeated actor behavior;
- ownership concentration;
- strategic holder emergence;
- ownership graph-lite relationships;
- actor behavior timeline;
- cross-signal correlation with corporate action;
- smart-money behavior score;
- evidence quality score;
- confidence based on observable evidence rather than subjective labels.

---

# 3. Product Philosophy

## 3.1 Actor-first, event-second, document-third

The UI and intelligence layer should think in this order:

```text
ACTOR
  -> BEHAVIOR
      -> EVENT
          -> DOCUMENT EVIDENCE
```

A document is evidence. It is not the final intelligence object.

## 3.2 Observable facts before interpretation

The engine should first establish facts:

- who;
- what instrument;
- how many shares;
- ownership percentage;
- before/after;
- direction;
- price;
- date;
- source;
- relationship to issuer;
- subsequent/preceding events.

Only after facts are normalized should the engine infer behavior.

## 3.3 Behavior before narrative

The engine should prefer:

> “Holder A increased ownership from 4.8% to 7.1%, acquiring 500 million shares at reported transaction price X.”

over:

> “Bandar sedang akumulasi.”

The first is evidence. The second is an interpretation.

The UI may display:

> **Behavior classification: Strategic Accumulation Candidate**

provided the supporting facts are visible.

## 3.4 No single-signal certainty

No single event should automatically be labeled “smart money accumulation.”

The strongest signals should come from **convergence**:

```text
ownership increase
+ meaningful size
+ repeated activity
+ strategic actor
+ favorable cost basis relationship
+ related corporate action
+ market confirmation
= high-priority strategic positioning candidate
```

## 3.5 Early is valuable, but early must remain unconfirmed

The earlier the signal, the lower the certainty is normally allowed to be.

The system must distinguish:

- FACT;
- INFERENCE;
- EARLY SIGNAL;
- CONFIRMED DISCLOSURE.

---

# 4. Core Product Questions

Every screening session should help answer:

1. **Who is moving?**
2. **What changed?**
3. **How much changed?**
4. **At what price?**
5. **When did the change occur?**
6. **Is this a new actor or an existing holder?**
7. **Is the behavior repeated?**
8. **Does the behavior indicate accumulation, distribution, strategic positioning, or administrative change?**
9. **Is there an associated corporate action?**
10. **Did the issuer's state progress, stagnate, reverse, or get cancelled?**
11. **What evidence supports the interpretation?**
12. **How reliable is the evidence?**

---

## V7.1 Required Composite Intelligence Scores

V7 uses **separate scores** so that one dimension cannot hide another.

### A. Strategic Positioning Score (0–100)

Measures observable evidence that a meaningful actor is building or reducing a position.

Possible components:

- actor significance;
- ownership delta;
- transaction size;
- repeated activity;
- threshold crossing;
- disclosed transaction purpose;
- timing coherence;
- evidence quality;
- administrative-change penalty.

### B. Corporate Transformation Score (0–100)

Measures evidence that the issuer is undergoing a meaningful structural/business transformation.

Possible components:

- control change;
- business change;
- asset/project acquisition;
- asset injection;
- strategic partnership;
- major financing;
- strategic investor;
- lifecycle advancement;
- magnitude stated in the disclosure;
- evidence quality.

### C. Corporate Action Preparation Score (0–100)

Measures how close the issuer appears to an explicit corporate action.

Possible components:

- precursor count;
- precursor diversity;
- lifecycle stage;
- RUPS/RUPSLB relevance;
- capital-structure change;
- strategic investor/standby buyer evidence;
- explicit planning language;
- contradiction/cancellation penalty.

### D. Alignment Score (0–100)

Measures whether independent evidence layers converge.

Strongest examples:

```text
Strategic actor movement
+
Repeated ownership increase
+
Corporate-action preparation
+
Transformation / asset catalyst
+
Temporal alignment
```

Repeated copies of the same document do not count as independent evidence.

### E. Lead-Time Metrics

Store:

- first public signal date;
- first positioning date;
- first transformation signal date;
- first action-preparation date;
- first alignment date;
- explicit corporate-action date;
- completion date where relevant.

Derived fields:

- days from first signal to explicit action;
- days from first alignment to explicit action;
- days from first positioning to explicit action.

Lead time is a **historical measurement**, not a prediction guarantee.

# 5. Strategic Intelligence Layers

V7 adds five first-class intelligence layers.

## 5.1 Strategic Actor Intelligence

Question:

> Who is moving, and how strategically meaningful is that actor?

Actor classes:

- controller;
- prospective controller;
- disclosed significant shareholder;
- director/commissioner;
- strategic investor;
- corporate/holding company;
- financial institution;
- institutional investor;
- public/free-float holder;
- unknown/other.

The engine must not infer undisclosed beneficial ownership merely from name similarity.

### Strategic Actor Score

The score may consider:

- control relevance;
- ownership magnitude;
- change magnitude;
- direct vs indirect ownership;
- repeated activity;
- relationship to issuer;
- disclosed strategic purpose;
- transaction recurrence;
- corroborating corporate-action evidence.

The score is a research-priority metric, not a probability of intent.

---

## 5.2 Strategic Positioning Intelligence

Question:

> Is the actor building, reducing, or reshaping a meaningful position?

Behavior states:

- NEW_POSITION;
- ACCUMULATION_CANDIDATE;
- DISTRIBUTION_CANDIDATE;
- POSITION_REDUCTION;
- STABLE_LARGE_HOLDER;
- THRESHOLD_CROSSING;
- CONTROL_BUILDING;
- CONTROL_REDUCING;
- ADMINISTRATIVE_CHANGE;
- UNKNOWN.

A single ownership change is not sufficient to label accumulation or distribution.

Preferred evidence pattern:

```text
repeated acquisition
+ meaningful quantity
+ meaningful percentage change
+ actor relevance
+ coherent timing
= stronger positioning candidate
```

---

## 5.3 Corporate Transformation Intelligence

Question:

> Is the issuer undergoing a change that can materially alter its future business, assets, control, or capital structure?

Transformation families:

1. change of control;
2. change of principal business;
3. entry into a new strategic industry;
4. acquisition of a strategic asset/business;
5. disposal of a major asset/business;
6. asset injection;
7. project injection;
8. strategic partnership;
9. new controlling group;
10. major financing / recapitalization;
11. new subsidiary / holding-company structure;
12. spin-off / separation;
13. merger / consolidation;
14. strategic investor entry.

The engine should track transformation as a lifecycle:

```text
IDEA / EXPLORATION
   ↓
DISCUSSION
   ↓
NEGOTIATION / DUE DILIGENCE
   ↓
AGREEMENT
   ↓
APPROVAL
   ↓
EXECUTION
   ↓
COMPLETION
```

---

## 5.4 Asset / Future-Value Intelligence

Question:

> What new asset, project, capability, concession, business, or economic right could change the issuer's future value?

Candidate value drivers:

- mining / mineral assets;
- energy projects;
- infrastructure;
- data centers;
- real estate / landbank;
- transportation assets;
- concessions;
- technology/IP;
- strategic subsidiaries;
- new large-scale contracts;
- licenses / permits;
- capacity expansion;
- new geographic market;
- business platform injection.

The engine must distinguish:

- asset disclosed;
- asset planned;
- asset under negotiation;
- asset acquired;
- asset injected;
- asset operational.

The engine must not calculate a valuation unless sufficiently reliable public data exists.

---

## 5.5 Corporate-Action Preparation Intelligence

Retain all prior corporate-action lifecycle detection.

Additional rule:

> Corporate-action preparation is an evidence layer that may precede formal announcement; it must never be treated as confirmation until the explicit disclosure occurs.

Examples:

```text
Funding requirement
+ capital agenda
+ RUPSLB
+ authorized/issued capital discussion
+ new-share discussion
= Developing capital-raising candidate
```

# 5. Goals

## 5.1 Primary goals

- Detect meaningful ownership and actor changes quickly.
- Identify event-level changes from IDX disclosures.
- Use public BEI/KSEI ownership data as periodic structural context.
- Extract transaction quantity, direction, percentage, and price where disclosed.
- Reconstruct actor behavior over time.
- Detect candidate strategic accumulation and distribution patterns.
- Link ownership activity to corporate actions.
- Link multiple disclosures into a single issuer/actor timeline.
- Detect early corporate-action signals without treating them as confirmed.
- Rank issuers by research priority.
- Preserve exact source evidence.
- Reduce deep PDF processing by using document-priority routing.
- Keep the system deterministic and independently testable.

## 5.2 Secondary goals

- Build reusable historical ownership state.
- Detect new large/strategic holders.
- Detect holders crossing meaningful ownership thresholds.
- Detect holders leaving meaningful ownership ranges.
- Identify recurring actors across multiple issuers without assuming wrongdoing or intent.
- Provide a research-grade audit trail.
- Prepare architecture for future broker-flow and foreign-flow integration.

---

# 6. Non-Goals / Explicit Exclusions

MVP does not include:

- automatic trading;
- buy/sell order execution;
- guaranteed price prediction;
- guaranteed detection of “the bandar”; 
- hidden beneficial-owner inference without disclosed evidence;
- illegal or private-data acquisition;
- scraping authenticated personal investor accounts;
- portfolio management;
- news aggregation as a required signal source;
- automatic Telegram/Discord/email alerts;
- mandatory LLM dependency;
- large-scale ML training;
- real-time market terminal;
- broker account integration;
- direct manipulation of broker/KSEI/IDX systems;
- investment advice presented as certainty.

---

# 7. Data Source Hierarchy

## 7.1 Tier 1 — Primary evidence

### IDX / BEI official disclosures

Primary source for:

- ownership reports;
- changes in ownership;
- director/commissioner ownership changes;
- control changes;
- corporate actions;
- material information;
- RUPS/RUPSLB disclosures;
- acquisitions/divestments;
- capital raising;
- strategic transactions;
- other issuer disclosures.

The system must preserve the original document/source URL and publication metadata.

## 7.2 Tier 2 — Public ownership structure context

### KSEI / BEI ownership data

The ownership layer should ingest public ownership snapshots where available.

As of 2026, BEI/KSEI publish public information on holdings above 1% on a monthly basis. This expands the structural context beyond a simple 5% threshold. The public monthly ownership data must therefore be treated as **periodic state/context**, not as a replacement for event-level ownership disclosures. 

Relevant official references:

- OJK/BEI/KSEI transparency reform announcement dated 2 April 2026.
- KSEI ownership-data download/archive pages.

## 7.3 Tier 3 — Optional future sources

Potential later integrations:

- broker summary;
- foreign flow;
- exchange trading data;
- public company financial statements;
- other officially published regulatory data.

These are deliberately not mandatory for the MVP.

---

# 8. Document Priority Architecture

The new architecture does **not** treat every PDF equally.

The system should use a two-level pipeline:

```text
ALL METADATA
     |
     v
FAST ROUTER
     |
     +--> Tier A: Deep Process immediately
     |
     +--> Tier B: Deep Process if trigger/context exists
     |
     +--> Tier C: Metadata + lightweight content scan
     |
     +--> Tier D: Archive unless discovery trigger appears
```

This is the main performance improvement from the old architecture.

## 8.1 Tier A — Mandatory deep processing

Examples:

- laporan kepemilikan saham;
- perubahan kepemilikan saham;
- laporan transaksi saham oleh Direksi/Komisaris;
- laporan pengendali;
- ownership/control disclosures;
- acquisition/divestment;
- change of control;
- tender offer;
- rights issue / HMETD;
- private placement / PMTHMETD;
- strategic investor;
- major capital transaction;
- share pledge or release when relevant to ownership/control analysis;
- any disclosure whose metadata explicitly indicates a material ownership or capital transaction.

## 8.2 Tier B — Deep process when triggered

Examples:

- RUPSLB involving capital or ownership matters;
- increase/decrease of authorized capital;
- financing arrangements connected to acquisition/expansion;
- major financing;
- merger/acquisition negotiations;
- strategic partnership;
- major expansion;
- material contract where strategic capital deployment is plausible;
- unusual shareholder-related announcements.

## 8.3 Tier C — Lightweight processing

Examples:

- routine corporate announcements;
- ordinary administrative changes;
- routine financial reporting;
- recurring disclosures with no obvious novelty.

The engine may process title/category/metadata and only escalate to PDF extraction if a lightweight trigger appears.

## 8.4 Tier D — Archive / discovery

Documents with no ownership/capital/corporate-action trigger remain recorded in metadata but do not require immediate deep PDF extraction in Smart Scan.

## 8.5 Full Audit Scan

A separate scan mode must exist for validation/research:

> **Full Audit Scan = deep-process all available supported documents in the selected range.**

This is used for:

- rule development;
- backtesting;
- missed-signal investigation;
- regulatory/source completeness checks;
- validating Smart Scan recall.

---

# 9. Screening Modes

## 9.1 Smart Scan — default

Goal: maximum research value per unit time.

Pipeline:

```text
retrieve all announcement metadata
 -> deduplicate
 -> route by document priority
 -> deep-process Tier A
 -> deep-process Tier B when triggered
 -> lightweight process Tier C
 -> archive Tier D
 -> normalize ownership events
 -> build actor timelines
 -> correlate with corporate actions
 -> rank
```

## 9.2 Full Audit Scan

Goal: maximum recall rather than speed.

```text
retrieve all metadata
 -> download all supported PDFs
 -> extract all PDFs
 -> run all detectors
 -> compare result against Smart Scan
```

The user should not run Full Audit Scan for routine daily screening.

## 9.3 Historical Bootstrap

If required ownership/action history is missing locally:

- retrieve configured historical range;
- prioritize Tier A ownership/capital documents first;
- use existing local data before re-downloading;
- mark incomplete historical context explicitly;
- reduce confidence when the actor history is incomplete.

Default lookback:

- 60 calendar days for general behavior;
- 120 days for slow-moving ownership/corporate-action patterns;
- configurable per signal family.

---

# 10. Core Intelligence Objects

The system should model the following objects separately:

1. **Issuer** — listed company.
2. **Actor** — person/entity appearing in ownership/activity evidence.
3. **Holder** — actor with disclosed holdings.
4. **Relationship** — control/affiliation relationship when explicitly disclosed.
5. **Ownership Snapshot** — state at a point in time.
6. **Ownership Event** — change between states.
7. **Transaction Event** — disclosed acquisition/disposal/subscription/etc.
8. **Corporate Action Event** — formal or developing corporate action.
9. **Signal Event** — normalized analytical observation.
10. **Actor Behavior State** — current interpretation of repeated actor behavior.
11. **Issuer Intelligence State** — aggregate state for an issuer.
12. **Evidence Item** — exact source excerpt and page.
13. **Scan Run** — execution metadata.

---

# 11. Actor Taxonomy

Each actor must have a normalized role where the source permits.

Possible roles:

- controlling shareholder;
- shareholder;
- beneficial owner, when explicitly disclosed;
- director;
- commissioner;
- affiliated party;
- strategic investor;
- institution;
- corporate investor;
- government entity;
- financial institution;
- investment vehicle;
- public investor/unknown;
- nominee/custodian, when explicitly described;
- other disclosed party.

The system must not invent a beneficial-owner relationship merely because two names appear related.

---

# 12. Ownership Intelligence

## 12.1 Ownership snapshot fields

Minimum:

- issuer;
- actor;
- role;
- shares held;
- voting shares if available;
- ownership percentage;
- snapshot date;
- source;
- source document/data version;
- evidence quality.

Optional:

- direct/indirect ownership;
- voting rights;
- pledge status;
- class of shares;
- relationship/control status.

## 12.2 Ownership change fields

Required when disclosed:

- previous shares;
- current shares;
- delta shares;
- previous percentage;
- current percentage;
- delta percentage;
- transaction date;
- reporting date;
- transaction direction;
- transaction type;
- transaction price;
- estimated transaction value;
- source document;
- evidence page.

## 12.3 Ownership event types

Examples:

- ACQUIRE;
- DISPOSE;
- SUBSCRIBE;
- EXERCISE;
- CONVERT;
- TRANSFER;
- INCREASE;
- DECREASE;
- ENTERED_POSITION;
- EXITED_POSITION;
- CROSSED_UP_THRESHOLD;
- CROSSED_DOWN_THRESHOLD;
- CONTROL_CHANGE;
- PLEDGE;
- RELEASE_PLEDGE;
- ADMINISTRATIVE_CHANGE;
- CORPORATE_ACTION_DERIVED.

---

# 13. Transaction Normalization

The extraction engine must normalize synonymous wording.

For example:

```text
membeli / acquisition / acquired / purchase
        -> ACQUIRE

menjual / disposal / disposed / sold
        -> DISPOSE

subscribe / mengambil bagian / memesan saham baru
        -> SUBSCRIBE
```

The original wording remains stored as evidence.

The normalized event must never replace the original document wording.

---

# 14. Cost Basis / Transaction Price Intelligence

Transaction price must be treated as first-class data when explicitly disclosed.

## 14.1 Reported transaction price

Store:

- price per share;
- transaction date;
- quantity;
- source.

## 14.2 Estimated cost basis

If multiple transactions by the same normalized actor are available:

```text
weighted average acquisition price
= sum(quantity_i * price_i) / sum(quantity_i)
```

Only calculate this when:

- quantity is known;
- transaction price is known;
- the events can confidently be attributed to the same actor;
- share class is compatible.

The UI must label the result:

> **Estimated disclosed cost basis**

It must not be represented as the actor's exact total portfolio cost basis unless the data supports that claim.

## 14.3 Current price relationship

Future market-price integration may compare:

```text
current price
vs
estimated disclosed cost basis
```

For MVP, the system may leave market price blank if no approved market-data source is integrated.

---

# 15. Distinguishing Real Positioning From Administrative Change

This is a mandatory anti-false-positive layer.

Ownership changes can arise from:

- corporate actions;
- internal transfers;
- conversion;
- inheritance;
- gifts;
- restructuring;
- settlement;
- nominee/custody mechanics;
- capital changes;
- other non-market mechanisms.

Therefore:

> **ownership increase != accumulation**

The system must classify the event context first.

Possible classifications:

- MARKET_ACQUISITION_CANDIDATE;
- MARKET_DISPOSAL_CANDIDATE;
- CORPORATE_ACTION_EFFECT;
- ADMINISTRATIVE_TRANSFER;
- CONTROL_RESTRUCTURE;
- UNCLEAR;
- INSUFFICIENT_EVIDENCE.

Only the first two may contribute strongly to an accumulation/distribution behavior score.

---

# 16. Strategic Accumulation / Distribution Detection

## 16.1 Accumulation candidate

Potential evidence:

- ownership increases;
- transaction direction is acquisition;
- material quantity;
- repeated acquisition events;
- ownership threshold crossed upward;
- strategic/controlling actor involved;
- acquisition price available;
- subsequent related corporate-action development;
- no strong contradiction.

## 16.2 Distribution candidate

Potential evidence:

- ownership decreases;
- disposition event;
- repeated selling;
- threshold crossed downward;
- strategic holder reduction;
- exit from meaningful ownership range;
- related corporate-action timing.

## 16.3 Behavior labels

The system may assign:

- ACCUMULATION_CANDIDATE;
- DISTRIBUTION_CANDIDATE;
- STRATEGIC_POSITIONING_CANDIDATE;
- EXIT_CANDIDATE;
- OWNERSHIP_REBALANCING;
- ADMINISTRATIVE_CHANGE;
- MIXED;
- INSUFFICIENT_EVIDENCE.

These are analytical labels, not accusations or facts about intent.

---

# 17. Repeated-Actor Behavior

One transaction is weak evidence.

Repeated behavior should become a first-class signal.

Example:

```text
01 Sep: acquire
05 Sep: acquire
09 Sep: acquire
15 Sep: ownership crosses 5%
```

The engine should create one behavior cluster:

> **Repeated acquisition sequence**

rather than four unrelated events.

The cluster should store:

- first event;
- last event;
- number of events;
- total shares acquired;
- weighted transaction price if possible;
- ownership change;
- duration;
- source evidence count;
- independent evidence count.

---

# 18. Ownership Thresholds

The engine should monitor thresholds without assuming they are inherently positive or negative.

Default analytical thresholds:

- 1%;
- 3%;
- 5%;
- 10%;
- 20%;
- controlling threshold where applicable;
- 50%+ where relevant.

These are analytical bands.

Regulatory reporting requirements must be represented separately from analytical thresholds.

The system must not hard-code legal conclusions into the scoring engine.

---

# 19. Public Ownership Snapshot Integration

KSEI/BEI monthly >1% ownership information becomes an important **structural context layer**.

Purpose:

- identify meaningful holders;
- establish ownership concentration;
- detect emergence/disappearance from the public snapshot;
- compare monthly structural state with event-level disclosures;
- improve historical actor mapping;
- identify potential strategic holders earlier than a 5% only model.

The monthly snapshot must be timestamped and treated as:

> **STATE DATA**

not:

> **REAL-TIME TRANSACTION DATA**.

The system should show the source date clearly.

---

# 20. Holder Identity Resolution

Identity normalization is critical.

Examples of normalization problems:

```text
PT ABC INVESTAMA
PT ABC Investama
PT. ABC Investama
ABC INVESTAMA PT
```

These may be the same entity.

Required approach:

1. normalize casing;
2. normalize punctuation;
3. normalize legal-entity suffixes carefully;
4. preserve original name;
5. create canonical actor key;
6. maintain aliases;
7. never merge two entities solely on similar names without sufficient evidence.

## 20.1 Entity confidence

Each merge should have:

- EXACT;
- HIGH_CONFIDENCE;
- MEDIUM_CONFIDENCE;
- LOW_CONFIDENCE;
- UNRESOLVED.

Low-confidence matches must not heavily influence Smart Money scores.

---

# 21. Relationship / Affiliation Layer

The system may connect actors when explicit evidence exists:

```text
Actor A
  |
  +-- controls --> Company B
  |
  +-- affiliated with --> Actor C
```

However, the system must not infer a corporate group merely from:

- similar names;
- same address;
- same broker;
- same industry;
- same director name;
- internet speculation.

Relationship sources must always be shown.

---

# 22. Corporate Action Intelligence

Corporate action detection remains mandatory but becomes a parallel intelligence layer.

Target families:

1. Right Issue / HMETD
2. Private Placement / PMTHMETD
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
16. Tender Offer
17. Material Capital Restructuring
18. Other strategic transaction

Each action family retains:

- explicit terms;
- precursor terms;
- lifecycle states;
- positive context;
- negative/distress context;
- negation;
- uncertainty;
- cancellation;
- supersession.

---

# 23. Corporate Action Lifecycle

Default state machine:

```text
NO_SIGNAL
    |
    v
EARLY
    |
    v
DEVELOPING
    |
    v
EXPLICIT
    |
    v
EXECUTING
    |
    v
COMPLETED
```

Alternative terminal/context states:

- CONTRADICTED;
- CANCELLED;
- EXPIRED;
- SUPERSEDED.

Historical evidence must remain visible.

---

# 24. Ownership Lifecycle

Ownership behavior should have its own state machine:

```text
NO_POSITION
   |
   v
INITIAL_ENTRY
   |
   v
ACCUMULATION_CANDIDATE
   |
   v
STRATEGIC_POSITIONING_CANDIDATE
   |
   +------------------+
   |                  |
   v                  v
HOLDING              DISTRIBUTION_CANDIDATE
   |                  |
   +--------+---------+
            |
            v
          EXIT
```

This is an analytical lifecycle, not a legal ownership state.

---

# 25. Cross-Signal Intelligence

This is the core of Version 7.0.

The system must connect:

```text
OWNERSHIP EVENT
      +
ACTOR BEHAVIOR
      +
CORPORATE ACTION
      +
ISSUER DISCLOSURE
      +
TEMPORAL SEQUENCE
      +
OPTIONAL MARKET CONFIRMATION
```

## 25.1 Example

```text
T-30
Strategic holder appears / increases ownership

T-21
Funding need disclosed

T-14
RUPSLB with capital agenda

T-7
Ownership increases again

T-3
Capital structure changes

T
HMETD explicitly disclosed
```

The system should not simply produce six cards.

It should build:

> **Strategic positioning + developing capital-raising sequence**

and display the evidence timeline.

---

# 26. Smart Money Signal Model

The system uses an explainable score to rank signals.

It must not call the score a probability.

Suggested components:

```text
Smart Money Priority Score (0–100)
=
Ownership Evidence
+ Actor Significance
+ Size / Materiality
+ Repetition
+ Cost-Basis Evidence
+ Timing / Recency
+ Corporate-Action Alignment
+ Lifecycle Advancement
+ Independent Corroboration
+ Novelty
- Administrative-Change Penalty
- Contradiction Penalty
- Distress Penalty
- Evidence-Quality Penalty
```

The exact weights must be configuration-driven and versioned.

## 26.1 Suggested conceptual weights

Do not hard-code these numbers in business logic; place them in a config file.

```text
ownership_change_strength       20
actor_significance              10
transaction_size                10
repeat_behavior                 10
cost_basis_quality               8
recency                          8
corporate_action_alignment      12
lifecycle_advancement            7
independent_corroboration        8
novelty                           7
penalties                        -20 max combined or rule-based
```

The final score must remain explainable.

## 26.2 Priority bands

```text
80–100  VERY HIGH PRIORITY
65–79   HIGH PRIORITY
50–64   MEDIUM PRIORITY
30–49   LOW PRIORITY
0–29    WATCH / INSUFFICIENT
```

These are prioritization categories, not probabilities.

---

# 27. Evidence Quality Score

Separate evidence quality from signal strength.

Evidence quality factors:

- primary official source;
- exact document;
- exact page;
- explicit numbers;
- explicit transaction direction;
- explicit actor;
- explicit price;
- multiple independent documents;
- current/recent date.

Lower-quality evidence:

- indirect wording;
- incomplete PDF;
- inferred actor identity;
- stale ownership snapshot;
- extraction uncertainty;
- single weak precursor.

---

# 28. Smart Money Signal Classification

The UI should present three layers:

### Facts

Example:

> Holder X increased ownership from 4.81% to 7.06%.

### Behavior interpretation

> Strategic accumulation candidate.

### Confidence

> High confidence in the ownership change; medium confidence in the strategic-accumulation interpretation.

This separation is mandatory.

---

# 29. Corporate Action + Ownership Correlation Rules

Examples of positive correlation:

### Pattern A — Strategic positioning before capital action

```text
ownership increase
+
capital/funding discussion
+
RUPSLB/capital agenda
+
subsequent HMETD/placement
```

Classify as:

> **High-priority developing strategic positioning candidate**

### Pattern B — New strategic holder before expansion

```text
new strategic holder
+
large capital entry
+
expansion plan
```

Potential classification:

> Strategic investment / capital deployment alignment.

### Pattern C — Large holder reducing before catalyst

```text
holder reduces position
+
corporate action later becomes explicit
```

Do not automatically call this bearish.

Classify as:

> Distribution candidate requiring context.

### Pattern D — Ownership rise caused by corporate action

```text
ownership increase
+
new shares issued
+
no evidence of open-market acquisition
```

Apply administrative/corporate-action penalty.

Do not call it stealth accumulation.

---

# 30. Early Detection Engine

The early-detection architecture from v5.x is preserved, but expanded.

Two parallel layers:

```text
DOCUMENT LEVEL
PDF
 -> actor extraction
 -> ownership extraction
 -> action extraction
 -> context
 -> evidence

ISSUER LEVEL
multiple documents
 -> actor timeline
 -> ownership changes
 -> action timeline
 -> novelty
 -> corroboration
 -> contradiction
 -> state transition
 -> smart-money ranking
```

---

# 31. Novelty / Change Detection

The engine must identify:

- ROUTINE;
- NEW_ACTOR;
- NEW_POSITION;
- OWNERSHIP_INCREASE;
- OWNERSHIP_DECREASE;
- THRESHOLD_CROSSING;
- MATERIAL_CHANGE;
- STATE_ADVANCEMENT;
- CONFIRMATION;
- REVERSAL;
- EXIT;
- CONTRADICTION.

Example:

Previous:

> No strategic holder above 1% identified in local history.

New:

> Holder A appears at 3.4% in public ownership snapshot.

Result:

> NEW_ACTOR / NEW_POSITION.

---

# 32. Corroboration Logic

Confidence increases when independent evidence types converge.

Strong corroboration examples:

- event-level ownership disclosure;
- monthly ownership snapshot;
- separate strategic transaction disclosure;
- subsequent corporate-action disclosure;
- repeated transactions by the same normalized actor.

Repeated copies of the same disclosure do not count as independent corroboration.

---

# 33. Contradiction / Cancellation / Supersession

Later authoritative information must be able to reduce earlier signals.

Examples:

```text
EARLY strategic acquisition
        |
        v
DEVELOPING
        |
        v
negotiations terminated
        |
        v
CANCELLED / CONTRADICTED
```

Similarly:

```text
funding discussion
   -> new financing secured
```

The second event should not necessarily increase a capital-raising signal; it may indicate that the earlier uncertainty has been resolved through another mechanism.

---

# 34. Negative / Distress Context

The engine must distinguish accumulation-like activity from financially distressed behavior.

Potential distress indicators:

- emergency liquidity requirement;
- forced disposal;
- debt restructuring;
- covenant breach;
- asset sale to meet obligations;
- capital raising primarily for survival.

A capital raise is therefore **not automatically positive**.

Likewise:

> ownership increase is not automatically bullish.

Impact classification remains separate from behavior classification.

---

# 35. Information Importance

Every processed disclosure receives:

- HIGH;
- MEDIUM;
- LOW;
- NO MATERIAL SIGNAL.

High importance examples:

- ownership change;
- control change;
- strategic investor;
- large acquisition/disposal;
- capital raising;
- buyback;
- major contract;
- material restructuring.

Importance is not identical to positive impact.

---

# 36. Impact Classification

Possible values:

- POSITIVE;
- NEUTRAL;
- NEGATIVE;
- MIXED;
- UNCLEAR;
- NO_SIGNAL.

Important:

> POSITIVE does not mean “the share price will rise.”

It means the disclosed information appears potentially favorable based on the information available.

---

# 37. Dashboard UX

The dashboard should no longer lead with “Corporate Actions.”

It should lead with **Smart Money / Ownership Signals**.

Recommended structure:

```text
========================================================
IDX SMART MONEY & OWNERSHIP INTELLIGENCE

Scan Range: [ Today v ]
Mode:       [ Smart Scan v ]
Lookback:   [ 60 days ]

[ RUN SCREENING ]
========================================================

VERY HIGH PRIORITY

BRMS
Strategic Positioning Candidate
Ownership: +X shares
Actor: Strategic Holder
Action Alignment: Capital Raising
Stage: DEVELOPING
Confidence: HIGH

--------------------------------------------------------

HIGH PRIORITY

XYZ
Repeated Accumulation Candidate
Ownership: 2.1% -> 4.3%
Transactions: 4
Cost Basis: RpX
Corporate Action: Strategic Investment

========================================================

OTHER IMPORTANT INFORMATION
...
```

---

# 38. Result Card

Every high-priority result should show:

- ticker;
- issuer;
- actor;
- behavior label;
- ownership before/after;
- shares delta;
- reported price if available;
- estimated disclosed cost basis if available;
- related corporate action;
- lifecycle stage;
- priority;
- confidence;
- evidence count.

---

# 39. Result Detail Page

Required sections:

## A. Executive summary

One sentence describing the signal.

## B. Facts

Exact normalized facts.

## C. Actor

Name, role, ownership, aliases, relationship evidence.

## D. Ownership history

Chronological table.

## E. Transaction history

Chronological transactions.

## F. Cost-basis information

Only where disclosed and calculable.

## G. Corporate-action linkage

Related action family and lifecycle.

## H. What changed

Difference vs previous state.

## I. Why flagged

Deterministic explanation.

## J. Evidence

Document, page, excerpt.

## K. Timeline

All supporting events.

## L. Original documents

Open source PDF/document.

---

# 40. Timeline UX

The timeline is mandatory because behavior is temporal.

Example:

```text
15 Aug
Funding requirement disclosed

21 Aug
RUPSLB capital agenda

24 Aug
Holder A +120m shares

28 Aug
Holder A +180m shares

30 Aug
Ownership crosses 5%

01 Sep
New share issuance disclosed

STATUS:
DEVELOPING STRATEGIC POSITIONING
```

---

# 41. Document Evidence UX

Each signal must allow the user to inspect:

- original document;
- page number;
- exact excerpt;
- document publication date;
- event date, if different;
- extraction status;
- source URL.

Evidence must remain visible even if the interpretation later changes.

---

# 42. Scan Processing UX

During scanning:

```text
Retrieving IDX announcements      ✓
Classifying document priority      ✓
Downloading Tier A PDFs            ✓
Downloading triggered Tier B PDFs  ✓
Extracting documents               72%
Building ownership events          ...
Correlating signals                ...
Ranking issuers                    ...
```

After completion:

- announcements retrieved;
- Tier A documents;
- Tier B documents;
- Tier C metadata-only;
- PDFs downloaded;
- extraction successes;
- OCR-required;
- failed documents;
- ownership events found;
- strategic-positioning candidates;
- corporate-action signals;
- high-priority issuers.

This avoids confusing “no signal” with “not processed.”

---

# 43. Data Model

## 43.1 companies

```text
id
 ticker
 name
 sector
 status
 created_at
 updated_at
```

## 43.2 actors

```text
id
 canonical_name
 actor_type
 normalized_key
 confidence
 created_at
 updated_at
```

## 43.3 actor_aliases

```text
id
 actor_id
 alias
 source
 confidence
```

## 43.4 actor_relationships

```text
id
 actor_id
 related_actor_id
 relationship_type
 source_document_id
 confidence
```

## 43.5 announcements

```text
id
 company_id
 source_announcement_id
 title
 category
 published_at
 source_url
 normalized_url
 processing_state
```

## 43.6 documents

```text
id
 announcement_id
 pdf_url
 local_path
 sha256
 document_priority
 acquisition_status
 extraction_status
 processed_at
```

## 43.7 document_pages

```text
id
 document_id
 page_number
 extracted_text
```

## 43.8 ownership_snapshots

```text
id
 company_id
 actor_id
 snapshot_date
 shares
 ownership_pct
 voting_pct
 source_type
 source_document_id
 evidence_quality
```

## 43.9 ownership_events

```text
id
 company_id
 actor_id
 event_date
 event_type
 shares_before
 shares_after
 delta_shares
 pct_before
 pct_after
 delta_pct
 transaction_price
 estimated_value
 source_document_id
 context_classification
 confidence
```

## 43.10 transaction_events

```text
id
 company_id
 actor_id
 event_date
 direction
 transaction_type
 quantity
 price
 estimated_value
 source_document_id
 evidence_id
```

## 43.11 corporate_action_events

```text
id
 company_id
 action_type
 event_date
 lifecycle_stage
 impact
 confidence
 source_document_id
```

## 43.12 evidence

```text
id
 source_document_id
 page_number
 excerpt
 evidence_type
 extraction_confidence
```

## 43.13 signal_events

```text
id
 company_id
 actor_id nullable
 signal_type
 event_date
 contribution
 confidence
 source_document_id
```

## 43.14 actor_behavior_states

```text
id
 company_id
 actor_id
 behavior_type
 current_stage
 priority
 confidence
 first_signal_at
 last_signal_at
 state_status
```

## 43.15 issuer_intelligence_states

```text
id
 company_id
 smart_money_score
 ownership_score
 corporate_action_score
 overall_priority
 current_summary
 updated_at
```

## 43.16 scans

```text
id
 started_at
 completed_at
 scan_from
 scan_to
 lookback_days
 scan_mode
 status
 announcements_found
 documents_downloaded
 ownership_events_found
 signals_found
```

## 43.17 rule_versions

```text
id
 rule_family
 version
 config_hash
 effective_from
 created_at
```

---

# 44. Recommended Indexes

Create indexes on:

```text
announcements(source_announcement_id)
documents(sha256)
documents(announcement_id)
ownership_events(company_id, actor_id, event_date)
ownership_snapshots(company_id, actor_id, snapshot_date)
transaction_events(company_id, actor_id, event_date)
corporate_action_events(company_id, action_type, event_date)
signal_events(company_id, event_date)
actor_relationships(actor_id)
```

---

# 45. API Contract

## POST /api/screen

Request:

```json
{
  "date_from": "2026-09-15",
  "date_to": "2026-09-15",
  "lookback_days": 60,
  "mode": "smart"
}
```

Response:

```json
{
  "scan_id": "...",
  "status": "completed",
  "announcements_found": 120,
  "tier_a_documents": 18,
  "tier_b_documents": 27,
  "tier_c_metadata_only": 75,
  "documents_processed": 45,
  "ownership_events": 14,
  "high_priority_signals": 5
}
```

## GET /api/signals

Filters:

- priority;
- behavior;
- action_type;
- stage;
- impact;
- ticker;
- actor;
- date range.

## GET /api/signals/{id}

Returns:

- signal;
- actor;
- ownership;
- transactions;
- corporate-action linkage;
- timeline;
- evidence.

## GET /api/actors/{id}

Returns:

- normalized identity;
- aliases;
- roles;
- issuer relationships;
- historical ownership events;
- behavior clusters.

## GET /api/companies/{ticker}/intelligence

Returns issuer-level intelligence state.

## GET /api/documents/{id}

Returns document metadata, source URL, local path, extraction status, and evidence.

## GET /api/scans/{id}

Returns scan progress and completeness metrics.

---

# 46. Screening Algorithm — Smart Scan

```text
1. Retrieve all IDX announcement metadata for selected range.
2. Deduplicate announcements/documents.
3. Normalize issuer metadata.
4. Assign document priority.
5. Deep-process Tier A documents.
6. Lightweight-process Tier B metadata/title/category.
7. Escalate Tier B documents when trigger rules fire.
8. Process Tier C metadata/lightweight signals.
9. Store Tier D as known/archived.
10. Download selected PDFs.
11. Extract page-aware text.
12. Normalize text.
13. Extract actors.
14. Extract ownership facts.
15. Extract transaction facts.
16. Extract corporate-action facts.
17. Apply context/negation/uncertainty rules.
18. Normalize events.
19. Compare with historical issuer/actor state.
20. Detect novelty and state changes.
21. Cluster repeated transactions.
22. Calculate disclosed cost basis where possible.
23. Detect accumulation/distribution candidates.
24. Build corporate-action lifecycle state.
25. Correlate ownership and corporate-action signals.
26. Apply administrative-change penalties.
27. Apply contradiction/cancellation/expiry logic.
28. Calculate evidence quality.
29. Calculate Smart Money Priority Score.
30. Rank issuer/action/actor signals.
31. Persist progressively.
32. Show results with exact evidence.
```

---

# 47. Full Audit Algorithm

Full Audit Scan uses the same analytical engine but changes document acquisition:

```text
all metadata
 -> all supported PDFs
 -> full extraction
 -> all rules
 -> compare against Smart Scan
```

The analytical rules must not be different between modes.

Only document coverage changes.

This prevents the system from producing different interpretations merely because the scan mode changed.

---

# 48. Rule Engine Architecture

Rules must live outside frontend code.

Recommended structure:

```text
rules/
  ownership/
    transaction_direction.yaml
    threshold.yaml
    administrative_change.yaml
    actor_significance.yaml
  corporate_action/
    hmetd.yaml
    placement.yaml
    acquisition.yaml
    buyback.yaml
    control_change.yaml
  behavior/
    accumulation.yaml
    distribution.yaml
    strategic_positioning.yaml
  scoring/
    smart_money_score.yaml
    evidence_quality.yaml
```

Rules must have:

- version;
- description;
- trigger;
- positive evidence;
- negative evidence;
- exclusion;
- test cases.

---

# 49. Keyword Strategy

Keywords are only triggers, not conclusions.

The engine should use three levels:

### Level 1 — lexical trigger

Example:

```text
kepemilikan
perubahan kepemilikan
membeli
menjual
menambah
mengurangi
pengendali
investor strategis
akuisisi
HMETD
PMTHMETD
```

### Level 2 — contextual trigger

The surrounding sentence/paragraph must contain relevant actors, quantities, dates, or transaction language.

### Level 3 — structured event extraction

Convert evidence into normalized facts.

Final signals should never be generated from keyword hit count alone.

---

# 50. Negation and Uncertainty

The engine must recognize patterns such as:

- tidak memiliki;
- tidak berencana;
- tidak akan melakukan;
- belum terdapat rencana;
- masih dalam kajian;
- kemungkinan;
- rencana awal;
- sedang mempertimbangkan;
- dibatalkan;
- dihentikan;
- tidak dilanjutkan.

English equivalents should also be recognized.

Uncertainty should reduce confidence, not always suppress the signal.

Example:

> “Perseroan sedang mengevaluasi kemungkinan akuisisi.”

Result:

> Acquisition — EARLY — Unconfirmed.

Not:

> Acquisition — EXPLICIT.

---

# 51. Cost-Basis and Price Rules

The system should distinguish:

1. reported transaction price;
2. weighted average disclosed transaction price;
3. estimated disclosed cost basis;
4. current market price, only when available from a validated source.

Never label any of these as “average purchase price” unless the exact definition is clear.

Preferred UI wording:

> **Weighted average disclosed acquisition price**

rather than:

> **True bandar average price**

---

# 52. Market Confirmation — Future Layer

When a validated market-data source is added, the system may use:

- current price;
- volume;
- turnover;
- price trend;
- volatility;
- relative volume.

These must remain **confirmation layers**, not substitutes for ownership evidence.

Future architecture:

```text
Ownership Intelligence
       +
Corporate Action Intelligence
       +
Market Behavior
       +
Broker Flow
       +
Foreign Flow
       =
Composite Smart Money Intelligence
```

---

# 53. Relationship With Broker Flow

Broker flow is intentionally not required for this PRD's MVP.

When integrated later, it should answer a different question:

> **Which brokers are participating in the market activity?**

Ownership intelligence answers:

> **Which disclosed actors changed their economic/ownership position?**

The two must not be conflated.

A broker is an execution channel; an identified shareholder is an ownership actor.

---

# 54. Relationship With Foreign Flow

Foreign-flow data can later strengthen timing/context but must not override issuer/ownership evidence.

Possible future convergence:

```text
strategic holder increase
+
foreign net buying
+
repeated large broker participation
+
related corporate action
```

This would create a high-confidence multi-layer signal.

---

# 55. Research Output Philosophy

The system should produce **research candidates**, not trading signals.

Good output:

> BRMS — High Priority — Strategic Positioning Candidate
>
> Holder A increased disclosed ownership by X shares over three events. A capital-raising sequence is simultaneously advancing from Early to Developing. Reported acquisition price is RpX. Evidence: three independent disclosures.

Bad output:

> BRMS — BUY — Bandar masuk.

---

# 56. Ranking Logic

Priority should combine:

```text
Actor evidence
+ ownership magnitude
+ repeated behavior
+ transaction evidence
+ cost-basis evidence
+ novelty
+ recency
+ corporate-action alignment
+ independent corroboration
+ lifecycle advancement
- administrative explanation
- contradiction
- distress
- weak extraction
```

Priority hierarchy for research:

```text
VERY HIGH
strategic positioning + multiple independent evidence + developing action

HIGH
repeated ownership accumulation + meaningful actor + relevant action

MEDIUM
single meaningful ownership event or early corporate-action signal

LOW
weak precursor / incomplete context

WATCH
metadata-only or insufficient evidence
```

---

# 57. Do Not Use Pseudo-Precision

The UI must not display:

> “Bandar probability 87.43%.”

Unless a validated statistical model is introduced later, use:

- High;
- Medium;
- Low;
- Very High Priority;
- High Priority;
- Watch.

Scores are ranking tools, not probabilities.

---

# 58. Backtesting / Historical Validation

Backtesting is not a user-facing MVP feature but is mandatory for engineering validation.

## 58.1 Test corpus

Create historical sets for:

- known HMETD/right issues;
- private placements;
- acquisitions;
- change of control;
- strategic investment;
- buyback;
- meaningful ownership accumulation;
- meaningful shareholder exits.

## 58.2 Evaluation windows

At minimum:

- T-120;
- T-90;
- T-60;
- T-30;
- T-14;
- T-7;
- T-1;
- T+1;
- T+7.

## 58.3 Metrics

Measure:

- lead time;
- signal precision;
- false-positive rate;
- false-negative rate;
- Smart Scan recall vs Full Audit;
- percentage of signals supported by primary evidence;
- administrative-change false positives;
- actor-normalization error rate;
- cost-basis calculation correctness;
- PDF processing success rate.

The project must not claim the detector “works” statistically until it has been measured against a defined historical set.

---

# 59. Critical Validation Test Cases

Every rule family must contain at least:

### Case A — Valid acquisition

Actor buys disclosed shares.

Expected:

> ACQUIRE + ownership increase.

### Case B — Valid disposal

Actor sells disclosed shares.

Expected:

> DISPOSE + ownership decrease.

### Case C — Administrative transfer

Shares change due to a disclosed transfer mechanism unrelated to open-market buying.

Expected:

> ADMINISTRATIVE_CHANGE or equivalent penalty.

### Case D — Corporate-action-driven increase

Ownership rises because new shares are issued.

Expected:

> CORPORATE_ACTION_EFFECT; no strong accumulation score.

### Case E — Repeated accumulation

Multiple acquisition events by one actor.

Expected:

> ACCUMULATION_CANDIDATE with higher priority.

### Case F — New strategic holder

A new actor appears in ownership data and event evidence.

Expected:

> NEW_ACTOR + STRATEGIC_POSITIONING candidate if context supports.

### Case G — Explicit action

HMETD explicitly disclosed.

Expected:

> EXPLICIT corporate action.

### Case H — Early action

Funding need + capital agenda + related new-share discussion.

Expected:

> EARLY/DEVELOPING, not Explicit.

### Case I — Cancellation

Later disclosure cancels plan.

Expected:

> CANCELLED/CONTRADICTED and active score reduced.

### Case J — OCR failure

Scanned PDF has no usable text.

Expected:

> OCR_REQUIRED, never No Signal.

---

# 60. Error Handling

The system must distinguish:

- IDX retrieval failure;
- rate/transport failure;
- missing attachment;
- unsupported attachment;
- PDF download failure;
- invalid PDF;
- extraction failure;
- OCR required;
- partial extraction;
- actor parsing failure;
- ownership parsing ambiguity;
- unresolved actor identity;
- insufficient historical context.

A technical failure must never silently become:

> NO SIGNAL.

---

# 61. Data Completeness Indicators

Every scan must show:

```text
Metadata retrieved            100%
Tier A processing              100%
Tier B triggered processing     94%
PDF extraction                  91%
Actor extraction                89%
Ownership extraction            86%
Historical context              COMPLETE / PARTIAL
```

The user must know whether the absence of a signal is because:

1. no signal exists; or
2. the relevant information was not processed successfully.

---

# 62. Performance Requirements

For routine Smart Scan:

- metadata acquisition should be the fastest stage;
- PDF work should be limited by document priority;
- documents should process independently;
- one broken PDF must never abort the scan;
- results should persist progressively;
- repeated PDFs should never be reprocessed unnecessarily.

Primary optimization principle:

> **Filter for intelligence value before doing expensive PDF work.**

---

# 63. Caching / Deduplication

Use:

1. stable announcement/document ID;
2. normalized source URL;
3. SHA-256 content hash.

A document known locally should not be downloaded again unless:

- source URL changed;
- content hash changed;
- processing rule version requires reprocessing;
- user explicitly requests reprocessing.

Rule-version changes must not require redownloading unchanged PDFs.

---

# 64. Rule Versioning

Every analysis result must retain:

- rule-library version;
- score configuration version;
- extraction version;
- actor-normalization version.

This makes results reproducible.

---

# 65. Technical Stack

## Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- TanStack Query

## Backend

- Python 3.13+
- FastAPI
- Uvicorn
- Pydantic
- SQLModel
- httpx

## IDX acquisition

- `nichsedge/idx-bei` as acquisition layer where verified operationally.

## PDF

- PyMuPDF primary parser
- OCR fallback architecture

## Database

- SQLite

## Tooling

- uv
- Ruff
- Pytest

## Optional

- Docker for reproducible local environment

Not required for MVP:

- PostgreSQL;
- Redis;
- Celery/RabbitMQ;
- Neo4j;
- LLM API dependency.

---

# 66. Security / Local Data Handling

- local application by default;
- no authentication in MVP;
- no public exposure by default;
- sanitize filenames;
- prevent path traversal;
- validate remote document URLs;
- do not execute downloaded document content;
- retain source URLs;
- store documents under a controlled local directory.

---

# 67. Scheduler Readiness

No scheduler in MVP.

However, the scanning pipeline must be callable as a single service:

```text
run_screening(date_from, date_to, mode, lookback_days)
```

A future scheduler should simply call the same service.

The scheduler must not require any changes to the intelligence engine.

---

# 68. Development Phases

## Phase 1 — Foundation migration

- rename/restructure product modules;
- retain v5.1 ingestion infrastructure;
- add actors;
- add ownership snapshots/events;
- add transaction model;
- add document-priority router.

## Phase 2 — Ownership extraction

- ownership rules;
- transaction direction;
- before/after ownership;
- quantity;
- price;
- actor normalization;
- evidence extraction.

## Phase 3 — Behavior engine

- repeated acquisition;
- repeated disposal;
- threshold crossings;
- new strategic holder;
- accumulation/distribution candidate;
- administrative-change suppression.

## Phase 4 — Corporate-action integration

- reuse v5.x action taxonomy;
- lifecycle engine;
- early/developing/explicit;
- contradiction/cancellation.

## Phase 5 — Cross-signal engine

- ownership + corporate action;
- actor + action;
- temporal alignment;
- corroboration;
- priority score.

## Phase 6 — Dashboard redesign

- Smart Money home screen;
- actor detail;
- ownership timeline;
- issuer intelligence page;
- evidence-first UX.

## Phase 7 — Validation

- historical corpus;
- Smart vs Full Audit recall comparison;
- false-positive tuning;
- actor-normalization validation.

---

# 69. MVP Acceptance Criteria

## Manual operation

- User selects scan range.
- User selects Smart Scan or Full Audit.
- User clicks Run Screening once.
- Complete pipeline runs without additional manual intervention.
- No scheduler is required.

## Data ingestion

- All announcement metadata within the selected range is retrieved.
- New/unprocessed announcements are identified.
- Documents are routed by priority.
- Tier A documents are deep processed.
- Triggered Tier B documents are deep processed.
- Smart Scan records which documents were not deeply processed.
- Full Audit can deep-process the complete supported set.

## Ownership intelligence

- Actor identities can be normalized.
- Ownership events can be extracted where disclosed.
- Previous/current ownership can be stored.
- Delta shares and percentage can be calculated.
- Transaction direction can be classified.
- Transaction price can be stored where disclosed.
- Evidence page/excerpt is retained.

## Behavior intelligence

- Repeated acquisition events can be grouped.
- Repeated disposal events can be grouped.
- Threshold crossings can be detected.
- New holder emergence can be detected.
- Administrative changes are penalized.
- Accumulation/distribution candidates are explainable.

## Corporate action intelligence

- Existing action families remain functional.
- Early/Developing/Explicit lifecycle works.
- Cancellation/supersession works.
- Corporate action is correlated with ownership evidence.

## Ranking

- Smart Money Priority Score is deterministic.
- Score components are visible.
- Priority ranking is explainable.
- No fabricated probability is shown.

## Evidence

- Every high-priority signal has source document, page and excerpt.
- Original PDF can be opened.
- Actor/issuer timeline is visible.
- Facts and interpretation are separated.

## Reliability

- PDF failure does not abort the scan.
- Extraction failure does not become No Signal.
- Partial historical context reduces confidence.
- Results persist progressively.

---

# 70. Definition of Success

The product succeeds when the user can perform this workflow quickly:

```text
RUN SCREENING
      |
      v
SEE 5–20 HIGH-VALUE CANDIDATES
      |
      v
UNDERSTAND WHO IS MOVING
      |
      v
SEE WHAT CHANGED
      |
      v
SEE HOW MUCH / AT WHAT PRICE
      |
      v
SEE RELATED CORPORATE ACTION
      |
      v
VERIFY ORIGINAL DOCUMENT
```

The product should not aim to produce the largest number of alerts.

It should aim to produce the **smallest useful set of evidence-backed candidates**.

---

# 71. Final Product Principle

> **Find the actor early. Connect the behavior. Measure the change. Follow the sequence. Corroborate with corporate actions. Show the evidence. Never confuse inference with fact.**

The product is not a “bandar detector.”

It is an **evidence-driven Smart Money / Ownership Intelligence Engine** that transforms scattered IDX and ownership disclosures into a structured picture of:

```text
WHO
  -> DID WHAT
      -> HOW MUCH
          -> AT WHAT PRICE
              -> WHEN
                  -> REPEATED HOW OFTEN
                      -> WHAT CHANGED NEXT
                          -> WHAT CORPORATE ACTION CONNECTS
                              -> HOW STRONG IS THE EVIDENCE
```

---

# 72. Migration Checklist From PRD v5.1

### Keep

- IDX ingestion foundation;
- local architecture;
- one-click screening;
- historical lookback;
- PDF extraction;
- evidence layer;
- action lifecycle;
- novelty detection;
- corroboration;
- contradiction/cancellation;
- backtesting;
- FastAPI + React + SQLite.

### Refactor

- dashboard center from Corporate Action to Smart Money;
- document pipeline into priority tiers;
- signal model into actor/behavior events;
- result ranking into Smart Money Priority;
- data model to include actors and ownership.

### Add

- actor entity;
- ownership snapshots;
- ownership events;
- transaction events;
- cost basis;
- actor aliases;
- actor relationships;
- behavior states;
- Smart Money Score;
- public >1% ownership snapshot layer;
- administrative-change classification;
- Smart Scan vs Full Audit;
- cross-layer correlation.

### Do not add in MVP

- real-time trading;
- broker execution;
- mandatory LLM;
- heavy graph database;
- automatic scheduler;
- notifications;
- private/authenticated investor data.

---


# 77. Current Regulatory / Data-Source Notes

The developer must verify live endpoints and actual document schemas before implementation.

Current official transparency references:

- OJK Regulation No. 4 of 2024 governs reports of ownership or changes in ownership of public companies and share-pledging activity. OJK identifies directors/commissioners with voting shares, holders of at least 5% of voting shares, and controllers among parties subject to the ownership reporting framework. citeturn196528search0turn196528search25
- OJK, IDX and KSEI announced in 2026 that listed-company shareholding data above 1% is made public on a monthly basis; the same reform package includes High Shareholding Concentration (HSC), more granular investor classifications, and beneficial-owner information availability for holders at or above 10% subject to the applicable framework. citeturn721946search0turn721946search12
- OJK described HSC disclosure as an early-warning mechanism for ownership concentration / limited liquidity. citeturn721946search2turn721946search5

Implementation meaning:

```text
>1% monthly ownership data
    = structural context

Ownership-change disclosures
    = event-level evidence

Corporate-action disclosures
    = lifecycle evidence

Issuer/actor history
    = temporal context

Cross-signal alignment
    = research priority
```

The system must not represent monthly >1% data as a real-time view of every market participant.

# 78. V7 Final Product Principle

> **Find the actor early. Measure the position change. Follow the sequence. Detect transformation. Connect capital actions. Estimate lead time. Verify the evidence.**

The system should help the user investigate this chain:

```text
WHO
  ↓
WHAT CHANGED
  ↓
HOW MUCH
  ↓
AT WHAT PRICE
  ↓
WHEN
  ↓
REPEATED?
  ↓
WHAT IS THE ISSUER PREPARING?
  ↓
IS THE BUSINESS / ASSET / CONTROL STRUCTURE CHANGING?
  ↓
IS THERE A CORPORATE-ACTION MECHANISM?
  ↓
DO THE SIGNALS ALIGN?
  ↓
HOW EARLY WAS THE FIRST PUBLIC EVIDENCE?
```

The desired output is not a buy signal. It is:

> **A concise, evidence-backed shortlist of issuers where observable strategic positioning and/or corporate transformation may be developing before a major corporate action becomes fully explicit.**

# 79. V7 Final Architecture Decision

Version 7.0 is the target architecture for the next development cycle.

The product is no longer:

> “Corporate Action Screener with ownership features.”

It is:

> **IDX Strategic Ownership, Smart Money & Corporate Transformation Intelligence Engine**

with four principal research engines:

```text
1. Strategic Actor / Ownership Engine
2. Corporate Transformation / Asset Engine
3. Corporate Action Early-Detection Engine
4. Cross-Signal / Lead-Time Engine
```

The highest-priority candidates are those where:

```text
Strategic Positioning
        +
Transformation / Value Catalyst
        +
Corporate-Action Preparation
        +
Temporal Alignment
        +
Strong Evidence
```

all converge.

The system must remain evidence-first, explainable, deterministic, local, and manual one-click in MVP.
