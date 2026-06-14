"""
Scoring Module - Scores businesses based on money leak potential.
"""
from typing import Dict, Tuple


def score_business(features: Dict, rating: float, reviews: int) -> Tuple[int, str]:
    """
    Score a business based on features and metrics.
    
    Returns (score, tier):
    - Score: 0-100 (higher = more opportunity)
    - Tier: A/B/C
    """
    score = 50  # Base score
    
    # Online booking absence (biggest opportunity)
    if not features["has_online_booking"]:
        score += 25
    else:
        score -= 20
    
    # Contact form
    if not features["has_contact_form"]:
        score += 10
    
    # Live chat
    if not features["has_live_chat"]:
        score += 10
    else:
        score -= 10
    
    # Website quality
    if features["website_quality"] == "outdated":
        score += 10
    else:
        score -= 5
    
    # Business hours
    if features["closing_hour"] <= 17:
        score += 10
    if not features["has_weekend_hours"]:
        score += 5
    
    # Rating (higher rating = more established = more potential revenue)
    if rating >= 4.8:
        score += 5
    elif rating < 4.0:
        score -= 10
    
    # Reviews (more reviews = more traffic = more potential loss)
    if reviews > 300:
        score += 5
    elif reviews < 50:
        score -= 5
    
    # Clamp to 0-100
    score = max(0, min(100, score))
    
    # Determine tier
    if score >= 70:
        tier = "A"
    elif score >= 45:
        tier = "B"
    else:
        tier = "C"
    
    return score, tier


def estimate_loss(features: Dict, tier: str) -> int:
    """
    Estimate monthly revenue loss based on features and tier.
    
    This is a rough estimate for the MVP.
    In production, use actual conversion data.
    """
    base_loss = {
        "A": 5000,
        "B": 2500,
        "C": 1000,
    }
    
    loss = base_loss.get(tier, 1000)
    
    # Adjust based on features
    if not features["has_online_booking"]:
        loss += 1500  # Missing after-hours bookings
    
    if not features["has_live_chat"]:
        loss += 800  # Missing instant responses
    
    if features["closing_hour"] <= 17:
        loss += 500  # Early closing = missed opportunities
    
    if not features["has_weekend_hours"]:
        loss += 700  # No weekend = lost weekend traffic
    
    return loss
