"""Stripe agent for handling subscription payments."""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Optional

class SubscriptionTier(Enum):
    """Available subscription tiers."""
    FREEMIUM = "freemium"
    PREMIUM = "premium"

@dataclass
class SubscriptionConfig:
    """Configuration for subscription tiers."""
    daily_plans: int
    resources_per_plan: int
    email_notifications: bool
    price: float  # Price in USD
    tier: SubscriptionTier = SubscriptionTier.FREEMIUM

class StripeAgent:
    """Agent for handling Stripe subscription payments."""
    
    def __init__(self):
        """Initialize the Stripe agent."""
        self.tier_configs = {
            SubscriptionTier.FREEMIUM: SubscriptionConfig(
                daily_plans=1,
                resources_per_plan=3,
                email_notifications=False,
                price=0.0,
                tier=SubscriptionTier.FREEMIUM
            ),
            SubscriptionTier.PREMIUM: SubscriptionConfig(
                daily_plans=10,
                resources_per_plan=10,
                email_notifications=True,
                price=9.99,
                tier=SubscriptionTier.PREMIUM
            )
        }

    def get_tier_features(self, tier: SubscriptionTier) -> Dict:
        """Get features for a subscription tier."""
        config = self.tier_configs[tier]
        return {
            "daily_plans": config.daily_plans,
            "resources_per_plan": config.resources_per_plan,
            "email_notifications": config.email_notifications,
            "price": config.price
        }

    def get_tier_description(self, tier: SubscriptionTier) -> str:
        """Get a formatted description of tier features."""
        features = self.get_tier_features(tier)
        price_str = 'Free' if features['price'] == 0 else f"${features['price']:.2f}/month"
        description = f"""
### {tier.value.title()} Plan Features:
- {features['daily_plans']} learning plans per day
- Up to {features['resources_per_plan']} resources per plan
- Email notifications: {'✅' if features['email_notifications'] else '❌'}
- Price: {price_str}
        """
        return description.strip()

    def create_checkout_session(self, success_url: str, cancel_url: str) -> Dict:
        """Create a Stripe checkout session for premium subscription using MCP."""
        try:
            return {
                "price_data": {
                    "currency": "usd",
                    "unit_amount": int(self.tier_configs[SubscriptionTier.PREMIUM].price * 100),
                    "product_data": {
                        "name": "Premium Subscription",
                        "description": "Access to premium features including unlimited plans and email notifications"
                    }
                },
                "success_url": success_url,
                "cancel_url": cancel_url,
                "mode": "subscription"
            }
        except Exception as e:
            raise Exception(f"Failed to create checkout session: {str(e)}")

    def can_create_plan(self, tier: SubscriptionTier, plans_created: int) -> bool:
        """Check if user can create more plans today."""
        return plans_created < self.tier_configs[tier].daily_plans

    def get_max_resources(self, tier: SubscriptionTier) -> int:
        """Get maximum number of resources allowed per plan for a tier."""
        return self.tier_configs[tier].resources_per_plan

    def can_receive_emails(self, tier: SubscriptionTier) -> bool:
        """Check if email notifications are enabled for a tier."""
        return self.tier_configs[tier].email_notifications

    def process_subscription_upgrade(self, session_id: str) -> bool:
        """Process a successful subscription upgrade."""
        try:
            # Here we would typically verify the session with Stripe
            # and update the user's subscription status
            return True
        except Exception as e:
            raise Exception(f"Failed to process subscription upgrade: {str(e)}")

    def get_upgrade_recommendation(self, current_tier: SubscriptionTier) -> str:
        """Get personalized upgrade recommendation."""
        if current_tier == SubscriptionTier.PREMIUM:
            return "You're already on the Premium tier with all features unlocked!"

        premium_features = self.get_tier_features(SubscriptionTier.PREMIUM)
        current_features = self.get_tier_features(current_tier)
        
        return f"""
Upgrade to Premium to unlock:
- {premium_features['daily_plans']} learning plans per day (currently {current_features['daily_plans']})
- Up to {premium_features['resources_per_plan']} resources per plan (currently {current_features['resources_per_plan']})
- Email notifications and plan sharing
- Priority support
        """.strip() 