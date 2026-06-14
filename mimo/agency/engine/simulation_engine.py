"""
Simulation Engine v1 - Predictive response model.
Predicts outcomes before sending outreach.
"""
import json
import os
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

import sys
sys.path.insert(0, os.path.dirname(__file__))
from lead_scorer import Tier, ScoredLead, ClinicData
from message_generator import MessageStyle


class TouchStage(Enum):
    CONNECTION = "connection"
    FIRST_MESSAGE = "first_message"
    FOLLOWUP_1 = "followup_1"
    FOLLOWUP_2 = "followup_2"


class ResponseType(Enum):
    ACCEPT = "accept"
    DECLINE = "decline"
    IGNORE = "ignore"
    REPLY_POSITIVE = "reply_positive"
    REPLY_NEUTRAL = "reply_neutral"
    REPLY_NEGATIVE = "reply_negative"
    NO_RESPONSE = "no_response"
    BOOK_DEMO = "book_demo"
    CLOSE_DEAL = "close_deal"


@dataclass
class PredictionInput:
    """Input for prediction."""
    tier: Tier
    country: str
    message_style: MessageStyle
    touch_stage: TouchStage
    pain_score: int = 50  # 0-100


@dataclass
class PredictionOutput:
    """Output prediction."""
    input_data: PredictionInput
    accept_probability: float
    reply_probability: float
    demo_probability: float
    close_probability: float
    likely_response: ResponseType
    expected_replies_per_100: float
    expected_demos_per_100: float
    confidence: str  # high, medium, low


class SimulationEngine:
    """
    Predictive model for outreach outcomes.
    
    Uses rule-based probability model calibrated to industry benchmarks:
    - Cold LinkedIn: 15-25% accept, 5-15% reply
    - Pain-based: higher reply but lower accept
    - Soft: higher accept but lower reply
    """
    
    # === BASE PROBABILITIES BY TIER ===
    
    TIER_BASE = {
        Tier.A: {"accept": 0.35, "reply": 0.20, "demo": 0.08, "close": 0.03},
        Tier.B: {"accept": 0.20, "reply": 0.10, "demo": 0.03, "close": 0.01},
        Tier.C: {"accept": 0.05, "reply": 0.02, "demo": 0.005, "close": 0.001},
    }
    
    # === COUNTRY MODIFIERS ===
    
    COUNTRY_MOD = {
        "USA": 1.0,
        "UK": 0.95,
        "Canada": 0.95,
        "Australia": 0.95,
        "Ireland": 0.9,
        "Russia": 0.75,
        "Kyrgyzstan": 0.6,
    }
    
    # === MESSAGE STYLE MODIFIERS ===
    
    STYLE_MOD = {
        MessageStyle.PAIN: {"accept": 0.85, "reply": 1.25, "demo": 1.1, "close": 1.2},
        MessageStyle.SOFT: {"accept": 1.15, "reply": 0.80, "demo": 0.9, "close": 0.85},
        MessageStyle.ROI: {"accept": 0.90, "reply": 1.15, "demo": 1.2, "close": 1.3},
    }
    
    # === TOUCH STAGE MODIFIERS ===
    
    STAGE_MOD = {
        TouchStage.CONNECTION: {"accept": 1.0, "reply": 0.0, "demo": 0.0, "close": 0.0},
        TouchStage.FIRST_MESSAGE: {"accept": 1.0, "reply": 1.0, "demo": 1.0, "close": 1.0},
        TouchStage.FOLLOWUP_1: {"accept": 1.0, "reply": 0.7, "demo": 0.8, "close": 0.7},
        TouchStage.FOLLOWUP_2: {"accept": 1.0, "reply": 0.5, "demo": 0.6, "close": 0.5},
    }
    
    # === PAIN SCORE MODIFIER ===
    
    def pain_modifier(self, pain_score: int) -> float:
        """Higher pain = higher reply probability."""
        return 0.7 + (pain_score / 100) * 0.6  # 0.7 to 1.3
    
    # === LIKELY RESPONSE TYPE ===
    
    RESPONSE_BY_TIER = {
        Tier.A: {
            TouchStage.CONNECTION: ResponseType.ACCEPT,
            TouchStage.FIRST_MESSAGE: ResponseType.REPLY_POSITIVE,
            TouchStage.FOLLOWUP_1: ResponseType.REPLY_NEUTRAL,
            TouchStage.FOLLOWUP_2: ResponseType.REPLY_NEGATIVE,
        },
        Tier.B: {
            TouchStage.CONNECTION: ResponseType.ACCEPT,
            TouchStage.FIRST_MESSAGE: ResponseType.REPLY_NEUTRAL,
            TouchStage.FOLLOWUP_1: ResponseType.NO_RESPONSE,
            TouchStage.FOLLOWUP_2: ResponseType.NO_RESPONSE,
        },
        Tier.C: {
            TouchStage.CONNECTION: ResponseType.IGNORE,
            TouchStage.FIRST_MESSAGE: ResponseType.NO_RESPONSE,
            TouchStage.FOLLOWUP_1: ResponseType.NO_RESPONSE,
            TouchStage.FOLLOWUP_2: ResponseType.NO_RESPONSE,
        },
    }
    
    def predict(self, input_data: PredictionInput) -> PredictionOutput:
        """Make a prediction based on input."""
        tier = input_data.tier
        country = input_data.country
        style = input_data.message_style
        stage = input_data.touch_stage
        pain = input_data.pain_score
        
        # Get base probabilities
        base = self.TIER_BASE[tier].copy()
        
        # Apply country modifier
        country_mod = self.COUNTRY_MOD.get(country, 0.8)
        for key in base:
            base[key] *= country_mod
        
        # Apply style modifier
        style_mod = self.STYLE_MOD[style]
        for key in base:
            base[key] *= style_mod[key]
        
        # Apply stage modifier
        stage_mod = self.STAGE_MOD[stage]
        for key in base:
            base[key] *= stage_mod[key]
        
        # Apply pain modifier (affects reply and demo)
        pain_mod = self.pain_modifier(pain)
        base["reply"] *= pain_mod
        base["demo"] *= pain_mod
        base["close"] *= pain_mod
        
        # Clamp to valid ranges
        accept_prob = min(0.60, max(0.01, base["accept"]))
        reply_prob = min(0.35, max(0.005, base["reply"]))
        demo_prob = min(0.15, max(0.001, base["demo"]))
        close_prob = min(0.08, max(0.0005, base["close"]))
        
        # Determine likely response
        likely_response = self.RESPONSE_BY_TIER[tier].get(stage, ResponseType.NO_RESPONSE)
        
        # Calculate per-100 metrics
        expected_replies = reply_prob * 100
        expected_demos = demo_prob * 100
        
        # Confidence level
        if tier == Tier.A:
            confidence = "high"
        elif tier == Tier.B:
            confidence = "medium"
        else:
            confidence = "low"
        
        return PredictionOutput(
            input_data=input_data,
            accept_probability=round(accept_prob, 4),
            reply_probability=round(reply_prob, 4),
            demo_probability=round(demo_prob, 4),
            close_probability=round(close_prob, 4),
            likely_response=likely_response,
            expected_replies_per_100=round(expected_replies, 2),
            expected_demos_per_100=round(expected_demos, 2),
            confidence=confidence,
        )
    
    def simulate_campaign(
        self,
        leads: List[ScoredLead],
        message_style: MessageStyle = MessageStyle.PAIN,
    ) -> Dict:
        """Simulate a full campaign with multiple leads."""
        results = []
        
        for lead in leads:
            # Connection stage
            conn_input = PredictionInput(
                tier=lead.tier,
                country=lead.clinic.country,
                message_style=message_style,
                touch_stage=TouchStage.CONNECTION,
                pain_score=lead.total_score,
            )
            conn_pred = self.predict(conn_input)
            
            # First message stage
            msg_input = PredictionInput(
                tier=lead.tier,
                country=lead.clinic.country,
                message_style=message_style,
                touch_stage=TouchStage.FIRST_MESSAGE,
                pain_score=lead.total_score,
            )
            msg_pred = self.predict(msg_input)
            
            results.append({
                "clinic": lead.clinic.name,
                "tier": lead.tier.value,
                "score": lead.total_score,
                "country": lead.clinic.country,
                "connection_accept_prob": conn_pred.accept_probability,
                "reply_prob": msg_pred.reply_probability,
                "demo_prob": msg_pred.demo_probability,
                "close_prob": msg_pred.close_probability,
                "expected_replies": msg_pred.expected_replies_per_100,
            })
        
        # Aggregate stats
        total_leads = len(results)
        tier_counts = {"A": 0, "B": 0, "C": 0}
        for r in results:
            tier_counts[r["tier"]] += 1
        
        avg_reply = sum(r["reply_prob"] for r in results) / total_leads if total_leads else 0
        avg_demo = sum(r["demo_prob"] for r in results) / total_leads if total_leads else 0
        
        return {
            "summary": {
                "total_leads": total_leads,
                "tier_distribution": tier_counts,
                "avg_reply_probability": round(avg_reply, 4),
                "avg_demo_probability": round(avg_demo, 4),
                "expected_total_replies": round(avg_reply * total_leads, 1),
                "expected_total_demos": round(avg_demo * total_leads, 1),
            },
            "leads": results,
        }
    
    def compare_strategies(
        self,
        leads: List[ScoredLead],
    ) -> Dict:
        """Compare pain vs soft vs ROI strategies."""
        strategies = {}
        
        for style in [MessageStyle.PAIN, MessageStyle.SOFT, MessageStyle.ROI]:
            campaign = self.simulate_campaign(leads, message_style=style)
            strategies[style.value] = campaign["summary"]
        
        return strategies


def demo_simulation():
    """Demo the simulation engine."""
    engine = SimulationEngine()
    
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
            clinic=ClinicData(name="Perfect Teeth", country="USA", city="Chicago"),
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
    
    # Single prediction
    print("=" * 60)
    print("SINGLE PREDICTION")
    print("=" * 60)
    
    pred_input = PredictionInput(
        tier=Tier.A,
        country="USA",
        message_style=MessageStyle.PAIN,
        touch_stage=TouchStage.FIRST_MESSAGE,
        pain_score=85,
    )
    
    result = engine.predict(pred_input)
    print(f"\nTier A, USA, Pain message, First touch:")
    print(f"  Accept prob: {result.accept_probability*100:.1f}%")
    print(f"  Reply prob:  {result.reply_probability*100:.1f}%")
    print(f"  Demo prob:   {result.demo_probability*100:.1f}%")
    print(f"  Close prob:  {result.close_probability*100:.1f}%")
    print(f"  Likely:      {result.likely_response.value}")
    print(f"  Per 100:     {result.expected_replies_per_100:.1f} replies, {result.expected_demos_per_100:.1f} demos")
    
    # Campaign simulation
    print(f"\n{'=' * 60}")
    print("CAMPAIGN SIMULATION (3 leads)")
    print("=" * 60)
    
    campaign = engine.simulate_campaign(leads)
    print(f"\nTotal leads: {campaign['summary']['total_leads']}")
    print(f"Tiers: {campaign['summary']['tier_distribution']}")
    print(f"Avg reply prob: {campaign['summary']['avg_reply_probability']*100:.1f}%")
    print(f"Avg demo prob: {campaign['summary']['avg_demo_probability']*100:.1f}%")
    print(f"Expected replies: {campaign['summary']['expected_total_replies']}")
    print(f"Expected demos: {campaign['summary']['expected_total_demos']}")
    
    # Strategy comparison
    print(f"\n{'=' * 60}")
    print("STRATEGY COMPARISON")
    print("=" * 60)
    
    comparison = engine.compare_strategies(leads)
    for strategy, stats in comparison.items():
        print(f"\n{strategy.upper()}:")
        print(f"  Reply prob: {stats['avg_reply_probability']*100:.1f}%")
        print(f"  Demo prob: {stats['avg_demo_probability']*100:.1f}%")
        print(f"  Expected replies/100: {stats['expected_total_replies']:.1f}")
    
    # Export
    filepath = os.path.join(os.path.dirname(__file__), "data", "simulation_results.json")
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        json.dump({
            "campaign": campaign,
            "comparison": comparison,
        }, f, indent=2)
    
    print(f"\nExported to: {filepath}")


if __name__ == "__main__":
    demo_simulation()
