"""
AI Agents page for demonstrating agent capabilities
"""

import streamlit as st
import asyncio
import json
from datetime import datetime
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from agents.base_agent import AgentTask, AgentContext
    from config import get_config
    agents_available = True
    
    # Try to import the full agent system
    try:
        from core.bootstrap import create_application, initialize_application
        full_agent_system_available = True
    except ImportError:
        full_agent_system_available = False
        
except ImportError:
    AgentTask = None
    AgentContext = None
    agents_available = False
    full_agent_system_available = False


def show_ai_agents():
    """Display AI agents demonstration page"""
    st.title("🤖 AI Agents")
    st.markdown("Demonstrate and test the AI-powered agents for job application automation.")
    
    if not agents_available:
        st.warning("⚠️ AI Agents core modules not available. Showing demo mode.")
        st.info("This page demonstrates the AI agent capabilities. The agents are integrated into the Resume Manager, Job Search, and Applications pages.")
        show_simplified_agent_demo()
        return
    
    # Check if full agent system is available
    if not full_agent_system_available:
        st.warning("⚠️ Full agent system not available. Showing simplified demo mode.")
        show_simplified_agent_demo()
        return
    
    # Initialize agent manager with full dependency injection
    if 'app_components' not in st.session_state:
        try:
            with st.spinner("Initializing AI agent system..."):
                # Create the full application
                app_components = create_application()
                
                # Initialize asynchronously
                import asyncio
                asyncio.run(initialize_application(app_components))
                
                st.session_state.app_components = app_components
                st.success("🎉 AI Agents initialized successfully!")
        except Exception as e:
            st.error(f"Failed to initialize agents: {str(e)}")
            st.session_state.app_components = None
            # Fall back to simplified demo
            show_simplified_agent_demo()
            return
    
    app_components = st.session_state.app_components
    
    if app_components is None:
        st.warning("⚠️ Full agent system not available. Switching to demo mode.")
        show_simplified_agent_demo()
        return
    
    agent_manager = app_components["agent_manager"]
    
    # Agent Status Overview
    st.header("📊 Agent Status")
    
    status = agent_manager.get_agent_status()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Agents", status.get("total_agents", 0))
    with col2:
        st.metric("Healthy Agents", status.get("healthy_agents", 0))
    with col3:
        st.metric("Orchestrator", "✅" if status.get("orchestrator_available", False) else "❌")
    
    # Agent Details
    st.subheader("🔧 Agent Details")
    agent_details = status.get("agents", {})
    for name, info in agent_details.items():
        with st.expander(f"{name.replace('_', ' ').title()}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Description:** {info.get('description', 'N/A')}")
                st.write(f"**Healthy:** {'✅' if info.get('healthy', False) else '❌'}")
            with col2:
                deps = info.get('dependencies_available', {})
                st.write(f"**OpenAI Client:** {'✅' if deps.get('openai_client', False) else '❌'}")
                st.write(f"**Config:** {'✅' if deps.get('config', False) else '❌'}")
    
    st.markdown("---")
    
    # Agent Testing Interface
    st.header("🧪 Test AI Agents")
    
    tab1, tab2, tab3 = st.tabs(["Resume Optimizer", "Cover Letter Generator", "Orchestrator"])
    
    with tab1:
        st.subheader("📄 Resume Optimization Agent")
        
        # Test inputs
        with st.form("resume_test"):
            job_desc = st.text_area(
                "Job Description",
                value="We are seeking a Python Developer with experience in AI/ML, web development, and database management. Must have 3+ years experience with Python, Django/Flask, and SQL databases.",
                height=100
            )
            
            current_resume = st.text_area(
                "Current Resume (JSON format)",
                value='{"professional_summary": "Software developer with 4 years experience", "skills": ["Python", "JavaScript", "SQL"], "experience": ["Backend development", "API design"]}',
                height=100
            )
            
            company_name = st.text_input("Company Name", value="TechCorp Inc.")
            job_title = st.text_input("Job Title", value="Senior Python Developer")
            
            submit_resume = st.form_submit_button("🚀 Optimize Resume")
        
        if submit_resume:
            with st.spinner("Optimizing resume..."):
                try:
                    resume_data = json.loads(current_resume)
                    
                    # Create task
                    task = AgentTask(
                        task_id="test_resume_opt",
                        task_type="optimize_resume",
                        description="Test resume optimization",
                        input_data={
                            "job_description": job_desc,
                            "current_resume": resume_data,
                            "company_name": company_name,
                            "job_title": job_title
                        }
                    )
                    
                    context = AgentContext(user_id="test_user")
                    
                    # Get agent and execute
                    resume_agent = agent_manager.get_agent("resume_optimizer")
                    result = asyncio.run(resume_agent.execute(task, context))
                    
                    if result['success']:
                        st.success("✅ Resume optimization completed!")
                        
                        # Display results
                        st.subheader("📊 Optimization Results")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Job Match Score", f"{result['data']['job_match_score']}%")
                        with col2:
                            st.metric("Keywords Added", len(result['data']['keywords_added']))
                        
                        # Show optimized resume
                        with st.expander("🔍 View Optimized Resume"):
                            st.json(result['data']['optimized_resume'])
                        
                        # Show optimization summary
                        with st.expander("📋 Optimization Summary"):
                            st.json(result['data']['optimization_summary'])
                    else:
                        st.error(f"❌ Optimization failed: {result['message']}")
                
                except json.JSONDecodeError:
                    st.error("❌ Invalid JSON format in resume data")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    with tab2:
        st.subheader("📝 Cover Letter Generation Agent")
        
        with st.form("cover_letter_test"):
            job_desc_cl = st.text_area(
                "Job Description",
                value="Looking for a passionate Python developer to join our AI team. You'll work on machine learning models, web applications, and data processing pipelines.",
                height=100
            )
            
            company_name_cl = st.text_input("Company Name", value="AI Innovations Ltd.")
            job_title_cl = st.text_input("Job Title", value="Python AI Developer")
            hiring_manager = st.text_input("Hiring Manager", value="Sarah Johnson")
            
            candidate_info = st.text_area(
                "Candidate Information (JSON)",
                value='{"name": "John Doe", "email": "john@example.com", "years_experience": 4, "current_role": "Software Developer"}',
                height=80
            )
            
            submit_cover = st.form_submit_button("✍️ Generate Cover Letter")
        
        if submit_cover:
            with st.spinner("Generating cover letter..."):
                try:
                    candidate_data = json.loads(candidate_info)
                    
                    task = AgentTask(
                        task_id="test_cover_letter",
                        task_type="generate_cover_letter",
                        description="Test cover letter generation",
                        input_data={
                            "job_description": job_desc_cl,
                            "company_name": company_name_cl,
                            "job_title": job_title_cl,
                            "hiring_manager": hiring_manager,
                            "candidate_info": candidate_data,
                            "resume_summary": {"skills": ["Python", "AI", "ML"]},
                            "company_research": {"mission": "Innovating with AI"}
                        }
                    )
                    
                    context = AgentContext(user_id="test_user")
                    
                    cover_agent = agent_manager.get_agent("cover_letter_generator")
                    result = asyncio.run(cover_agent.execute(task, context))
                    
                    if result['success']:
                        st.success("✅ Cover letter generated successfully!")
                        
                        # Display metrics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Quality Score", f"{result['data']['quality_score']}/100")
                        with col2:
                            st.metric("Word Count", result['data']['word_count'])
                        with col3:
                            st.metric("Paragraphs", result['data']['cover_letter']['paragraph_count'])
                        
                        # Show cover letter
                        st.subheader("📄 Generated Cover Letter")
                        st.text_area(
                            "Cover Letter Content",
                            value=result['data']['cover_letter']['full_text'],
                            height=400,
                            disabled=True
                        )
                        
                        # Show analysis
                        with st.expander("📊 Analysis & Key Points"):
                            st.write("**Key Points:**")
                            for point in result['data']['key_points']:
                                st.write(f"• {point}")
                            
                            st.write("**Personalization Elements:**")
                            for element in result['data']['personalization_elements']:
                                st.write(f"• {element}")
                    else:
                        st.error(f"❌ Generation failed: {result['message']}")
                
                except json.JSONDecodeError:
                    st.error("❌ Invalid JSON format in candidate information")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    with tab3:
        st.subheader("🎯 Orchestrator Agent")
        
        st.info("The Orchestrator manages complete job application workflows by coordinating multiple agents.")
        
        with st.form("workflow_test"):
            job_listing_id = st.text_input("Job Listing ID", value="job_12345")
            resume_template_id = st.text_input("Resume Template ID", value="resume_template_1")
            
            submit_workflow = st.form_submit_button("🚀 Create Workflow")
        
        if submit_workflow:
            with st.spinner("Creating workflow..."):
                try:
                    orchestrator = agent_manager.get_orchestrator()
                    
                    # Create workflow
                    workflow = orchestrator.create_job_application_workflow(
                        user_id="test_user",
                        job_listing_id=job_listing_id,
                        resume_template_id=resume_template_id
                    )
                    
                    st.success("✅ Workflow created successfully!")
                    
                    # Display workflow details
                    st.subheader("📋 Workflow Details")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Workflow ID:** {workflow.workflow_id}")
                        st.write(f"**Name:** {workflow.name}")
                    with col2:
                        st.write(f"**Status:** {workflow.status}")
                        st.write(f"**Steps:** {len(workflow.steps)}")
                    
                    # Show workflow steps
                    st.subheader("📝 Workflow Steps")
                    for i, step in enumerate(workflow.steps, 1):
                        with st.expander(f"Step {i}: {step.description}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Agent:** {step.agent_name}")
                                st.write(f"**Task Type:** {step.task_type}")
                            with col2:
                                st.write(f"**Priority:** {step.priority}")
                                if step.depends_on:
                                    st.write(f"**Depends on:** {', '.join(step.depends_on)}")
                    
                    # Option to execute workflow (mock)
                    if st.button("▶️ Execute Workflow (Demo)"):
                        st.info("In a real scenario, this would execute all workflow steps automatically.")
                        st.write("**Workflow execution would include:**")
                        st.write("1. ✅ Analyze job description")
                        st.write("2. ✅ Optimize resume")
                        st.write("3. ✅ Generate cover letter")
                        st.write("4. ✅ Submit application")
                        st.write("5. ✅ Send notification")
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    st.markdown("---")
    
    # Agent Performance
    st.header("⚡ Agent Performance")
    
    if st.button("🧪 Run Agent Tests"):
        with st.spinner("Testing all agents..."):
            test_results = agent_manager.test_agents()
            
            st.subheader("Test Results")
            for agent_name, passed in test_results.items():
                status_icon = "✅" if passed else "❌"
                st.write(f"{status_icon} **{agent_name.replace('_', ' ').title()}**: {'PASS' if passed else 'FAIL'}")
            
            # Summary
            passed_count = sum(test_results.values())
            total_count = len(test_results)
            
            if passed_count == total_count:
                st.success(f"🎉 All {total_count} agents are working correctly!")
            else:
                st.warning(f"⚠️ {passed_count}/{total_count} agents passed tests")


def show_simplified_agent_demo():
    """Show a simplified agent demo when the full system isn't available"""
    
    st.info("📝 **Demo Mode**: Full agent system not available. Showing conceptual demonstration.")
    
    # Mock agent status
    st.header("📊 Mock Agent Status")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Agents", 5)
    with col2:
        st.metric("Demo Mode", "✅")
    with col3:
        st.metric("Configuration", "⚙️")
    
    # Available agents demo
    st.subheader("🤖 Available Agent Types")
    
    agents_info = {
        "Resume Optimizer": {
            "description": "AI-powered resume optimization for specific job requirements",
            "status": "Available in production",
            "features": ["Job-specific keyword optimization", "Format enhancement", "Skills matching"]
        },
        "Cover Letter Generator": {
            "description": "Personalized cover letter generation based on job description",
            "status": "Available in production", 
            "features": ["Company research integration", "Tone customization", "Template variety"]
        },
        "Job Discovery": {
            "description": "Intelligent job search and discovery agent",
            "status": "Available in production",
            "features": ["Multi-platform search", "Relevance scoring", "Automated filtering"]
        },
        "Application Submitter": {
            "description": "Automated job application submission",
            "status": "Development",
            "features": ["Form auto-fill", "Document upload", "Submission tracking"]
        },
        "Email Notification": {
            "description": "Automated email notifications and follow-ups",
            "status": "Available in production",
            "features": ["Status updates", "Interview reminders", "Follow-up sequences"]
        }
    }
    
    for agent_name, info in agents_info.items():
        with st.expander(f"🔧 {agent_name}"):
            st.write(f"**Description:** {info['description']}")
            st.write(f"**Status:** {info['status']}")
            st.write("**Features:**")
            for feature in info['features']:
                st.write(f"• {feature}")
    
    st.markdown("---")
    
    # Demo functionality
    st.header("🎯 Demo Functionality")
    
    tab1, tab2 = st.tabs(["Resume Optimization Demo", "Cover Letter Demo"])
    
    with tab1:
        st.subheader("📄 Resume Optimization Preview")
        
        job_desc = st.text_area(
            "Job Description",
            value="We are seeking a Python Developer with experience in AI/ML, web development, and database management.",
            height=100
        )
        
        if st.button("🚀 Preview Optimization", key="resume_demo"):
            st.success("✅ Optimization complete! (Demo)")
            st.write("**Sample optimizations:**")
            st.write("• Added relevant keywords: 'Python', 'AI/ML', 'web development'")
            st.write("• Enhanced technical skills section")
            st.write("• Improved project descriptions for relevance")
            st.write("• Adjusted formatting for ATS compatibility")
    
    with tab2:
        st.subheader("📝 Cover Letter Generation Preview")
        
        company_name = st.text_input("Company Name", value="TechCorp Inc.")
        job_title = st.text_input("Job Title", value="Python Developer")
        
        if st.button("✍️ Preview Generation", key="cover_demo"):
            st.success("✅ Cover letter generated! (Demo)")
            with st.expander("📄 Sample Cover Letter"):
                st.write(f"""
                Dear TechCorp Inc. Hiring Team,
                
                I am writing to express my strong interest in the {job_title} position at {company_name}. 
                With my background in Python development and experience in AI/ML technologies, I am excited 
                about the opportunity to contribute to your innovative team.
                
                [This is a demo preview - the actual system would generate a full, personalized cover letter]
                
                Thank you for your consideration.
                
                Best regards,
                [Your Name]
                """)
    
    st.markdown("---")
    
    st.info("💡 **Note**: To access the full agent system, ensure all dependencies are properly configured and the application is running in production mode.")


if __name__ == "__main__":
    show_ai_agents()