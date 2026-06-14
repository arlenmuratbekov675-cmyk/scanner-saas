"""
Message Generator - Create personalized outreach for each company.
"""
import json
import os

LEADS_DIR = os.path.join(os.path.dirname(__file__), "leads")
COMPANIES_FILE = os.path.join(LEADS_DIR, "company_list.json")


def load_companies() -> list:
    if os.path.exists(COMPANIES_FILE):
        with open(COMPANIES_FILE, "r") as f:
            return json.load(f)
    return []


LINKEDIN_TEMPLATES = {
    "dental": [
        "Hi {name},\n\nI noticed {company} might be missing patient calls after hours.\n\nWe built an AI receptionist that books appointments 24/7. Our dental clients capture 15-20 extra appointments per month.\n\nWant to see how it works?",
        
        "Hi {name},\n\nQuick question for {company}: how do you handle patient inquiries that come in at night or weekends?\n\nWe help dental clinics respond in 60 seconds, 24/7. Would love to show you the demo.",
        
        "Hi {name},\n\nI was looking at {company}'s online presence. Looks great!\n\nOne thing I noticed: no automated booking system. This means missed appointments and lost revenue.\n\nWe fix this for dental clinics. Interested in a quick chat?"
    ],
    "real_estate": [
        "Hi {name},\n\nSaw you're active in {city} real estate.\n\nQuick question: how fast do you respond to new leads?\n\nOur AI system responds in 60 seconds, 24/7. Agents using it close 30% more deals.\n\nWant to see it in action?",
        
        "Hi {name},\n\nI help real estate agents automate their lead follow-up.\n\nThe problem: 78% of buyers go with the first agent who responds. Most responses take hours.\n\nOur system responds in under a minute. Worth a 15-min chat?",
        
        "Hi {name},\n\nChecked out {company} - nice listings!\n\nOne question: when a lead fills out a form on your site, how quickly do they hear back?\n\nWe automate that response to under 60 seconds. Want to see how?"
    ],
    "fitness": [
        "Hi {name},\n\nChecked out {company} - looks like a great studio!\n\nQuick question: how many potential members go cold because of slow follow-up?\n\nWe help fitness studios capture and nurture leads automatically. Interested in a quick demo?",
        
        "Hi {name},\n\nI noticed {company} doesn't have automated lead follow-up.\n\nThis means: leads come in at 9pm, don't hear back until next day, go to competitor.\n\nWe fix this. Studios see 25-40% more trial-to-member conversions.\n\nWorth a chat?",
        
        "Hi {name},\n\nQuick question for {company}: what's your trial-to-member conversion rate?\n\nMost studios lose 50%+ of trial members due to slow follow-up.\n\nOur AI nurtures leads automatically. Want to see the numbers?"
    ]
}

EMAIL_TEMPLATES = {
    "dental": [
        {
            "subject": "Quick question about {company}'s patient booking",
            "body": "Hi {name},\n\nI was researching dental clinics in {city} and came across {company}.\n\nI noticed you might not have automated appointment booking in place. This means:\n- After-hours inquiries go unanswered\n- Patients book with competitors\n- Front desk staff are overwhelmed\n\nWe build AI systems that fix this. Our dental clients capture 15-20 extra appointments per month.\n\nI created a quick demo showing how this would work for {company}. Would you have 15 minutes to see it?\n\nBest,\n[Your name]"
        }
    ],
    "real_estate": [
        {
            "subject": "Quick question about {company}'s lead response time",
            "body": "Hi {name},\n\nI was researching real estate agents in {city} and came across {company}.\n\nQuick question: when a lead fills out a form on your site, how quickly do they hear back?\n\nStudies show 78% of buyers go with the first agent who responds. Most responses take hours.\n\nWe build AI systems that respond in 60 seconds, 24/7. Agents using our system close 30% more deals.\n\nWould you have 15 minutes to see a quick demo?\n\nBest,\n[Your name]"
        }
    ],
    "fitness": [
        {
            "subject": "Quick question about {company}'s trial conversions",
            "body": "Hi {name},\n\nI was researching fitness studios in {city} and came across {company}.\n\nQuick question: what's your trial-to-member conversion rate?\n\nMost studios lose 50%+ of trial members due to slow follow-up. Leads come in at 9pm, don't hear back until next day, and go to a competitor.\n\nWe build AI systems that nurture leads automatically. Studios using our system see 25-40% more conversions.\n\nWould you have 15 minutes to see a quick demo?\n\nBest,\n[Your name]"
        }
    ]
}


def generate_linkedin_message(company: dict, template_index: int = 0) -> str:
    """Generate personalized LinkedIn message."""
    niche = company.get("niche", "dental")
    templates = LINKEDIN_TEMPLATES.get(niche, LINKEDIN_TEMPLATES["dental"])
    
    template = templates[template_index % len(templates)]
    
    return template.format(
        name=company.get("contact_name", "there"),
        company=company["name"],
        city=company.get("city", "your area")
    )


def generate_email(company: dict) -> dict:
    """Generate personalized email."""
    niche = company.get("niche", "dental")
    templates = EMAIL_TEMPLATES.get(niche, EMAIL_TEMPLATES["dental"])
    
    template = templates[0]
    
    return {
        "to": company.get("contact_email", ""),
        "subject": template["subject"].format(
            company=company["name"],
            city=company.get("city", "your area")
        ),
        "body": template["body"].format(
            name=company.get("contact_name", "there"),
            company=company["name"],
            city=company.get("city", "your area")
        )
    }


def generate_all_messages():
    """Generate messages for all companies."""
    companies = load_companies()
    
    print(f"Generating messages for {len(companies)} companies...\n")
    
    for company in companies:
        print(f"=== {company['name']} ({company['city']}) ===")
        print(f"\nLinkedIn Message:")
        print("-" * 40)
        print(generate_linkedin_message(company))
        
        if company.get("contact_email"):
            email = generate_email(company)
            print(f"\nEmail:")
            print("-" * 40)
            print(f"To: {email['to']}")
            print(f"Subject: {email['subject']}")
            print(f"\n{email['body']}")
        
        print("\n" + "=" * 40 + "\n")


if __name__ == "__main__":
    generate_all_messages()
