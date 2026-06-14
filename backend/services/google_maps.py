"""
Google Maps Service - Real business data from Google Places API.
"""
import os
import httpx
from typing import List, Dict, Optional


class GoogleMapsService:
    """
    Fetch real business data from Google Maps / Places API.
    
    Requires: GOOGLE_MAPS_API_KEY environment variable
    """
    
    BASE_URL = "https://maps.googleapis.com/maps/api/place"
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GOOGLE_MAPS_API_KEY")
    
    def search_businesses(
        self,
        city: str,
        niche: str,
        limit: int = 20
    ) -> List[Dict]:
        """
        Search for businesses in a city/niche using Google Places API.
        """
        if not self.api_key:
            return self._fallback_search(city, niche, limit)
        
        # Build search query
        query = f"{niche} in {city}"
        
        # Google Places Text Search
        url = f"{self.BASE_URL}/textsearch/json"
        params = {
            "query": query,
            "key": self.api_key,
            "type": "dentist" if niche == "dental" else "beauty_salon",
        }
        
        try:
            response = httpx.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get("status") != "OK":
                return self._fallback_search(city, niche, limit)
            
            businesses = []
            for place in data.get("results", [])[:limit]:
                business = {
                    "name": place.get("name"),
                    "address": place.get("formatted_address"),
                    "rating": place.get("rating", 0),
                    "reviews": place.get("user_ratings_total", 0),
                    "place_id": place.get("place_id"),
                    "website": None,
                    "phone": None,
                    "opening_hours": place.get("opening_hours"),
                }
                businesses.append(business)
            
            # Fetch additional details for each business
            for biz in businesses:
                details = self._get_place_details(biz["place_id"])
                if details:
                    biz["website"] = details.get("website")
                    biz["phone"] = details.get("formatted_phone_number")
                    biz["opening_hours"] = details.get("opening_hours")
            
            return businesses
            
        except Exception as e:
            print(f"Google Maps API error: {e}")
            return self._fallback_search(city, niche, limit)
    
    def _get_place_details(self, place_id: str) -> Optional[Dict]:
        """Get detailed info for a specific place."""
        if not self.api_key or not place_id:
            return None
        
        url = f"{self.BASE_URL}/details/json"
        params = {
            "place_id": place_id,
            "key": self.api_key,
            "fields": "website,formatted_phone_number,opening_hours",
        }
        
        try:
            response = httpx.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get("status") == "OK":
                return data.get("result")
            return None
            
        except Exception:
            return None
    
    def _fallback_search(self, city: str, niche: str, limit: int) -> List[Dict]:
        """
        Fallback to mock data when API is not available.
        In production, replace with 2GIS or other local directory.
        """
        # Import mock data from scanner
        from core.scanner import MOCK_BUSINESSES
        
        mock_data = MOCK_BUSINESSES.get(niche, {}).get(city, [])
        
        businesses = []
        for biz in mock_data[:limit]:
            businesses.append({
                "name": biz["name"],
                "address": f"{city}, Kyrgyzstan",
                "rating": biz.get("rating", 4.5),
                "reviews": biz.get("reviews", 100),
                "place_id": None,
                "website": biz.get("website"),
                "phone": None,
                "opening_hours": None,
            })
        
        return businesses
    
    def analyze_business(self, business: Dict) -> Dict:
        """
        Analyze a business for money leak indicators.
        """
        features = {
            "has_website": bool(business.get("website")),
            "has_phone": bool(business.get("phone")),
            "rating": business.get("rating", 0),
            "reviews": business.get("reviews", 0),
            "has_hours": bool(business.get("opening_hours")),
        }
        
        # Check website for booking/chat
        if business.get("website"):
            try:
                response = httpx.get(business["website"], timeout=5)
                html = response.text.lower()
                features["has_online_booking"] = any(term in html for term in [
                    "booking", "appointment", "schedule", "zocdoc"
                ])
                features["has_live_chat"] = any(term in html for term in [
                    "chat", "intercom", "drift", "crisp", "tawk"
                ])
            except Exception:
                features["has_online_booking"] = False
                features["has_live_chat"] = False
        else:
            features["has_online_booking"] = False
            features["has_live_chat"] = False
        
        return features
