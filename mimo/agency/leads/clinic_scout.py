"""
Clinic Scout - Find dental clinics with missed call problems.
Interactive tool for scoring and qualifying leads.
"""
import json
import os
from datetime import datetime

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "leads")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "qualified_clinics.json")


def load_clinics() -> list:
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r") as f:
            return json.load(f)
    return []


def save_clinics(clinics: list):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(clinics, f, indent=2)


def score_clinic(checks: dict) -> int:
    """Calculate lead score based on checks."""
    score = 0
    
    # Website signals
    if checks.get("no_online_booking"):
        score += 20
    if checks.get("no_contact_form"):
        score += 15
    if checks.get("no_live_chat"):
        score += 15
    
    # Review signals
    if checks.get("response_time_complaints"):
        score += 20
    
    # Hours signals
    if checks.get("closes_before_6pm"):
        score += 10
    if checks.get("no_weekend_hours"):
        score += 10
    
    # Social signals
    if checks.get("no_social_activity"):
        score += 10
    
    return score


def qualify_clinic(score: int) -> str:
    if score >= 60:
        return "HIGH"
    elif score >= 40:
        return "MEDIUM"
    else:
        return "LOW"


def add_clinic_interactive():
    """Interactive mode to add and score a clinic."""
    print("\n=== Clinic Scout ===")
    print("Answer 'y' for yes, 'n' for no\n")
    
    name = input("Clinic name: ").strip()
    website = input("Website: ").strip()
    city = input("City: ").strip()
    
    # Website checks
    print("\n--- Website Analysis ---")
    no_booking = input("No online booking? (y/n): ").strip().lower() == "y"
    no_form = input("No contact form? (y/n): ").strip().lower() == "y"
    no_chat = input("No live chat? (y/n): ").strip().lower() == "y"
    
    # Review checks
    print("\n--- Review Analysis ---")
    complaints = input("Complaints about response time? (y/n): ").strip().lower() == "y"
    
    # Hours checks
    print("\n--- Hours Analysis ---")
    closes_early = input("Closes before 6pm? (y/n): ").strip().lower() == "y"
    no_weekend = input("No weekend hours? (y/n): ").strip().lower() == "y"
    
    # Social checks
    print("\n--- Social Analysis ---")
    no_social = input("No recent social media activity? (y/n): ").strip().lower() == "y"
    
    # Call test
    print("\n--- Call Test ---")
    misses_calls = input("Missed your after-hours call? (y/n): ").strip().lower() == "y"
    
    # Calculate score
    checks = {
        "no_online_booking": no_booking,
        "no_contact_form": no_form,
        "no_live_chat": no_chat,
        "response_time_complaints": complaints,
        "closes_before_6pm": closes_early,
        "no_weekend_hours": no_weekend,
        "no_social_activity": no_social,
        "misses_after_hours_calls": misses_calls
    }
    
    score = score_clinic(checks)
    qualification = qualify_clinic(score)
    
    # Display results
    print("\n" + "=" * 40)
    print(f"CLINIC: {name}")
    print(f"WEBSITE: {website}")
    print(f"CITY: {city}")
    print("=" * 40)
    print(f"\nSCORE: {score}/100")
    print(f"QUALIFICATION: {qualification}")
    
    if qualification == "HIGH":
        print("\n>>> STRONG LEAD - Add to outreach list!")
    elif qualification == "MEDIUM":
        print("\n>>> MEDIUM LEAD - Worth contacting")
    else:
        print("\n>>> LOW LEAD - Consider skipping")
    
    # Save
    clinics = load_clinics()
    clinic = {
        "id": len(clinics) + 1,
        "name": name,
        "website": website,
        "city": city,
        "checks": checks,
        "score": score,
        "qualification": qualification,
        "added_at": datetime.now().isoformat(),
        "status": "new",
        "outreach_sent": False,
        "response_received": False,
        "demo_booked": False,
        "deal_closed": False
    }
    
    clinics.append(clinic)
    save_clinics(clinics)
    
    print(f"\nSaved to {OUTPUT_FILE}")
    return clinic


def show_stats():
    """Show statistics of qualified clinics."""
    clinics = load_clinics()
    
    if not clinics:
        print("No clinics found.")
        return
    
    total = len(clinics)
    high = len([c for c in clinics if c["qualification"] == "HIGH"])
    medium = len([c for c in clinics if c["qualification"] == "MEDIUM"])
    low = len([c for c in clinics if c["qualification"] == "LOW"])
    
    contacted = len([c for c in clinics if c["outreach_sent"]])
    responded = len([c for c in clinics if c["response_received"]])
    demo = len([c for c in clinics if c["demo_booked"]])
    closed = len([c for c in clinics if c["deal_closed"]])
    
    print("\n=== Clinic Stats ===")
    print(f"Total: {total}")
    print(f"HIGH priority: {high}")
    print(f"MEDIUM priority: {medium}")
    print(f"LOW priority: {low}")
    print(f"\nOutreach sent: {contacted}")
    print(f"Responses: {responded}")
    print(f"Demos booked: {demo}")
    print(f"Deals closed: {closed}")


def show_high_priority():
    """Show only high priority clinics."""
    clinics = load_clinics()
    high = [c for c in clinics if c["qualification"] == "HIGH"]
    
    if not high:
        print("No high priority clinics found.")
        return
    
    print(f"\n=== HIGH PRIORITY CLINICS ({len(high)}) ===\n")
    
    for c in high:
        print(f"#{c['id']} {c['name']} ({c['city']})")
        print(f"   Website: {c['website']}")
        print(f"   Score: {c['score']}/100")
        print(f"   Status: {c['status']}")
        print()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "stats":
            show_stats()
        elif sys.argv[1] == "high":
            show_high_priority()
        elif sys.argv[1] == "add":
            add_clinic_interactive()
        else:
            print("Usage: python clinic_scout.py [add|stats|high]")
    else:
        print("Clinic Scout - Find clinics with missed call problems")
        print("=" * 50)
        print("\nCommands:")
        print("  add   - Add and score a new clinic")
        print("  stats - Show statistics")
        print("  high  - Show high priority clinics")
