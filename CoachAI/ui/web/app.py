"""Streamlit web interface for CoachAI."""

import streamlit as st
from typing import Dict, Optional
from datetime import datetime, timezone

from agents.planner import LearningGoal, PlannerAgent
from agents.email_agent import EmailAgent, EmailConfig
from agents.stripe_agent import StripeAgent, SubscriptionTier, SubscriptionConfig

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'responses' not in st.session_state:
    st.session_state.responses = {}
if 'subscription' not in st.session_state:
    # Initialize with Freemium configuration
    st.session_state.subscription = SubscriptionConfig(
        daily_plans=1,
        resources_per_plan=3,
        email_notifications=False,
        price=0.0,
        tier=SubscriptionTier.FREEMIUM
    )
if 'plans_created_today' not in st.session_state:
    st.session_state.plans_created_today = 0
if 'stripe_agent' not in st.session_state:
    st.session_state.stripe_agent = StripeAgent()

def init_session():
    """Initialize or reset session state."""
    st.session_state.step = 1
    st.session_state.responses = {}

def next_step():
    """Proceed to next step."""
    st.session_state.step += 1

def prev_step():
    """Go back to previous step."""
    st.session_state.step -= 1

def handle_subscription_upgrade():
    """Handle the subscription upgrade process."""
    try:
        stripe_agent = st.session_state.stripe_agent
        
        with st.spinner("Processing upgrade to Premium..."):
            # Notify admin of upgrade request
            st.session_state.mcp.gmail_send_email(
                to="admin@coachai.com",
                subject="New Premium Subscription Request",
                body="A user has requested to upgrade to Premium."
            )
            
            # Update subscription tier
            st.session_state.subscription.tier = SubscriptionTier.PREMIUM
            st.success("🎉 Successfully upgraded to Premium!")
            st.balloons()
            st.rerun()
            
    except Exception as e:
        st.error("Unable to process upgrade. Please try again later.")

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
            handle_subscription_upgrade()
    
    # Show usage statistics
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Today's Usage")
    max_plans = stripe_agent.get_tier_features(current_tier)["daily_plans"]
    st.sidebar.markdown(f"Plans created today: {st.session_state.plans_created_today}/{max_plans}")

def generate_plan():
    """Generate and display the learning plan."""
    stripe_agent = st.session_state.stripe_agent
    
    # Check if user can create more plans
    if not stripe_agent.can_create_plan(st.session_state.subscription.tier, st.session_state.plans_created_today):
        st.error("You've reached your daily plan limit!")
        if st.session_state.subscription.tier == SubscriptionTier.FREEMIUM:
            st.info("Upgrade to Premium for unlimited plans!")
        return

    with st.spinner("Generating your personalized learning plan..."):
        try:
            # Create learning goal from responses
            goal = LearningGoal(
                topic=st.session_state.responses['topic'],
                current_level=st.session_state.responses['current_level'],
                target_level=st.session_state.responses['target_level'],
                time_commitment=st.session_state.responses['time_commitment'],
                learning_style=st.session_state.responses['learning_style']
            )

            # Generate plan using planner agent
            planner = PlannerAgent()
            plan = planner.create_plan(goal)

            # Increment plans created today
            st.session_state.plans_created_today += 1

            # Display plan
            st.success("Your learning plan is ready!")
            
            st.subheader("Learning Plan")
            st.write(plan.content)
            
            st.subheader("Estimated Duration")
            st.write(plan.estimated_duration)
            
            st.subheader("Recommended Resources")
            max_resources = stripe_agent.get_max_resources(st.session_state.subscription.tier)
            for i, resource in enumerate(plan.suggested_resources[:max_resources]):
                st.write(f"- {resource}")
            
            if len(plan.suggested_resources) > max_resources:
                st.info(f"Upgrade to Premium to access {len(plan.suggested_resources) - max_resources} more resources!")

            # Email notification option
            if stripe_agent.can_receive_emails(st.session_state.subscription.tier):
                email = st.text_input("Enter your email to receive the plan:")
                if email and st.button("Send to Email"):
                    try:
                        email_agent = EmailAgent()
                        email_config = EmailConfig(recipient_email=email, subscribe_to_notifications=True)
                        email_agent.send_learning_plan_email(email_config, plan, goal)
                        st.success("Plan sent to your email!")
                    except Exception as e:
                        st.error(f"Failed to send email: {str(e)}")

            # Download button for the plan
            plan_text = f"""
            Learning Plan for {goal.topic}
            
            {plan.content}
            
            Estimated Duration: {plan.estimated_duration}
            
            Recommended Resources:
            {chr(10).join(f'- {r}' for r in plan.suggested_resources[:max_resources])}
            """
            st.download_button(
                label="Download Plan",
                data=plan_text,
                file_name="learning_plan.txt",
                mime="text/plain"
            )

            # Reset button
            if st.button("Start Over"):
                init_session()

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            if st.button("Try Again"):
                st.session_state.step = 5

def main():
    """Main Streamlit application."""
    subscription_sidebar()
    
    st.title("🎓 AI Learning Path Generator")
    st.subheader("Let's create your personalized learning plan")

    # Progress bar
    progress = (st.session_state.step - 1) / 5
    st.progress(progress)

    # Wizard steps
    if st.session_state.step == 1:
        st.header("Step 1: What would you like to learn?")
        topic = st.text_input(
            "Enter the subject or skill you want to learn:",
            value=st.session_state.responses.get('topic', ''),
            help="Example: Python Programming, Machine Learning, Web Development"
        )
        if st.button("Next") and topic:
            st.session_state.responses['topic'] = topic
            next_step()

    elif st.session_state.step == 2:
        st.header("Step 2: What's your current level?")
        current_level = st.selectbox(
            "Select your current level of expertise:",
            ["Beginner", "Intermediate", "Advanced"],
            index=["Beginner", "Intermediate", "Advanced"].index(
                st.session_state.responses.get('current_level', 'Beginner')
            )
        )
        col1, col2 = st.columns(2)
        if col1.button("Previous"):
            prev_step()
        if col2.button("Next"):
            st.session_state.responses['current_level'] = current_level
            next_step()

    elif st.session_state.step == 3:
        st.header("Step 3: What's your target level?")
        target_level = st.selectbox(
            "Select your desired level of expertise:",
            ["Intermediate", "Advanced", "Expert"],
            index=["Intermediate", "Advanced", "Expert"].index(
                st.session_state.responses.get('target_level', 'Intermediate')
            )
        )
        col1, col2 = st.columns(2)
        if col1.button("Previous"):
            prev_step()
        if col2.button("Next"):
            st.session_state.responses['target_level'] = target_level
            next_step()

    elif st.session_state.step == 4:
        st.header("Step 4: How much time can you commit?")
        time_commitment = st.selectbox(
            "Select your weekly time commitment:",
            ["1-2 hours", "3-5 hours", "5-10 hours", "10+ hours"],
            index=["1-2 hours", "3-5 hours", "5-10 hours", "10+ hours"].index(
                st.session_state.responses.get('time_commitment', '3-5 hours')
            )
        )
        col1, col2 = st.columns(2)
        if col1.button("Previous"):
            prev_step()
        if col2.button("Next"):
            st.session_state.responses['time_commitment'] = time_commitment
            next_step()

    elif st.session_state.step == 5:
        st.header("Step 5: What's your preferred learning style?")
        learning_style = st.selectbox(
            "Select your preferred way of learning:",
            ["Visual", "Reading/Writing", "Auditory", "Hands-on"],
            index=["Visual", "Reading/Writing", "Auditory", "Hands-on"].index(
                st.session_state.responses.get('learning_style', 'Visual')
            )
        )
        col1, col2 = st.columns(2)
        if col1.button("Previous"):
            prev_step()
        if col2.button("Generate Plan"):
            st.session_state.responses['learning_style'] = learning_style
            generate_plan()

if __name__ == "__main__":
    main() 