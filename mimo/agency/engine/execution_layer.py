"""
Execution Layer - Bridge between simulation and real-world outreach.
Handles: export, tracking, feedback input, model correction.
"""
import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict, field
from enum import Enum
from datetime import datetime

import sys
sys.path.insert(0, os.path.dirname(__file__))
from lead_scorer import Tier, ScoredLead, ClinicData
from message_generator import MessageGeneratorV2, MessageStyle
from simulation_engine import SimulationEngine, PredictionInput, TouchStage


class OutreachStatus(Enum):
    PENDING = "pending"
    CONNECTION_SENT = "connection_sent"
    CONNECTION_ACCEPTED = "connection_accepted"
    CONNECTION_DECLINED = "connection_declined"
    MESSAGE_SENT = "message_sent"
    REPLY_POSITIVE = "reply_positive"
    REPLY_NEUTRAL = "reply_neutral"
    REPLY_NEGATIVE = "reply_negative"
    NO_RESPONSE = "no_response"
    DEMO_BOOKED = "demo_booked"
    DEAL_CLOSED = "deal_closed"
    LOST = "lost"


@dataclass
class OutreachRecord:
    """Record of a single outreach attempt."""
    lead_name: str
    country: str
    tier: str
    message_style: str
    status: OutreachStatus
    sent_at: str = ""
    responded_at: str = ""
    notes: str = ""
    
    # Actual outcomes (for feedback)
    actual_accept: Optional[bool] = None
    actual_reply: Optional[bool] = None
    actual_reply_type: Optional[str] = None  # positive/neutral/negative
    actual_demo: Optional[bool] = None
    actual_close: Optional[bool] = None
    
    # Prediction vs actual
    predicted_reply_prob: Optional[float] = None
    prediction_error: Optional[float] = None


@dataclass
class FeedbackEntry:
    """Real-world feedback for model correction."""
    lead_name: str
    actual_outcome: str
    predicted_outcome: str
    error_margin: float
    tier: str
    country: str
    message_style: str
    timestamp: str = ""
    notes: str = ""


class ExecutionLayer:
    """
    Bridges simulation and real-world outreach.
    
    Functions:
    1. Export ready-to-send messages
    2. Track outreach status
    3. Input real-world feedback
    4. Calculate prediction errors
    5. Generate learning signals for model correction
    """
    
    def __init__(self):
        self.records: List[OutreachRecord] = []
        self.feedback: List[FeedbackEntry] = []
        self.data_dir = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(self.data_dir, exist_ok=True)
    
    # === EXPORT ===
    
    def export_for_sending(
        self,
        leads: List[ScoredLead],
        message_style: MessageStyle = MessageStyle.PAIN,
    ) -> List[Dict]:
        """
        Export leads with ready-to-send messages.
        Returns list of dicts with lead info + messages.
        """
        generator = MessageGeneratorV2()
        sim_engine = SimulationEngine()
        
        export_data = []
        
        for lead in leads:
            # Generate messages
            msg = generator.generate_for_lead(lead)
            if not msg:
                continue  # Skip C-tier
            
            # Get prediction
            pred_input = PredictionInput(
                tier=lead.tier,
                country=lead.clinic.country,
                message_style=message_style,
                touch_stage=TouchStage.FIRST_MESSAGE,
                pain_score=lead.total_score,
            )
            prediction = sim_engine.predict(pred_input)
            
            export_data.append({
                "lead": {
                    "name": lead.clinic.name,
                    "country": lead.clinic.country,
                    "city": lead.clinic.city,
                    "website": lead.clinic.website,
                    "owner_name": lead.clinic.owner_name,
                    "owner_linkedin": lead.clinic.owner_linkedin,
                    "tier": lead.tier.value,
                    "score": lead.total_score,
                },
                "messages": {
                    "connection_request": msg.connection_request,
                    "first_message": msg.first_message,
                    "followup_1": msg.followup_1,
                    "followup_2": msg.followup_2,
                },
                "prediction": {
                    "accept_prob": prediction.accept_probability,
                    "reply_prob": prediction.reply_probability,
                    "demo_prob": prediction.demo_probability,
                },
                "status": OutreachStatus.PENDING.value,
            })
        
        # Save to file
        filepath = os.path.join(self.data_dir, "outreach_queue.json")
        with open(filepath, "w") as f:
            json.dump(export_data, f, indent=2)
        
        return export_data
    
    # === TRACKING ===
    
    def log_connection_sent(self, lead_name: str, country: str, tier: str, style: str):
        """Log that connection request was sent."""
        record = OutreachRecord(
            lead_name=lead_name,
            country=country,
            tier=tier,
            message_style=style,
            status=OutreachStatus.CONNECTION_SENT,
            sent_at=datetime.now().isoformat(),
        )
        self.records.append(record)
    
    def log_connection_response(self, lead_name: str, accepted: bool):
        """Log connection response."""
        for record in reversed(self.records):
            if record.lead_name == lead_name and record.status == OutreachStatus.CONNECTION_SENT:
                record.status = OutreachStatus.CONNECTION_ACCEPTED if accepted else OutreachStatus.CONNECTION_DECLINED
                record.responded_at = datetime.now().isoformat()
                record.actual_accept = accepted
                break
    
    def log_message_sent(self, lead_name: str):
        """Log that first message was sent."""
        for record in reversed(self.records):
            if record.lead_name == lead_name and record.status == OutreachStatus.CONNECTION_ACCEPTED:
                record.status = OutreachStatus.MESSAGE_SENT
                break
    
    def log_reply(self, lead_name: str, reply_type: str):
        """Log a reply (positive/neutral/negative)."""
        status_map = {
            "positive": OutreachStatus.REPLY_POSITIVE,
            "neutral": OutreachStatus.REPLY_NEUTRAL,
            "negative": OutreachStatus.REPLY_NEGATIVE,
        }
        for record in reversed(self.records):
            if record.lead_name == lead_name and record.status == OutreachStatus.MESSAGE_SENT:
                record.status = status_map.get(reply_type, OutreachStatus.NO_RESPONSE)
                record.responded_at = datetime.now().isoformat()
                record.actual_reply = True
                record.actual_reply_type = reply_type
                break
    
    def log_no_response(self, lead_name: str):
        """Log no response after follow-up period."""
        for record in reversed(self.records):
            if record.lead_name == lead_name:
                if record.status in [OutreachStatus.MESSAGE_SENT, OutreachStatus.NO_RESPONSE]:
                    record.status = OutreachStatus.NO_RESPONSE
                    record.actual_reply = False
                    break
    
    def log_demo_booked(self, lead_name: str):
        """Log demo booking."""
        for record in reversed(self.records):
            if record.lead_name == lead_name:
                record.status = OutreachStatus.DEMO_BOOKED
                record.actual_demo = True
                break
    
    def log_deal_closed(self, lead_name: str):
        """Log deal closure."""
        for record in reversed(self.records):
            if record.lead_name == lead_name:
                record.status = OutreachStatus.DEAL_CLOSED
                record.actual_close = True
                break
    
    # === FEEDBACK LOOP ===
    
    def submit_feedback(
        self,
        lead_name: str,
        actual_outcome: str,
        predicted_outcome: str,
        tier: str,
        country: str,
        message_style: str,
        notes: str = "",
    ):
        """
        Submit real-world feedback for model learning.
        
        actual_outcome: what actually happened
        predicted_outcome: what the model predicted
        """
        error_margin = 0.0
        if predicted_outcome != actual_outcome:
            error_margin = 1.0  # Full error if wrong
        
        feedback = FeedbackEntry(
            lead_name=lead_name,
            actual_outcome=actual_outcome,
            predicted_outcome=predicted_outcome,
            error_margin=error_margin,
            tier=tier,
            country=country,
            message_style=message_style,
            timestamp=datetime.now().isoformat(),
            notes=notes,
        )
        self.feedback.append(feedback)
    
    def get_prediction_accuracy(self) -> Dict:
        """Calculate overall prediction accuracy."""
        if not self.feedback:
            return {"total": 0, "accuracy": 0.0}
        
        correct = sum(1 for f in self.feedback if f.error_margin == 0)
        total = len(self.feedback)
        
        return {
            "total": total,
            "correct": correct,
            "accuracy": round(correct / total, 4),
            "error_rate": round(1 - correct / total, 4),
        }
    
    def get_accuracy_by_tier(self) -> Dict:
        """Get accuracy broken down by tier."""
        tier_stats = {}
        
        for tier in ["A", "B", "C"]:
            tier_feedback = [f for f in self.feedback if f.tier == tier]
            if tier_feedback:
                correct = sum(1 for f in tier_feedback if f.error_margin == 0)
                tier_stats[f"tier_{tier}"] = {
                    "total": len(tier_feedback),
                    "correct": correct,
                    "accuracy": round(correct / len(tier_feedback), 4),
                }
        
        return tier_stats
    
    def get_learning_signals(self) -> List[Dict]:
        """
        Generate learning signals for model correction.
        Identifies where predictions were wrong and why.
        """
        signals = []
        
        for f in self.feedback:
            if f.error_margin > 0:  # Wrong prediction
                signal = {
                    "lead": f.lead_name,
                    "tier": f.tier,
                    "country": f.country,
                    "style": f.message_style,
                    "predicted": f.predicted_outcome,
                    "actual": f.actual_outcome,
                    "timestamp": f.timestamp,
                }
                signals.append(signal)
        
        return signals
    
    # === ANALYTICS ===
    
    def get_funnel_stats(self) -> Dict:
        """Get outreach funnel statistics."""
        status_counts = {}
        for record in self.records:
            status = record.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        total = len(self.records)
        sent = status_counts.get("connection_sent", 0)
        accepted = status_counts.get("connection_accepted", 0)
        messaged = status_counts.get("message_sent", 0)
        replied = (
            status_counts.get("reply_positive", 0) +
            status_counts.get("reply_neutral", 0) +
            status_counts.get("reply_negative", 0)
        )
        demos = status_counts.get("demo_booked", 0)
        closed = status_counts.get("deal_closed", 0)
        
        return {
            "total_records": total,
            "connection_accept_rate": round(accepted / sent, 4) if sent > 0 else 0,
            "reply_rate": round(replied / messaged, 4) if messaged > 0 else 0,
            "demo_rate": round(demos / messaged, 4) if messaged > 0 else 0,
            "close_rate": round(closed / messaged, 4) if messaged > 0 else 0,
            "status_counts": status_counts,
        }
    
    def export_analytics(self) -> Dict:
        """Export full analytics report."""
        return {
            "funnel": self.get_funnel_stats(),
            "prediction_accuracy": self.get_prediction_accuracy(),
            "accuracy_by_tier": self.get_accuracy_by_tier(),
            "learning_signals": self.get_learning_signals(),
            "total_feedback": len(self.feedback),
        }
    
    def save_state(self):
        """Save execution state to disk."""
        def serialize_record(r):
            d = asdict(r)
            d["status"] = r.status.value
            return d
        
        def serialize_feedback(f):
            d = asdict(f)
            return d
        
        state = {
            "records": [serialize_record(r) for r in self.records],
            "feedback": [serialize_feedback(f) for f in self.feedback],
            "saved_at": datetime.now().isoformat(),
        }
        
        filepath = os.path.join(self.data_dir, "execution_state.json")
        with open(filepath, "w") as f:
            json.dump(state, f, indent=2)
    
    def load_state(self):
        """Load execution state from disk."""
        filepath = os.path.join(self.data_dir, "execution_state.json")
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                state = json.load(f)
            
            self.records = [OutreachRecord(**r) for r in state.get("records", [])]
            self.feedback = [FeedbackEntry(**fb) for fb in state.get("feedback", [])]


def demo_execution():
    """Demo the execution layer."""
    engine = ExecutionLayer()
    
    # Create sample leads
    leads = [
        ScoredLead(
            clinic=ClinicData(
                name="Smile Dental NYC",
                country="USA",
                city="New York",
                owner_name="Dr. Smith",
            ),
            total_score=85,
            tier=Tier.A,
            score_breakdown={},
            pain_signals=["No online booking"],
            recommended_approach="Direct pain-based",
            estimated_deal_size="$1,500-3,000/month",
        ),
    ]
    
    print("=" * 60)
    print("EXECUTION LAYER DEMO")
    print("=" * 60)
    
    # Export for sending
    print("\n1. EXPORT FOR SENDING")
    export = engine.export_for_sending(leads)
    print(f"   Exported {len(export)} leads")
    for item in export:
        print(f"   - {item['lead']['name']} ({item['lead']['tier']})")
        print(f"     Connection: {item['messages']['connection_request'][:50]}...")
    
    # Simulate outreach
    print("\n2. SIMULATE OUTREACH")
    engine.log_connection_sent("Smile Dental NYC", "USA", "A", "pain")
    engine.log_connection_response("Smile Dental NYC", accepted=True)
    engine.log_message_sent("Smile Dental NYC")
    engine.log_reply("Smile Dental NYC", "positive")
    engine.log_demo_booked("Smile Dental NYC")
    
    # Submit feedback
    print("\n3. SUBMIT FEEDBACK")
    engine.submit_feedback(
        lead_name="Smile Dental NYC",
        actual_outcome="reply_positive",
        predicted_outcome="reply_positive",
        tier="A",
        country="USA",
        message_style="pain",
        notes="They responded within 2 hours"
    )
    
    # Get analytics
    print("\n4. ANALYTICS")
    analytics = engine.export_analytics()
    print(f"   Funnel: {analytics['funnel']}")
    print(f"   Accuracy: {analytics['prediction_accuracy']}")
    print(f"   Learning signals: {len(analytics['learning_signals'])}")
    
    # Save state
    engine.save_state()
    print(f"\n   State saved to data/execution_state.json")


if __name__ == "__main__":
    demo_execution()
