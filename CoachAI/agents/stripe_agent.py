"""Stripe agent for handling subscription payments."""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Optional, Any, List
from datetime import datetime, timezone
import os
import stripe
import json
import asyncio

class PaymentStatus(Enum):
    """Payment status enum."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

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
    payment_status: PaymentStatus = PaymentStatus.PENDING
    payment_id: Optional[str] = None
    subscription_id: Optional[str] = None
    last_updated: Optional[datetime] = None

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
        
        # Get API key from environment
        self.api_key = os.getenv('STRIPE_SECRET_KEY', '')
        if not self.api_key:
            print("Warning: Stripe API key not found in environment variables")
            
        # Initialize Stripe API
        stripe.api_key = self.api_key
        
    async def setup_webhook_endpoint(self, webhook_url: str) -> Dict:
        """Set up webhook endpoint for payment notifications."""
        try:
            # Run stripe API calls in a separate thread to avoid blocking
            loop = asyncio.get_event_loop()
            
            # Get API key from environment
            api_key = os.getenv('STRIPE_SECRET_KEY', '')
            if not api_key:
                raise Exception("Stripe API key not found in environment variables")
                
            webhook = await loop.run_in_executor(
                None,
                lambda: stripe.WebhookEndpoint.create(
                    url=webhook_url,
                    enabled_events=[
                        "checkout.session.completed",
                        "invoice.payment_failed",
                        "customer.subscription.created",
                        "customer.subscription.updated",
                        "customer.subscription.deleted"
                    ],
                    api_key=api_key
                )
            )
            return {"webhook_secret": webhook.secret}
        except Exception as e:
            raise Exception(f"Failed to set up webhook: {str(e)}")

    async def create_customer(self, email: str, name: Optional[str] = None) -> Dict:
        """Create a new customer in Stripe."""
        try:
            loop = asyncio.get_event_loop()
            customer = await loop.run_in_executor(
                None,
                lambda: stripe.Customer.create(
                    email=email,
                    name=name,
                    metadata={"tier": SubscriptionTier.FREEMIUM.value},
                    api_key=self.api_key
                )
            )
            return {"customer_id": customer.id}
        except Exception as e:
            raise Exception(f"Failed to create customer: {str(e)}")

    async def create_checkout_session(self, success_url: str, cancel_url: str, customer_id: Optional[str] = None) -> Dict:
        """Create a Stripe checkout session for premium subscription."""
        try:
            # Set stripe API key
            import stripe
            stripe.api_key = self.api_key
            
            print(f"Creating checkout session with API key: {self.api_key[:5]}...")
            
            # Get or create a price for the subscription
            price_id = None
            
            # First try to find an existing price
            try:
                prices = stripe.Price.list(
                    active=True,
                    limit=10,
                    expand=["data.product"]
                )
                
                # Look for a price with a subscription that matches our description
                for price in prices.data:
                    if hasattr(price, 'product') and price.product and hasattr(price.product, 'name'):
                        if price.product.name == "Premium Subscription":
                            price_id = price.id
                            print(f"Found existing price: {price_id}")
                            break
            except Exception as e:
                print(f"Error finding prices: {str(e)}")
            
            # If no price found, create a new one
            if not price_id:
                print("Creating new product and price...")
                try:
                    # Create product
                    product = stripe.Product.create(
                        name="Premium Subscription",
                        description="Access to premium features"
                    )
                    
                    # Create price
                    price = stripe.Price.create(
                        product=product.id,
                        unit_amount=int(self.tier_configs[SubscriptionTier.PREMIUM].price * 100),
                        currency="usd",
                        recurring={"interval": "month"}
                    )
                    
                    price_id = price.id
                    print(f"Created new price: {price_id}")
                except Exception as e:
                    print(f"Error creating product/price: {str(e)}")
                    raise e
            
            # Prepare success URL with session ID parameter
            # Make sure to use the Stripe format {CHECKOUT_SESSION_ID} (without quotes)
            success_url_with_session = f"{success_url}?session_id={{CHECKOUT_SESSION_ID}}"
            
            print(f"Using success URL: {success_url_with_session}")
            
            # Prepare checkout session data
            checkout_data = {
                "success_url": success_url_with_session,
                "cancel_url": cancel_url,
                "mode": "subscription",
                "line_items": [
                    {
                        "price": price_id,
                        "quantity": 1
                    }
                ]
            }
            
            # Add customer only if provided
            if customer_id:
                checkout_data["customer"] = customer_id
                print(f"Added customer {customer_id} to checkout data")
            
            print("Creating checkout session with data:", checkout_data)
            
            # Create checkout session with minimal parameters
            checkout_session = stripe.checkout.Session.create(**checkout_data)
            
            print(f"Checkout session created with ID: {checkout_session.id}")
            print(f"Payment URL: {checkout_session.url}")
            
            return {
                "payment_link": checkout_session.url,
                "session_id": checkout_session.id
            }
            
        except Exception as e:
            print(f"Error creating checkout session: {str(e)}")
            raise Exception(f"Failed to create checkout session: {str(e)}")

    def update_subscription_status(self, customer_id: str, subscription_id: str, tier: SubscriptionTier) -> Dict:
        """Update a user's subscription status."""
        try:
            # Update customer metadata
            customer = stripe.Customer.modify(
                customer_id,
                metadata={"tier": tier.value},
                api_key=self.api_key
            )
            
            # Update subscription metadata
            subscription = stripe.Subscription.modify(
                subscription_id,
                metadata={"tier": tier.value},
                api_key=self.api_key
            )
            
            return {
                "status": "success",
                "customer_id": customer_id,
                "subscription_id": subscription_id,
                "tier": tier.value
            }
        except Exception as e:
            raise Exception(f"Failed to update subscription status: {str(e)}")

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

    def can_create_plan(self, tier: SubscriptionTier, plans_created: int) -> bool:
        """Check if user can create more plans today."""
        return plans_created < self.tier_configs[tier].daily_plans

    def get_max_resources(self, tier: SubscriptionTier) -> int:
        """Get maximum number of resources allowed per plan for a tier."""
        return self.tier_configs[tier].resources_per_plan

    def can_receive_emails(self, tier: SubscriptionTier) -> bool:
        """Check if email notifications are enabled for this tier."""
        return self.tier_configs[tier].email_notifications

    def get_max_plans(self, tier: SubscriptionTier) -> int:
        """Get maximum number of plans allowed for a tier.
        
        Args:
            tier: The subscription tier to check
            
        Returns:
            int: Maximum number of plans allowed for this tier
        """
        return self.tier_configs[tier].daily_plans

    def get_upgrade_recommendation(self, current_tier: SubscriptionTier) -> str:
        """Get a recommendation message for upgrading to a higher tier."""
        if current_tier == SubscriptionTier.PREMIUM:
            return "You already have our premium plan!"
        
        return "Upgrade to Premium for more learning plans, resources, and email notifications!"
        
    async def verify_checkout_session(self, session_id: str) -> Dict:
        """Verify a checkout session by ID.
        
        Args:
            session_id: The Stripe checkout session ID to verify
            
        Returns:
            Dict containing session details and status
        """
        try:
            # Import stripe here to avoid circular imports
            import stripe
            
            # Set API key
            stripe.api_key = self.api_key
            
            # Use event loop to avoid blocking
            loop = asyncio.get_event_loop()
            
            # Retrieve the session
            session = await loop.run_in_executor(
                None,
                lambda: stripe.checkout.Session.retrieve(
                    session_id,
                    expand=['subscription', 'customer']
                )
            )
            
            # Check if the session is paid
            if session.payment_status == 'paid':
                # If we have both customer and subscription, update our records
                customer_id = session.customer.id if session.customer else None
                subscription_id = session.subscription.id if session.subscription else None
                
                if customer_id and subscription_id:
                    # Update subscription status
                    self.update_subscription_status(
                        customer_id=customer_id,
                        subscription_id=subscription_id,
                        tier=SubscriptionTier.PREMIUM
                    )
                
                return {
                    "status": "success",
                    "payment_status": session.payment_status,
                    "customer_id": customer_id,
                    "subscription_id": subscription_id
                }
            else:
                return {
                    "status": "pending",
                    "payment_status": session.payment_status,
                    "message": "Payment is not yet complete"
                }
            
        except Exception as e:
            print(f"Error verifying checkout session: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            } 