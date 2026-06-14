"""
Company Finder - Find businesses for outreach.
Usage: python find_companies.py
"""
import json
import os
from datetime import datetime

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "leads")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "company_list.json")


def save_companies(companies: list):
    """Save companies to file."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(companies, f, indent=2)


def load_companies() -> list:
    """Load existing companies."""
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r") as f:
            return json.load(f)
    return []


def add_company(
    name: str,
    website: str,
    niche: str,
    city: str,
    contact_name: str = "",
    contact_email: str = "",
    contact_linkedin: str = "",
    notes: str = ""
) -> dict:
    """Add a company to the list."""
    companies = load_companies()
    
    company = {
        "id": len(companies) + 1,
        "name": name,
        "website": website,
        "niche": niche,
        "city": city,
        "contact_name": contact_name,
        "contact_email": contact_email,
        "contact_linkedin": contact_linkedin,
        "notes": notes,
        "status": "new",
        "added_at": datetime.now().isoformat(),
        "outreach_sent": False,
        "response_received": False,
        "demo_booked": False,
        "deal_closed": False
    }
    
    companies.append(company)
    save_companies(companies)
    return company


def update_company(company_id: int, **kwargs):
    """Update company fields."""
    companies = load_companies()
    for company in companies:
        if company["id"] == company_id:
            for key, value in kwargs.items():
                if key in company:
                    company[key] = value
            break
    save_companies(companies)


def get_stats() -> dict:
    """Get statistics."""
    companies = load_companies()
    return {
        "total": len(companies),
        "new": len([c for c in companies if c["status"] == "new"]),
        "contacted": len([c for c in companies if c["outreach_sent"]]),
        "responded": len([c for c in companies if c["response_received"]]),
        "demo_booked": len([c for c in companies if c["demo_booked"]]),
        "deal_closed": len([c for c in companies if c["deal_closed"]])
    }


# Pre-built templates for quick company entry
DENTAL_CLINICS_TEMPLATE = [
    {"name": "Smile Dental", "city": "New York", "website": "smiledentalnyc.com"},
    {"name": "Bright Smile Clinic", "city": "Los Angeles", "website": "brightsmilela.com"},
    {"name": "Perfect Teeth", "city": "Chicago", "website": "perfectteethchi.com"},
    {"name": "Dental Care Plus", "city": "Houston", "website": "dentalcareplus.com"},
    {"name": "Happy Dentist", "city": "Phoenix", "website": "happydentist.com"},
]

REAL_ESTATE_TEMPLATE = [
    {"name": "HomeFinders Realty", "city": "Miami", "website": "homefindersrealty.com"},
    {"name": "Prime Properties", "city": "Seattle", "website": "primeproperties.com"},
    {"name": "Dream Home Realty", "city": "Denver", "website": "dreamhomerealty.com"},
    {"name": "City Living Real Estate", "city": "Boston", "website": "cityliving.com"},
    {"name": "Elite Homes", "city": "Austin", "website": "elitehomes.com"},
]


def find_companies_manual():
    """Interactive mode to add companies."""
    print("Company Finder - Manual Mode")
    print("Type 'quit' to exit\n")
    
    while True:
        name = input("Company name: ").strip()
        if name.lower() == "quit":
            break
        
        website = input("Website: ").strip()
        niche = input("Niche (dental/real_estate/fitness/other): ").strip()
        city = input("City: ").strip()
        contact_name = input("Contact name (optional): ").strip()
        contact_email = input("Contact email (optional): ").strip()
        
        company = add_company(
            name=name,
            website=website,
            niche=niche,
            city=city,
            contact_name=contact_name,
            contact_email=contact_email
        )
        print(f"Added: {company['name']} (ID: {company['id']})\n")
    
    print(f"\nTotal companies: {len(load_companies())}")


def generate_search_queries(niche: str, city: str) -> list:
    """Generate Google search queries for finding companies."""
    queries = {
        "dental": [
            f"dental clinic {city}",
            f"dentist office {city}",
            f"dental practice {city}",
            f"teeth cleaning {city}",
            f"dental implants {city}",
        ],
        "real_estate": [
            f"real estate agent {city}",
            f"realtor {city}",
            f"real estate agency {city}",
            f"property management {city}",
            f"homes for sale {city}",
        ],
        "fitness": [
            f"yoga studio {city}",
            f"crossfit gym {city}",
            f"fitness center {city}",
            f"personal trainer {city}",
            f"gym {city}",
        ],
        "saas": [
            f"saas company {city}",
            f"software startup {city}",
            f"tech company {city}",
        ]
    }
    
    return queries.get(niche, [f"{niche} business {city}"])


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "manual":
        find_companies_manual()
    else:
        print("Company Finder")
        print("=" * 40)
        print("\nUsage:")
        print("  python find_companies.py manual     # Interactive mode")
        print("  python find_companies.py stats      # Show statistics")
        print("  python find_companies.py queries    # Generate search queries")
        
        if len(sys.argv) > 1 and sys.argv[1] == "stats":
            stats = get_stats()
            print(f"\nStatistics:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
        
        elif len(sys.argv) > 1 and sys.argv[1] == "queries":
            niche = input("Niche (dental/real_estate/fitness): ").strip()
            city = input("City: ").strip()
            queries = generate_search_queries(niche, city)
            print(f"\nSearch queries for {niche} in {city}:")
            for q in queries:
                print(f"  - {q}")
