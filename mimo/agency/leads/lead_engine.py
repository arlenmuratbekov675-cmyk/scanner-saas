"""
MiMo Lead Engine - Lead Generation Module
Generates qualified leads for AI agency outreach.
"""
import json
import os
from datetime import datetime
from typing import List, Dict

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
BRIDGE_PATH = os.path.join(OUTPUT_DIR, "leads.json")


def load_leads() -> List[Dict]:
    """Load existing leads from file."""
    if os.path.exists(BRIDGE_PATH):
        with open(BRIDGE_PATH, "r") as f:
            return json.load(f)
    return []


def save_leads(leads: List[Dict]):
    """Save leads to file."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(BRIDGE_PATH, "w") as f:
        json.dump(leads, f, indent=2)


def add_lead(
    company: str,
    website: str,
    niche: str,
    contact_email: str = "",
    contact_name: str = "",
    notes: str = "",
    score: int = 0
) -> Dict:
    """
    Add a new lead to the system.
    Score: 0-100 (higher = better fit for AI services)
    """
    leads = load_leads()
    
    lead = {
        "id": len(leads) + 1,
        "company": company,
        "website": website,
        "niche": niche,
        "contact_email": contact_email,
        "contact_name": contact_name,
        "notes": notes,
        "score": score,
        "status": "new",
        "created_at": datetime.now().isoformat(),
        "outreach_sent": False,
        "response_received": False
    }
    
    leads.append(lead)
    save_leads(leads)
    return lead


def update_lead_status(lead_id: int, status: str, notes: str = ""):
    """Update lead status (new, contacted, responded, converted, rejected)."""
    leads = load_leads()
    for lead in leads:
        if lead["id"] == lead_id:
            lead["status"] = status
            if notes:
                lead["notes"] = notes
            break
    save_leads(leads)


def get_qualified_leads(min_score: int = 70) -> List[Dict]:
    """Get leads with score >= min_score."""
    leads = load_leads()
    return [l for l in leads if l["score"] >= min_score and l["status"] == "new"]


def get_stats() -> Dict:
    """Get lead generation statistics."""
    leads = load_leads()
    return {
        "total": len(leads),
        "new": len([l for l in leads if l["status"] == "new"]),
        "contacted": len([l for l in leads if l["status"] == "contacted"]),
        "responded": len([l for l in leads if l["status"] == "responded"]),
        "converted": len([l for l in leads if l["status"] == "converted"]),
        "avg_score": sum(l["score"] for l in leads) / len(leads) if leads else 0
    }


# Niche templates for quick lead generation
NICHE_TEMPLATES = {
    "real_estate": {
        "keywords": ["real estate", "property", "realtor", "mortgage"],
        "pain_points": ["missing leads", "slow follow-up", "no automation"],
        "ai_solution": "AI Lead Generator + Sales Assistant"
    },
    "dental": {
        "keywords": ["dental", "dentist", "clinic"],
        "pain_points": ["no online booking", "missed calls", "no follow-up"],
        "ai_solution": "AI Receptionist + Appointment Bot"
    },
    "fitness": {
        "keywords": ["gym", "fitness", "personal trainer", "studio"],
        "pain_points": ["low membership", "no lead capture", "manual follow-up"],
        "ai_solution": "AI Lead Generator + CRM Automation"
    },
    "ecommerce": {
        "keywords": ["shop", "store", "ecommerce", "retail"],
        "pain_points": ["abandoned carts", "no upsells", "poor support"],
        "ai_solution": "AI Sales Assistant + Recovery Bot"
    },
    "saas": {
        "keywords": ["saas", "software", "startup", "tech"],
        "pain_points": ["low trial conversion", "churn", "manual onboarding"],
        "ai_solution": "AI Onboarding + Support Bot"
    }
}


def generate_outreach_message(lead: Dict, niche: str = None) -> str:
    """Generate personalized outreach message for a lead."""
    template = NICHE_TEMPLATES.get(niche or lead.get("niche", ""), {})
    pain_points = template.get("pain_points", ["inefficiency", "manual processes"])
    solution = template.get("ai_solution", "AI automation system")
    
    message = f"""Hi {lead.get('contact_name', 'there')},

I analyzed {lead['company']} and noticed you might be missing automated lead handling and follow-up systems.

We build AI systems that:
- generate qualified leads automatically
- respond to customers 24/7
- increase conversion without extra ad spend

Specifically for {lead.get('niche', 'your industry')}, we've helped businesses reduce missed opportunities by 60%.

I can show you a quick demo tailored to {lead['company']}.

Would you have 15 minutes this week?"""
    
    return message


if __name__ == "__main__":
    # Example usage
    lead = add_lead(
        company="Test Corp",
        website="https://testcorp.com",
        niche="saas",
        contact_email="ceo@testcorp.com",
        contact_name="John Doe",
        score=85
    )
    print(f"Added lead: {lead['company']} (score: {lead['score']})")
    
    qualified = get_qualified_leads(min_score=70)
    print(f"Qualified leads: {len(qualified)}")
    
    msg = generate_outreach_message(lead)
    print(f"\nOutreach message:\n{msg}")
