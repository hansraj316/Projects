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

from agents import AgentManager, AgentTask, AgentContext
from config import load_config


def show_ai_agents():
    """Display AI agents demonstration page"""
    st.title("🤖 AI Agents")
    st.markdown("Demonstrate and test the AI-powered agents for job application automation.")
    
    # Initialize agent manager
    if 'agent_manager' not in st.session_state:
        try:
            config = load_config()
            agent_manager = AgentManager(config)
            agent_manager.initialize_agents()
            st.session_state.agent_manager = agent_manager
            st.success("🎉 AI Agents initialized successfully!")
        except Exception as e:
            st.error(f"Failed to initialize agents: {str(e)}")
            st.session_state.agent_manager = None
            return
    
    agent_manager = st.session_state.agent_manager
    
    if agent_manager is None:
        st.error("Agent manager not available")
        return
    
    # Agent Status Overview
    st.header("📊 Agent Status")
    
    status = agent_manager.get_agent_status()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Agents", len(status))
    with col2:
        openai_agents = sum(1 for s in status.values() if s['has_openai'])
        st.metric("OpenAI Enabled", openai_agents)
    with col3:
        config_agents = sum(1 for s in status.values() if s['config_loaded'])
        st.metric("Configured", config_agents)
    
    # Agent Details
    st.subheader("🔧 Agent Details")
    for name, info in status.items():
        with st.expander(f"{name.replace('_', ' ').title()}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Description:** {info['description']}")
                st.write(f"**OpenAI Available:** {'✅' if info['has_openai'] else '❌'}")
            with col2:
                st.write(f"**Configuration Loaded:** {'✅' if info['config_loaded'] else '❌'}")
    
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


if __name__ == "__main__":
    show_ai_agents()