"""
Scanner SaaS - Backend API
Find businesses that are losing customers.
Includes paywall logic for free/paid tiers.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

from core.scanner import run_scan
from services.stripe_service import stripe_service, PLANS


app = FastAPI(
    title="Business Scanner API",
    description="Find businesses losing money from operational gaps",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScanRequest(BaseModel):
    city: str
    niche: str
    limit: int = 20
    user_email: Optional[str] = None
    plan: str = "free"


class CheckoutRequest(BaseModel):
    plan: str
    email: str


class BusinessResult(BaseModel):
    name: str
    city: str
    country: str
    website: str
    score: int
    tier: str
    monthly_loss_estimate: int
    reasons: List[str]
    has_online_booking: bool
    has_contact_form: bool
    has_live_chat: bool
    rating: float
    review_count: int


class ScanResponse(BaseModel):
    city: str
    niche: str
    total_found: int
    total_available: int
    results: List[BusinessResult]
    summary: dict
    is_preview: bool
    paywall_message: Optional[str] = None
    upgrade_url: Optional[str] = None


@app.get("/")
def root():
    return {
        "name": "Business Scanner API",
        "version": "1.0.0",
        "docs": "/docs",
        "plans": PLANS,
    }


@app.post("/scan", response_model=ScanResponse)
def scan(request: ScanRequest):
    """Scan businesses in a city/niche and find money leaks."""
    plan_config = PLANS.get(request.plan, PLANS["free"])
    
    # Get all results
    all_results = run_scan(request.city, request.niche, 200)
    total_available = len(all_results)
    
    # Apply limits based on plan
    max_businesses = plan_config["businesses_per_scan"]
    if max_businesses == -1:
        # Unlimited
        results = all_results
        is_preview = False
    else:
        results = all_results[:max_businesses]
        is_preview = total_available > max_businesses
    
    # Calculate summary
    tier_counts = {"A": 0, "B": 0, "C": 0}
    total_loss = 0
    for r in results:
        tier_counts[r["tier"]] += 1
        total_loss += r["monthly_loss_estimate"]
    
    # Calculate full summary (including hidden results)
    full_total_loss = sum(r["monthly_loss_estimate"] for r in all_results)
    
    summary = {
        "tier_distribution": tier_counts,
        "total_estimated_monthly_loss": total_loss,
        "full_estimated_monthly_loss": full_total_loss,
        "avg_score": sum(r["score"] for r in results) / len(results) if results else 0,
    }
    
    # Paywall message
    paywall_message = None
    upgrade_url = None
    if is_preview:
        hidden_count = total_available - max_businesses
        paywall_message = f"You're seeing {max_businesses} of {total_available} businesses. Unlock {hidden_count} more + full report."
        upgrade_url = "/checkout?plan=pro"
    
    return ScanResponse(
        city=request.city,
        niche=request.niche,
        total_found=len(results),
        total_available=total_available,
        results=results,
        summary=summary,
        is_preview=is_preview,
        paywall_message=paywall_message,
        upgrade_url=upgrade_url,
    )


@app.post("/checkout")
def create_checkout(request: CheckoutRequest):
    """Create Stripe checkout session for subscription."""
    if request.plan == "free":
        raise HTTPException(status_code=400, detail="Free plan doesn't require checkout")
    
    checkout_url = stripe_service.create_checkout_session(
        plan=request.plan,
        user_email=request.email,
        success_url="https://scanner-saas-five.vercel.app/app.html?paid=true",
        cancel_url="https://scanner-saas-five.vercel.app/app.html",
    )
    
    if not checkout_url:
        # Fallback: return pricing info
        plan_data = PLANS.get(request.plan, {})
        return {
            "message": "Stripe not configured. Contact us to upgrade.",
            "plan": request.plan,
            "price": plan_data.get("price", 0),
            "features": plan_data.get("features", []),
        }
    
    return {"checkout_url": checkout_url}


@app.get("/plans")
def get_plans():
    """Get available pricing plans."""
    return PLANS


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/debug/stripe")
def debug_stripe():
    import os
    key = os.getenv("STRIPE_SECRET_KEY", "")
    return {
        "env_key_exists": bool(key),
        "key_prefix": key[:7] if key else "none",
        "service_enabled": stripe_service.enabled,
        "pro_price": PLANS["pro"]["stripe_price_id"],
        "biz_price": PLANS["business"]["stripe_price_id"],
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
