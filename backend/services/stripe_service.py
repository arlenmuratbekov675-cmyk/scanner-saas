"""
Stripe Integration - Paywall + Payment processing.
"""
import os
import stripe
from typing import Optional


PLANS = {
    "free": {
        "name": "Free",
        "price": 0,
        "scans_per_day": 1,
        "businesses_per_scan": 3,
        "features": ["Basic scores", "Limited results"],
    },
    "pro": {
        "name": "Pro",
        "price": 19,
        "stripe_price_id": "price_1TiLBe1FfXNVtspmv26Lbva0",
        "scans_per_day": -1,
        "businesses_per_scan": 50,
        "features": ["Unlimited scans", "Full results", "PDF export", "Priority support"],
    },
    "business": {
        "name": "Business",
        "price": 49,
        "stripe_price_id": "price_1TiLFG1FfXNVtspmYZzA02r3",
        "scans_per_day": -1,
        "businesses_per_scan": 200,
        "features": ["Everything in Pro", "API access", "Custom niches", "White-label reports"],
    },
}


class StripeService:
    """Handle Stripe payments and subscriptions."""

    def _get_key(self):
        return os.getenv("STRIPE_SECRET_KEY", "")

    @property
    def enabled(self):
        key = self._get_key()
        return bool(key) and key.startswith("sk_")

    def create_checkout_session(
        self,
        plan: str,
        user_email: str,
        success_url: str,
        cancel_url: str,
    ) -> Optional[str]:
        if not self.enabled:
            return None

        plan_data = PLANS.get(plan)
        if not plan_data or plan == "free":
            return None

        try:
            stripe.api_key = self._get_key()
            session = stripe.checkout.Session.create(
                mode="subscription",
                payment_method_types=["card"],
                customer_email=user_email,
                line_items=[{
                    "price": plan_data["stripe_price_id"],
                    "quantity": 1,
                }],
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={"plan": plan},
            )
            return session.url
        except Exception as e:
            print(f"Stripe error: {e}")
            return None

    def create_portal_session(
        self,
        customer_id: str,
        return_url: str,
    ) -> Optional[str]:
        if not self.enabled:
            return None

        try:
            stripe.api_key = self._get_key()
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )
            return session.url
        except Exception as e:
            print(f"Stripe portal error: {e}")
            return None

    def check_subscription(self, customer_id: str) -> dict:
        if not self.enabled:
            return {"active": False, "plan": "free"}

        try:
            stripe.api_key = self._get_key()
            subscriptions = stripe.Subscription.list(
                customer=customer_id,
                status="active",
            )
            if subscriptions.data:
                sub = subscriptions.data[0]
                plan = sub.metadata.get("plan", "free")
                return {"active": True, "plan": plan, "subscription_id": sub.id}
            return {"active": False, "plan": "free"}
        except Exception:
            return {"active": False, "plan": "free"}


stripe_service = StripeService()
