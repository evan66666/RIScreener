# PRD PATCH — IDX Smart Money, Ownership & Corporate Transformation Intelligence

**Patch Version:** 7.3  
**Base Version:** v7.2  
**Patch Type:** Incremental implementation update only  
**Status:** Required addition to existing v7.2 implementation  
**Scope:** Corporate Action Quality, Strategic Attractiveness, Shareholder Value Assessment

> **Important:** This is a patch, not a replacement PRD. Do not rewrite modules already implemented in v7.0–v7.2. Add only the requirements below.

---

# 1. Purpose of This Patch

The existing v7.2 system can identify ownership changes, strategic positioning, corporate-action preparation, transformation signals, convergence, and lead-time candidates.

However, the system must now answer a separate question:

> **“If this corporate action occurs, does the disclosed structure appear economically attractive or harmful to existing shareholders?”**

The system must therefore separate:

1. **Corporate Action Likelihood** — how strongly the evidence indicates that an action is being prepared or will occur.
2. **Corporate Action Quality** — how attractive the disclosed structure appears on strategic/economic grounds.
3. **Shareholder Value Impact** — how the action may affect existing shareholders based only on disclosed, measurable evidence.

These are independent dimensions and must never be collapsed into one score.

---

# 2. Architecture Delta

## Existing v7.2

```text
Ownership / Actor
        ↓
Behavior / Sequence
        ↓
Corporate Action Preparation
        ↓
Transformation / Asset Catalyst
        ↓
Convergence
        ↓
Lead Time
        ↓
Priority Candidate
```

## v7.3

```text
Ownership / Actor
        ↓
Behavior / Sequence
        ↓
Corporate Action Preparation
        ↓
Corporate Action Likelihood
        ↓
        ┌─────────────────────────────┐
        │ Corporate Action Quality    │
        │ Shareholder Value Assessment│
        └──────────────┬──────────────┘
                       ↓
              Risk / Dilution / Value
                       ↓
                Opportunity State
                       ↓
                 Priority Candidate
```

Corporate Action Likelihood and Corporate Action Quality must remain separate throughout the data model, scoring engine, API, and UI.

---

# 3. New Core Principle

The system must distinguish:

```text
“Is the corporate action likely?”
```
from:

```text
“Is the corporate action attractive?”
```

and from:

```text
“Is the disclosed structure favorable or unfavorable to existing shareholders?”
```

Example:

```text
Likelihood: 90/100
Quality: 40/100
```

means:

> The action appears likely, but its disclosed economics are unattractive or risky.

Another example:

```text
Likelihood: 60/100
Quality: 90/100
```

means:

> The action is not yet confirmed, but if executed on the disclosed terms, it appears strategically attractive.

The system must never convert either result directly into a BUY/SELL recommendation.

---

# 4. New Intermediate Object: Corporate Action Assessment

Add a new object/table linked to the existing corporate-action state.

Suggested structure:

```text
corporate_action_assessments
----------------------------
id
issuer_action_state_id
action_type
likelihood_score
quality_score
shareholder_value_score
risk_score
dilution_score
strategic_rationale_score
capital_efficiency_score
funding_quality_score
asset_quality_score
control_alignment_score
execution_risk_score
related_party_risk_score
confidence
assessment_state
created_at
updated_at
```

Do not duplicate raw evidence. Link the assessment to existing evidence/document/event records.

---

# 5. Corporate Action Likelihood

This score already has a conceptual foundation in v7.2. v7.3 formalizes it as an independent output.

It measures:

> **How strongly the available evidence indicates that a specific corporate action is being prepared, developing, or becoming explicit.**

Inputs may include:

- precursor sequence;
- lifecycle stage;
- repeated disclosures;
- issuer/action corroboration;
- ownership alignment;
- strategic actor activity;
- formal agenda/approval;
- explicit announcement;
- contradiction/cancellation penalties;
- recency;
- evidence quality.

Suggested states:

```text
NO_SIGNAL
EARLY
DEVELOPING
LIKELY
EXPLICIT
CONTRADICTED
CANCELLED
EXPIRED
SUPERSEDED
```

The existing Early → Developing → Explicit engine remains authoritative for lifecycle state.

---

# 6. New Corporate Action Quality Engine

The Quality Engine evaluates whether the disclosed action appears economically/strategically attractive.

It must not judge the stock price itself.

It evaluates the structure of the action and its disclosed rationale.

## 6.1 Core dimensions

### A. Strategic Rationale

Assess whether the stated purpose is connected to a credible strategic objective.

Examples of potentially favorable context:

- productive expansion;
- acquisition of an operating asset/business;
- capacity expansion with disclosed demand support;
- meaningful deleveraging that improves strategic flexibility;
- strategic business transformation;
- strategic investor participation;
- asset/business injection with credible value rationale.

Potentially weak context:

- vague purpose;
- generic working-capital explanation without material detail;
- repeated refinancing without clear improvement;
- unclear value-creation mechanism.

The engine must not infer quality solely from optimistic wording.

---

# 7. Use of Proceeds Quality

For capital-raising actions, extract and classify the disclosed use of proceeds.

Required fields when available:

```text
use_of_proceeds
amount_per_use
percentage_per_use
project_or_asset
funding_deadline
stated_expected_benefit
```

Classify proceeds into:

```text
PRODUCTIVE_GROWTH
STRATEGIC_ACQUISITION
DELEVERAGING
GENERAL_WORKING_CAPITAL
LIQUIDITY_SUPPORT
LOSS_COVERAGE
DEBT_SERVICE
RELATED_PARTY_SETTLEMENT
MIXED
UNCLEAR
```

Do not automatically classify:

> “Expansion” = positive.

The score must consider supporting evidence and risk context.

---

# 8. Dilution Assessment

Dilution must be a first-class factor for actions involving new shares.

Where data is disclosed, calculate or extract:

```text
existing_shares
new_shares
post_action_shares
new_share_ratio
approximate_dilution_pct
rights_ratio
subscription_price
```

For existing holders, distinguish:

- dilution if they do not participate;
- dilution protection if rights are available;
- potential dilution from non-participation;
- post-action ownership of strategic parties when disclosed.

Do not call dilution automatically negative.

Examples:

```text
Large dilution + productive asset injection
→ mixed, requires quality analysis

Large dilution + liquidity rescue only
→ negative/risky candidate

Low dilution + high-quality strategic asset
→ potentially attractive
```

---

# 9. Pricing Attractiveness

When an issuance/subscription price is explicitly disclosed, compare it with relevant reference prices already available in the system.

Possible reference fields:

```text
current_market_price
reference_market_price
subscription_price
transaction_price
```

The system may show:

```text
subscription_price_vs_market
transaction_price_vs_market
```

But it must not claim that a discount automatically makes the action attractive.

A discounted price can also represent:

- high execution risk;
- distress financing;
- dilution risk;
- control transfer economics.

Therefore price is an input, not a conclusion.

---

# 10. Who Receives the New Securities?

For capital-raising actions, identify, where disclosed:

```text
recipient_type
recipient_name
recipient_role
subscription_commitment
standby_buyer
strategic_investor
related_party
existing_controller
new_controller
public_holders
```

This is critical because the same corporate action can have different economic implications depending on who receives the securities.

Examples:

```text
Strategic investor + operating capability
→ potentially positive strategic alignment

Related party + unclear economics
→ related-party risk increases

New controller + large ownership transfer
→ control-transition assessment required
```

---

# 11. Control and Ownership Alignment

Evaluate whether the action creates or changes control.

Required fields when available:

```text
controller_before
controller_after
strategic_holder_before
strategic_holder_after
ownership_concentration_before
ownership_concentration_after
```

Potential states:

```text
CONTROL_STABLE
CONTROL_STRENGTHENED
CONTROL_WEAKENED
CONTROL_TRANSFER
NEW_STRATEGIC_CONTROLLER
UNCLEAR
```

Control change must be analyzed separately from ordinary dilution.

---

# 12. Asset / Business Quality Assessment

When the action involves an acquisition, asset injection, business transformation, or major project, extract:

```text
asset_name
asset_type
ownership_acquired
purchase_price
transaction_value
stated_asset_capacity
commercial_status
contracted_revenue_if_disclosed
operating_status
strategic_fit
funding_source
```

Classify asset/business catalyst as:

```text
HIGH_QUALITY_CATALYST
MEDIUM_QUALITY_CATALYST
LOW_QUALITY_CATALYST
DISTRESS_ASSET
UNCLEAR
```

The system must not independently value an asset unless reliable valuation inputs are explicitly available.

It should instead say:

> “Large strategic asset disclosed; economic value not independently verifiable from available disclosure.”

---

# 13. Funding Quality

Assess how the company finances the action.

Possible funding sources:

```text
INTERNAL_CASH
BANK_DEBT
BOND
RIGHTS_ISSUE
PRIVATE_PLACEMENT
STRATEGIC_INVESTOR
ASSET_SALE
MIXED
UNCLEAR
```

Assess:

- funding certainty;
- dependence on future financing;
- refinancing risk;
- liquidity pressure;
- debt burden when disclosed;
- funding concentration;
- execution dependencies.

Do not infer financial distress solely from the use of debt.

---

# 14. Related-Party Risk

A corporate action must receive a separate related-party assessment where applicable.

Detect:

- related-party transaction;
- connected party;
- affiliate involvement;
- controller-related transaction;
- asset transfer between related parties;
- financing with related parties;
- securities issued to related parties.

Possible states:

```text
NONE_IDENTIFIED
LOW
MEDIUM
HIGH
UNCLEAR
```

Related-party presence is not automatically negative, but unexplained or weakly justified related-party economics must reduce Quality confidence.

---

# 15. Execution Risk

Assess whether the stated corporate action depends on unresolved conditions.

Signals include:

- regulatory approval;
- shareholder approval;
- financing not yet secured;
- acquisition agreement not final;
- conditions precedent;
- third-party consent;
- due diligence pending;
- uncertain asset closing;
- uncertain investor commitment.

States:

```text
LOW_EXECUTION_RISK
MEDIUM_EXECUTION_RISK
HIGH_EXECUTION_RISK
UNCLEAR
```

This is distinct from Corporate Action Likelihood.

Example:

```text
Corporate Action Likelihood = HIGH
Execution Risk = HIGH
```

means the intended action is strongly evidenced but still faces substantial execution uncertainty.

---

# 16. Distress / Value-Destruction Detection

The Quality Engine must actively look for negative economic context.

Signals include:

- emergency liquidity requirements;
- repeated losses requiring capital support;
- debt-service pressure;
- forced disposal;
- covenant pressure;
- restructuring due to financial distress;
- financing primarily required to sustain operations without disclosed strategic improvement;
- extreme dilution without clear value-creation rationale.

These signals reduce Quality and Shareholder Value scores.

The engine should label:

```text
DISTRESS_FINANCING_RISK
```

when supported by multiple independent evidence items.

A single mention of “liquidity” must not be sufficient.

---

# 17. Shareholder Value Impact Score

Add a separate score from 0–100.

Suggested conceptual dimensions:

```text
Strategic Rationale        20%
Use of Proceeds             20%
Dilution / Ownership        15%
Asset / Business Quality    15%
Funding Quality             10%
Control Alignment            5%
Pricing / Terms               5%
Execution Risk                5%
Related-Party Risk             3%
Distress Risk                  2%
```

These weights are initial configuration, not permanent truth. They must be backtested and adjustable.

The system must never present the score as a probability of price appreciation.

---

# 18. Corporate Action Quality Score

Calculate a separate 0–100 score.

Suggested qualitative bands:

```text
80–100  VERY_ATTRACTIVE
65–79   ATTRACTIVE
50–64   NEUTRAL / MIXED
35–49   RISKY / DILUTIVE
0–34    UNATTRACTIVE / DISTRESS
```

If evidence is insufficient, the system must return:

```text
QUALITY_UNCLEAR
```

rather than forcing a numeric classification.

---

# 19. Quality Confidence

Quality Score and Quality Confidence must be separate.

Example:

```text
Quality Score: 82
Confidence: Low
```

means:

> Available disclosed factors appear attractive, but the evidence is incomplete.

Confidence should increase with:

- multiple independent documents;
- explicit numerical terms;
- confirmed commitments;
- transparent use of proceeds;
- clear ownership/control structure;
- completed or approved transactions;
- consistent disclosures.

Confidence should decrease with:

- hypothetical plans;
- missing economics;
- contradictory documents;
- uncertain financing;
- unresolved approvals;
- incomplete disclosure.

---

# 20. Opportunity State

Add a new state that combines likelihood and quality without becoming a buy signal.

```text
EARLY_ATTRACTIVE
DEVELOPING_ATTRACTIVE
EXPLICIT_ATTRACTIVE
EARLY_UNCLEAR
DEVELOPING_UNCLEAR
EXPLICIT_UNCLEAR
DEVELOPING_RISKY
EXPLICIT_RISKY
DISTRESS_RISK
CONTRADICTED
CANCELLED
EXPIRED
SUPERSEDED
```

Highest research priority should generally be:

```text
DEVELOPING_ATTRACTIVE
        >
EARLY_ATTRACTIVE
        >
EXPLICIT_ATTRACTIVE
```

but only when evidence quality and confidence are adequate.

---

# 21. Quality Red Flags

The UI must display red flags separately rather than hiding them inside a score.

Examples:

```text
HIGH_DILUTION
DISTRESS_FINANCING
RELATED_PARTY_RISK
EXECUTION_UNCERTAINTY
CONTROL_TRANSFER
UNCLEAR_USE_OF_PROCEEDS
WEAK_STRATEGIC_RATIONALE
FUNDING_DEPENDENCY
LOW_EVIDENCE_QUALITY
```

A candidate may have a high attractiveness score and still show important red flags.

---

# 22. Quality Positive Drivers

Display positive drivers separately.

Examples:

```text
STRATEGIC_INVESTOR
PRODUCTIVE_ASSET
SECURED_FINANCING
CONTRACTED_REVENUE
CLEAR_USE_OF_PROCEEDS
CONTROL_ALIGNMENT
STRATEGIC_TRANSFORMATION
DELEVERAGING_BENEFIT
ASSET_INJECTION
REPEATED_SUPPORTING_EVIDENCE
```

The engine must only emit these labels when supported by source evidence.

---

# 23. Why-This-Action-Is-Good Explanation

Every non-unclear Quality assessment must provide an evidence-based explanation.

Example:

```text
WHY POTENTIALLY ATTRACTIVE

• Proceeds are primarily allocated to productive expansion.
• A strategic investor has disclosed a participation commitment.
• The acquired asset has a disclosed long-term commercial contract.
• Funding is substantially identified.

KEY RISKS

• New shares create meaningful dilution for non-participating holders.
• Completion remains subject to shareholder approval.
```

The explanation must not claim future price appreciation.

---

# 24. Why-This-Action-Is-Bad Explanation

Example:

```text
WHY POTENTIALLY UNATTRACTIVE

• Proceeds are primarily intended for immediate liquidity support.
• Significant new shares may dilute existing holders.
• No strategic investor commitment is disclosed.
• Financing remains dependent on execution of the offering.

KEY UNKNOWN

• Long-term value creation from the transaction is not clearly disclosed.
```

---

# 25. Example Decision Matrix

| Likelihood | Quality | Interpretation |
|---|---|---|
| High | High | Strong research candidate |
| High | Medium | Attractive but requires verification |
| High | Low | Likely action, poor economics |
| Medium | High | Early opportunity candidate |
| Medium | Unclear | Watch / research |
| Low | High | Interesting thesis, weak confirmation |
| Low | Low | Low priority |

The system must not transform this matrix into an automatic trading rule.

---

# 26. Example: Right Issue

```text
Corporate Action Likelihood: DEVELOPING / HIGH
Corporate Action Quality: ATTRACTIVE
Shareholder Value Impact: 78/100
Confidence: MEDIUM-HIGH
```

Supporting evidence:

- proceeds primarily allocated to productive expansion;
- strategic investor participation;
- meaningful asset/project catalyst;
- funding path identified;
- dilution exists but appears proportionate to the disclosed strategic benefit.

This should become:

```text
DEVELOPING_ATTRACTIVE
```

not BUY.

---

# 27. Example: Distress Right Issue

```text
Corporate Action Likelihood: EXPLICIT
Corporate Action Quality: RISKY / DILUTIVE
Shareholder Value Impact: 31/100
Confidence: HIGH
```

Supporting evidence:

- primary objective is immediate liquidity support;
- high potential dilution;
- no strategic investor commitment;
- limited disclosed value-creation mechanism.

This should become:

```text
EXPLICIT_RISKY
```

---

# 28. Interaction With Smart Money Score

The existing Smart Money Score must remain separate.

Do not do:

```text
Smart Money Score + Corporate Action Quality
= BUY SCORE
```

Instead show:

```text
Smart Money / Positioning: 84
Corporate Action Likelihood: 78
Corporate Action Quality: 82
Shareholder Value Impact: 76
Lead Time: 21 days
Evidence Confidence: Medium-High
```

This allows the user to understand the thesis rather than receive an opaque single score.

---

# 29. Priority Ranking Update

Priority should reward convergence of:

```text
Strategic Positioning
+
Corporate Action Likelihood
+
Corporate Action Quality
+
Transformation / Asset Catalyst
+
Lead Time
+
Evidence Confidence
```

Priority should be penalized by:

```text
High Dilution
Distress Risk
Related-Party Risk
Execution Risk
Contradiction
Weak Evidence
```

No isolated metric may dominate the entire priority ranking.

---

# 30. Required Evidence Traceability

Every Quality driver must link to source evidence.

Minimum fields:

```text
assessment_id
document_id
page_number
excerpt
evidence_type
driver_type
impact
confidence
```

Example evidence types:

```text
USE_OF_PROCEEDS
ISSUANCE_TERMS
DILUTION
STRATEGIC_INVESTOR
ASSET_VALUE_CONTEXT
FUNDING
CONTROL
RELATED_PARTY
EXECUTION_CONDITION
DISTRESS
```

No score component may be generated without an explainable evidence source or an explicitly derived calculation from sourced numerical facts.

---

# 31. Anti-Hallucination / Anti-Overreach Rules

The engine must not infer:

- guaranteed future earnings;
- guaranteed asset value;
- guaranteed price appreciation;
- guaranteed success of an acquisition;
- insider intent without evidence;
- that a strategic investor guarantees future stock performance;
- that discounted securities are automatically cheap;
- that an issuer is undervalued simply because assets are large.

When evidence is insufficient, use:

```text
UNCLEAR
```

instead of inventing an assessment.

---

# 32. Full Audit Requirements

For Full Audit / historical validation, the system should preserve the assessment **as-of the information available at that historical date**.

Do not allow later documents to leak backward into historical assessment.

This is required for valid backtesting.

Example:

```text
As-of 01 Sep:
Likelihood = Developing
Quality = Unclear

Later 15 Sep:
Action became Explicit
Quality became Attractive
```

The 01 Sep historical result must remain unchanged.

---

# 33. Backtesting Requirements

Add historical validation for Corporate Action Quality.

For known corporate actions, create an event window:

```text
T-90
T-60
T-30
T-14
T-7
T-1
T+1
T+30
```

Measure:

- quality classification accuracy;
- false attractive rate;
- false negative rate;
- lead-time of attractive candidates;
- dilution assessment accuracy;
- distress classification accuracy;
- use-of-proceeds classification accuracy;
- relationship/control classification accuracy;
- confidence calibration.

Do not claim that the Quality Score predicts stock returns unless a separate statistically validated model is developed.

---

# 34. UI Update

The existing v7.2 detail page should add:

```text
CORPORATE ACTION
HMETD / RIGHT ISSUE

LIKELIHOOD
Developing · High

QUALITY
ATTRACTIVE · 82/100

SHAREHOLDER VALUE
76/100

CONFIDENCE
Medium-High

LEAD TIME
21 days
```

Then:

```text
POSITIVE DRIVERS
✓ Strategic investor
✓ Productive expansion
✓ Clear use of proceeds
✓ Funding identified

RED FLAGS
⚠ 18% potential dilution
⚠ Shareholder approval pending
```

Then:

```text
WHY IT MAY BE ATTRACTIVE
[Evidence-backed explanation]

WHY IT MAY FAIL / CREATE RISK
[Evidence-backed explanation]
```

Original PDF and evidence remain accessible.

---

# 35. API Update

Add:

```text
GET /api/corporate-action-assessments/{issuer_action_state_id}
```

Return:

```json
{
  "likelihood_score": 82,
  "likelihood_stage": "DEVELOPING",
  "quality_score": 78,
  "quality_label": "ATTRACTIVE",
  "shareholder_value_score": 74,
  "risk_score": 32,
  "confidence": "MEDIUM_HIGH",
  "positive_drivers": [],
  "red_flags": [],
  "evidence": [],
  "opportunity_state": "DEVELOPING_ATTRACTIVE"
}
```

Existing v7.2 APIs remain valid.

---

# 36. Minimum Test Corpus

Add fixtures for:

### Attractive actions

1. productive Right Issue;
2. strategic investor participation;
3. asset acquisition with disclosed commercial rationale;
4. productive expansion funding;
5. deleveraging with strategic benefit.

### Risky actions

6. emergency liquidity Right Issue;
7. high-dilution issuance;
8. related-party issuance;
9. uncertain financing;
10. forced asset disposal.

### Mixed

11. strategic acquisition + major dilution;
12. attractive asset + weak financing;
13. strong investor + high execution risk.

### Unclear

14. vague use of proceeds;
15. incomplete transaction terms;
16. hypothetical corporate action;
17. insufficient economic information.

Every fixture must assert:

- action likelihood state;
- quality label;
- shareholder value label/score range;
- confidence;
- key positive drivers;
- key red flags;
- evidence pages/excerpts.

---

# 37. Acceptance Criteria

v7.3 is complete when:

### Separation

- Corporate Action Likelihood and Quality are separate outputs.
- Shareholder Value Impact is separately reported.
- Smart Money Score remains separate.

### Quality analysis

- Use of proceeds is extracted where disclosed.
- Dilution is calculated where data permits.
- Issuance/subscription terms are captured.
- Recipient / strategic investor information is captured.
- Control implications are assessed where disclosed.
- Asset/business catalyst is classified when evidence exists.
- Funding quality is assessed.
- Related-party risk is assessed.
- Execution risk is assessed.
- Distress context is assessed.

### Explainability

- Every positive/negative quality driver has source evidence.
- Every derived numerical metric is reproducible.
- Missing evidence produces Unclear rather than invented conclusions.

### Historical integrity

- Historical assessments use only information available at that time.
- Later documents cannot leak backward into historical results.

### Product behavior

- The system never outputs BUY/SELL as a consequence of this patch.
- A high likelihood score does not imply high quality.
- A high quality score does not imply the action will happen.
- No single metric can dominate the assessment.

---

# 38. Final Patch Principle

> **Detect the action early, then judge the structure separately.**

The system must first ask:

```text
Is it happening?
```

Then:

```text
Why is it happening?
```

Then:

```text
Who benefits?
```

Then:

```text
Who bears dilution / risk / control change?
```

Then:

```text
Does the action appear capable of creating shareholder value based on the disclosed facts?
```

The output is an **evidence-backed opportunity assessment**, not an investment recommendation.
