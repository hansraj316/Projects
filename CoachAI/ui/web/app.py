"""
Streamlit web application for CoachAI.
Provides UI for creating personalized learning plans.
"""

import os
import json
import hmac
import hashlib
import asyncio
import nest_asyncio
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
import logging
import re

import streamlit as st

# Set page config - must be the first Streamlit command
st.set_page_config(
    page_title="CoachAI - Your Personalized Learning Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Check for OpenAI API key at startup
api_key = os.environ.get("OPENAI_API_KEY", "")
if not api_key or api_key == "your_openai_api_key_here":
    st.sidebar.warning("⚠️ OpenAI API Key Not Set")
    st.sidebar.info("""
    To generate learning plans, you need a valid OpenAI API key.
    
    1. Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
    2. Create an API key
    3. Enter it below and click 'Save'
    """)
    
    # Input field for API key
    new_api_key = st.sidebar.text_input("Enter OpenAI API Key", type="password", key="api_key_input")
    
    if st.sidebar.button("Save API Key"):
        if new_api_key and new_api_key.strip():
            os.environ["OPENAI_API_KEY"] = new_api_key
            st.sidebar.success("✅ API key saved!")
            st.rerun()
        else:
            st.sidebar.error("Please enter a valid API key")

# Configure logging to redirect to a file instead of to console (to avoid UI errors)
try:
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    logging.basicConfig(
        filename='logs/coachai.log',
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    # Create a logger instance
    logger = logging.getLogger('coachai')
except Exception as e:
    # Fallback logging setup that won't break the UI
    logger = logging.getLogger('coachai')
    logger.setLevel(logging.ERROR)
    logger.addHandler(logging.NullHandler())
    print(f"Warning: Could not configure logging: {e}")

# Apply modern, clean UI styling with dark mode
st.markdown("""
<style>
/* Global styles - Dark Mode */
.stApp {
    background-color: #121212;
    color: #e0e0e0;
    font-family: 'Inter', sans-serif;
}

/* Hide error messages */
.stException, .element-container:has(div.stException) {
    display: none !important;
}

/* Sidebar styling - Dark Mode */
section[data-testid="stSidebar"] {
    background-color: #1e1e1e !important;
    border-right: 1px solid #333;
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 1rem;
}

/* Logo and app name - Dark Mode */
.logo-container {
    display: flex;
    align-items: center;
    padding: 15px 20px;
    margin-bottom: 20px;
    border-bottom: 1px solid #333;
}

.logo-text {
    font-size: 20px;
    font-weight: bold;
    color: #e0e0e0;
    margin-left: 10px;
}

/* Navigation items - Dark Mode */
.nav-item {
    display: flex;
    align-items: center;
    padding: 10px 20px;
    margin: 5px 10px;
    border-radius: 8px;
    color: #e0e0e0;
    text-decoration: none;
    transition: background-color 0.3s;
}

.nav-item:hover {
    background-color: #2c2c2c;
}

.nav-item.active {
    background-color: #2c2c2c;
    color: #60a5fa;
    font-weight: 500;
}

.nav-item-icon {
    margin-right: 10px;
    width: 24px;
    text-align: center;
}

/* Main content area - Dark Mode */
.main-content {
    background-color: #1e1e1e;
    border-radius: 12px;
    padding: 20px;
    margin: 10px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

/* Cards and dashboard widgets - Dark Mode */
.card {
    background-color: #2c2c2c;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    border: 1px solid #444;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.card-title {
    font-size: 16px;
    font-weight: 600;
    color: #e0e0e0;
}

/* Headings - Dark Mode */
h1, h2, h3, h4, h5, h6 {
    color: #e0e0e0;
}

/* Text color - Dark Mode */
p, div, span, label {
    color: #e0e0e0;
}

/* Input fields - Dark Mode */
input, .stTextInput>div>div>input, div[data-baseweb="base-input"] {
    background-color: #333 !important;
    color: #e0e0e0 !important;
    border-color: #555 !important;
}

/* Buttons styling - Dark Mode */
.stButton button {
    border-radius: 8px;
    font-weight: 500;
    transition: all 0.2s;
    background-color: #2c2c2c;
    color: #e0e0e0;
    border: 1px solid #444;
}

.stButton button:hover {
    background-color: #3a3a3a;
}

.stButton button[kind="primary"] {
    background-color: #3b82f6;
    color: white;
}

.stButton button[kind="primary"]:hover {
    background-color: #2563eb;
}

/* Header with welcome message - Dark Mode */
.welcome-header {
    background-color: #2c2c2c;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.welcome-text {
    color: #e0e0e0;
}

.welcome-text h2 {
    font-weight: 600;
    margin-bottom: 10px;
}

.welcome-text p {
    color: #b0b0b0;
}

/* Learning plan timetable - Dark Mode */
.timetable-week {
    background-color: #2c2c2c;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 10px;
}

.timetable-week-header {
    font-weight: 600;
    margin-bottom: 10px;
    color: #60a5fa;
}

.activity-item {
    padding: 10px;
    border-left: 3px solid #3b82f6;
    background-color: #333;
    margin-bottom: 8px;
    border-radius: 0 4px 4px 0;
}

/* Progress bar styling - Dark Mode */
.stProgress > div > div {
    background-color: #3b82f6;
}

/* Premium badge - Dark Mode */
.premium-badge {
    background-color: #422006;
    color: #f59e0b;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;
}

/* Upgrade button - Dark Mode */
.upgrade-button {
    background-color: #3b82f6;
    color: white;
    padding: 8px 16px;
    border-radius: 8px;
    font-weight: 500;
    text-align: center;
    cursor: pointer;
    transition: background-color 0.3s;
}

.upgrade-button:hover {
    background-color: #2563eb;
}

/* User profile - Dark Mode */
.user-profile {
    display: flex;
    align-items: center;
    padding: 10px;
    border-radius: 8px;
    margin-bottom: 20px;
}

.profile-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background-color: #444;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 10px;
}

.profile-name {
    font-weight: 500;
}

/* Tab styling - Dark Mode */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: #1e1e1e;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 4px 4px 0 0;
    padding: 10px 16px;
    font-weight: 500;
    color: #e0e0e0;
}

.stTabs [aria-selected="true"] {
    background-color: #2c2c2c !important;
    color: #60a5fa !important;
}

/* Selectbox styles - Dark Mode */
div[data-baseweb="select"] {
    background-color: #333;
}

div[data-baseweb="select"] > div {
    background-color: #333;
    color: #e0e0e0;
    border-color: #555;
}

/* Radio button styles - Dark Mode */
.stRadio label {
    color: #e0e0e0;
}

/* Slider styles - Dark Mode */
.stSlider div[role="slider"] {
    background-color: #3b82f6;
}

/* Info box - Dark Mode */
.stAlert {
    background-color: #2c2c2c;
    color: #e0e0e0;
}

/* Success box - Dark Mode */
div[data-baseweb="notification"] {
    background-color: #1e392a !important;
}

/* Error box - Dark Mode */
div[role="alert"] {
    background-color: #3a1c1c !important;
}

/* Warning box - Dark Mode */
div[data-baseweb="notification"][kind="warning"] {
    background-color: #3a2e1a !important;
}
</style>
""", unsafe_allow_html=True)

# Apply nest_asyncio to allow running asyncio in Streamlit
nest_asyncio.apply()

# Import custom agents and models
from agents.planner import PlannerAgent, LearningGoal, LearningPlan
from agents.email_agent import EmailAgent, EmailConfig
from agents.stripe_agent import StripeAgent, SubscriptionTier, SubscriptionConfig, PaymentStatus

# Initialize session state at startup
if 'step' not in st.session_state:
    st.session_state.step = 1

if 'responses' not in st.session_state:
    st.session_state.responses = {}
    
if 'plans_created_today' not in st.session_state:
    st.session_state.plans_created_today = 0
    
if 'upgrading' not in st.session_state:
    st.session_state.upgrading = False
    
# Initialize UI state variables
if 'show_notes' not in st.session_state:
    st.session_state.show_notes = False
    
if 'show_schedule' not in st.session_state:
    st.session_state.show_schedule = False
    
if 'show_more_resources' not in st.session_state:
    st.session_state.show_more_resources = False
    
if 'show_progress_tracker' not in st.session_state:
    st.session_state.show_progress_tracker = False
    
if 'has_plan' not in st.session_state:
    st.session_state.has_plan = False
    
if 'current_plan' not in st.session_state:
    st.session_state.current_plan = None
    
if 'planner_agent' not in st.session_state:
    try:
        from agents.planner import PlannerAgent
        st.session_state.planner_agent = PlannerAgent()
    except Exception as e:
        st.error(f"Failed to initialize PlannerAgent: {str(e)}")
    
if 'stripe_agent' not in st.session_state:
    st.session_state.stripe_agent = StripeAgent()
    
if 'email_agent' not in st.session_state:
    st.session_state.email_agent = EmailAgent()
    
if 'webhook_secret' not in st.session_state:
    st.session_state.webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET', '')
    
if 'subscription' not in st.session_state:
    st.session_state.subscription = SubscriptionConfig(
        daily_plans=1,
        resources_per_plan=3,
        email_notifications=False,
        price=0.0,
        tier=SubscriptionTier.FREEMIUM
    )
    
if 'customer_id' not in st.session_state:
    st.session_state.customer_id = None
    
if 'has_premium' not in st.session_state:
    st.session_state.has_premium = False
else:
    # If user had premium, make sure their tier is set correctly
    if st.session_state.has_premium:
        st.session_state.subscription.tier = SubscriptionTier.PREMIUM

# Functions for session state management
def init_session():
    """Initialize session state variables."""
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        st.session_state.current_step = 0
        st.session_state.responses = {}
        st.session_state.plan = None
        st.session_state.error = None
        
        # Initialize subscription with default freemium tier
        st.session_state.subscription = SubscriptionConfig(
            daily_plans=3,
            resources_per_plan=5,
            email_notifications=False,
            price=0,
            tier=SubscriptionTier.FREEMIUM
        )
        st.session_state.has_premium = False
        st.session_state.customer_id = None
        st.session_state.user_email = None
        
        # Check for existing subscription if user is logged in
        if "user_email" in st.session_state:
            user_email = st.session_state.user_email
            subscriptions_dir = os.path.join(os.path.dirname(__file__), "subscriptions")
            file_name = os.path.join(subscriptions_dir, f"{user_email.replace('@', '_at_')}.json")
            
            if os.path.exists(file_name):
                try:
                    with open(file_name, "r") as f:
                        subscription_data = json.load(f)
                    
                    if subscription_data.get("status") == "active":
                        # Load premium subscription
                        st.session_state.subscription = SubscriptionConfig(
                            daily_plans=10,
                            resources_per_plan=10,
                            email_notifications=True,
                            price=9.99,
                            tier=SubscriptionTier.PREMIUM
                        )
                        st.session_state.has_premium = True
                        st.session_state.customer_id = subscription_data.get("customer_id")
                except Exception as e:
                    logging.error(f"Error loading subscription data: {e}")
                    # Keep default freemium tier on error
                    pass
        
        # Initialize agents
        try:
            from agents.planner import PlannerAgent
            from agents.email_agent import EmailAgent
            from agents.stripe_agent import StripeAgent
            
            st.session_state.planner_agent = PlannerAgent()
            st.session_state.email_agent = EmailAgent()
            st.session_state.stripe_agent = StripeAgent()
        except Exception as e:
            logging.error(f"Error initializing agents: {e}")
            st.session_state.error = str(e)
            
        # Initialize other session variables
        st.session_state.webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
        st.session_state.plans_created_today = 0
        st.session_state.last_plan_date = None

def next_step():
    """Proceed to next step."""
    st.session_state.step += 1

def prev_step():
    """Go back to previous step."""
    st.session_state.step -= 1

def verify_webhook_signature(payload: Dict, signature: str, webhook_secret: str) -> bool:
    """
    Verify the webhook request from Stripe.
    
    Args:
        payload: The webhook payload as a dictionary
        signature: The Stripe signature from the request header
        webhook_secret: The webhook secret from Stripe
        
    Returns:
        bool: True if the signature is valid, False otherwise
    """
    try:
        if not payload or not signature or not webhook_secret:
            return False
            
        # The payload should be a JSON string, not a dictionary
        payload_str = json.dumps(payload, separators=(',', ':'))
        
        # Extract timestamp and signatures from the Stripe signature
        timestamp = ""
        signatures = []
        
        parts = signature.split(",")
        for part in parts:
            key_value = part.strip().split("=", 1)
            if len(key_value) != 2:
                continue
                
            key, value = key_value
            if key == "t":
                timestamp = value
            elif key == "v1":
                signatures.append(value)
                
        if not timestamp or not signatures:
            return False
            
        # Prepare the signed payload
        signed_payload = f"{timestamp}.{payload_str}"
        
        # Generate the expected signature
        hmac_obj = hmac.new(
            webhook_secret.encode('utf-8'),
            signed_payload.encode('utf-8'),
            hashlib.sha256
        )
        expected_signature = hmac_obj.hexdigest()
        
        # Check if the expected signature matches any of the provided signatures
        return any(hmac.compare_digest(expected_signature, sig) for sig in signatures)
        
    except Exception as e:
        print(f"Error verifying webhook signature: {e}")
        return False

def _get_websocket_headers() -> Dict[str, str]:
    """Get headers from the Streamlit websocket request."""
    try:
        ctx = st.runtime.scriptrunner.get_script_run_ctx()
        if not ctx:
            return {}
            
        # A safer way to get session info without directly calling get_client
        # which was causing the "missing session_id" parameter error
        if hasattr(st.runtime, 'get_instance'):
            try:
                session_info = st.runtime.get_instance().get_client(ctx.session_id)
                if session_info and hasattr(session_info, 'request') and hasattr(session_info.request, 'headers'):
                    return session_info.request.headers
            except Exception as e:
                print(f"Could not get headers from session: {e}")
                pass
                
        # Fallback to getting headers from the context directly
        if hasattr(ctx, 'request') and hasattr(ctx.request, 'headers'):
            return ctx.request.headers
            
        return {}
    except Exception as e:
        print(f"Error getting websocket headers: {e}")
        return {}

async def setup_webhooks():
    """Set up webhook endpoints if not already configured."""
    if not st.session_state.webhook_secret:
        try:
            # Check if we're in development mode
            is_dev = os.getenv('APP_ENV', 'development') == 'development'
            
            if is_dev:
                # In development, use the webhook secret from env vars (set by Stripe CLI)
                webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
                if webhook_secret:
                    st.session_state.webhook_secret = webhook_secret
                    return
                else:
                    st.warning("Local development requires Stripe CLI for webhook forwarding. Please run: stripe listen --forward-to localhost:8501/webhook")
                    st.info("Copy the webhook signing secret and add it to your .env file as STRIPE_WEBHOOK_SECRET")
                    return
            else:
                # In production, create a webhook endpoint
                base_url = st.get_option('server.baseUrlPath') or "http://localhost:8501"
                webhook_url = f"{base_url}/webhook"
                result = await st.session_state.stripe_agent.setup_webhook_endpoint(webhook_url)
                st.session_state.webhook_secret = result["webhook_secret"]
        except Exception as e:
            st.error(f"Failed to set up webhooks: {str(e)}")
            st.info("For local development, use Stripe CLI: `stripe listen --forward-to localhost:8501/webhook`")

async def handle_subscription_upgrade():
    """Handle the subscription upgrade process using Stripe."""
    try:
        # Make sure stripe agent is initialized
        if 'stripe_agent' not in st.session_state:
            from agents.stripe_agent import StripeAgent
            st.session_state.stripe_agent = StripeAgent()
            
        stripe_agent = st.session_state.stripe_agent
        
        # Initialize webhook secret from environment if not already set
        if not st.session_state.webhook_secret:
            webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
            if webhook_secret:
                st.session_state.webhook_secret = webhook_secret
        
        # Create or get customer - simplified email collection
        email = st.session_state.get('user_email')
        if not email:
            st.markdown("""
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                <h2 style="color: #1e3a8a; margin-bottom: 15px;">Upgrade to Premium Plan 🌟</h2>
                <p style="color: #4b5563; margin-bottom: 15px; font-size: 16px;">
                    Get access to all premium features including unlimited learning plans, more resources per plan, 
                    and email notifications!
                </p>
                <ul style="color: #4b5563; margin-bottom: 20px; font-size: 16px;">
                    <li>✅ 10 learning plans per day</li>
                    <li>✅ Up to 10 resources per plan</li>
                    <li>✅ Email notifications</li>
                    <li>✅ Priority support</li>
                </ul>
                <p style="color: #4b5563; margin-bottom: 10px; font-size: 16px;"><strong>Just $9.99/month</strong></p>
            </div>
            """, unsafe_allow_html=True)
            
            email = st.text_input("Enter your email to continue:", key="email_input")
            
            if st.button("Continue to Payment"):
                if email:
                    # Store email and continue
                    st.session_state.user_email = email
                    # Don't use st.rerun() which causes problems with async functions
                    # Instead, set a flag to continue the function
                    st.session_state.continue_payment = True
                else:
                    st.warning("Please enter your email to continue.")
            
            # Check if we should continue processing based on flag
            if not st.session_state.get("continue_payment", False):
                # Exit function here until email is provided and button is clicked
                return
            else:
                # Get the email from session state since we've just set it
                email = st.session_state.user_email
                # Reset the flag for next time
                st.session_state.continue_payment = False
        
        # Debug - confirm we have the email
        print(f"Processing payment with email: {email}")
        
        # Only try to setup webhooks if we don't have a secret already
        if not st.session_state.webhook_secret:
            await setup_webhooks()
        
        # Create or get customer
        if not st.session_state.customer_id:
            with st.spinner("Creating your account..."):
                try:
                    customer_result = await stripe_agent.create_customer(email)
                    st.session_state.customer_id = customer_result["customer_id"]
                except Exception as e:
                    st.error(f"Error creating customer: {str(e)}")
                    return
        
        # Get the current server port from the request
        try:
            server_port = st.get_option("server.port")
            # If we can't get the port from options, try to parse it from the URL
            if not server_port:
                current_url = st.query_params.get('_streamlit_app_url', ['http://localhost:8501'])[0]
                server_port = current_url.split(':')[-1].split('/')[0]
        except Exception:
            # Default to 8501 if we can't determine the port
            server_port = "8501"
            
        print(f"Using server port: {server_port}")
        
        # Create URLs with query parameters instead of paths
        base_url = f"http://localhost:{server_port}"
        success_url = f"{base_url}?success=true"
        cancel_url = f"{base_url}?cancel=true"
        
        try:
            with st.spinner("Preparing your checkout session..."):
                # Directly create a checkout session with Stripe API
                import stripe
                stripe.api_key = os.getenv('STRIPE_SECRET_KEY', '')
                print(f"Creating checkout session with API key: {stripe.api_key[:5]}...")
                
                # First try to find an existing price
                prices = stripe.Price.list(
                    active=True,
                    limit=10,
                    expand=["data.product"]
                )
                
                price_id = None
                for price in prices.data:
                    if hasattr(price, 'product') and price.product and hasattr(price.product, 'name'):
                        if price.product.name == "Premium Subscription":
                            price_id = price.id
                            print(f"Found existing price: {price_id}")
                            break
                
                # If no price found, create a new one
                if not price_id:
                    print("Creating new product and price...")
                    # Create product
                    product = stripe.Product.create(
                        name="Premium Subscription",
                        description="Access to premium features"
                    )
                    
                    # Create price
                    price = stripe.Price.create(
                        product=product.id,
                        unit_amount=999,  # $9.99
                        currency="usd",
                        recurring={"interval": "month"}
                    )
                    
                    price_id = price.id
                    print(f"Created new price: {price_id}")
                
                # Add customer ID if we have one
                if st.session_state.customer_id:
                    print(f"Added customer {st.session_state.customer_id} to checkout data")
                
                # Create checkout session
                print(f"Creating checkout session with data: {{success_url: '{success_url}', cancel_url: '{cancel_url}', mode: 'subscription', line_items: [{{'price': '{price_id}', 'quantity': 1}}], customer: '{st.session_state.customer_id}'}}")
                
                checkout_session = stripe.checkout.Session.create(
                    success_url=success_url,
                    cancel_url=cancel_url,
                    mode="subscription",
                    customer=st.session_state.customer_id,
                    line_items=[
                        {
                            "price": price_id,
                            "quantity": 1
                        }
                    ]
                )
                
                payment_link = checkout_session.url
                print(f"Checkout session created with ID: {checkout_session.id}")
                print(f"Payment URL: {payment_link}")
                
                st.session_state.payment_link = payment_link
            
            # Clear any previous UI elements with an empty container
            with st.empty():
                pass
                
            # Display payment link with prominent button and clear messaging
            st.markdown(
                f"""
                <div style="text-align: center; padding: 30px; margin: 20px 0; background-color: #f1f5f9; border-radius: 10px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                    <h2 style="color: #1e3a8a; margin-bottom: 20px;">Complete Your Premium Subscription</h2>
                    <p style="color: #4b5563; margin-bottom: 20px; font-size: 16px;">Your checkout session is ready! Click the button below to complete your payment securely through Stripe:</p>
                    <a href="{payment_link}" target="_blank" 
                       style="display: inline-block; padding: 14px 28px; 
                              background-color: #4f46e5; color: white; 
                              text-decoration: none; border-radius: 5px;
                              font-weight: bold; font-size: 16px;
                              transition: all 0.3s ease;
                              box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                        Proceed to Secure Payment
                    </a>
                    <p style="color: #6b7280; margin-top: 20px; font-size: 14px;">
                        Secure payment processed by <img src="https://cdn.worldvectorlogo.com/logos/stripe-2.svg" style="height: 20px; vertical-align: middle;" alt="Stripe">
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Add JavaScript to automatically open the payment link
            js_code = f"""
            <script>
                // Open payment link in a new tab
                window.open("{payment_link}", "_blank");
            </script>
            """
            st.components.v1.html(js_code, height=0)
            
            st.info("A new tab should open automatically to complete your payment. If it doesn't, please click the button above.")
            
            # Add additional information about what happens after payment
            st.markdown(
                """
                <div style="padding: 15px; background-color: #f8fafc; border-radius: 5px; margin-top: 20px; border-left: 4px solid #3b82f6;">
                    <h4 style="color: #1e40af; margin-top: 0;">What happens next?</h4>
                    <p style="color: #4b5563; margin-bottom: 5px;">After completing your payment:</p>
                    <ol style="color: #4b5563;">
                        <li>Your account will be instantly upgraded to Premium</li>
                        <li>You'll receive a confirmation email</li>
                        <li>You'll be redirected back to the app</li>
                        <li>You can immediately start using all premium features</li>
                    </ol>
                    <p style="color: #64748b; font-size: 14px; margin-top: 15px;"><strong>Note:</strong> When you return to this site, your premium status will be automatically applied</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Add a button to manually activate premium if user has already completed payment
            if st.button("I've completed payment - activate premium now"):
                st.session_state.subscription.tier = SubscriptionTier.PREMIUM
                st.session_state.has_premium = True
                st.rerun()
            
        except Exception as e:
            st.error(f"Error creating checkout session: {str(e)}")
            print(f"Error creating checkout session: {str(e)}")
            
    except Exception as e:
        st.error(f"Unable to process upgrade: {str(e)}")
        print(f"Unable to process upgrade: {str(e)}")

def show_success_page(session_id: str):
    """DEPRECATED: Use handle_success_route instead. This function is kept for backward compatibility."""
    # Redirect to the new implementation
    handle_success_route()
    return

def show_cancel_page():
    """Show the cancellation page."""
    # Display custom header with gradient background
    st.markdown("""
    <style>
        .header-container {
            background: linear-gradient(135deg, #EF4444 0%, #B91C1C 100%);
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .header-title {
            color: white;
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        }
        .header-subtitle {
            color: rgba(255, 255, 255, 0.9);
            font-size: 1.3rem;
            font-weight: 400;
            margin-bottom: 1.5rem;
        }
        .header-icons {
            font-size: 3rem;
            margin: 0.5rem 0;
        }
        .cancel-container {
            max-width: 800px;
            margin: 0 auto;
            background-color: white;
            border-radius: 10px;
            padding: 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .benefits-list {
            list-style-type: none;
            padding-left: 0;
        }
        .benefit-item {
            padding: 0.75rem 0;
            border-bottom: 1px solid #e5e7eb;
        }
        .benefit-item:last-child {
            border-bottom: none;
        }
        .feature-title {
            font-weight: bold;
            color: #1e3a8a;
        }
    </style>
    <div class="header-container">
        <div class="header-icons">❌</div>
        <div class="header-title">Payment Cancelled</div>
        <div class="header-subtitle">No charges were made to your account</div>
    </div>
    
    <div class="cancel-container">
        <h3 style="color: #1e3a8a; margin-bottom: 1.5rem;">Why Upgrade to Premium?</h3>
        <ul class="benefits-list">
            <li class="benefit-item"><span class="feature-title">More Plans:</span> Create up to 10 learning plans per day</li>
            <li class="benefit-item"><span class="feature-title">More Resources:</span> Get up to 10 resources per plan</li>
            <li class="benefit-item"><span class="feature-title">Email Notifications:</span> Get your plans delivered to your inbox</li>
            <li class="benefit-item"><span class="feature-title">Priority Support:</span> Get help when you need it</li>
        </ul>
        <p style="color: #6b7280; margin: 1.5rem 0; font-size: 14px; text-align: center;">You can try again whenever you're ready.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Go Back to App", use_container_width=True):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if st.button("Try Again", type="primary", use_container_width=True):
            # Use the existing event loop patched by nest_asyncio
            loop = asyncio.get_event_loop()
            loop.run_until_complete(handle_subscription_upgrade())

async def handle_webhook():
    """Handle incoming webhook events from Stripe."""
    try:
        # Get the webhook secret from environment or session state
        webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
        if not webhook_secret:
            if "webhook_secret" in st.session_state:
                webhook_secret = st.session_state.webhook_secret
            else:
                logging.error("Webhook secret not configured")
                return {"success": False, "message": "Webhook secret not configured"}, 500
        
        # Get headers from the request to extract signature
        try:
            headers = _get_websocket_headers()
            signature = headers.get("Stripe-Signature")
            if not signature:
                logging.error("No Stripe signature found in request")
                return {"success": False, "message": "No Stripe signature found in request"}, 400
        except Exception as e:
            logging.error(f"Error getting Stripe signature: {e}")
            return {"success": False, "message": f"Error getting Stripe signature: {str(e)}"}, 400
        
        # Get the request body and parse as JSON
        try:
            request_body = st.runtime.scriptrunner.get_script_run_ctx().session.request.get_body()
            if not request_body:
                logging.error("Empty request body")
                return {"success": False, "message": "Empty request body"}, 400
            
            payload = json.loads(request_body.decode("utf-8"))
        except Exception as e:
            logging.error(f"Error parsing webhook payload: {e}")
            return {"success": False, "message": f"Error parsing webhook payload: {str(e)}"}, 400
        
        # Verify webhook signature
        if not verify_webhook_signature(payload, signature, webhook_secret):
            logging.error("Invalid webhook signature")
            return {"success": False, "message": "Invalid webhook signature"}, 400
        
        # Process the event based on its type
        event_type = payload.get("type")
        logging.info(f"Processing webhook event: {event_type}")
        
        # Extract data from the event
        if "data" in payload and "object" in payload["data"]:
            event_data = payload["data"]["object"]
            
            # Handle checkout.session.completed event
            if event_type == "checkout.session.completed":
                # Extract customer details
                customer_email = event_data.get("customer_details", {}).get("email")
                customer_id = event_data.get("customer")
                
                if not customer_email:
                    logging.error("No customer email found in checkout session")
                    return {"success": False, "message": "Customer email not found"}, 400
                
                # Update session state with premium status
                st.session_state.subscription = SubscriptionConfig(
                    daily_plans=10,
                    resources_per_plan=10,
                    email_notifications=True,
                    price=9.99,
                    tier=SubscriptionTier.PREMIUM
                )
                st.session_state.has_premium = True
                st.session_state.customer_id = customer_id
                st.session_state.user_email = customer_email
                
                # Store subscription data in a file for persistence
                subscription_data = {
                    "email": customer_email,
                    "customer_id": customer_id,
                    "subscription_tier": "PREMIUM",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "status": "active"
                }
                
                # Create subscriptions directory if it doesn't exist
                subscriptions_dir = os.path.join(os.path.dirname(__file__), "subscriptions")
                os.makedirs(subscriptions_dir, exist_ok=True)
                
                # Save subscription data to a file named after the customer email
                file_name = os.path.join(subscriptions_dir, f"{customer_email.replace('@', '_at_')}.json")
                with open(file_name, "w") as f:
                    json.dump(subscription_data, f, indent=2)
                
                logging.info(f"Premium status saved for {customer_email}")
                
                # Try to send email notification if email agent is available
                try:
                    email_agent = st.session_state.get("email_agent")
                    if email_agent:
                        email_subject = "Welcome to CoachAI Premium!"
                        email_body = f"""
                        Hi there!
                        
                        Thank you for subscribing to CoachAI Premium. Your subscription has been activated successfully.
                        
                        You now have access to:
                        - Unlimited learning plans per day
                        - More resources per plan
                        - Email notifications
                        - And much more!
                        
                        Visit http://localhost:8505/success to get started with your premium features.
                        
                        Best regards,
                        The CoachAI Team
                        """
                        
                        # Use the existing event loop patched by nest_asyncio
                        loop = asyncio.get_event_loop()
                        loop.run_until_complete(email_agent.send_email(customer_email, email_subject, email_body))
                        logging.info(f"Subscription confirmation email sent to {customer_email}")
                except Exception as e:
                    logging.error(f"Error sending subscription confirmation email: {e}")
                
                return {"success": True, "message": "Subscription processed successfully"}, 200
            
            # Handle invoice.payment_failed event
            elif event_type == "invoice.payment_failed":
                customer_email = event_data.get("customer_email")
                customer_id = event_data.get("customer")
                
                if not customer_email:
                    # Try to get customer email from customer ID
                    try:
                        from agents.stripe_agent import StripeAgent
                        stripe_agent = StripeAgent()
                        customer = stripe_agent.stripe.Customer.retrieve(customer_id)
                        customer_email = customer.get("email")
                    except Exception as e:
                        logging.error(f"Error retrieving customer data: {e}")
                
                if customer_email:
                    # Update subscription status in file
                    subscriptions_dir = os.path.join(os.path.dirname(__file__), "subscriptions")
                    file_name = os.path.join(subscriptions_dir, f"{customer_email.replace('@', '_at_')}.json")
                    
                    if os.path.exists(file_name):
                        with open(file_name, "r") as f:
                            subscription_data = json.load(f)
                        
                        subscription_data["status"] = "payment_failed"
                        subscription_data["updated_at"] = datetime.now(timezone.utc).isoformat()
                        
                        with open(file_name, "w") as f:
                            json.dump(subscription_data, f)
                    
                    # Try to send email notification
                    try:
                        from agents.email_agent import EmailAgent
                        email_agent = EmailAgent()
                        
                        email_subject = "Payment Failed for CoachAI Premium"
                        email_body = f"""
                        Hi there,
                        
                        We were unable to process your payment for CoachAI Premium.
                        
                        Please update your payment information to continue enjoying premium features:
                        http://localhost:8505/upgrade
                        
                        If you need assistance, please reply to this email.
                        
                        Best regards,
                        The CoachAI Team
                        """
                        
                        # Use the existing event loop patched by nest_asyncio
                        loop = asyncio.get_event_loop()
                        loop.run_until_complete(email_agent.send_email(customer_email, email_subject, email_body))
                        logging.info(f"Payment failure email sent to {customer_email}")
                    except Exception as e:
                        logging.error(f"Error sending payment failure email: {e}")
                
                return {"success": True, "message": "Payment failure processed"}, 200
        
        # Return success for other event types
        return {"success": True, "message": f"Event {event_type} received but not processed"}, 200
    
    except Exception as e:
        logging.error(f"Error processing webhook: {e}")
        return {"success": False, "message": f"Error processing webhook: {str(e)}"}, 500

def subscription_sidebar():
    """Display subscription information in sidebar."""
    st.sidebar.title("📊 Subscription Status")
    
    stripe_agent = st.session_state.stripe_agent
    current_tier = st.session_state.subscription.tier
    
    # Display current tier and features
    st.sidebar.markdown(f"**Current Tier:** {current_tier.value.title()}")
    st.sidebar.markdown(stripe_agent.get_tier_description(current_tier))
    
    # Show upgrade button for freemium users
    if current_tier == SubscriptionTier.FREEMIUM:
        st.sidebar.markdown("---")
        if st.sidebar.button("🌟 Upgrade to Premium"):
            # Set upgrading state to true
            st.session_state.upgrading = True
            st.rerun()
    
    # Show usage statistics
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Today's Usage")
    max_plans = stripe_agent.get_tier_features(current_tier)["daily_plans"]
    st.sidebar.markdown(f"Plans created today: {st.session_state.plans_created_today}/{max_plans}")
    
    # Add OpenAI API key configuration
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ API Settings")
    
    # Get current API key from settings
    from src.config import settings
    current_key = settings.openai_api_key
    
    # Show API key status prominently
    if not current_key or current_key.strip() == "":
        st.sidebar.warning("⚠️ OpenAI API Key not set")
        st.sidebar.info("""
        **An OpenAI API key is required to generate learning plans.**
        
        Without a valid API key, plan generation will fail.
        """)
    else:
        masked_key = f"{current_key[:5]}...{current_key[-4:]}"
        st.sidebar.success(f"✅ OpenAI API Key: {masked_key}")
    
    # Provide information about getting an API key
    with st.sidebar.expander("How to get an OpenAI API Key"):
        st.markdown("""
        1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
        2. Sign in or create an account
        3. Click "Create new secret key"
        4. Copy your new API key
        5. Paste it below and click "Save API Key"
        """)
    
    # Input field for API key
    new_api_key = st.sidebar.text_input("Enter OpenAI API Key", type="password", key="new_api_key")
    
    if st.sidebar.button("Save API Key", type="primary"):
        if new_api_key:
            try:
                # Update environment variable
                os.environ["OPENAI_API_KEY"] = new_api_key
                # Update settings
                settings.openai_api_key = new_api_key
                # Update PlannerAgent's API key
                if "planner_agent" in st.session_state:
                    st.session_state.planner_agent.update_api_key(new_api_key)
                st.sidebar.success("✅ API key updated successfully!")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Failed to update API key: {str(e)}")
        else:
            st.sidebar.warning("Please enter a valid API key")

async def generate_plan():
    """Generate a personalized learning plan based on user inputs."""
    try:
        # Get all responses from session state
        responses = st.session_state.responses
        
        # Create the learning goal object
        goal = LearningGoal(
            subject=responses["subject"],
            level=responses["current_level"],
            current_knowledge=responses["current_knowledge"],
            learning_purpose=responses["learning_purpose"],
            time_commitment=responses["time_commitment"],
            preferred_resources=responses["preferred_resources"]
        )

        with st.spinner("Generating your personalized learning plan..."):
            # Generate the plan
            plan = await st.session_state.planner_agent.create_plan(goal)
            
            if not plan:
                st.error("Failed to generate plan. Please try again.")
                return
                
            # Store the plan in session state
            st.session_state.current_plan = plan
            
            # Update plan count
            st.session_state.plans_created_today = st.session_state.get("plans_created_today", 0) + 1
            st.session_state.last_plan_date = datetime.now().date()
            
            # Display the plan
            display_learning_plan(plan)
                
    except Exception as e:
        error_msg = str(e)
        if "API key" in error_msg.lower() or "openai" in error_msg.lower():
            st.error("""
            ### OpenAI API Key Required
            
            To generate learning plans, you need to provide your OpenAI API key. Please follow these steps:
            
            1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys) and sign in/create an account
            2. Create a new API key
            3. Copy your API key
            4. Look for the "API Settings" section in the sidebar on the left side of this app
            5. Paste your API key in the "Enter OpenAI API Key" field
            6. Click "Save API Key"
            7. Try generating your plan again
            
            Your API key is stored securely and is only used to generate your learning plans.
            """)
        else:
            st.error("We encountered an issue while creating your plan. Please try again later.")
        
        # Log the error using the configured logger
        try:
            logger.error(f"Plan generation error: {str(e)}", exc_info=True)
        except Exception:
            # Fallback if logger isn't properly configured
            print(f"Error in plan generation: {str(e)}")

def handle_success_route():
    """Handle the success route after payment completion."""
    try:
        # Set the user's subscription to premium
        st.session_state["subscription_tier"] = SubscriptionTier.PREMIUM
        st.session_state["has_premium"] = True
        
        # If we have the user's email, save their premium status
        if "user_email" in st.session_state:
            email = st.session_state["user_email"]
            subscription_data = {
                "email": email,
                "subscription_tier": "PREMIUM",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "active"
            }
            
            # Create subscriptions directory if it doesn't exist
            subscriptions_dir = os.path.join(os.path.dirname(__file__), "subscriptions")
            os.makedirs(subscriptions_dir, exist_ok=True)
            
            # Save subscription data
            file_name = os.path.join(subscriptions_dir, f"{email.replace('@', '_at_')}.json")
            with open(file_name, "w") as f:
                json.dump(subscription_data, f, indent=2)
            
            logging.info(f"Premium status saved for {email}")
        
        # Show confetti effect for celebration
        st.balloons()
        
        # Create styled success page
        st.markdown("""
        <style>
        .success-header {
            text-align: center;
            color: #4CAF50;
            font-size: 2.5rem;
            margin-bottom: 2rem;
        }
        .success-subheader {
            text-align: center;
            font-size: 1.5rem;
            margin-bottom: 3rem;
            color: #555;
        }
        .benefit-card {
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            text-align: center;
            height: 100%;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .benefit-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        }
        .benefit-icon {
            font-size: 2rem;
            margin-bottom: 15px;
            color: #4CAF50;
        }
        .benefit-title {
            font-weight: bold;
            margin-bottom: 10px;
            font-size: 1.2rem;
        }
        .benefit-description {
            color: #666;
        }
        .start-button {
            text-align: center;
            margin-top: 2rem;
        }
        </style>
        
        <div class="success-header">🎉 Welcome to Premium!</div>
        <div class="success-subheader">Your subscription has been successfully activated</div>
        """, unsafe_allow_html=True)
        
        # Display premium benefits in a grid
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="benefit-card">
                <div class="benefit-icon">🚀</div>
                <div class="benefit-title">Unlimited Learning Plans</div>
                <div class="benefit-description">Create as many personalized learning plans as you need for different topics and goals.</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="benefit-card" style="margin-top: 20px;">
                <div class="benefit-icon">📧</div>
                <div class="benefit-title">Email Notifications</div>
                <div class="benefit-description">Receive email updates and reminders to stay on track with your learning goals.</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="benefit-card">
                <div class="benefit-icon">⚙️</div>
                <div class="benefit-title">Advanced Customization</div>
                <div class="benefit-description">Access to advanced customization options for more tailored learning experiences.</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="benefit-card" style="margin-top: 20px;">
                <div class="benefit-icon">🔍</div>
                <div class="benefit-title">Priority Support</div>
                <div class="benefit-description">Get faster responses and dedicated assistance whenever you need help.</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Add button to start using the premium features
        st.markdown("""
        <div class="start-button">
            <a href="/" target="_self">
                <button style="background-color: #4CAF50; color: white; border: none; padding: 12px 24px; 
                       text-align: center; text-decoration: none; display: inline-block; font-size: 16px; 
                       margin: 4px 2px; cursor: pointer; border-radius: 4px; font-weight: bold;">
                    Start Creating Plans Now
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error displaying success page: {e}")
        st.button("Return Home", on_click=lambda: st.switch_page("app.py"))

def check_premium_status(email):
    """Check if a user has premium status based on stored subscription data."""
    if not email:
        return False
    
    # Check for subscription file
    subscriptions_dir = os.path.join(os.path.dirname(__file__), "subscriptions")
    file_name = os.path.join(subscriptions_dir, f"{email.replace('@', '_at_')}.json")
    
    if os.path.exists(file_name):
        try:
            with open(file_name, "r") as f:
                subscription_data = json.load(f)
            
            # Check if subscription is active
            if subscription_data.get("status") == "active" and subscription_data.get("subscription_tier") == "PREMIUM":
                return True
        except Exception as e:
            logging.error(f"Error checking premium status: {e}")
    
    return False

def count_user_plans(user_email):
    """Count how many plans a user has created."""
    try:
        plans_directory = "user_plans"
        if not os.path.exists(plans_directory):
            return 0
        
        # Count files that start with the user's email
        count = 0
        for filename in os.listdir(plans_directory):
            if filename.startswith(f"{user_email}_") and filename.endswith(".json"):
                count += 1
        
        return count
    except Exception as e:
        logging.error(f"Error counting user plans: {e}")
        return 0

def save_plan_to_file(learning_plan, user_email):
    """Save the learning plan to a JSON file."""
    try:
        # Create directory if it doesn't exist
        plans_directory = "user_plans"
        if not os.path.exists(plans_directory):
            os.makedirs(plans_directory)
        
        # Generate a unique filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{user_email}_{timestamp}.json"
        filepath = os.path.join(plans_directory, filename)
        
        # Convert learning plan to dictionary
        plan_dict = {
            "subject": learning_plan.subject,
            "current_knowledge": learning_plan.current_knowledge,
            "learning_purpose": learning_plan.learning_purpose,
            "time_commitment": learning_plan.time_commitment,
            "preferred_resources": learning_plan.preferred_resources,
            "plan_content": learning_plan.plan_content,
            "resources": learning_plan.resources,
            "created_at": timestamp
        }
        
        # Save to file
        with open(filepath, "w") as f:
            json.dump(plan_dict, f, indent=2)
            
        return filepath
    except Exception as e:
        logging.error(f"Error saving plan to file: {e}")
        return None

def main():
    """Main function to display the app UI."""
    # Check for the active tab in session state
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "Learning Plan"
    
    # Navigation sidebar setup
    with st.sidebar:
        st.image("https://em-content.zobj.net/thumbs/120/apple/325/brain_1f9e0.png", width=50)
        st.title("CoachAI")
        
        # Navigation options
        st.subheader("Navigation")
        nav_options = ["Dashboard", "Learning Plan", "Settings"]
        
        for nav_option in nav_options:
            # Create a custom styled button for each nav option
            is_active = st.session_state.active_tab == nav_option
            button_style = "active" if is_active else ""
            
            if st.sidebar.button(
                f"{'📊' if nav_option == 'Dashboard' else '📝' if nav_option == 'Learning Plan' else '⚙️'} {nav_option}",
                key=f"nav_{nav_option}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state.active_tab = nav_option
                st.rerun()
                
        # User stats section
        st.sidebar.markdown("---")
        st.sidebar.subheader("User Statistics")
        
        # Show current tier
        if "subscription" not in st.session_state:
            st.session_state.subscription = SubscriptionConfig(
                daily_plans=1,
                resources_per_plan=3,
                email_notifications=False,
                price=0.0,
                tier=SubscriptionTier.FREEMIUM
            )
            
        current_tier = st.session_state.subscription.tier.value.title()
        st.sidebar.markdown(f"**Current Plan:** {current_tier}")
        
        # Show usage
        plans_created = st.session_state.get("plans_created_today", 0)
        max_plans = 1 if current_tier == "Freemium" else 10
        st.sidebar.markdown(f"**Plans created today:** {plans_created}/{max_plans}")
        
        # Learning time tracking
        learning_time = st.session_state.get("total_learning_time", 0)
        st.sidebar.markdown(f"**Total learning time:** {learning_time} hours")
    
    # Display content based on active tab
    if st.session_state.active_tab == "Dashboard":
        display_dashboard()
    elif st.session_state.active_tab == "Learning Plan":
        display_learning_plan_tab()
    elif st.session_state.active_tab == "Settings":
        display_settings()

def display_dashboard():
    """Display the dashboard with learning statistics."""
    st.title("📊 Your Learning Dashboard")
    
    # Initialize user data if not present
    if "user_data" not in st.session_state:
        st.session_state.user_data = {
            "total_learning_time": 0,
            "completed_tasks": 0,
            "plans_created": 0,
            "active_plans": 0,
            "topics": {},
            "weekly_activity": [0, 0, 0, 0, 2, 3, 1],  # Sample data
            "time_tracking": {}  # For estimated vs actual time tracking
        }
    
    # Create dashboard layout
    col1, col2 = st.columns(2)
    
    with col1:
        # Learning time card
        with st.container(border=True):
            st.subheader("Learning Time")
            total_hours = st.session_state.user_data["total_learning_time"]
            st.markdown(f"## {total_hours} hours")
            st.markdown("Total time spent learning")
    
    with col2:
        # Tasks completed card
        with st.container(border=True):
            st.subheader("Tasks Completed")
            completed = st.session_state.user_data["completed_tasks"]
            st.markdown(f"## {completed}")
            st.markdown("Learning tasks completed")
    
    # Check if we have a current plan
    if st.session_state.has_plan and st.session_state.current_plan:
        plan = st.session_state.current_plan
        # Get subject from session state, not from plan
        subject = st.session_state.get("subject", "Current Topic")
        
        # Ensure the subject exists in time tracking
        if subject not in st.session_state.user_data["time_tracking"]:
            # Extract estimated time from plan duration
            estimated_time = 0
            duration_text = plan.estimated_duration
            if "hours" in duration_text.lower():
                # Try to extract the number
                try:
                    # Find numbers in the string
                    import re
                    numbers = re.findall(r'\d+', duration_text)
                    if numbers:
                        estimated_time = int(numbers[0])
                    else:
                        # Default based on time commitment if parsing fails
                        time_commitment = st.session_state.get("time_commitment", "3-5 hours")
                        if "1-2" in time_commitment:
                            estimated_time = 2 * 4  # 2 hours/week * 4 weeks
                        elif "3-5" in time_commitment:
                            estimated_time = 4 * 4  # 4 hours/week * 4 weeks
                        elif "6-10" in time_commitment:
                            estimated_time = 8 * 4  # 8 hours/week * 4 weeks
                        elif "11-15" in time_commitment:
                            estimated_time = 12 * 4  # 12 hours/week * 4 weeks
                        else:
                            estimated_time = 16 * 4  # 16 hours/week * 4 weeks
                except:
                    # Fallback to default if parsing fails
                    estimated_time = 16
            
            # Initialize tracking data for this subject
            st.session_state.user_data["time_tracking"][subject] = {
                "estimated_time": estimated_time,
                "actual_time": 0,
                "start_date": datetime.now().strftime("%Y-%m-%d"),
                "last_updated": datetime.now().strftime("%Y-%m-%d")
            }
    
    # Time Tracking Section
    st.subheader("Estimated vs. Actual Time")
    
    if not st.session_state.user_data["time_tracking"]:
        st.info("No time tracking data available yet. Generate a learning plan to start tracking your time.")
    else:
        # Create a dataframe for the time tracking data
        import pandas as pd
        time_data = []
        for subject, tracking in st.session_state.user_data["time_tracking"].items():
            time_data.append({
                "Subject": subject,
                "Estimated Time (hours)": tracking["estimated_time"],
                "Actual Time (hours)": tracking["actual_time"],
                "Progress": f"{min(100, int((tracking['actual_time'] / max(1, tracking['estimated_time'])) * 100))}%"
            })
        
        time_df = pd.DataFrame(time_data)
        
        # Display the time tracking table
        st.table(time_df)
        
        # Create a bar chart comparing estimated vs actual time
        if len(time_data) > 0:
            st.subheader("Time Comparison Chart")
            
            # Extract data for plotting
            subjects = [item["Subject"] for item in time_data]
            estimated_times = [item["Estimated Time (hours)"] for item in time_data]
            actual_times = [item["Actual Time (hours)"] for item in time_data]
            
            # Create chart data for Vega Lite
            chart_data = []
            for i, subject in enumerate(subjects):
                chart_data.append({
                    "Subject": subject,
                    "Hours": estimated_times[i],
                    "Type": "Estimated"
                })
                chart_data.append({
                    "Subject": subject,
                    "Hours": actual_times[i],
                    "Type": "Actual"
                })
            
            # Create the chart specification
            chart_spec = {
                "mark": "bar",
                "encoding": {
                    "x": {"field": "Subject", "type": "nominal"},
                    "y": {"field": "Hours", "type": "quantitative"},
                    "color": {
                        "field": "Type", 
                        "type": "nominal",
                        "scale": {"range": ["#3b82f6", "#34d399"]}
                    },
                    "xOffset": {"field": "Type", "type": "nominal"},
                    "tooltip": [
                        {"field": "Subject", "type": "nominal"},
                        {"field": "Type", "type": "nominal"},
                        {"field": "Hours", "type": "quantitative"}
                    ]
                }
            }
            
            # Add the chart
            st.vega_lite_chart(pd.DataFrame(chart_data), chart_spec, use_container_width=True)
    
    # Weekly activity chart
    st.subheader("Weekly Activity")
    
    # Create weekly activity chart data
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    activity = st.session_state.user_data["weekly_activity"]
    
    # Create the chart
    chart_data = {
        "day": days,
        "hours": activity
    }
    
    chart = {
        "mark": "bar",
        "encoding": {
            "x": {"field": "day", "type": "nominal", "title": "Day"},
            "y": {"field": "hours", "type": "quantitative", "title": "Hours"},
            "color": {"value": "#3b82f6"}
        }
    }
    
    st.vega_lite_chart(chart_data, chart, use_container_width=True)
    
    # Learning topics breakdown
    st.subheader("Your Learning Topics")
    
    if not st.session_state.user_data["topics"]:
        st.info("You haven't created any learning plans yet. Go to the Learning Plan tab to get started!")
    else:
        # Create a pie chart for topics
        topics = list(st.session_state.user_data["topics"].keys())
        hours = list(st.session_state.user_data["topics"].values())
        
        # Create chart data
        topic_data = {
            "topic": topics,
            "hours": hours
        }
        
        topic_chart = {
            "mark": "arc",
            "encoding": {
                "theta": {"field": "hours", "type": "quantitative"},
                "color": {"field": "topic", "type": "nominal"}
            }
        }
        
        st.vega_lite_chart(topic_data, topic_chart, use_container_width=True)
    
    # Progress tracking
    st.subheader("Track Your Learning Progress")
    
    if st.session_state.has_plan and st.session_state.current_plan:
        # Track progress for current plan
        # Get subject from session state, not from plan
        subject = st.session_state.get("subject", "Current Topic")
        
        st.markdown(f"### Current Plan Progress - {subject}")
        plan_progress = st.session_state.get("plan_progress", 0)
        st.progress(plan_progress / 100)
        st.markdown(f"**{plan_progress}%** completed")
        
        # Get current tracking data
        tracking_data = st.session_state.user_data["time_tracking"].get(subject, {
            "estimated_time": 16,
            "actual_time": 0
        })
        
        # Show estimated vs actual time for this plan
        # Use separate containers instead of nested columns
        st.markdown("### Time Tracking")
        metric_col1, metric_col2 = st.columns(2)
        with metric_col1:
            st.metric("Estimated Time", f"{tracking_data['estimated_time']} hours")
        with metric_col2:
            st.metric("Actual Time", f"{tracking_data['actual_time']} hours")
        
        # Input for updating actual time spent
        st.markdown("### Update Your Learning Time")
        
        hours_spent = st.number_input(
            "Hours spent today:",
            min_value=0.0,
            max_value=24.0,
            step=0.5,
            key="hours_input"
        )
        
        if st.button("Log Time", type="primary"):
            if hours_spent > 0:
                # Update the actual time
                if subject not in st.session_state.user_data["time_tracking"]:
                    st.session_state.user_data["time_tracking"][subject] = {
                        "estimated_time": 16,
                        "actual_time": 0,
                        "start_date": datetime.now().strftime("%Y-%m-%d"),
                        "last_updated": datetime.now().strftime("%Y-%m-%d")
                    }
                
                # Update the actual time
                st.session_state.user_data["time_tracking"][subject]["actual_time"] += hours_spent
                st.session_state.user_data["time_tracking"][subject]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
                
                # Update topic hours and total learning time
                if subject not in st.session_state.user_data["topics"]:
                    st.session_state.user_data["topics"][subject] = 0
                
                st.session_state.user_data["topics"][subject] += hours_spent
                st.session_state.user_data["total_learning_time"] += hours_spent
                
                # Update weekly activity
                today_index = datetime.now().weekday()  # 0 for Monday, 6 for Sunday
                st.session_state.user_data["weekly_activity"][today_index] += hours_spent
                
                # Show success message
                st.success(f"Added {hours_spent} hours to your learning time for {subject}!")
                
                # Update completed tasks based on progress (1 task per 20% progress)
                new_tasks = int(hours_spent / 2)  # Roughly 1 task per 2 hours
                if new_tasks > 0:
                    st.session_state.user_data["completed_tasks"] += new_tasks
                
                # Rerun to update the dashboard
                st.rerun()
            else:
                st.warning("Please enter a value greater than 0.")
    else:
        st.info("No active learning plan. Create one in the Learning Plan tab!")

def display_learning_plan_tab():
    """Display the learning plan creation and viewing interface."""
    st.title("🧠 Learning Plan")
    
    # Add a button to view the latest plan if one exists
    if st.session_state.get("has_plan", False) and st.session_state.get("current_plan") is not None:
        st.success("You have an active learning plan!")
        if st.button("📋 View Your Current Plan", type="primary"):
            # Display the existing plan and skip the form
            display_learning_plan(st.session_state.current_plan)
            return
        
        st.button("📝 Create New Plan", on_click=lambda: reset_plan_form())
    
    # Multi-step form for plan creation
    display_plan_creation_form()

def reset_plan_form():
    """Reset the plan creation form."""
    st.session_state.step = 1
    st.session_state.has_plan = False
    st.session_state.current_plan = None
    st.rerun()

def display_plan_creation_form():
    """Display the multi-step form for creating a learning plan."""
    # Display a multi-step form for collecting user input
    if st.session_state.step == 1:
        st.header("Step 1: What would you like to learn?")
        
        # Pre-fill with existing value if available
        subject_value = st.session_state.get("subject", "")
        subject = st.text_input("Subject or Topic", value=subject_value, 
                                placeholder="E.g., Python Programming, Machine Learning, Piano...")
        
        if st.button("Next", key="next_1", type="primary"):
            if subject.strip():
                # Store the value in session state
                st.session_state["subject"] = subject
                st.session_state.responses["subject"] = subject
                next_step()
                st.rerun()
            else:
                st.warning("Please enter a topic to continue.")
    
    elif st.session_state.step == 2:
        st.header("Step 2: Your Current Knowledge Level")
        
        st.write(f"Topic: **{st.session_state.subject}**")
        
        # Pre-fill with existing values if available
        level_value = st.session_state.get("level", "Beginner (No prior knowledge)")
        # Ensure level_value is one of the valid options
        valid_options = ["Beginner (No prior knowledge)", "Intermediate (Some basics understood)", "Advanced (Looking to deepen knowledge)"]
        if level_value not in valid_options:
            level_value = valid_options[0]  # Default to Beginner
            
        current_knowledge_value = st.session_state.get("current_knowledge", "")
        
        level = st.radio(
            "What's your current knowledge level?",
            valid_options,
            index=valid_options.index(level_value)
        )
        
        current_knowledge = st.text_area(
            "Briefly describe what you already know about this topic (optional)",
            value=current_knowledge_value,
            placeholder="E.g., I understand basic concepts but struggle with advanced topics..."
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Back", key="back_2"):
                prev_step()
                st.rerun()
        with col2:
            if st.button("Next", key="next_2", type="primary"):
                # Store values in session state
                st.session_state["level"] = level
                st.session_state["current_knowledge"] = current_knowledge
                st.session_state.responses["current_level"] = level
                st.session_state.responses["current_knowledge"] = current_knowledge
                next_step()
                st.rerun()
    
    elif st.session_state.step == 3:
        st.header("Step 3: Learning Purpose")
        
        st.write(f"Topic: **{st.session_state.subject}**")
        st.write(f"Level: **{st.session_state.level}**")
        
        # Pre-fill with existing value if available
        learning_purpose_value = st.session_state.get("learning_purpose", "")
        
        learning_purpose = st.text_area(
            "What's your goal or purpose for learning this?",
            value=learning_purpose_value,
            placeholder="E.g., For career advancement, personal project, academic requirement..."
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Back", key="back_3"):
                prev_step()
                st.rerun()
        with col2:
            if st.button("Next", key="next_3", type="primary"):
                if learning_purpose.strip():
                    # Store value in session state
                    st.session_state["learning_purpose"] = learning_purpose
                    st.session_state.responses["learning_purpose"] = learning_purpose
                    next_step()
                    st.rerun()
                else:
                    st.warning("Please describe your learning purpose to continue.")
    
    elif st.session_state.step == 4:
        st.header("Step 4: Time Commitment")
        
        st.write(f"Topic: **{st.session_state.subject}**")
        st.write(f"Level: **{st.session_state.level}**")
        
        # Pre-fill with existing value if available
        time_options = ["1-2 hours", "3-5 hours", "6-10 hours", "11-15 hours", "16+ hours"]
        time_commitment_value = st.session_state.get("time_commitment", "3-5 hours")
        
        # Ensure time_commitment_value is one of the valid options
        if time_commitment_value not in time_options:
            time_commitment_value = time_options[1]  # Default to "3-5 hours"
        
        time_commitment = st.select_slider(
            "How much time can you commit per week?",
            options=time_options,
            value=time_commitment_value
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Back", key="back_4"):
                prev_step()
                st.rerun()
        with col2:
            if st.button("Next", key="next_4", type="primary"):
                # Store value in session state
                st.session_state["time_commitment"] = time_commitment
                st.session_state.responses["time_commitment"] = time_commitment
                next_step()
                st.rerun()
    
    elif st.session_state.step == 5:
        st.header("Step 5: Preferred Resources")
        
        st.write(f"Topic: **{st.session_state.subject}**")
        st.write(f"Level: **{st.session_state.level}**")
        st.write(f"Time Commitment: **{st.session_state.time_commitment}**")
        
        # Define the available options
        resource_options = ["Online courses", "Books", "Video tutorials", "Interactive exercises", 
                          "Documentation", "Academic papers", "Community forums", "Podcasts"]
        
        # Get the default selection
        default_resources = []
        if "preferred_resources" in st.session_state:
            if isinstance(st.session_state.preferred_resources, str) and st.session_state.preferred_resources.strip():
                # Convert string back to list if needed
                default_resources = [r.strip() for r in st.session_state.preferred_resources.split(",")]
            elif isinstance(st.session_state.preferred_resources, list):
                default_resources = st.session_state.preferred_resources
        
        # Ensure all default values exist in options
        default_resources = [r for r in default_resources if r in resource_options]
        
        preferred_resources = st.multiselect(
            "What types of learning resources do you prefer?",
            resource_options,
            default=default_resources
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Back", key="back_5"):
                prev_step()
                st.rerun()
        with col2:
            # Get OpenAI API key status before showing the button
            api_key = os.environ.get("OPENAI_API_KEY", "")
            api_key_valid = api_key and api_key.strip() != ""
            
            # Disable the button if no API key is present
            if not api_key_valid:
                st.warning("""
                ⚠️ **OpenAI API Key Required**
                
                You need to add your OpenAI API key before generating a plan. Please check the Settings tab.
                """)
                
                # Generate Plan button (disabled)
                st.button("Generate Plan", key="next_5_disabled", type="primary", disabled=True, 
                         help="Add your OpenAI API key in the Settings tab to enable this button")
                
                # Add a direct link to the settings
                if st.button("Go to Settings", key="goto_settings"):
                    st.session_state.active_tab = "Settings"
                    st.rerun()
            else:
                # API key is valid, show normal button
                if st.button("Generate Plan", key="next_5", type="primary"):
                    if preferred_resources:
                        # Store values in session state
                        st.session_state["preferred_resources"] = preferred_resources
                        st.session_state["preferred_resources_str"] = ", ".join(preferred_resources)
                        st.session_state.responses["preferred_resources"] = preferred_resources
                        
                        # Use the existing event loop patched by nest_asyncio
                        loop = asyncio.get_event_loop()
                        loop.run_until_complete(generate_plan())
                    else:
                        st.warning("Please select at least one resource type to continue.")

def display_settings():
    """Display settings page with API configuration and subscription options."""
    st.title("⚙️ Settings")
    
    # Create tabs for different settings categories
    tab1, tab2 = st.tabs(["API Settings", "Subscription"])
    
    with tab1:
        st.header("OpenAI API Settings")
        st.markdown("""
        Your learning plans are generated using OpenAI's powerful AI models. To use this feature, you need to provide your own OpenAI API key.
        """)
        
        # Get current API key from settings
        from src.config import settings
        current_key = settings.openai_api_key
        
        # Show API key status prominently
        if not current_key or current_key.strip() == "":
            st.warning("⚠️ OpenAI API Key not set")
            st.info("""
            **An OpenAI API key is required to generate learning plans.**
            
            Without a valid API key, plan generation will fail.
            """)
        else:
            masked_key = f"{current_key[:5]}...{current_key[-4:]}"
            st.success(f"✅ OpenAI API Key: {masked_key}")
        
        # Provide information about getting an API key
        with st.expander("How to get an OpenAI API Key"):
            st.markdown("""
            1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
            2. Sign in or create an account
            3. Click "Create new secret key"
            4. Copy your new API key
            5. Paste it below and click "Save API Key"
            """)
        
        # Input field for API key
        new_api_key = st.text_input("Enter OpenAI API Key", type="password", key="new_api_key")
        
        if st.button("Save API Key", type="primary"):
            if new_api_key:
                try:
                    # Update environment variable
                    os.environ["OPENAI_API_KEY"] = new_api_key
                    # Update settings
                    settings.openai_api_key = new_api_key
                    # Update PlannerAgent's API key
                    if "planner_agent" in st.session_state:
                        st.session_state.planner_agent.update_api_key(new_api_key)
                    st.success("✅ API key updated successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to update API key: {str(e)}")
            else:
                st.warning("Please enter a valid API key")
    
    with tab2:
        st.header("Subscription Management")
        
        # Initialize subscription if it doesn't exist
        if "subscription" not in st.session_state:
            st.session_state.subscription = SubscriptionConfig(
                daily_plans=1,
                resources_per_plan=3,
                email_notifications=False,
                price=0.0,
                tier=SubscriptionTier.FREEMIUM
            )
            
        # Get current subscription tier
        stripe_agent = st.session_state.stripe_agent
        current_tier = st.session_state.subscription.tier
        
        # Create comparison table
        st.markdown("### Plans Comparison")
        
        comparison_data = {
            "Feature": ["Learning Plans per Day", "Resources per Plan", "Email Notifications", "Progress Tracking", "Price"],
            "Freemium": ["1", "3", "❌", "✅", "$0"],
            "Premium": ["10", "10", "✅", "✅", "$9.99/month"]
        }
        
        # Convert to DataFrame for display
        import pandas as pd
        df_comparison = pd.DataFrame(comparison_data)
        st.table(df_comparison.set_index("Feature"))
        
        # Display current tier and features
        st.markdown(f"**Current Plan:** {current_tier.value.title()}")
        
        # Add premium badge for premium users
        if current_tier == SubscriptionTier.PREMIUM:
            st.markdown("""
            <div style="background-color:#422006; color:#f59e0b; padding:10px; border-radius:5px; display:inline-block; margin-bottom:20px;">
                <strong>Premium User</strong> ✨
            </div>
            """, unsafe_allow_html=True)
            
            # Show subscription management options
            st.markdown("### Manage Your Premium Subscription")
            st.info("Your subscription renews automatically. If you wish to cancel, please contact support.")
        else:
            # Show upgrade button for freemium users
            st.markdown("### Upgrade to Premium")
            st.markdown("""
            Get more out of CoachAI with our Premium plan:
            - Create up to 10 learning plans per day
            - Access more resources per plan
            - Receive email notifications
            - Priority support
            """)
            
            if st.button("🌟 Upgrade to Premium", type="primary"):
                # Set upgrading state to true
                st.session_state.upgrading = True
                st.rerun()

# Add imports for user data storage (placeholder for Supabase)
try:
    import json
    import os
    from datetime import datetime
    
    # Placeholder for Supabase integration
    class UserStorage:
        """Placeholder class for user data storage."""
        
        def __init__(self):
            """Initialize the storage with local file-based fallback."""
            self.storage_dir = os.path.join(os.path.dirname(__file__), "user_data")
            os.makedirs(self.storage_dir, exist_ok=True)
        
        def save_user_data(self, user_id, data):
            """Save user data to storage (currently file-based)."""
            try:
                file_path = os.path.join(self.storage_dir, f"{user_id}.json")
                with open(file_path, 'w') as f:
                    json.dump(data, f)
                return True
            except Exception as e:
                print(f"Error saving user data: {e}")
                return False
        
        def load_user_data(self, user_id):
            """Load user data from storage (currently file-based)."""
            try:
                file_path = os.path.join(self.storage_dir, f"{user_id}.json")
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        return json.load(f)
                return None
            except Exception as e:
                print(f"Error loading user data: {e}")
                return None
    
    # Initialize user storage
    if 'user_storage' not in st.session_state:
        st.session_state.user_storage = UserStorage()
except ImportError:
    print("Could not import required modules for user storage")

def format_learning_plan_as_timetable(content, time_commitment):
    """
    Format the learning plan content into a structured timetable.
    
    Args:
        content: The raw learning plan content
        time_commitment: The time commitment string (e.g., "3-5 hours")
    
    Returns:
        A list of weeks with activities
    """
    try:
        # Extract number value from time commitment string
        hours_per_week = 0
        if "1-2" in time_commitment:
            hours_per_week = 2
        elif "3-5" in time_commitment:
            hours_per_week = 5
        elif "6-10" in time_commitment:
            hours_per_week = 8
        elif "11-15" in time_commitment:
            hours_per_week = 12
        else:
            hours_per_week = 15
        
        # Extract learning objectives or tasks from content
        lines = content.strip().split('\n')
        
        # Look for numbered items as tasks
        tasks = []
        for line in lines:
            line = line.strip()
            # Match patterns like "1. Task description" or "• Task description"
            if (line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '•', '-')) and 
                len(line) > 3):
                tasks.append(line)
        
        # If no tasks were found, use paragraphs as tasks
        if not tasks:
            for line in lines:
                if len(line.strip()) > 15 and not line.startswith('#'):
                    tasks.append(line.strip())
        
        # Ensure we have at least some tasks
        if not tasks:
            tasks = ["Review fundamentals", "Practice exercises", "Build sample project"]
        
        # Create a structured timetable (up to 6 weeks)
        weeks = []
        
        # Determine number of weeks based on tasks and hours
        num_weeks = min(len(tasks) // 2 + 1, 6)
        
        # Distribute tasks across weeks
        tasks_per_week = max(1, len(tasks) // num_weeks)
        
        for week in range(1, num_weeks + 1):
            week_data = {
                "week": week,
                "activities": [],
                "hours": hours_per_week
            }
            
            # Get tasks for this week
            start_idx = (week - 1) * tasks_per_week
            end_idx = min(start_idx + tasks_per_week, len(tasks))
            
            # Add activities for this week
            for i in range(start_idx, end_idx):
                if i < len(tasks):
                    # Remove numbering and bullet points
                    task = tasks[i]
                    for prefix in ['1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '•', '-']:
                        if task.startswith(prefix):
                            task = task[len(prefix):].strip()
                            break
                    
                    week_data["activities"].append(task)
            
            weeks.append(week_data)
            
        return weeks
    
    except Exception as e:
        print(f"Error formatting plan as timetable: {e}")
        # Return a basic structure if parsing fails
        return [
            {"week": 1, "activities": ["Get started with fundamentals"], "hours": 5},
            {"week": 2, "activities": ["Continue learning core concepts"], "hours": 5}
        ]

def display_learning_plan(plan):
    """Display the generated learning plan with a timetable view."""
    try:
        # Success message
        st.success("Your personalized learning plan has been created!")
        
        # Store the plan in session state for access from other pages
        st.session_state.current_plan = plan
        st.session_state.has_plan = True
        
        # Get subject from session state, not from plan object
        subject = st.session_state.get("subject", "Learning Topic")
        
        # Plan title
        st.header(f"Learning Plan for {subject}")
        
        # Ensure user data is initialized
        if "user_data" not in st.session_state:
            st.session_state.user_data = {
                "total_learning_time": 0,
                "completed_tasks": 0,
                "plans_created": 0,
                "active_plans": 0,
                "topics": {},
                "weekly_activity": [0, 0, 0, 0, 2, 3, 1],
                "time_tracking": {}
            }
            
        # Extract estimated time from plan duration
        estimated_time = 0
        duration_text = plan.estimated_duration
        if "hours" in duration_text.lower():
            # Try to extract the number
            try:
                # Find numbers in the string
                import re
                numbers = re.findall(r'\d+', duration_text)
                if numbers:
                    estimated_time = int(numbers[0])
                else:
                    # Default based on time commitment if parsing fails
                    time_commitment = st.session_state.get("time_commitment", "3-5 hours")
                    if "1-2" in time_commitment:
                        estimated_time = 2 * 4  # 2 hours/week * 4 weeks
                    elif "3-5" in time_commitment:
                        estimated_time = 4 * 4  # 4 hours/week * 4 weeks
                    elif "6-10" in time_commitment:
                        estimated_time = 8 * 4  # 8 hours/week * 4 weeks
                    elif "11-15" in time_commitment:
                        estimated_time = 12 * 4  # 12 hours/week * 4 weeks
                    else:
                        estimated_time = 16 * 4  # 16 hours/week * 4 weeks
            except:
                # Fallback to default if parsing fails
                estimated_time = 16
                
        # Initialize tracking data for this subject
        st.session_state.user_data["time_tracking"][subject] = {
            "estimated_time": estimated_time,
            "actual_time": 0,
            "start_date": datetime.now().strftime("%Y-%m-%d"),
            "last_updated": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Update plans created count
        st.session_state.user_data["plans_created"] = st.session_state.user_data.get("plans_created", 0) + 1
        st.session_state.user_data["active_plans"] = st.session_state.user_data.get("active_plans", 0) + 1
        
        # Add topic if not already present
        if subject not in st.session_state.user_data["topics"]:
            st.session_state.user_data["topics"][subject] = 0
        
        # Set initial progress to 0%
        st.session_state.plan_progress = 0
        
        # Use tabs for organization
        tab1, tab2, tab3 = st.tabs(["Timetable", "Full Plan", "Resources"])
        
        # Format content as timetable
        time_commitment = st.session_state.get("time_commitment", "3-5 hours")
        weeks_timetable = format_learning_plan_as_timetable(plan.content, time_commitment)
        
        with tab1:
            # Timetable view
            st.subheader("Your Learning Schedule")
            
            # Add a description
            st.write(f"This schedule is designed for {time_commitment} per week of study time.")
            
            # Display the timetable
            for week in weeks_timetable:
                with st.expander(f"Week {week['week']} ({week['hours']} hours)", expanded=week['week'] == 1):
                    for i, activity in enumerate(week['activities']):
                        st.markdown(f"**Activity {i+1}:** {activity}")
                    
                    # Show recommended hours per activity
                    hours_per_activity = round(week['hours'] / max(len(week['activities']), 1), 1)
                    st.info(f"Dedicate approximately {hours_per_activity} hours to each activity this week")
        
        with tab2:
            # Full plan content
            st.subheader("Complete Learning Plan")
            st.write(plan.content)
            
            # Time Estimate
            st.info(f"**Time Estimate:** {plan.estimated_duration}")
            
        with tab3:
            # Resources
            st.subheader("Recommended Resources")
            
            # Display resources in a more structured way
            for i, resource in enumerate(plan.suggested_resources):
                st.markdown(f"**{i+1}.** {resource}")
                
                # Add action buttons for each resource
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    resource_name = f"resource_{i}"
                    if st.button("📝 Take Notes", key=f"notes_{resource_name}"):
                        st.session_state[f"notes_{resource_name}_active"] = True
                
                with btn_col2:
                    if st.button("🔍 Find Similar", key=f"similar_{resource_name}"):
                        st.info(f"Finding similar resources to: {resource[:30]}...")
                
                # Show notes area if active
                if st.session_state.get(f"notes_{resource_name}_active", False):
                    with st.expander("Resource Notes", expanded=True):
                        notes = st.text_area("Your notes:", key=f"notes_text_{resource_name}")
                        if st.button("Save Notes", key=f"save_notes_{resource_name}"):
                            st.success("Notes saved!")
                            st.session_state[f"notes_{resource_name}_active"] = False
                            
                st.markdown("---")
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Download Plan", key="download_plan", use_container_width=True):
                if "user_email" in st.session_state:
                    try:
                        file_path = save_plan_to_file(plan, st.session_state.user_email)
                        if file_path:
                            st.success("Plan saved successfully!")
                    except:
                        st.error("Error saving plan")
                else:
                    st.warning("Please log in to save your plan")
        
        with col2:
            if st.button("📊 Track Progress", key="track_progress", use_container_width=True):
                st.session_state.active_tab = "Dashboard"
                st.rerun()
        
        with col3:
            if st.button("🔄 Create New Plan", key="reset", type="primary", use_container_width=True):
                try:
                    init_session()
                    st.rerun()
                except:
                    st.error("Error creating new plan")
        
        # Show progress tracker if requested
        if st.session_state.get("show_progress_tracker", False):
            st.markdown("---")
            st.subheader("Progress Tracker")
            
            progress = st.slider("Your overall completion:", 0, 100, 0, key="progress_overall")
            st.progress(progress / 100.0)
            
            if st.button("Save Progress"):
                st.success("Progress saved!")
                st.session_state.show_progress_tracker = False
    
    except Exception as e:
        # Fallback in case of any error
        print(f"Error displaying learning plan: {e}")
        st.error("An error occurred while displaying the learning plan")
        
        # Simple fallback display
        st.header(f"Learning Plan for {st.session_state.subject}")
        st.write("Your learning plan has been created, but there was an error displaying the timetable view.")
        st.write(plan.content)

# We'll handle errors directly in the main function instead of using a decorator

# Main app entry point
def run_app():
    """Run the main application with error handling"""
    try:
        # Initialize the session state
        if "step" not in st.session_state:
            st.session_state.step = 1
        
        if "learning_goal" not in st.session_state:
            st.session_state.learning_goal = None
        
        if "learning_plan" not in st.session_state:
            st.session_state.learning_plan = None
        
        if "subscription_tier" not in st.session_state:
            st.session_state.subscription_tier = SubscriptionTier.FREEMIUM
        
        # Initialize the subject field to avoid AttributeError
        if "subject" not in st.session_state:
            st.session_state.subject = ""
        
        # Initialize other required fields
        if "level" not in st.session_state:
            st.session_state.level = ""
        
        if "current_knowledge" not in st.session_state:
            st.session_state.current_knowledge = ""
        
        if "learning_purpose" not in st.session_state:
            st.session_state.learning_purpose = ""
        
        if "time_commitment" not in st.session_state:
            st.session_state.time_commitment = ""
        
        if "preferred_resources" not in st.session_state:
            st.session_state.preferred_resources = ""
        
        # Initialize plans counter
        if "plans_created" not in st.session_state:
            st.session_state.plans_created = 0
        
        # Initialize plans_created_today
        if "plans_created_today" not in st.session_state:
            st.session_state.plans_created_today = 0
        
        # Check if user has a premium subscription stored
        if "user_email" in st.session_state:
            user_email = st.session_state.user_email
            if check_premium_status(user_email):
                st.session_state.subscription_tier = SubscriptionTier.PREMIUM
                
        # Initialize agents
        if "email_agent" not in st.session_state:
            try:
                from agents.email_agent import EmailAgent
                st.session_state.email_agent = EmailAgent()
            except Exception as e:
                print(f"Failed to initialize EmailAgent: {e}")
                st.session_state.email_agent = None
        
        if "stripe_agent" not in st.session_state:
            try:
                from agents.stripe_agent import StripeAgent
                st.session_state.stripe_agent = StripeAgent()
            except Exception as e:
                print(f"Failed to initialize StripeAgent: {e}")
                st.session_state.stripe_agent = None
        
        # Check for URL parameters to handle routes
        query_params = st.query_params
        
        if "success" in query_params:
            handle_success_route()
        elif "cancel" in query_params:
            show_cancel_page()
        else:
            main()
    
    except Exception as e:
        # Log the error
        print(f"Error in app initialization: {e}")
        
        # Display user-friendly error message
        st.error("Something went wrong. Please try refreshing the page.")
        st.title("🧠 CoachAI - Your Personalized Learning Assistant")
        st.info("The application is currently experiencing technical difficulties. Please try again later.")

# Run the app
if __name__ == "__main__":
    run_app()