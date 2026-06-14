"""
RCP-1: Reality Calibration Protocol
One country. 10 leads. One message style. Compare with simulation.
"""
import json
import os
from typing import Dict, List
from dataclasses import dataclass, asdict
from datetime import datetime

import sys
sys.path.insert(0, os.path.dirname(__file__))
from lead_scorer import LeadScoringEngine, ClinicData, ScoredLead, Tier
from message_generator import MessageGeneratorV2, MessageStyle
from simulation_engine import SimulationEngine, PredictionInput, TouchStage


@dataclass
class CalibrationLead:
    """Lead for calibration run."""
    name: str
    country: str
    city: str
    website: str
    phone: str
    address: str
    rating: float
    review_count: int
    has_online_booking: bool
    owner_name: str = ""
    owner_linkedin: str = ""
    notes: str = ""


@dataclass
class CalibrationResult:
    """Result of outreach to a calibration lead."""
    lead_name: str
    status: str  # pending/sent/accepted/replied/demo/closed
    
    # Simulation predictions
    predicted_accept: float
    predicted_reply: float
    predicted_demo: float
    
    # Actual outcomes (filled manually)
    actual_accept: bool = None
    actual_reply: bool = None
    actual_reply_type: str = None  # positive/neutral/negative
    actual_demo: bool = None
    
    # Metadata
    sent_at: str = ""
    responded_at: str = ""
    notes: str = ""


class RealityCalibrationProtocol:
    """
    RCP-1: Reality Calibration Protocol
    
    Purpose: Validate simulation model against real-world data.
    Scope: 1 country, 10 leads, 1 message style.
    """
    
    # Kyrgyzstan clinics from 2GIS
    KYRGYZSTAN_CLINICS = [
        CalibrationLead(
            name="Али-Дент",
            country="Kyrgyzstan",
            city="Bishkek",
            website="ali-dent.kg",
            phone="+996 312 00 00 00",
            address="ул. Фрунзе 364/3",
            rating=4.7,
            review_count=335,
            has_online_booking=False,
            notes="2 филиала, ортодонт + хирург"
        ),
        CalibrationLead(
            name="Life Stom",
            country="Kyrgyzstan",
            city="Bishkek",
            website="lifestom.kg",
            phone="+996 555 00 00 00",
            address="ул. Анарбека Бакаева 130/2",
            rating=4.9,
            review_count=261,
            has_online_booking=False,
            notes="Круглосуточно, современное оборудование"
        ),
        CalibrationLead(
            name="Olio",
            country="Kyrgyzstan",
            city="Bishkek",
            website="olio.kg",
            phone="+996 700 00 00 00",
            address="ул. Ибраимова 103/1а",
            rating=5.0,
            review_count=61,
            has_online_booking=False,
            notes="Экспертный уровень, детям и взрослым"
        ),
        CalibrationLead(
            name="Эксперт Дентал Студия",
            country="Kyrgyzstan",
            city="Bishkek",
            website="expertdental.kg",
            phone="+996 500 00 00 00",
            address="Киевская ул. 88",
            rating=4.9,
            review_count=213,
            has_online_booking=False,
            notes="Имплантация, реабилитация ВНЧС"
        ),
        CalibrationLead(
            name="Emmar",
            country="Kyrgyzstan",
            city="Bishkek",
            website="emmar.kg",
            phone="+996 550 00 00 00",
            address="ул. Айтиева 17/1",
            rating=4.9,
            review_count=413,
            has_online_booking=False,
            notes="Инновационное оборудование, лечение под микроскопом"
        ),
        CalibrationLead(
            name="Metadent",
            country="Kyrgyzstan",
            city="Bishkek",
            website="metadent.kg",
            phone="+996 770 00 00 00",
            address="ул. Арстанбека Дуйшеева 8",
            rating=5.0,
            review_count=533,
            has_online_booking=False,
            notes="Комплексное лечение, Air Flow EMS"
        ),
        CalibrationLead(
            name="32 Стоматология",
            country="Kyrgyzstan",
            city="Bishkek",
            website="32.kg",
            phone="+996 505 00 00 00",
            address="ул. Исы Ахунбаева 42а",
            rating=4.8,
            review_count=129,
            has_online_booking=False,
            notes="Лечим без боли, весь спектр услуг"
        ),
        CalibrationLead(
            name="Smile Clinic",
            country="Kyrgyzstan",
            city="Bishkek",
            website="smileclinic.kg",
            phone="+996 553 00 00 00",
            address="Микрорайон Джал-23 18/2",
            rating=4.8,
            review_count=411,
            has_online_booking=False,
            notes="24/7, частный стоматолог"
        ),
        CalibrationLead(
            name="Grafdent",
            country="Kyrgyzstan",
            city="Bishkek",
            website="grafdent.kg",
            phone="+996 705 00 00 00",
            address="ул. Турусбекова 13",
            rating=4.8,
            review_count=101,
            has_online_booking=False,
            notes="Ортодонтия, ортопедия, терапия, 24/7"
        ),
        CalibrationLead(
            name="Azuu Dent",
            country="Kyrgyzstan",
            city="Bishkek",
            website="azudent.kg",
            phone="+996 557 00 00 00",
            address="Микрорайон Асанбай 8/1",
            rating=4.7,
            review_count=238,
            has_online_booking=False,
            notes="Скидка на лечение кариеса"
        ),
    ]
    
    def __init__(self):
        self.scorer = LeadScoringEngine()
        self.msg_generator = MessageGeneratorV2()
        self.sim_engine = SimulationEngine()
        self.results: List[CalibrationResult] = []
        self.data_dir = os.path.join(os.path.dirname(__file__), "data", "rcp1")
        os.makedirs(self.data_dir, exist_ok=True)
    
    def score_leads(self) -> List[ScoredLead]:
        """Score all calibration leads."""
        scored = []
        
        for clinic in self.KYRGYZSTAN_CLINICS:
            clinic_data = ClinicData(
                name=clinic.name,
                country=clinic.country,
                city=clinic.city,
                website=clinic.website,
                has_online_booking=clinic.has_online_booking,
                doctor_count=3,  # Assume small practice
                is_chain=False,
                website_quality="outdated",
                closing_hour=18,
                has_weekend_hours=False,
            )
            
            scored_lead = self.scorer.score_clinic(clinic_data)
            scored.append(scored_lead)
        
        return scored
    
    def generate_messages(self) -> Dict:
        """Generate PAIN messages for all leads."""
        scored = self.score_leads()
        messages = {}
        
        for lead in scored:
            msg = self.msg_generator.generate_for_lead(lead)
            if msg:
                messages[lead.clinic.name] = {
                    "score": lead.total_score,
                    "tier": lead.tier.value,
                    "connection_request": msg.connection_request,
                    "first_message": msg.first_message,
                }
        
        return messages
    
    def get_predictions(self) -> Dict:
        """Get simulation predictions for all leads."""
        scored = self.score_leads()
        predictions = {}
        
        for lead in scored:
            pred_input = PredictionInput(
                tier=lead.tier,
                country="Kyrgyzstan",
                message_style=MessageStyle.PAIN,
                touch_stage=TouchStage.FIRST_MESSAGE,
                pain_score=lead.total_score,
            )
            prediction = self.sim_engine.predict(pred_input)
            
            predictions[lead.clinic.name] = {
                "accept_prob": prediction.accept_probability,
                "reply_prob": prediction.reply_probability,
                "demo_prob": prediction.demo_probability,
            }
        
        return predictions
    
    def initialize_results(self):
        """Initialize calibration results for all leads."""
        predictions = self.get_predictions()
        
        self.results = []
        for clinic in self.KYRGYZSTAN_CLINICS:
            pred = predictions.get(clinic.name, {})
            
            result = CalibrationResult(
                lead_name=clinic.name,
                status="pending",
                predicted_accept=pred.get("accept_prob", 0),
                predicted_reply=pred.get("reply_prob", 0),
                predicted_demo=pred.get("demo_prob", 0),
            )
            self.results.append(result)
    
    def update_result(self, lead_name: str, **kwargs):
        """Update a lead's result with actual outcomes."""
        for result in self.results:
            if result.lead_name == lead_name:
                for key, value in kwargs.items():
                    if hasattr(result, key):
                        setattr(result, key, value)
                break
    
    def calculate_calibration(self) -> Dict:
        """Compare predictions vs actuals."""
        completed = [r for r in self.results if r.status != "pending"]
        
        if not completed:
            return {"status": "no_data"}
        
        # Calculate averages
        avg_predicted_accept = sum(r.predicted_accept for r in completed) / len(completed)
        avg_predicted_reply = sum(r.predicted_reply for r in completed) / len(completed)
        
        actual_accepts = [r.actual_accept for r in completed if r.actual_accept is not None]
        actual_replies = [r.actual_reply for r in completed if r.actual_reply is not None]
        
        actual_accept_rate = len(actual_accepts) / len(completed) if completed else 0
        actual_reply_rate = len(actual_replies) / len(completed) if completed else 0
        
        # Error calculation
        accept_error = abs(avg_predicted_accept - actual_accept_rate)
        reply_error = abs(avg_predicted_reply - actual_reply_rate)
        
        return {
            "total_leads": len(self.results),
            "completed": len(completed),
            "predictions": {
                "avg_accept": round(avg_predicted_accept, 4),
                "avg_reply": round(avg_predicted_reply, 4),
            },
            "actuals": {
                "accept_rate": round(actual_accept_rate, 4),
                "reply_rate": round(actual_reply_rate, 4),
            },
            "errors": {
                "accept_error": round(accept_error, 4),
                "reply_error": round(reply_error, 4),
            },
            "verdict": self._get_verdict(accept_error, reply_error),
        }
    
    def _get_verdict(self, accept_error: float, reply_error: float) -> str:
        """Determine if model is calibrated."""
        avg_error = (accept_error + reply_error) / 2
        
        if avg_error < 0.1:
            return "CALIBRATED - Model is accurate"
        elif avg_error < 0.2:
            return "NEAR CALIBRATED - Minor adjustment needed"
        elif avg_error < 0.3:
            return "UNCALIBRATED - Significant correction needed"
        else:
            return "POORLY CALIBRATED - Model needs major revision"
    
    def export_calibration_report(self) -> str:
        """Export full calibration report."""
        report = {
            "protocol": "RCP-1: Reality Calibration Protocol",
            "country": "Kyrgyzstan",
            "message_style": "PAIN",
            "generated_at": datetime.now().isoformat(),
            "leads": [
                {
                    "name": r.lead_name,
                    "status": r.status,
                    "predicted_accept": r.predicted_accept,
                    "predicted_reply": r.predicted_reply,
                    "actual_accept": r.actual_accept,
                    "actual_reply": r.actual_reply,
                    "notes": r.notes,
                }
                for r in self.results
            ],
            "calibration": self.calculate_calibration(),
        }
        
        filepath = os.path.join(self.data_dir, "calibration_report.json")
        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)
        
        return filepath
    
    def print_lead_list(self):
        """Print formatted lead list for manual outreach."""
        print("=" * 70)
        print("RCP-1: KYRGYZSTAN CALIBRATION LEADS (10)")
        print("=" * 70)
        
        scored = self.score_leads()
        predictions = self.get_predictions()
        
        for i, (clinic, lead) in enumerate(zip(self.KYRGYZSTAN_CLINICS, scored), 1):
            pred = predictions.get(clinic.name, {})
            name = clinic.name.encode('ascii', 'replace').decode('ascii')
            addr = clinic.address.encode('ascii', 'replace').decode('ascii')
            notes = clinic.notes.encode('ascii', 'replace').decode('ascii')
            print(f"\n{i}. {name}")
            print(f"   City: {clinic.city}")
            print(f"   Address: {addr}")
            print(f"   Website: {clinic.website}")
            print(f"   Rating: {clinic.rating} ({clinic.review_count} reviews)")
            print(f"   Online Booking: {'Yes' if clinic.has_online_booking else 'NO'}")
            print(f"   Score: {lead.total_score}/100 (Tier {lead.tier.value})")
            print(f"   Predicted Reply: {pred.get('reply_prob', 0)*100:.1f}%")
            print(f"   Notes: {notes}")
    
    def print_messages(self):
        """Print ready-to-send messages."""
        messages = self.generate_messages()
        
        print("\n" + "=" * 70)
        print("MESSAGES (PAIN STYLE)")
        print("=" * 70)
        
        for clinic_name, msg_data in messages.items():
            name = clinic_name.encode('ascii', 'replace').decode('ascii')
            cr = msg_data["connection_request"].encode('ascii', 'replace').decode('ascii')
            fm = msg_data["first_message"].encode('ascii', 'replace').decode('ascii')
            print(f"\n--- {name} (Score: {msg_data['score']}) ---")
            print(f"\n[Connection Request]")
            print(cr)
            print(f"\n[First Message]")
            print(fm)


def run_rcp1():
    """Run the Reality Calibration Protocol."""
    rcp = RealityCalibrationProtocol()
    
    # Score and display leads
    rcp.print_lead_list()
    
    # Show messages
    rcp.print_messages()
    
    # Initialize tracking
    rcp.initialize_results()
    
    # Export report
    filepath = rcp.export_calibration_report()
    print(f"\n{'=' * 70}")
    print(f"Report exported to: {filepath}")
    print(f"\nNEXT STEPS:")
    print(f"1. Send 10 connection requests (PAIN message)")
    print(f"2. Log responses in Execution Layer")
    print(f"3. Compare with simulation predictions")
    print(f"4. Run calibration report")


if __name__ == "__main__":
    run_rcp1()
