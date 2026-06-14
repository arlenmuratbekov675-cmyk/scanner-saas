"""
A/B Testing Engine - Self-optimizing sales system.
Compares message strategies and finds the best performer.
"""
import json
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime

import sys
sys.path.insert(0, os.path.dirname(__file__))
from lead_scorer import Tier, ScoredLead, ClinicData, LeadScoringEngine
from message_generator import MessageGeneratorV2, MessageStyle
from simulation_engine import SimulationEngine, PredictionInput, TouchStage


class TestStatus(Enum):
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"


@dataclass
class Variant:
    """A message variant to test."""
    name: str
    style: MessageStyle
    description: str


@dataclass
class TestResult:
    """Result for a single variant on a single lead."""
    variant_name: str
    lead_name: str
    tier: str
    accept_prob: float
    reply_prob: float
    demo_prob: float
    close_prob: float


@dataclass
class TestSummary:
    """Aggregated results for a variant."""
    variant_name: str
    style: str
    total_leads: int
    avg_accept: float
    avg_reply: float
    avg_demo: float
    avg_close: float
    wins: int  # times this variant was best
    win_rate: float


@dataclass
class ABTest:
    """Complete A/B test."""
    test_id: str
    name: str
    status: TestStatus
    variants: List[Variant]
    results: List[TestResult]
    summary: Optional[Dict] = None
    winner: Optional[str] = None
    created_at: str = ""
    completed_at: str = ""


class ABTestingEngine:
    """
    Self-optimizing A/B testing engine.
    
    Compares message strategies across tiers and countries.
    Finds the best performing variant for each segment.
    """
    
    # Default variants to test
    DEFAULT_VARIANTS = [
        Variant(
            name="pain",
            style=MessageStyle.PAIN,
            description="Direct pain-based: 'Do you lose patients from missed calls?'",
        ),
        Variant(
            name="soft",
            style=MessageStyle.SOFT,
            description="Soft curiosity: 'I help clinics capture missing patients'",
        ),
        Variant(
            name="roi",
            style=MessageStyle.ROI,
            description="ROI-focused: 'Recover $5K-15K/month in missed revenue'",
        ),
    ]
    
    def __init__(self):
        self.sim_engine = SimulationEngine()
        self.msg_generator = MessageGeneratorV2()
        self.scorer = LeadScoringEngine()
        self.tests: List[ABTest] = []
        os.makedirs(os.path.join(os.path.dirname(__file__), "data"), exist_ok=True)
    
    def create_test(
        self,
        name: str,
        leads: List[ScoredLead],
        variants: List[Variant] = None,
    ) -> ABTest:
        """Create a new A/B test."""
        if variants is None:
            variants = self.DEFAULT_VARIANTS
        
        test = ABTest(
            test_id=f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name=name,
            status=TestStatus.DRAFT,
            variants=variants,
            results=[],
            created_at=datetime.now().isoformat(),
        )
        
        self.tests.append(test)
        return test
    
    def run_test(self, test: ABTest, leads: List[ScoredLead]) -> ABTest:
        """Run the A/B test on a set of leads."""
        test.status = TestStatus.RUNNING
        test.results = []
        
        for lead in leads:
            for variant in test.variants:
                # Create prediction input
                pred_input = PredictionInput(
                    tier=lead.tier,
                    country=lead.clinic.country,
                    message_style=variant.style,
                    touch_stage=TouchStage.FIRST_MESSAGE,
                    pain_score=lead.total_score,
                )
                
                # Get prediction
                prediction = self.sim_engine.predict(pred_input)
                
                # Record result
                result = TestResult(
                    variant_name=variant.name,
                    lead_name=lead.clinic.name,
                    tier=lead.tier.value,
                    accept_prob=prediction.accept_probability,
                    reply_prob=prediction.reply_probability,
                    demo_prob=prediction.demo_probability,
                    close_prob=prediction.close_probability,
                )
                test.results.append(result)
        
        # Calculate summary
        test.summary = self._calculate_summary(test)
        test.winner = self._find_winner(test)
        test.status = TestStatus.COMPLETED
        test.completed_at = datetime.now().isoformat()
        
        return test
    
    def _calculate_summary(self, test: ABTest) -> Dict:
        """Calculate summary stats for each variant."""
        summaries = {}
        
        for variant in test.variants:
            variant_results = [r for r in test.results if r.variant_name == variant.name]
            
            if not variant_results:
                continue
            
            n = len(variant_results)
            avg_accept = sum(r.accept_prob for r in variant_results) / n
            avg_reply = sum(r.reply_prob for r in variant_results) / n
            avg_demo = sum(r.demo_prob for r in variant_results) / n
            avg_close = sum(r.close_prob for r in variant_results) / n
            
            summaries[variant.name] = {
                "variant": variant.name,
                "style": variant.style.value,
                "description": variant.description,
                "total_leads": n,
                "avg_accept": round(avg_accept, 4),
                "avg_reply": round(avg_reply, 4),
                "avg_demo": round(avg_demo, 4),
                "avg_close": round(avg_close, 4),
            }
        
        # Calculate wins per variant
        lead_names = list(set(r.lead_name for r in test.results))
        wins = {v.name: 0 for v in test.variants}
        
        for lead_name in lead_names:
            lead_results = [r for r in test.results if r.lead_name == lead_name]
            if lead_results:
                best = max(lead_results, key=lambda r: r.reply_prob)
                wins[best.variant_name] += 1
        
        for variant_name, win_count in wins.items():
            if variant_name in summaries:
                summaries[variant_name]["wins"] = win_count
                summaries[variant_name]["win_rate"] = round(win_count / len(lead_names), 4) if lead_names else 0
        
        return summaries
    
    def _find_winner(self, test: ABTest) -> Optional[str]:
        """Find the winning variant."""
        if not test.summary:
            return None
        
        best_variant = None
        best_score = -1
        
        for variant_name, stats in test.summary.items():
            # Score = weighted combination of reply + demo
            score = stats.get("avg_reply", 0) * 0.6 + stats.get("avg_demo", 0) * 0.4
            if score > best_score:
                best_score = score
                best_variant = variant_name
        
        return best_variant
    
    def compare_by_tier(self, test: ABTest) -> Dict:
        """Compare variants broken down by tier."""
        tiers = {}
        
        for tier in ["A", "B", "C"]:
            tier_results = [r for r in test.results if r.tier == tier]
            if not tier_results:
                continue
            
            tier_summary = {}
            for variant in test.variants:
                variant_results = [r for r in tier_results if r.variant_name == variant.name]
                if variant_results:
                    n = len(variant_results)
                    tier_summary[variant.name] = {
                        "avg_reply": round(sum(r.reply_prob for r in variant_results) / n, 4),
                        "avg_demo": round(sum(r.demo_prob for r in variant_results) / n, 4),
                        "count": n,
                    }
            
            # Find winner for this tier
            if tier_summary:
                best = max(tier_summary.items(), key=lambda x: x[1]["avg_reply"])
                tier_summary["winner"] = best[0]
            
            tiers[f"tier_{tier}"] = tier_summary
        
        return tiers
    
    def compare_by_country(self, test: ABTest) -> Dict:
        """Compare variants broken down by country."""
        countries = {}
        
        for result in test.results:
            # We need country from lead, but we only have lead_name
            # This is a simplified version
            pass
        
        return countries  # Placeholder for future implementation
    
    def get_recommendations(self, test: ABTest) -> List[str]:
        """Get actionable recommendations from test results."""
        recommendations = []
        
        if not test.summary or not test.winner:
            return ["No clear winner found. Need more data."]
        
        winner_stats = test.summary[test.winner]
        
        # Main recommendation
        recommendations.append(
            f"USE {test.winner.upper()} MESSAGES: "
            f"Reply rate {winner_stats['avg_reply']*100:.1f}% vs others"
        )
        
        # Tier-specific recommendations
        tier_comparison = self.compare_by_tier(test)
        for tier_key, tier_data in tier_comparison.items():
            if "winner" in tier_data:
                recommendations.append(
                    f"For {tier_key}: use {tier_data['winner']} messages"
                )
        
        # Performance insight
        all_replies = [s["avg_reply"] for s in test.summary.values()]
        if max(all_replies) - min(all_replies) > 0.05:
            recommendations.append(
                "Large performance gap between variants - message style matters significantly"
            )
        else:
            recommendations.append(
                "Small performance gap - other factors (timing, targeting) may matter more"
            )
        
        return recommendations
    
    def export_test(self, test: ABTest, filepath: str = None):
        """Export test results to JSON."""
        if filepath is None:
            filepath = os.path.join(
                os.path.dirname(__file__), "data", f"{test.test_id}.json"
            )
        
        data = {
            "test_id": test.test_id,
            "name": test.name,
            "status": test.status.value,
            "created_at": test.created_at,
            "completed_at": test.completed_at,
            "winner": test.winner,
            "summary": test.summary,
            "tier_analysis": self.compare_by_tier(test),
            "recommendations": self.get_recommendations(test),
            "results": [asdict(r) for r in test.results],
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        
        return filepath


def demo_ab_test():
    """Demo the A/B testing engine."""
    engine = ABTestingEngine()
    
    # Create sample leads
    leads = [
        ScoredLead(
            clinic=ClinicData(name="Smile Dental NYC", country="USA", city="New York"),
            total_score=85,
            tier=Tier.A,
            score_breakdown={},
            pain_signals=["No online booking"],
            recommended_approach="Direct pain-based",
            estimated_deal_size="$1,500-3,000/month",
        ),
        ScoredLead(
            clinic=ClinicData(name="Downtown Dental", country="USA", city="Chicago"),
            total_score=75,
            tier=Tier.A,
            score_breakdown={},
            pain_signals=["No contact form"],
            recommended_approach="Direct pain-based",
            estimated_deal_size="$1,500-3,000/month",
        ),
        ScoredLead(
            clinic=ClinicData(name="Family Dentist", country="UK", city="London"),
            total_score=55,
            tier=Tier.B,
            score_breakdown={},
            pain_signals=["Limited hours"],
            recommended_approach="Soft curiosity",
            estimated_deal_size="$500-1,500/month",
        ),
        ScoredLead(
            clinic=ClinicData(name="Metro Chain", country="USA", city="LA"),
            total_score=15,
            tier=Tier.C,
            score_breakdown={},
            pain_signals=[],
            recommended_approach="Skip",
            estimated_deal_size="Low",
        ),
    ]
    
    # Create and run test
    print("=" * 60)
    print("A/B TESTING ENGINE")
    print("=" * 60)
    
    test = engine.create_test(
        name="Pain vs Soft vs ROI - Multi-market",
        leads=leads,
    )
    
    test = engine.run_test(test, leads)
    
    # Print results
    print(f"\nTest: {test.name}")
    print(f"Status: {test.status.value}")
    print(f"Winner: {test.winner}")
    
    print(f"\n--- Variant Performance ---")
    for variant_name, stats in test.summary.items():
        print(f"\n{variant_name.upper()}:")
        print(f"  Reply: {stats['avg_reply']*100:.1f}%")
        print(f"  Demo:  {stats['avg_demo']*100:.1f}%")
        print(f"  Wins:  {stats.get('wins', 0)}/{stats['total_leads']}")
    
    # Tier analysis
    print(f"\n--- Tier Analysis ---")
    tier_analysis = engine.compare_by_tier(test)
    for tier_key, tier_data in tier_analysis.items():
        if "winner" in tier_data:
            print(f"{tier_key}: winner = {tier_data['winner']}")
    
    # Recommendations
    print(f"\n--- Recommendations ---")
    for rec in engine.get_recommendations(test):
        print(f"  - {rec}")
    
    # Export
    filepath = engine.export_test(test)
    print(f"\nExported to: {filepath}")


if __name__ == "__main__":
    demo_ab_test()
