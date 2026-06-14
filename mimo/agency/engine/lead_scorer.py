"""
Lead Scoring Engine - AI-driven lead intelligence system.
Scores dental clinics based on likelihood to convert.
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data")


class Tier(Enum):
    A = "A"  # High intent - manual systems, high pain
    B = "B"  # Medium intent - some automation gaps
    C = "C"  # Low intent - already automated or wrong fit


@dataclass
class ClinicData:
    """Raw clinic data from research."""
    name: str
    country: str
    city: str
    website: str = ""
    phone: str = ""
    owner_name: str = ""
    owner_linkedin: str = ""
    rating: float = 0.0
    review_count: int = 0
    has_online_booking: bool = False
    has_contact_form: bool = False
    has_live_chat: bool = False
    doctor_count: int = 0
    is_chain: bool = False
    is_hospital: bool = False
    website_quality: str = "unknown"  # modern, outdated, unknown
    closing_hour: int = 17  # default 5pm
    has_weekend_hours: bool = False
    notes: str = ""


@dataclass
class ScoredLead:
    """Scored lead with breakdown."""
    clinic: ClinicData
    total_score: int
    tier: Tier
    score_breakdown: Dict[str, int]
    pain_signals: List[str]
    recommended_approach: str
    estimated_deal_size: str
    scored_at: str = ""


class LeadScoringEngine:
    """
    Scores dental clinics based on conversion likelihood.
    
    Scoring factors:
    - Online booking presence (absence = opportunity)
    - Website quality (outdated = higher pain)
    - Review signals (complaints = pain)
    - Practice size (small = easier to close)
    - Business hours (limited = more missed calls)
    """
    
    # Scoring weights
    WEIGHTS = {
        "no_online_booking": 25,
        "no_contact_form": 15,
        "no_live_chat": 15,
        "outdated_website": 15,
        "small_practice": 10,
        "limited_hours": 10,
        "no_weekend": 5,
        "review_complaints": 20,
        "single_location": 5,
        "private_practice": 10,
    }
    
    # Negative factors
    PENALTIES = {
        "is_chain": -30,
        "is_hospital": -40,
        "modern_website_with_booking": -25,
        "high_review_count_with_high_rating": -10,
    }
    
    # Pain signals to look for in reviews
    PAIN_KEYWORDS = [
        "voicemail", "no answer", "called", "waited",
        "callback", "response time", "hold", "busy",
        "unavailable", "closed", "after hours", "weekend"
    ]
    
    # Country-based adjustments
    COUNTRY_MULTIPLIER = {
        "USA": 1.0,
        "UK": 0.9,
        "Canada": 0.95,
        "Australia": 0.95,
        "Ireland": 0.85,
        "Russia": 0.7,
        "Kyrgyzstan": 0.5,
    }
    
    def __init__(self):
        self.leads: List[ScoredLead] = []
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    def score_clinic(self, clinic: ClinicData) -> ScoredLead:
        """Score a single clinic."""
        breakdown = {}
        pain_signals = []
        
        # === POSITIVE FACTORS ===
        
        # Online booking absence (biggest opportunity)
        if not clinic.has_online_booking:
            breakdown["no_online_booking"] = self.WEIGHTS["no_online_booking"]
        else:
            breakdown["no_online_booking"] = self.PENALTIES["modern_website_with_booking"]
        
        # Contact form absence
        if not clinic.has_contact_form:
            breakdown["no_contact_form"] = self.WEIGHTS["no_contact_form"]
        
        # Live chat absence
        if not clinic.has_live_chat:
            breakdown["no_live_chat"] = self.WEIGHTS["no_live_chat"]
        
        # Website quality
        if clinic.website_quality == "outdated":
            breakdown["outdated_website"] = self.WEIGHTS["outdated_website"]
        elif clinic.website_quality == "modern":
            breakdown["outdated_website"] = self.PENALTIES["modern_website_with_booking"]
        
        # Practice size (small = easier to close)
        if 1 <= clinic.doctor_count <= 3:
            breakdown["small_practice"] = self.WEIGHTS["small_practice"]
        elif clinic.doctor_count > 10:
            breakdown["small_practice"] = -10  # Too large
        
        # Hours analysis
        if clinic.closing_hour <= 16:
            breakdown["limited_hours"] = self.WEIGHTS["limited_hours"]
            pain_signals.append("Closes early (before 4pm)")
        
        if not clinic.has_weekend_hours:
            breakdown["no_weekend"] = self.WEIGHTS["no_weekend"]
            pain_signals.append("No weekend hours")
        
        # Review analysis
        if clinic.review_count > 0 and clinic.rating < 4.0:
            breakdown["review_complaints"] = self.WEIGHTS["review_complaints"]
            pain_signals.append("Low rating indicates issues")
        
        # Single location (independent practice)
        if not clinic.is_chain:
            breakdown["single_location"] = self.WEIGHTS["single_location"]
            breakdown["private_practice"] = self.WEIGHTS["private_practice"]
        
        # === NEGATIVE FACTORS ===
        
        if clinic.is_chain:
            breakdown["is_chain"] = self.PENALTIES["is_chain"]
            pain_signals.append("Chain - harder to close")
        
        if clinic.is_hospital:
            breakdown["is_hospital"] = self.PENALTIES["is_hospital"]
            pain_signals.append("Hospital - not a target")
        
        # === CALCULATE TOTAL ===
        
        total_score = sum(breakdown.values())
        
        # Apply country multiplier
        country_mult = self.COUNTRY_MULTIPLIER.get(clinic.country, 0.8)
        total_score = int(total_score * country_mult)
        
        # Clamp to 0-100
        total_score = max(0, min(100, total_score))
        
        # === DETERMINE TIER ===
        
        if total_score >= 70:
            tier = Tier.A
        elif total_score >= 45:
            tier = Tier.B
        else:
            tier = Tier.C
        
        # === PAIN SIGNALS ===
        
        if not clinic.has_online_booking:
            pain_signals.append("No online booking - manual process")
        if not clinic.has_contact_form:
            pain_signals.append("No contact form - hard to reach")
        if not clinic.has_live_chat:
            pain_signals.append("No live chat - no instant response")
        if clinic.closing_hour <= 17 and not clinic.has_weekend_hours:
            pain_signals.append("Limited hours = missed after-hours calls")
        
        # === RECOMMENDED APPROACH ===
        
        if tier == Tier.A:
            approach = "Direct pain-based outreach. Focus on missed revenue."
            deal_size = "$1,500-3,000/month"
        elif tier == Tier.B:
            approach = "Soft curiosity. Ask about their current process."
            deal_size = "$500-1,500/month"
        else:
            approach = "Low priority. Monitor or skip."
            deal_size = "Low probability"
        
        return ScoredLead(
            clinic=clinic,
            total_score=total_score,
            tier=tier,
            score_breakdown=breakdown,
            pain_signals=pain_signals,
            recommended_approach=approach,
            estimated_deal_size=deal_size,
            scored_at=datetime.now().isoformat()
        )
    
    def score_batch(self, clinics: List[ClinicData]) -> List[ScoredLead]:
        """Score multiple clinics."""
        scored = [self.score_clinic(c) for c in clinics]
        scored.sort(key=lambda x: x.total_score, reverse=True)
        self.leads = scored
        return scored
    
    def get_tier(self, tier: Tier) -> List[ScoredLead]:
        """Get leads by tier."""
        return [l for l in self.leads if l.tier == tier]
    
    def get_stats(self) -> Dict:
        """Get scoring statistics."""
        if not self.leads:
            return {"total": 0}
        
        return {
            "total": len(self.leads),
            "tier_a": len(self.get_tier(Tier.A)),
            "tier_b": len(self.get_tier(Tier.B)),
            "tier_c": len(self.get_tier(Tier.C)),
            "avg_score": sum(l.total_score for l in self.leads) / len(self.leads),
            "countries": list(set(l.clinic.country for l in self.leads)),
        }
    
    def export_json(self, filepath: str = None):
        """Export scored leads to JSON."""
        if filepath is None:
            filepath = os.path.join(OUTPUT_DIR, "scored_leads.json")
        
        data = {
            "scored_at": datetime.now().isoformat(),
            "stats": self.get_stats(),
            "leads": [
                {
                    "name": l.clinic.name,
                    "country": l.clinic.country,
                    "city": l.clinic.city,
                    "website": l.clinic.website,
                    "score": l.total_score,
                    "tier": l.tier.value,
                    "pain_signals": l.pain_signals,
                    "approach": l.recommended_approach,
                    "deal_size": l.estimated_deal_size,
                }
                for l in self.leads
            ]
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        
        return filepath


# === EXAMPLE USAGE ===

def demo_scoring():
    """Demo the scoring engine with sample clinics."""
    engine = LeadScoringEngine()
    
    # Sample clinics
    clinics = [
        ClinicData(
            name="Smile Dental NYC",
            country="USA",
            city="New York",
            website="smiledentalnyc.com",
            has_online_booking=False,
            has_contact_form=False,
            has_live_chat=False,
            doctor_count=2,
            is_chain=False,
            website_quality="outdated",
            closing_hour=17,
            has_weekend_hours=False,
        ),
        ClinicData(
            name="Perfect Teeth Chicago",
            country="USA",
            city="Chicago",
            website="perfectteeth.com",
            has_online_booking=True,
            has_contact_form=True,
            has_live_chat=True,
            doctor_count=5,
            is_chain=False,
            website_quality="modern",
            closing_hour=18,
            has_weekend_hours=True,
        ),
        ClinicData(
            name="Metro Dental Chain",
            country="USA",
            city="Los Angeles",
            website="metrodental.com",
            has_online_booking=True,
            has_contact_form=True,
            has_live_chat=True,
            doctor_count=50,
            is_chain=True,
            website_quality="modern",
            closing_hour=20,
            has_weekend_hours=True,
        ),
        ClinicData(
            name="Али-Дент",
            country="Kyrgyzstan",
            city="Bishkek",
            website="ali-dent.kg",
            has_online_booking=False,
            has_contact_form=False,
            has_live_chat=False,
            doctor_count=3,
            is_chain=False,
            website_quality="outdated",
            closing_hour=18,
            has_weekend_hours=False,
        ),
    ]
    
    # Score all
    results = engine.score_batch(clinics)
    
    # Print results
    print("=" * 60)
    print("LEAD SCORING RESULTS")
    print("=" * 60)
    
    for lead in results:
        name = lead.clinic.name.encode('ascii', 'replace').decode('ascii')
        country = lead.clinic.country.encode('ascii', 'replace').decode('ascii')
        print(f"\n{name} ({country})")
        print(f"  Score: {lead.total_score}/100 | Tier: {lead.tier.value}")
        pain = ', '.join(lead.pain_signals[:3])
        print(f"  Pain signals: {pain}")
        print(f"  Approach: {lead.recommended_approach}")
        print(f"  Deal size: {lead.estimated_deal_size}")
    
    # Stats
    stats = engine.get_stats()
    print(f"\n{'=' * 60}")
    print(f"STATS: {stats['tier_a']} A-tier | {stats['tier_b']} B-tier | {stats['tier_c']} C-tier")
    print(f"Average score: {stats['avg_score']:.1f}")
    
    # Export
    filepath = engine.export_json()
    print(f"\nExported to: {filepath}")


if __name__ == "__main__":
    demo_scoring()
