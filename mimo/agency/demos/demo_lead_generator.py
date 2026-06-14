"""
Demo 2: AI Lead Generator
Demonstrates automated lead discovery and scoring.
"""
import json
from datetime import datetime
from typing import List, Dict


# Simulated business database (in production, scrape Google, LinkedIn, etc.)
SAMPLE_BUSINESSES = [
    {"name": "Downtown Dental", "website": "downtowndental.com", "niche": "dental", "city": "New York"},
    {"name": "FitLife Studio", "website": "fitlifestudio.com", "niche": "fitness", "city": "Los Angeles"},
    {"name": "HomeFinders Realty", "website": "homefindersrealty.com", "niche": "real_estate", "city": "Chicago"},
    {"name": "ShopEasy", "website": "shopeasy.com", "niche": "ecommerce", "city": "Miami"},
    {"name": "CloudSoft SaaS", "website": "cloudsoft.io", "niche": "saas", "city": "San Francisco"},
    {"name": "Smile Clinic", "website": "smileclinic.com", "niche": "dental", "city": "Boston"},
    {"name": "Peak Performance Gym", "website": "peakgym.com", "niche": "fitness", "city": "Denver"},
    {"name": "Urban Properties", "website": "urbanproperties.com", "niche": "real_estate", "city": "Seattle"},
]


def analyze_business(business: Dict) -> Dict:
    """
    AI analysis of a business to determine if they need AI services.
    In production, this would scrape their website and analyze with LLM.
    """
    # Simulated analysis
    niche = business["niche"]
    
    # Score based on niche fit
    niche_scores = {
        "dental": 85,
        "real_estate": 80,
        "fitness": 75,
        "ecommerce": 70,
        "saas": 90
    }
    
    score = niche_scores.get(niche, 60)
    
    # Identify pain points
    pain_points = {
        "dental": ["No online booking system", "Missed patient calls", "No automated follow-ups"],
        "real_estate": ["Slow lead response time", "No automated nurturing", "Manual lead qualification"],
        "fitness": ["Low membership conversion", "No lead capture", "Manual class booking"],
        "ecommerce": ["Abandoned carts", "No upsell automation", "Poor customer support"],
        "saas": ["Low trial conversion", "High churn", "Manual onboarding"]
    }
    
    # AI solutions
    solutions = {
        "dental": "AI Receptionist + Appointment Booking Bot",
        "real_estate": "AI Lead Generator + Follow-up System",
        "fitness": "AI Lead Capture + Membership Bot",
        "ecommerce": "AI Sales Assistant + Cart Recovery",
        "saas": "AI Onboarding + Support Bot"
    }
    
    return {
        "business": business,
        "score": score,
        "qualified": score >= 70,
        "pain_points": pain_points.get(niche, ["Generic inefficiency"]),
        "recommended_solution": solutions.get(niche, "Custom AI Automation"),
        "estimated_roi": f"${score * 100}/month potential increase"
    }


def generate_outreach(analysis: Dict) -> str:
    """Generate personalized outreach message based on analysis."""
    biz = analysis["business"]
    pain = analysis["pain_points"][0]
    solution = analysis["recommended_solution"]
    
    return f"""Hi,

I was looking at {biz['name']} and noticed you might be dealing with {pain.lower()}.

We've helped similar {biz['niche']} businesses with {solution}.

Would you be open to a quick 15-minute demo to see how this could work for {biz['name']}?

Best regards"""


def run_demo():
    print("=" * 60)
    print("DEMO: AI Lead Generator")
    print("=" * 60)
    
    print("\n[Step 1] Scanning for businesses...\n")
    
    analyzed = []
    for biz in SAMPLE_BUSINESSES:
        result = analyze_business(biz)
        analyzed.append(result)
        status = "[QUALIFIED]" if result["qualified"] else "[Not a fit]"
        print(f"  {biz['name']:25} Score: {result['score']:3} {status}")
    
    # Filter qualified leads
    qualified = [a for a in analyzed if a["qualified"]]
    qualified.sort(key=lambda x: x["score"], reverse=True)
    
    print(f"\n[Step 2] Found {len(qualified)} qualified leads out of {len(analyzed)}\n")
    
    # Show top 3 leads with outreach
    print("=" * 60)
    print("TOP 3 LEADS WITH PERSONALIZED OUTREACH")
    print("=" * 60)
    
    for i, lead in enumerate(qualified[:3], 1):
        biz = lead["business"]
        print(f"\n--- Lead #{i} ---")
        print(f"Company:  {biz['name']}")
        print(f"Website:  {biz['website']}")
        print(f"Niche:    {biz['niche']}")
        print(f"Score:    {lead['score']}/100")
        print(f"Pain:     {lead['pain_points'][0]}")
        print(f"Solution: {lead['recommended_solution']}")
        print(f"\nOutreach Message:")
        print("-" * 40)
        print(generate_outreach(lead))
        print("-" * 40)
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Businesses scanned: {len(analyzed)}")
    print(f"Qualified leads:    {len(qualified)}")
    print(f"Potential revenue:  ${len(qualified) * 1500}")
    print(f"\nNext steps:")
    print("  1. Export leads to leads.json")
    print("  2. Send outreach messages")
    print("  3. Track responses")
    
    # Save to file
    output = {
        "timestamp": datetime.now().isoformat(),
        "leads": [{"name": l["business"]["name"], "score": l["score"], "solution": l["recommended_solution"]} for l in qualified]
    }
    
    with open("demo_leads_output.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to demo_leads_output.json")


if __name__ == "__main__":
    run_demo()
