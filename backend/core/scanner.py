"""
Core Scanner - Analyzes businesses and finds money leaks.
Uses Google Maps API for real data, falls back to mock data.
"""
from typing import List, Dict
from core.analyzer import analyze_website
from core.scoring import score_business, estimate_loss
from services.google_maps import GoogleMapsService


# Mock business data (fallback when API not available)
MOCK_BUSINESSES = {
    "dental": {
        "Bishkek": [
            {"name": "Али-Дент", "website": "ali-dent.kg", "rating": 4.7, "reviews": 335},
            {"name": "Life Stom", "website": "lifestom.kg", "rating": 4.9, "reviews": 261},
            {"name": "Olio", "website": "olio.kg", "rating": 5.0, "reviews": 61},
            {"name": "Эксперт Дентал", "website": "expertdental.kg", "rating": 4.9, "reviews": 213},
            {"name": "Emmar", "website": "emmar.kg", "rating": 4.9, "reviews": 413},
            {"name": "Metadent", "website": "metadent.kg", "rating": 5.0, "reviews": 533},
            {"name": "32 Стоматология", "website": "32.kg", "rating": 4.8, "reviews": 129},
            {"name": "Smile Clinic", "website": "smileclinic.kg", "rating": 4.8, "reviews": 411},
            {"name": "Grafdent", "website": "grafdent.kg", "rating": 4.8, "reviews": 101},
            {"name": "Azuu Dent", "website": "azudent.kg", "rating": 4.7, "reviews": 238},
        ],
        "London": [
            {"name": "Smile Dental London", "website": "smiledentallondon.com", "rating": 4.6, "reviews": 180},
            {"name": "Bright Dental", "website": "brightdental.co.uk", "rating": 4.8, "reviews": 220},
            {"name": "City Dental Care", "website": "citydentalcare.co.uk", "rating": 4.5, "reviews": 150},
            {"name": "Perfect Teeth London", "website": "perfectteethlondon.com", "rating": 4.7, "reviews": 190},
            {"name": "Dental Health Plus", "website": "dentalhealthplus.co.uk", "rating": 4.4, "reviews": 120},
        ],
        "New York": [
            {"name": "NYC Dental Arts", "website": "nycdentalarts.com", "rating": 4.7, "reviews": 320},
            {"name": "Manhattan Smile", "website": "manhattansmiledental.com", "rating": 4.8, "reviews": 280},
            {"name": "Brooklyn Dental Care", "website": "brooklyndentalcare.com", "rating": 4.6, "reviews": 200},
            {"name": "Queens Dental Studio", "website": "queensdentalstudio.com", "rating": 4.5, "reviews": 150},
            {"name": "Bronx Family Dental", "website": "bronxfamilydental.com", "rating": 4.4, "reviews": 130},
        ],
    },
    "beauty": {
        "Bishkek": [
            {"name": "Beauty Lounge Bishkek", "website": "beautylounge.kg", "rating": 4.8, "reviews": 180},
            {"name": "Glam Studio", "website": "glamstudio.kg", "rating": 4.7, "reviews": 150},
        ],
        "London": [
            {"name": "London Beauty Spa", "website": "londonbeautyspa.co.uk", "rating": 4.6, "reviews": 200},
        ],
    },
}


def run_scan(city: str, niche: str, limit: int = 20) -> List[Dict]:
    """
    Run a scan on businesses in city/niche.
    Returns scored results with money leak estimates.
    """
    # Try Google Maps API first
    google_maps = GoogleMapsService()
    businesses = google_maps.search_businesses(city, niche, limit)
    
    # If no results from API, use mock data
    if not businesses:
        businesses = MOCK_BUSINESSES.get(niche, {}).get(city, [])
    
    if not businesses:
        return []
    
    results = []
    
    for biz in businesses[:limit]:
        # Get website
        website = biz.get("website")
        
        # Analyze website
        if website:
            features = analyze_website(website)
        else:
            # No website = major leak
            features = {
                "has_online_booking": False,
                "has_contact_form": False,
                "has_live_chat": False,
                "closing_hour": 17,
                "has_weekend_hours": False,
                "website_quality": "none",
            }
        
        # Score business
        score, tier = score_business(features, biz.get("rating", 4.0), biz.get("reviews", 100))
        
        # Estimate loss
        loss = estimate_loss(features, tier)
        
        # Build reasons list
        reasons = []
        if not website:
            reasons.append("No website")
        if not features["has_online_booking"]:
            reasons.append("No online booking system")
        if not features["has_contact_form"]:
            reasons.append("No contact form on website")
        if not features["has_live_chat"]:
            reasons.append("No live chat or instant response")
        if features["closing_hour"] <= 17:
            reasons.append("Closes early (before 5pm)")
        if not features["has_weekend_hours"]:
            reasons.append("No weekend hours")
        
        # Determine country
        if "Bishkek" in city or "bishkek" in city.lower():
            country = "Kyrgyzstan"
        elif "London" in city or "london" in city.lower():
            country = "UK"
        else:
            country = "USA"
        
        results.append({
            "name": biz["name"],
            "city": city,
            "country": country,
            "website": website or "No website",
            "score": score,
            "tier": tier,
            "monthly_loss_estimate": loss,
            "reasons": reasons,
            "has_online_booking": features["has_online_booking"],
            "has_contact_form": features["has_contact_form"],
            "has_live_chat": features["has_live_chat"],
            "rating": biz.get("rating", 0),
            "review_count": biz.get("reviews", 0),
        })
    
    # Sort by score (highest first)
    results.sort(key=lambda x: x["score"], reverse=True)
    
    return results
