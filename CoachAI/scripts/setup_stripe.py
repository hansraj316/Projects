"""Script to validate Stripe configuration and set up webhooks."""

import os
import stripe
from dotenv import load_dotenv
import sys
from pathlib import Path

def load_env():
    """Load environment variables."""
    env_path = Path(__file__).parent.parent / 'config' / '.env'
    load_dotenv(env_path)
    
    required_vars = [
        'STRIPE_SECRET_KEY',
        'STRIPE_PUBLISHABLE_KEY'
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        print(f"❌ Missing required environment variables: {', '.join(missing)}")
        sys.exit(1)

def validate_stripe_keys():
    """Validate Stripe API keys."""
    try:
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        # Test the API key by making a simple request
        account = stripe.Account.retrieve()
        print("✅ Stripe API keys are valid")
        print(f"Connected to Stripe account: {account.id}")
        return True
    except stripe.error.AuthenticationError:
        print("❌ Invalid Stripe API key")
        return False
    except Exception as e:
        print(f"❌ Error validating Stripe keys: {str(e)}")
        return False

def setup_products():
    """Set up Stripe products and prices."""
    try:
        # Create or retrieve the premium subscription product
        products = stripe.Product.list(limit=1, active=True)
        if not products.data:
            product = stripe.Product.create(
                name="Premium Subscription",
                description="Access to premium features including unlimited plans and email notifications"
            )
            print("✅ Created new product for premium subscription")
        else:
            product = products.data[0]
            print("✅ Using existing product for premium subscription")

        # Create or retrieve the price
        prices = stripe.Price.list(
            product=product.id,
            active=True,
            limit=1
        )
        if not prices.data:
            price = stripe.Price.create(
                product=product.id,
                unit_amount=999,  # $9.99
                currency="usd",
                recurring={"interval": "month"}
            )
            print("✅ Created new price for premium subscription")
        else:
            price = prices.data[0]
            print("✅ Using existing price for premium subscription")

        print(f"Product ID: {product.id}")
        print(f"Price ID: {price.id}")
        return True
    except Exception as e:
        print(f"❌ Error setting up products: {str(e)}")
        return False

def setup_local_dev():
    """Set up local development environment."""
    print("\n🔧 Local Development Setup")
    print("1. Install Stripe CLI:")
    print("   brew install stripe/stripe-cli/stripe")
    print("\n2. Login to Stripe CLI:")
    print("   stripe login")
    print("\n3. Start webhook forwarding:")
    print("   stripe listen --forward-to localhost:8501/webhook")
    print("\n4. Copy the webhook signing secret and update STRIPE_WEBHOOK_SECRET in your .env file")
    
    input("\nPress Enter when you've completed these steps...")

def main():
    """Main function."""
    print("🔄 Setting up Stripe integration...")
    
    # Load environment variables
    load_env()
    
    # Validate Stripe keys
    if not validate_stripe_keys():
        return
    
    # Set up products and prices
    if not setup_products():
        return
    
    # Guide through local development setup
    setup_local_dev()
    
    print("\n✨ Stripe setup completed!")
    print("\nNext steps:")
    print("1. Start the Stripe MCP server:")
    print("   npx -y @stripe/mcp --tools=all")
    print("2. Start your Streamlit app:")
    print("   streamlit run ui/web/app.py")

if __name__ == "__main__":
    main() 