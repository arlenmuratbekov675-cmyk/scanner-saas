"""
Website Analyzer - Checks features that indicate money leaks.
"""
from typing import Dict
import random


def analyze_website(url: str) -> Dict:
    """
    Analyze a website for features that indicate money leaks.
    
    In production, this would:
    1. Fetch the website
    2. Check for booking systems
    3. Check for contact forms
    4. Check for live chat
    5. Analyze business hours
    
    For MVP, we use mock data based on URL patterns.
    """
    # Mock analysis based on URL patterns
    # In production, replace with real scraping
    
    has_booking = any(term in url.lower() for term in [
        "booking", "appointm", "schedule", "zocdoc", "healthgrades"
    ])
    
    has_chat = any(term in url.lower() for term in [
        "chat", "intercom", "drift", "crisp", "tawk"
    ])
    
    # Most SMB websites don't have these features
    # So we default to False unless explicitly found
    return {
        "has_online_booking": has_booking,
        "has_contact_form": not has_booking,  # If no booking, likely has form
        "has_live_chat": has_chat,
        "closing_hour": random.choice([16, 17, 18]),
        "has_weekend_hours": random.random() > 0.6,  # 40% have weekend hours
        "website_quality": "outdated" if random.random() > 0.5 else "modern",
    }
