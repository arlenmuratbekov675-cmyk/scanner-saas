"""
Core Scanner - Analyzes businesses and finds money leaks.
Uses Google Maps API for real data, falls back to mock data.
"""
from typing import List, Dict
from core.analyzer import analyze_website
from core.scoring import score_business, estimate_loss
from services.google_maps import GoogleMapsService


MOCK_BUSINESSES = {
    "dental": {
        "Bishkek": [
            {"name": "Али-Дент", "website": "ali-dent.kg", "rating": 4.7, "reviews": 335},
            {"name": "Life Stom", "website": "lifestom.kg", "rating": 4.9, "reviews": 261},
            {"name": "Olio", "website": "olio.kg", "rating": 5.0, "reviews": 61},
            {"name": "Expert Dental", "website": "expertdental.kg", "rating": 4.9, "reviews": 213},
            {"name": "Emmar Dental", "website": "emmar.kg", "rating": 4.9, "reviews": 413},
            {"name": "Metadent", "website": "metadent.kg", "rating": 5.0, "reviews": 533},
            {"name": "32 Stomatology", "website": "32.kg", "rating": 4.8, "reviews": 129},
            {"name": "Smile Clinic", "website": "smileclinic.kg", "rating": 4.8, "reviews": 411},
            {"name": "Grafdent", "website": "grafdent.kg", "rating": 4.8, "reviews": 101},
            {"name": "Azuu Dent", "website": "azudent.kg", "rating": 4.7, "reviews": 238},
            {"name": "Bishkek Dental Center", "website": "bdc.kg", "rating": 4.6, "reviews": 188},
            {"name": "Dent Pro", "website": "dentpro.kg", "rating": 4.5, "reviews": 92},
        ],
        "London": [
            {"name": "Smile Dental London", "website": "smiledentallondon.com", "rating": 4.6, "reviews": 180},
            {"name": "Bright Dental", "website": "brightdental.co.uk", "rating": 4.8, "reviews": 220},
            {"name": "City Dental Care", "website": "citydentalcare.co.uk", "rating": 4.5, "reviews": 150},
            {"name": "Perfect Teeth London", "website": "perfectteethlondon.com", "rating": 4.7, "reviews": 190},
            {"name": "Dental Health Plus", "website": "dentalhealthplus.co.uk", "rating": 4.4, "reviews": 120},
            {"name": "Harley Street Dental", "website": "harleystreetdental.co.uk", "rating": 4.9, "reviews": 340},
            {"name": "Wimpole Street Dental", "website": "wimpolestreetdental.co.uk", "rating": 4.7, "reviews": 210},
            {"name": "Kensington Dental Spa", "website": "kensingtondentalspa.co.uk", "rating": 4.8, "reviews": 285},
            {"name": "Marylebone Dental Care", "website": "marylebonedentalcare.co.uk", "rating": 4.5, "reviews": 145},
            {"name": "Canary Wharf Dentist", "website": "canarywharfdentist.co.uk", "rating": 4.6, "reviews": 170},
            {"name": "Shoreditch Dental", "website": "shoreditchdental.co.uk", "rating": 4.4, "reviews": 98},
            {"name": "Clapham Dental Centre", "website": "claphamdentalcentre.co.uk", "rating": 4.7, "reviews": 205},
        ],
        "New York": [
            {"name": "NYC Dental Arts", "website": "nycdentalarts.com", "rating": 4.7, "reviews": 320},
            {"name": "Manhattan Smile", "website": "manhattansmiledental.com", "rating": 4.8, "reviews": 280},
            {"name": "Brooklyn Dental Care", "website": "brooklyndentalcare.com", "rating": 4.6, "reviews": 200},
            {"name": "Queens Dental Studio", "website": "queensdentalstudio.com", "rating": 4.5, "reviews": 150},
            {"name": "Bronx Family Dental", "website": "bronxfamilydental.com", "rating": 4.4, "reviews": 130},
            {"name": "Upper East Side Dental", "website": "upperwestdental.com", "rating": 4.9, "reviews": 410},
            {"name": "Midtown Dental Group", "website": "midtowndentalgroup.com", "rating": 4.7, "reviews": 265},
            {"name": "SoHo Smiles", "website": "sohismiles.com", "rating": 4.8, "reviews": 195},
            {"name": "Williamsburg Dental", "website": "williamsburgdental.com", "rating": 4.5, "reviews": 142},
            {"name": "Chelsea Dental Arts", "website": "chelseadentalarts.com", "rating": 4.6, "reviews": 178},
            {"name": "Gramercy Park Dental", "website": "gramercyparkdental.com", "rating": 4.7, "reviews": 215},
            {"name": "Tribeca Dental Care", "website": "tribecadentalcare.com", "rating": 4.8, "reviews": 298},
        ],
    },
    "beauty": {
        "Bishkek": [
            {"name": "Beauty Lounge Bishkek", "website": "beautylounge.kg", "rating": 4.8, "reviews": 180},
            {"name": "Glam Studio", "website": "glamstudio.kg", "rating": 4.7, "reviews": 150},
            {"name": "Bishkek Beauty Bar", "website": "bishkekbeautybar.kg", "rating": 4.6, "reviews": 120},
            {"name": "Luxe Nail & Beauty", "website": "luxenail.kg", "rating": 4.9, "reviews": 210},
            {"name": "Flora Beauty Salon", "website": "florabeauty.kg", "rating": 4.5, "reviews": 95},
            {"name": "Crystal Beauty Spa", "website": "crystalbeauty.kg", "rating": 4.7, "reviews": 165},
        ],
        "London": [
            {"name": "London Beauty Spa", "website": "londonbeautyspa.co.uk", "rating": 4.6, "reviews": 200},
            {"name": "Covent Garden Beauty", "website": "coventgardenbeauty.co.uk", "rating": 4.8, "reviews": 310},
            {"name": "Notting Hill Nail Studio", "website": "nottinghillnails.co.uk", "rating": 4.7, "reviews": 175},
            {"name": "Soho Beauty Room", "website": "sobeautyroom.co.uk", "rating": 4.5, "reviews": 130},
            {"name": "Chelsea Skin Clinic", "website": "chelseaskinclinic.co.uk", "rating": 4.9, "reviews": 285},
            {"name": "Greenwich Beauty Hub", "website": "greenwichbeautyhub.co.uk", "rating": 4.4, "reviews": 88},
            {"name": "Camden Brow Bar", "website": "camdenbrowbar.co.uk", "rating": 4.6, "reviews": 142},
        ],
        "New York": [
            {"name": "Gloss Salon NYC", "website": "glosssalonnyc.com", "rating": 4.7, "reviews": 245},
            {"name": "Upper East Beauty", "website": "uppereastbeauty.com", "rating": 4.8, "reviews": 310},
            {"name": "Brooklyn Glow Studio", "website": "brooklynglowstudio.com", "rating": 4.6, "reviews": 168},
            {"name": "SoHo Nail Art", "website": "sohonailart.com", "rating": 4.5, "reviews": 125},
            {"name": "Midtown Lash Bar", "website": "midtownlashbar.com", "rating": 4.9, "reviews": 290},
            {"name": "Harlem Beauty Lounge", "website": "harlembeautylounge.com", "rating": 4.4, "reviews": 95},
        ],
    },
    "fitness": {
        "Bishkek": [
            {"name": "FitZone Bishkek", "website": "fitzone.kg", "rating": 4.7, "reviews": 290},
            {"name": "Iron Gym Bishkek", "website": "irongym.kg", "rating": 4.5, "reviews": 180},
            {"name": "CrossFit Bishkek", "website": "crossfitbishkek.kg", "rating": 4.8, "reviews": 145},
            {"name": "World Class Bishkek", "website": "worldclass.kg", "rating": 4.6, "reviews": 220},
            {"name": "Fitness Park", "website": "fitnesspark.kg", "rating": 4.4, "reviews": 110},
            {"name": "Alpha Fitness", "website": "alphafitness.kg", "rating": 4.7, "reviews": 165},
        ],
        "London": [
            {"name": "Third Space London", "website": "thirdspace.london", "rating": 4.8, "reviews": 420},
            {"name": "Barry's Bootcamp London", "website": "barrysbootcamp.com/london", "rating": 4.7, "reviews": 380},
            {"name": "PureGym Soho", "website": "puregym.com/soho", "rating": 4.3, "reviews": 520},
            {"name": "Gymbox Covent Garden", "website": "gymbox.com", "rating": 4.6, "reviews": 290},
            {"name": "1Rebel Shoreditch", "website": "1rebel.com", "rating": 4.8, "reviews": 245},
            {"name": "F45 Camden", "website": "f45training.com/camden", "rating": 4.5, "reviews": 130},
            {"name": "Core Collective", "website": "corecollective.com", "rating": 4.7, "reviews": 185},
        ],
        "New York": [
            {"name": "Equinox Hudson Yards", "website": "equinox.com", "rating": 4.8, "reviews": 510},
            {"name": "SoulCycle Tribeca", "website": "soul-cycle.com", "rating": 4.7, "reviews": 385},
            {"name": "Orange Theory Chelsea", "website": "orangetheoryfitness.com/chelsea", "rating": 4.6, "reviews": 280},
            {"name": "Rumble Boxing SoHo", "website": "rfrumble.com", "rating": 4.8, "reviews": 215},
            {"name": " Blink Fitness Midtown", "website": "blinkfitness.com/midtown", "rating": 4.4, "reviews": 445},
            {"name": "Barry's Bootcamp NYC", "website": "barrysbootcamp.com/nyc", "rating": 4.7, "reviews": 350},
        ],
    },
    "restaurants": {
        "Bishkek": [
            {"name": "Navat Restaurant", "website": "navat.kg", "rating": 4.7, "reviews": 520},
            {"name": "Café du Soleil", "website": "cafedusoleil.kg", "rating": 4.8, "reviews": 310},
            {"name": "Bishkek Pizza House", "website": "bishkekpizza.kg", "rating": 4.5, "reviews": 185},
            {"name": "Sulaiman Coffee", "website": "sulaiman.kg", "rating": 4.6, "reviews": 240},
            {"name": "Burger Republic", "website": "burgerrepublic.kg", "rating": 4.4, "reviews": 155},
            {"name": "Tandoor Indian Kitchen", "website": "tandoor.kg", "rating": 4.9, "reviews": 195},
            {"name": "Mandarin Garden", "website": "mandaringarden.kg", "rating": 4.3, "reviews": 130},
            {"name": "Cilantro Mexican Grill", "website": "cilantro.kg", "rating": 4.6, "reviews": 170},
        ],
        "London": [
            {"name": "Dishoom Covent Garden", "website": "dishoom.com", "rating": 4.8, "reviews": 1200},
            {"name": "The Clove Club", "website": "thecloveclub.com", "rating": 4.7, "reviews": 420},
            {"name": "Flat Iron Soho", "website": "flatironsteak.co.uk", "rating": 4.5, "reviews": 680},
            {"name": "Padella Borough", "website": "padella.uk", "rating": 4.6, "reviews": 890},
            {"name": "Noble Rot Soho", "website": "noblerot.co.uk", "rating": 4.8, "reviews": 350},
            {"name": "Brat Shoreditch", "website": "bratrestaurant.com", "rating": 4.7, "reviews": 410},
            {"name": "Granger & Co Chelsea", "website": "grangerandco.com", "rating": 4.5, "reviews": 520},
            {"name": "Dishoom King's Cross", "website": "dishoom.com/kings-cross", "rating": 4.8, "reviews": 950},
        ],
        "New York": [
            {"name": "Joe's Pizza Greenwich", "website": "joespizzanyc.com", "rating": 4.6, "reviews": 2100},
            {"name": "Prince Street Pizza", "website": "princestreetpizza.com", "rating": 4.7, "reviews": 1800},
            {"name": "Carbone Greenwich Village", "website": "carbone.nyc", "rating": 4.8, "reviews": 920},
            {"name": "Tatiana by Lincoln Center", "website": "tatianalincollnctr.com", "rating": 4.9, "reviews": 480},
            {"name": "Lucali Carroll Gardens", "website": "lucali.com", "rating": 4.7, "reviews": 1450},
            {"name": "Xi'an Famous Foods", "website": "xianfoodies.com", "rating": 4.5, "reviews": 1600},
            {"name": "Los Tacos No.1 Chelsea", "website": "lostacos1.com", "rating": 4.6, "reviews": 980},
            {"name": "Peter Luger Steakhouse", "website": "peterluger.com", "rating": 4.4, "reviews": 3200},
        ],
    },
    "auto": {
        "Bishkek": [
            {"name": "AutoPro Service", "website": "autopro.kg", "rating": 4.6, "reviews": 180},
            {"name": "EuroAuto Bishkek", "website": "euroauto.kg", "rating": 4.7, "reviews": 225},
            {"name": "Master Auto", "website": "masterauto.kg", "rating": 4.5, "reviews": 145},
            {"name": "AutoFix Pro", "website": "autofix.kg", "rating": 4.4, "reviews": 110},
            {"name": "Smart Mechanic", "website": "smartmechanic.kg", "rating": 4.8, "reviews": 95},
            {"name": "QuickService Auto", "website": "quickservice.kg", "rating": 4.3, "reviews": 75},
        ],
        "London": [
            {"name": "Kwik Fit Battersea", "website": "kwik-fit.com/battersea", "rating": 4.2, "reviews": 450},
            {"name": "Halfords Autocentre", "website": "halfords.com/autocentre", "rating": 4.1, "reviews": 680},
            {"name": "ACS Auto Services", "website": "acsautoservices.co.uk", "rating": 4.7, "reviews": 210},
            {"name": "Pit Stop Garage", "website": "pitstopgarage.co.uk", "rating": 4.5, "reviews": 165},
            {"name": "Greenwich Motor Works", "website": "greenwichmotorworks.co.uk", "rating": 4.6, "reviews": 190},
            {"name": "Euro Car Parts Service", "website": "eurocarparts.com/service", "rating": 4.3, "reviews": 320},
        ],
        "New York": [
            {"name": "Meineke Midtown", "website": "meineke.com/midtown", "rating": 4.3, "reviews": 380},
            {"name": "Jiffy Lube Brooklyn", "website": "jiffylube.com/brooklyn", "rating": 4.2, "reviews": 290},
            {"name": "Prestige Auto Repair", "website": "prestigeautorepair.com", "rating": 4.7, "reviews": 245},
            {"name": "Manhattan Auto Service", "website": "manhattanauto.com", "rating": 4.6, "reviews": 180},
            {"name": "Brooklyn Mechanic Hub", "website": "brooklynmechanic.com", "rating": 4.8, "reviews": 155},
            {"name": "Quick Lane Times Square", "website": "quicklane.com/timessquare", "rating": 4.1, "reviews": 520},
        ],
    },
}


COUNTRY_MAP = {
    "bishkek": "Kyrgyzstan",
    "london": "UK",
    "new york": "USA",
    "nyc": "USA",
}


def _detect_country(city: str) -> str:
    lower = city.lower()
    for key, country in COUNTRY_MAP.items():
        if key in lower:
            return country
    return "Unknown"


def run_scan(city: str, niche: str, limit: int = 20) -> List[Dict]:
    google_maps = GoogleMapsService()
    businesses = google_maps.search_businesses(city, niche, limit)

    if not businesses:
        businesses = MOCK_BUSINESSES.get(niche, {}).get(city, [])

    if not businesses:
        return []

    country = _detect_country(city)
    results = []

    for biz in businesses[:limit]:
        website = biz.get("website")

        if website:
            features = analyze_website(website)
        else:
            features = {
                "has_online_booking": False,
                "has_contact_form": False,
                "has_live_chat": False,
                "closing_hour": 17,
                "has_weekend_hours": False,
                "website_quality": "none",
            }

        score, tier = score_business(features, biz.get("rating", 4.0), biz.get("reviews", 100))
        loss = estimate_loss(features, tier)

        reasons = []
        if not website:
            reasons.append("No website")
        if not features["has_online_booking"]:
            reasons.append("No online booking")
        if not features["has_contact_form"]:
            reasons.append("No contact form")
        if not features["has_live_chat"]:
            reasons.append("No live chat")
        if features["closing_hour"] <= 17:
            reasons.append("Closes early")
        if not features["has_weekend_hours"]:
            reasons.append("No weekend hours")

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

    results.sort(key=lambda x: x["score"], reverse=True)
    return results
