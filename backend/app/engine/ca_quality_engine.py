"""
Corporate Action Quality & Shareholder Value Assessment Engine (PRD v7.3 Patch)
Separates:
1. Corporate Action Likelihood (How strongly evidence indicates preparation/occurrence)
2. Corporate Action Quality (How attractive the disclosed structure appears on economic/strategic grounds)
3. Shareholder Value Impact (Effect on existing shareholders based strictly on disclosed evidence)

Strictly non-probabilistic, fully explainable, anti-hallucination.
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from app.rules.definitions import (
    USE_OF_PROCEEDS_TAXONOMY,
    QUALITY_BANDS,
    OPPORTUNITY_STATES,
    QUALITY_POSITIVE_DRIVERS,
    QUALITY_RED_FLAGS,
    DILUTION_PATTERNS,
    SUBSCRIPTION_PRICE_PATTERNS,
    RECIPIENT_PATTERNS,
    DISTRESS_PATTERNS,
    EXECUTION_CONDITION_PATTERNS,
    ASSET_QUALITY_PATTERNS
)


class CorporateActionQualityEngine:
    """
    Evaluates corporate action quality and shareholder value impact
    from disclosed document texts and structured evidence.
    """

    def __init__(self):
        pass

    def extract_use_of_proceeds(self, text: str) -> List[Dict[str, Any]]:
        """
        Extracts use of proceeds breakdown and classifies into taxonomy.
        """
        results = []
        if not text:
            return results

        text_lower = text.lower()
        
        # Check for explicit percentages near proceeds keywords
        # e.g., "sekitar 70% untuk ekspansi", "sebesar 30% untuk modal kerja"
        pct_matches = re.findall(
            r"(?:sebesar|sekitar|alokasi|sebanyak)?\s*(\d+(?:[\.,]\d+)?)\s*%\s*(?:akan\s+)?(?:digunakan\s+)?(?:untuk\s+)?([^;\.\n\r]+)",
            text_lower
        )
        
        found_categories = set()
        for pct_str, context in pct_matches:
            pct_val = float(pct_str.replace(",", "."))
            # match context against taxonomy
            matched_cat = None
            for cat, patterns in USE_OF_PROCEEDS_TAXONOMY.items():
                for pat in patterns:
                    if re.search(pat, context):
                        matched_cat = cat
                        break
                if matched_cat:
                    break
            
            if matched_cat and matched_cat not in found_categories:
                found_categories.add(matched_cat)
                results.append({
                    "category": matched_cat,
                    "percentage": pct_val,
                    "description": context.strip()[:100]
                })

        # If no explicit percentages parsed, match general taxonomy patterns
        if not results:
            for cat, patterns in USE_OF_PROCEEDS_TAXONOMY.items():
                for pat in patterns:
                    m = re.search(pat, text_lower)
                    if m and cat not in found_categories:
                        found_categories.add(cat)
                        results.append({
                            "category": cat,
                            "percentage": None,
                            "description": m.group(0)
                        })
                        break

        return results

    def extract_dilution_metrics(self, text: str) -> Dict[str, Any]:
        """
        Extracts dilution percentage, new shares ratio, and subscription price.
        """
        metrics = {
            "dilution_pct": None,
            "new_share_ratio": None,
            "subscription_price": None,
            "new_shares_count": None
        }
        if not text:
            return metrics

        text_lower = text.lower()

        # Dilution percentage
        for pat in [
            r"persentase\s+dilusi\s+(?:sebesar\s+)?(?:mencapai\s+)?([\d\.,]+)%",
            r"terdilusi\s+(?:sebesar\s+)?([\d\.,]+)%",
            r"dilution\s+(?:of\s+)?([\d\.,]+)%"
        ]:
            m = re.search(pat, text_lower)
            if m:
                try:
                    metrics["dilution_pct"] = float(m.group(1).replace(",", "."))
                    break
                except ValueError:
                    pass

        # Rights ratio e.g. "100 : 35", "10 : 3"
        m_ratio = re.search(r"rasio\s+(?:hmetd|right\s+issue|saham)?\s*(?:adalah\s*)?(\d+\s*:\s*\d+)", text_lower)
        if m_ratio:
            metrics["new_share_ratio"] = m_ratio.group(1).replace(" ", "")

        # Subscription / Exercise price
        for pat in SUBSCRIPTION_PRICE_PATTERNS:
            m_price = re.search(pat, text_lower)
            if m_price:
                try:
                    # Clean dots and commas
                    raw_p = m_price.group(1).replace(".", "").replace(",", ".")
                    metrics["subscription_price"] = float(raw_p)
                    break
                except ValueError:
                    pass

        return metrics

    def _is_negated(self, text: str, match_span: Tuple[int, int]) -> bool:
        start = max(0, match_span[0] - 40)
        prefix = text[start:match_span[0]].lower()
        neg_patterns = [
            r"belum\s+(?:ada|terdapat|memiliki|ditunjuk)",
            r"tidak\s+(?:ada|terdapat|memiliki|menggunakan)",
            r"tanpa\s+(?:adanya)?",
            r"bukan\s+merupakan"
        ]
        return any(re.search(pat, prefix) for pat in neg_patterns)

    def detect_recipients_and_standby(self, text: str) -> Dict[str, Any]:
        """
        Detects standby buyer, strategic investors, or affiliate recipients with negation handling.
        """
        recipients = {
            "has_standby_buyer": False,
            "has_strategic_investor": False,
            "has_related_party_recipient": False,
            "standby_buyer_names": [],
            "strategic_investor_names": []
        }
        if not text:
            return recipients

        text_lower = text.lower()

        for pat in RECIPIENT_PATTERNS["STANDBY_BUYER"]:
            for m in re.finditer(pat, text_lower):
                if not self._is_negated(text_lower, m.span()):
                    recipients["has_standby_buyer"] = True
                    break
            if recipients["has_standby_buyer"]:
                break

        for pat in RECIPIENT_PATTERNS["STRATEGIC_INVESTOR"]:
            for m in re.finditer(pat, text_lower):
                if not self._is_negated(text_lower, m.span()):
                    recipients["has_strategic_investor"] = True
                    break
            if recipients["has_strategic_investor"]:
                break

        for pat in RECIPIENT_PATTERNS["RELATED_PARTY_RECIPIENT"]:
            for m in re.finditer(pat, text_lower):
                if not self._is_negated(text_lower, m.span()):
                    recipients["has_related_party_recipient"] = True
                    break
            if recipients["has_related_party_recipient"]:
                break

        # Attempt to capture named entities following standby buyer
        sb_name_match = re.search(
            r"(?:pembeli\s+siaga|standby\s+buyer)\s*(?:adalah|yaitu)?\s*(pt\s+[a-zA-Z0-9\s]+?)(?:,|\.|\s+dan|\s+sebesar|\s+yang)",
            text_lower
        )
        if sb_name_match and recipients["has_standby_buyer"]:
            recipients["standby_buyer_names"].append(sb_name_match.group(1).upper().strip())

        return recipients

    def detect_risk_and_catalyst_signals(self, text: str) -> Dict[str, Any]:
        """
        Detects distress financing, execution conditions, and commercial asset quality.
        """
        signals = {
            "is_distress": False,
            "has_execution_risk": False,
            "has_commercial_asset": False,
            "is_related_party_tx": False,
            "distress_matches": [],
            "execution_matches": []
        }
        if not text:
            return signals

        text_lower = text.lower()

        # Distress patterns
        for pat in DISTRESS_PATTERNS:
            m = re.search(pat, text_lower)
            if m:
                signals["is_distress"] = True
                signals["distress_matches"].append(m.group(0))

        # Execution condition patterns
        for pat in EXECUTION_CONDITION_PATTERNS:
            m = re.search(pat, text_lower)
            if m:
                signals["has_execution_risk"] = True
                signals["execution_matches"].append(m.group(0))

        # Commercial Asset quality patterns
        for pat in ASSET_QUALITY_PATTERNS:
            if re.search(pat, text_lower):
                signals["has_commercial_asset"] = True
                break

        # Related party transaction
        if re.search(r"\b(?:transaksi\s+afiliasi|pihak\s+berelasi|benturan\s+kepentingan)\b", text_lower):
            signals["is_related_party_tx"] = True

        return signals

    def evaluate_quality(
        self,
        document_text: str,
        action_type: str = "RIGHTS_ISSUE",
        lifecycle_stage: str = "DEVELOPING",
        likelihood_score: float = 70.0
    ) -> Dict[str, Any]:
        """
        Evaluates the 10 dimensions of Corporate Action Quality and synthesizes scores.
        """
        text = document_text or ""
        proceeds = self.extract_use_of_proceeds(text)
        dilution = self.extract_dilution_metrics(text)
        recipients = self.detect_recipients_and_standby(text)
        risks = self.detect_risk_and_catalyst_signals(text)

        # Dimension 1: Strategic Rationale (20% weight)
        strat_score = 50.0
        # Dimension 2: Use of Proceeds Quality (20% weight)
        proceeds_score = 50.0

        has_productive = any(p["category"] in ["PRODUCTIVE_GROWTH", "STRATEGIC_ACQUISITION"] for p in proceeds)
        has_deleveraging = any(p["category"] == "DELEVERAGING" for p in proceeds)
        has_working_cap = any(p["category"] == "GENERAL_WORKING_CAPITAL" for p in proceeds)
        has_liquidity_distress = any(p["category"] in ["LIQUIDITY_SUPPORT", "LOSS_COVERAGE", "DEBT_SERVICE"] for p in proceeds)
        has_related_settle = any(p["category"] == "RELATED_PARTY_SETTLEMENT" for p in proceeds)

        if has_productive:
            strat_score += 25.0
            proceeds_score += 30.0
        if has_deleveraging:
            strat_score += 15.0
            proceeds_score += 15.0
        if has_working_cap and not has_productive and not has_deleveraging:
            strat_score -= 10.0
            proceeds_score -= 10.0
        if has_liquidity_distress or risks["is_distress"]:
            strat_score -= 30.0
            proceeds_score -= 35.0
        if has_related_settle:
            strat_score -= 15.0
            proceeds_score -= 20.0

        # Dimension 3: Dilution Assessment (15% weight)
        dilution_score = 50.0
        dilution_pct = dilution["dilution_pct"]
        if dilution_pct is not None:
            if dilution_pct < 10.0:
                dilution_score = 80.0
            elif dilution_pct <= 25.0:
                dilution_score = 65.0
            elif dilution_pct <= 40.0:
                dilution_score = 45.0
            else:
                dilution_score = 25.0
        else:
            dilution_score = 50.0

        # Dimension 4: Asset / Business Quality (15% weight)
        asset_score = 50.0
        if risks["has_commercial_asset"]:
            asset_score = 85.0
        elif has_productive:
            asset_score = 70.0
        elif risks["is_distress"]:
            asset_score = 20.0

        # Dimension 5: Funding Quality (10% weight)
        funding_score = 50.0
        if recipients["has_strategic_investor"]:
            funding_score += 25.0
        if recipients["has_standby_buyer"]:
            funding_score += 15.0
        if risks["is_distress"]:
            funding_score -= 30.0

        # Dimension 6: Control Alignment (5% weight)
        control_score = 50.0
        if recipients["has_strategic_investor"]:
            control_score = 75.0
        elif recipients["has_related_party_recipient"]:
            control_score = 45.0

        # Dimension 7: Pricing / Terms (5% weight)
        pricing_score = 50.0
        if dilution["subscription_price"] is not None:
            pricing_score = 60.0

        # Dimension 8: Execution Risk (5% weight)
        # Note: High execution conditions mean lower execution safety score
        execution_score = 60.0
        if risks["has_execution_risk"]:
            execution_score = 35.0

        # Dimension 9: Related-Party Risk (3% weight)
        related_party_score = 75.0
        if risks["is_related_party_tx"] or has_related_settle or recipients["has_related_party_recipient"]:
            related_party_score = 30.0

        # Dimension 10: Distress Risk (2% weight)
        distress_score = 85.0
        if risks["is_distress"] or has_liquidity_distress:
            distress_score = 15.0

        # Clamp all subscores 0-100
        strat_score = max(0.0, min(100.0, strat_score))
        proceeds_score = max(0.0, min(100.0, proceeds_score))
        dilution_score = max(0.0, min(100.0, dilution_score))
        asset_score = max(0.0, min(100.0, asset_score))
        funding_score = max(0.0, min(100.0, funding_score))
        control_score = max(0.0, min(100.0, control_score))
        pricing_score = max(0.0, min(100.0, pricing_score))
        execution_score = max(0.0, min(100.0, execution_score))
        related_party_score = max(0.0, min(100.0, related_party_score))
        distress_score = max(0.0, min(100.0, distress_score))

        # Weighted Corporate Action Quality Score (0 - 100)
        # Weights: Strat 20%, Proceeds 20%, Dilution 15%, Asset 15%, Funding 10%, Control 5%, Pricing 5%, Exec 5%, Rel 3%, Dist 2%
        quality_score = (
            strat_score * 0.20 +
            proceeds_score * 0.20 +
            dilution_score * 0.15 +
            asset_score * 0.15 +
            funding_score * 0.10 +
            control_score * 0.05 +
            pricing_score * 0.05 +
            execution_score * 0.05 +
            related_party_score * 0.03 +
            distress_score * 0.02
        )

        # Shareholder Value Impact Score
        # Similar weighting, but penalizes dilution and distress more directly
        sv_score = (
            strat_score * 0.20 +
            proceeds_score * 0.20 +
            dilution_score * 0.20 +
            asset_score * 0.15 +
            funding_score * 0.10 +
            execution_score * 0.05 +
            related_party_score * 0.05 +
            distress_score * 0.05
        )

        quality_score = round(max(0.0, min(100.0, quality_score)), 1)
        sv_score = round(max(0.0, min(100.0, sv_score)), 1)
        risk_score = round(max(0.0, min(100.0, 100.0 - quality_score)), 1)

        # Evidence Completeness & Confidence Check (PRD Section 19 & 31)
        # If there's barely any text or no proceeds / economic factors disclosed
        has_economic_data = (
            bool(proceeds) or 
            dilution_pct is not None or 
            recipients["has_standby_buyer"] or 
            recipients["has_strategic_investor"] or 
            risks["is_distress"] or 
            risks["has_commercial_asset"]
        )

        if not has_economic_data:
            quality_label = "QUALITY_UNCLEAR"
            confidence = "LOW"
        else:
            if quality_score >= 80.0:
                quality_label = "VERY_ATTRACTIVE"
            elif quality_score >= 65.0:
                quality_label = "ATTRACTIVE"
            elif quality_score >= 50.0:
                quality_label = "NEUTRAL_MIXED"
            elif quality_score >= 35.0:
                quality_label = "RISKY_DILUTIVE"
            else:
                quality_label = "UNATTRACTIVE_DISTRESS"

            # Confidence determination
            factors_count = (
                (1 if proceeds else 0) +
                (1 if dilution_pct is not None else 0) +
                (1 if recipients["has_standby_buyer"] or recipients["has_strategic_investor"] else 0) +
                (1 if dilution["subscription_price"] is not None else 0) +
                (1 if risks["has_commercial_asset"] or risks["is_distress"] else 0)
            )
            if factors_count >= 3:
                confidence = "HIGH"
            elif factors_count == 2:
                confidence = "MEDIUM_HIGH"
            elif factors_count == 1:
                confidence = "MEDIUM"
            else:
                confidence = "LOW"

        # Opportunity State (PRD Section 20)
        opportunity_state = self._determine_opportunity_state(
            lifecycle_stage=lifecycle_stage,
            quality_label=quality_label,
            is_distress=risks["is_distress"]
        )

        # Positive Drivers & Red Flags identification (PRD Sections 21 & 22)
        positive_drivers = []
        red_flags = []

        if recipients["has_strategic_investor"]:
            positive_drivers.append("STRATEGIC_INVESTOR")
        if has_productive or risks["has_commercial_asset"]:
            positive_drivers.append("PRODUCTIVE_ASSET")
        if recipients["has_standby_buyer"]:
            positive_drivers.append("SECURED_FINANCING")
        if risks["has_commercial_asset"]:
            positive_drivers.append("CONTRACTED_REVENUE")
        if proceeds and any(p["category"] in ["PRODUCTIVE_GROWTH", "STRATEGIC_ACQUISITION", "DELEVERAGING"] for p in proceeds):
            positive_drivers.append("CLEAR_USE_OF_PROCEEDS")
        if has_deleveraging:
            positive_drivers.append("DELEVERAGING_BENEFIT")

        if dilution_pct is not None and dilution_pct > 20.0:
            red_flags.append("HIGH_DILUTION")
        if risks["is_distress"] or has_liquidity_distress:
            red_flags.append("DISTRESS_FINANCING")
        if risks["is_related_party_tx"] or has_related_settle:
            red_flags.append("RELATED_PARTY_RISK")
        if risks["has_execution_risk"]:
            red_flags.append("EXECUTION_UNCERTAINTY")
        if not proceeds:
            red_flags.append("UNCLEAR_USE_OF_PROCEEDS")
        if not recipients["has_standby_buyer"] and not recipients["has_strategic_investor"] and action_type in ["RIGHTS_ISSUE", "PRIVATE_PLACEMENT"]:
            red_flags.append("FUNDING_DEPENDENCY")

        # Synthesize Why-Attractive and Why-Risky Explanations (PRD Sections 23 & 24)
        why_attractive, why_risky = self._synthesize_explanations(
            positive_drivers=positive_drivers,
            red_flags=red_flags,
            proceeds=proceeds,
            dilution_pct=dilution_pct,
            recipients=recipients,
            risks=risks
        )

        return {
            "likelihood_score": likelihood_score,
            "likelihood_stage": lifecycle_stage,
            "quality_score": quality_score,
            "quality_label": quality_label,
            "shareholder_value_score": sv_score,
            "risk_score": risk_score,
            "confidence": confidence,
            "opportunity_state": opportunity_state,
            "scores_decomposition": {
                "strategic_rationale_score": strat_score,
                "capital_efficiency_score": proceeds_score,
                "funding_quality_score": funding_score,
                "asset_quality_score": asset_score,
                "control_alignment_score": control_score,
                "pricing_attractiveness_score": pricing_score,
                "execution_risk_score": execution_score,
                "related_party_risk_score": related_party_score,
                "distress_risk_score": distress_score,
                "dilution_score": dilution_score
            },
            "dilution_pct": dilution_pct,
            "new_share_ratio": dilution["new_share_ratio"],
            "subscription_price": dilution["subscription_price"],
            "use_of_proceeds": proceeds,
            "recipients": recipients,
            "positive_drivers": positive_drivers,
            "red_flags": red_flags,
            "why_attractive": why_attractive,
            "why_risky": why_risky
        }

    def _determine_opportunity_state(
        self,
        lifecycle_stage: str,
        quality_label: str,
        is_distress: bool
    ) -> str:
        """
        Combines lifecycle stage and quality label into Opportunity State.
        """
        if is_distress:
            return "DISTRESS_RISK"

        stage = lifecycle_stage.upper()
        if quality_label == "QUALITY_UNCLEAR":
            if "EARLY" in stage:
                return "EARLY_UNCLEAR"
            elif "EXPLICIT" in stage:
                return "EXPLICIT_UNCLEAR"
            return "DEVELOPING_UNCLEAR"

        if quality_label in ["VERY_ATTRACTIVE", "ATTRACTIVE"]:
            if "EARLY" in stage:
                return "EARLY_ATTRACTIVE"
            elif "EXPLICIT" in stage:
                return "EXPLICIT_ATTRACTIVE"
            return "DEVELOPING_ATTRACTIVE"

        if quality_label in ["RISKY_DILUTIVE", "UNATTRACTIVE_DISTRESS"]:
            if "EXPLICIT" in stage:
                return "EXPLICIT_RISKY"
            return "DEVELOPING_RISKY"

        # NEUTRAL_MIXED fallback
        if "EARLY" in stage:
            return "EARLY_UNCLEAR"
        elif "EXPLICIT" in stage:
            return "EXPLICIT_UNCLEAR"
        return "DEVELOPING_UNCLEAR"

    def _synthesize_explanations(
        self,
        positive_drivers: List[str],
        red_flags: List[str],
        proceeds: List[Dict[str, Any]],
        dilution_pct: Optional[float],
        recipients: Dict[str, Any],
        risks: Dict[str, Any]
    ) -> Tuple[str, str]:
        """
        Generates evidence-backed bullet points for Why Potentially Attractive and Key Risks.
        """
        attractive_points = []
        risky_points = []

        # Attractive drivers
        if "PRODUCTIVE_ASSET" in positive_drivers or "CLEAR_USE_OF_PROCEEDS" in positive_drivers:
            prod_items = [p["category"].replace("_", " ").title() for p in proceeds if p["category"] in ["PRODUCTIVE_GROWTH", "STRATEGIC_ACQUISITION"]]
            if prod_items:
                attractive_points.append(f"Dana hasil penawaran dialokasikan secara transparan untuk {', '.join(prod_items)}.")
            else:
                attractive_points.append("Alokasi dana ditujukan untuk ekspansi produktif atau pertumbuhan aset operasional.")

        if "STRATEGIC_INVESTOR" in positive_drivers:
            attractive_points.append("Keterbukaan mencatat partisipasi atau komitmen dari investor strategis.")

        if "SECURED_FINANCING" in positive_drivers:
            sb_names = recipients.get("standby_buyer_names", [])
            if sb_names:
                attractive_points.append(f"Telah terdapat komitmen pembeli siaga pasti ({', '.join(sb_names)}).")
            else:
                attractive_points.append("Terdapat penjaminan / pembeli siaga yang memperkuat kepastian pendanaan.")

        if "CONTRACTED_REVENUE" in positive_drivers:
            attractive_points.append("Aset yang diakuisisi/diinjeksi telah memiliki arus pendapatan atau kontrak komersial.")

        if "DELEVERAGING_BENEFIT" in positive_drivers:
            attractive_points.append("Sebagian dana dialokasikan untuk melunasi kewajiban utang guna memangkas beban bunga.")

        # Risky red flags
        if "HIGH_DILUTION" in red_flags and dilution_pct is not None:
            risky_points.append(f"Penerbitan saham baru berpotensi mendilusi pemegang saham eksisting hingga {dilution_pct.toFixed if hasattr(dilution_pct, 'toFixed') else dilution_pct}%.")
        elif "HIGH_DILUTION" in red_flags:
            risky_points.append("Penerbitan saham baru berpotensi menimbulkan dilusi material bagi pemegang saham yang tidak mengeksekusi hak.")

        if "DISTRESS_FINANCING" in red_flags:
            risky_points.append("Pencarian dana diindikasikan untuk kebutuhan likuiditas mendesak atau penyelamatan kelangsungan usaha.")

        if "RELATED_PARTY_RISK" in red_flags:
            risky_points.append("Transaksi melibatkan pihak berelasi/afiliasi yang memerlukan penelaahan independensi lebih mendalam.")

        if "EXECUTION_UNCERTAINTY" in red_flags:
            risky_points.append("Rencana masih bergantung pada persetujuan RUPS atau pemenuhan syarat tangguh (conditions precedent).")

        if "FUNDING_DEPENDENCY" in red_flags:
            risky_points.append("Belum diungkapkan adanya pembeli siaga atau investor strategis yang menyerap sisa saham.")

        if "UNCLEAR_USE_OF_PROCEEDS" in red_flags:
            risky_points.append("Rincian penggunaan dana belum diuraikan secara spesifik dalam keterbukaan informasi.")

        why_attractive = "\n".join([f"• {p}" for p in attractive_points]) if attractive_points else "Informasi faktor penarik strategis belum terungkap secara spesifik."
        why_risky = "\n".join([f"• {p}" for p in risky_points]) if risky_points else "Risiko struktural material belum teridentifikasi dari keterbukaan awal."

        return why_attractive, why_risky
