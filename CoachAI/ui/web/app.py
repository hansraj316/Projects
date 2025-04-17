"""Streamlit web interface for CoachAI."""

import streamlit as st
from typing import Dict, Optional

from agents.planner import LearningGoal, PlannerAgent

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'responses' not in st.session_state:
    st.session_state.responses = {}

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

def generate_plan():
    """Generate and display the learning plan."""
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

            # Display plan
            st.success("Your learning plan is ready!")
            
            st.subheader("Learning Plan")
            st.write(plan.content)
            
            st.subheader("Estimated Duration")
            st.write(plan.estimated_duration)
            
            st.subheader("Recommended Resources")
            for resource in plan.suggested_resources:
                st.write(f"- {resource}")

            # Download button for the plan
            plan_text = f"""
            Learning Plan for {goal.topic}
            
            {plan.content}
            
            Estimated Duration: {plan.estimated_duration}
            
            Recommended Resources:
            {chr(10).join(f'- {r}' for r in plan.suggested_resources)}
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
    st.title("CoachAI Learning Wizard")
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