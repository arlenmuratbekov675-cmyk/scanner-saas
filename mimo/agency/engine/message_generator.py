"""
Message Generator v2 - Adaptive messaging based on lead tier.
Generates personalized outreach messages for dental clinics.
"""
import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

# Import lead scorer
import sys
sys.path.insert(0, os.path.dirname(__file__))
from lead_scorer import ClinicData, Tier, ScoredLead


class MessageStyle(Enum):
    SOFT = "soft"           # Curiosity-based, low pressure
    PAIN = "pain"           # Problem-aware, medium pressure
    ROI = "roi"             # Numbers-focused, direct


@dataclass
class Message:
    """Generated message with metadata."""
    style: MessageStyle
    tier: Tier
    connection_request: str
    first_message: str
    followup_1: str
    followup_2: str
    response_handlers: Dict[str, str]


class MessageGeneratorV2:
    """
    Generates adaptive messages based on lead score.
    
    Tier A → ROI + Pain (aggressive)
    Tier B → Soft curiosity
    Tier C → Skip / minimal
    """
    
    # === CONNECTION REQUESTS ===
    
    CONNECTION_REQUESTS = {
        "pain": {
            "USA": """Hi {name},

quick question — do you ever lose patients from missed calls or after-hours inquiries at {clinic}?""",
            "UK": """Hi {name},

quick question — do you ever lose patients from missed calls or after-hours inquiries at {clinic}?""",
            "Kyrgyzstan": """{name},

подскажите, бывает ли у вас, что пациенты не доходят из-за пропущенных звонков?""",
            "Russia": """{name},

подскажите, бывает ли у вас потеря пациентов из-за пропущенных звонков или отсутствия обратной связи?""",
            "default": """Hi {name},

quick question — do you ever lose patients from missed calls or after-hours inquiries at {clinic}?""",
        },
        "soft": {
            "default": """Hi {name},

I help dental clinics capture patients they might be missing. Would love to connect.""",
        },
        "roi": {
            "default": """Hi {name},

I help clinics recover $5K-15K/month in missed revenue. Quick question for you.""",
        },
    }
    
    # === FIRST MESSAGES ===
    
    FIRST_MESSAGES = {
        "pain": {
            "USA": """Thanks for connecting, {name}.

Most dental clinics I looked at lose 10–30% of potential patients because calls come in after hours or don't get followed up properly.

Is that something you notice at {clinic}?""",
            "UK": """Thanks for connecting, {name}.

Most dental clinics I looked at lose 10–30% of potential patients because calls come in after hours or don't get followed up properly.

Is that something you notice at {clinic}?""",
            "Kyrgyzstan": """Спасибо за связь, {name}.

Я заметил, что многие стоматологии теряют 10-30% пациентов из-за пропущенных звонков после работы.

Это актуально для {clinic}?""",
            "Russia": """Спасибо за связь, {name}.

Многие стоматологии теряют 10-30% пациентов из-за пропущенных звонков и отсутствия обратной связи.

Это актуально для {clinic}?""",
            "default": """Thanks for connecting, {name}.

Most dental clinics I looked at lose 10–30% of potential patients because calls come in after hours or don't get followed up properly.

Is that something you notice at {clinic}?""",
        },
        "soft": {
            "default": """Thanks for connecting, {name}.

I work with dental clinics on capturing patients that might be slipping through — usually from after-hours calls or slow follow-up.

Curious — how does {clinic} currently handle patient inquiries that come in outside business hours?""",
        },
        "roi": {
            "default": """Thanks for connecting, {name}.

I help dental clinics recover lost revenue from missed calls. Average recovery: $5K-15K/month.

Quick question — when someone calls {clinic} after 5pm, what happens to that lead?""",
        },
    }
    
    # === FOLLOW-UPS ===
    
    FOLLOWUPS = {
        1: {
            "default": """Hey {name}, just bumping this up — is after-hours lead capture a challenge for {clinic}?""",
        },
        2: {
            "default": """Hi {name}, one more follow-up.

If this isn't a priority right now, totally understand.

If it is, happy to show you how we help clinics recover 15-20 extra appointments per month.""",
        },
    }
    
    # === RESPONSE HANDLERS ===
    
    RESPONSE_HANDLERS = {
        "voicemail": """That's exactly what we fix.

Our system answers in 60 seconds and books the appointment directly into your calendar.

Clinics using this recover 15-20 extra patients per month.

Want a quick 10-min demo?""",
        
        "has_system": """Good. Quick question — does it actually book the appointment, or just take a message?""",
        
        "price": """$1,500/month. But let me ask — how much is a missed patient worth to {clinic}?

If it's $500+, and we recover 3 per month, you're making money from day one.

Want to see the math for {clinic}?""",
        
        "send_info": """I will. But real quick — what questions do you have right now?

I want to send you exactly what helps you decide.""",
        
        "not_interested": """No problem. Can I ask — is it because you already have a solution, or because you don't see the need?

Just curious so I'm not wasting your time.""",
        
        "interested": """Great. Here's the link: {{demo_link}}

I'll show you exactly how this works for {clinic}. Takes 15 min.""",
    }
    
    def generate_for_lead(self, lead: ScoredLead) -> Optional[Message]:
        """Generate messages for a scored lead."""
        if lead.tier == Tier.C:
            return None  # Skip C-tier
        
        # Determine style based on tier
        if lead.tier == Tier.A:
            # A-tier: alternate between pain and ROI
            style = MessageStyle.PAIN
        else:
            # B-tier: soft approach
            style = MessageStyle.SOFT
        
        # Get country-specific templates or default
        country = lead.clinic.country
        
        # Connection request
        cr_templates = self.CONNECTION_REQUESTS.get(style.value, self.CONNECTION_REQUESTS["soft"])
        cr_template = cr_templates.get(country, cr_templates.get("default", ""))
        
        # First message
        fm_templates = self.FIRST_MESSAGES.get(style.value, self.FIRST_MESSAGES["soft"])
        fm_template = fm_templates.get(country, fm_templates.get("default", ""))
        
        # Fill in variables
        vars_dict = {
            "name": lead.clinic.owner_name or "there",
            "clinic": lead.clinic.name,
        }
        
        connection_request = cr_template.format(**vars_dict)
        first_message = fm_template.format(**vars_dict)
        followup_1 = self.FOLLOWUPS[1]["default"].format(**vars_dict)
        followup_2 = self.FOLLOWUPS[2]["default"].format(**vars_dict)
        
        # Response handlers with clinic name
        handlers = {k: v.format(**vars_dict) for k, v in self.RESPONSE_HANDLERS.items()}
        
        return Message(
            style=style,
            tier=lead.tier,
            connection_request=connection_request,
            first_message=first_message,
            followup_1=followup_1,
            followup_2=followup_2,
            response_handlers=handlers,
        )
    
    def generate_batch(self, leads: List[ScoredLead]) -> Dict[str, Message]:
        """Generate messages for multiple leads."""
        results = {}
        for lead in leads:
            msg = self.generate_for_lead(lead)
            if msg:
                results[lead.clinic.name] = msg
        return results
    
    def export_messages(self, messages: Dict[str, Message], filepath: str = None):
        """Export messages to JSON."""
        if filepath is None:
            filepath = os.path.join(os.path.dirname(__file__), "data", "generated_messages.json")
        
        data = {}
        for clinic_name, msg in messages.items():
            data[clinic_name] = {
                "style": msg.style.value,
                "tier": msg.tier.value,
                "connection_request": msg.connection_request,
                "first_message": msg.first_message,
                "followup_1": msg.followup_1,
                "followup_2": msg.followup_2,
                "response_handlers": msg.response_handlers,
            }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        
        return filepath


def demo_generator():
    """Demo the message generator."""
    from lead_scorer import LeadScoringEngine
    
    # Score some clinics
    scorer = LeadScoringEngine()
    
    clinics = [
        ClinicData(
            name="Smile Dental NYC",
            country="USA",
            city="New York",
            owner_name="Dr. Smith",
            has_online_booking=False,
            has_contact_form=False,
            doctor_count=2,
        ),
        ClinicData(
            name="Perfect Teeth Chicago",
            country="USA",
            city="Chicago",
            owner_name="Dr. Johnson",
            has_online_booking=True,
            has_contact_form=True,
            doctor_count=5,
        ),
        ClinicData(
            name="Али-Дент",
            country="Kyrgyzstan",
            city="Bishkek",
            owner_name="Dr. Козлов",
            has_online_booking=False,
            doctor_count=3,
        ),
    ]
    
    scored = scorer.score_batch(clinics)
    
    # Generate messages
    generator = MessageGeneratorV2()
    messages = generator.generate_batch(scored)
    
    print("=" * 60)
    print("MESSAGE GENERATOR v2 RESULTS")
    print("=" * 60)
    
    for clinic_name, msg in messages.items():
        print(f"\n--- {clinic_name} (Tier {msg.tier.value}) ---")
        print(f"\n[Connection Request]")
        print(msg.connection_request)
        print(f"\n[First Message]")
        print(msg.first_message)
        print(f"\n[Follow-up 1]")
        print(msg.followup_1)
    
    # Export
    filepath = generator.export_messages(messages)
    print(f"\n{'=' * 60}")
    print(f"Exported to: {filepath}")


if __name__ == "__main__":
    demo_generator()
