"""
Company Management page for InterviewAgent Streamlit app
Manages company information and career page discovery
"""

import streamlit as st
import asyncio
from typing import List, Dict, Any
from datetime import datetime

from src.config import get_config
from src.database.operations import get_db_operations


# Predefined company lists for discovery
TECH_COMPANIES = [
    "Google", "Microsoft", "Apple", "Amazon", "Meta", "Netflix", "Tesla",
    "Nvidia", "Adobe", "Salesforce", "Oracle", "IBM", "Intel", "Cisco"
]

FINANCE_COMPANIES = [
    "JPMorgan Chase", "Goldman Sachs", "Morgan Stanley", "Bank of America",
    "Wells Fargo", "American Express", "Visa", "Mastercard", "PayPal"
]

HEALTHCARE_COMPANIES = [
    "Johnson & Johnson", "Pfizer", "UnitedHealth", "Merck", "Bristol Myers Squibb",
    "AbbVie", "Roche", "Novartis", "Moderna", "Gilead Sciences"
]

STARTUP_COMPANIES = [
    "Stripe", "SpaceX", "Databricks", "Canva", "Discord", "Figma",
    "Notion", "Airbnb", "Uber", "DoorDash", "Coinbase", "Robinhood"
]


def show_company_management():
    """Display the company management interface"""
    
    st.header("🏢 Company Management")
    st.write("Manage company information for targeted job applications.")
    
    # Initialize session state
    if 'company_data' not in st.session_state:
        st.session_state.company_data = []
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📋 Company Database", "🔍 Add Companies", "📊 Analytics"])
    
    with tab1:
        _show_company_database()
    
    with tab2:
        _show_add_companies()
    
    with tab3:
        _show_company_analytics()


def _show_company_database():
    """Show the company database management interface"""
    st.subheader("Company Database")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_term = st.text_input("Search companies", placeholder="Enter company name...")
    
    with col2:
        if st.button("🔄 Refresh"):
            st.rerun()
    
    # Mock company data for MVP
    mock_companies = [
        {"name": "Google", "industry": "Technology", "size": "Large", "status": "Active"},
        {"name": "Microsoft", "industry": "Technology", "size": "Large", "status": "Active"},
        {"name": "Stripe", "industry": "Fintech", "size": "Medium", "status": "Active"},
        {"name": "OpenAI", "industry": "AI/ML", "size": "Medium", "status": "Active"},
    ]
    
    # Filter companies based on search
    if search_term:
        filtered_companies = [
            comp for comp in mock_companies 
            if search_term.lower() in comp["name"].lower()
        ]
    else:
        filtered_companies = mock_companies
    
    if filtered_companies:
        st.dataframe(
            filtered_companies,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No companies found. Try adjusting your search or add new companies.")


def _show_add_companies():
    """Show the add companies interface"""
    st.subheader("Add Companies")
    
    # Manual company addition
    with st.form("add_company_form"):
        st.write("**Add Individual Company**")
        
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input("Company Name *", placeholder="e.g., Google")
            industry = st.selectbox(
                "Industry",
                ["Technology", "Finance", "Healthcare", "Manufacturing", "Retail", "Other"]
            )
        
        with col2:
            website = st.text_input("Website", placeholder="https://company.com")
            company_size = st.selectbox("Company Size", ["Startup", "Small", "Medium", "Large"])
        
        notes = st.text_area("Notes", placeholder="Additional information about the company...")
        
        submitted = st.form_submit_button("Add Company", type="primary")
        
        if submitted and company_name:
            st.success(f"✅ Added {company_name} to the database!")
    
    st.divider()
    
    # Bulk company addition from predefined lists
    st.write("**Add from Predefined Lists**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("➕ Add Tech Companies", help="Add major technology companies"):
            st.success(f"Added {len(TECH_COMPANIES)} tech companies!")
        
        if st.button("➕ Add Healthcare Companies", help="Add major healthcare companies"):
            st.success(f"Added {len(HEALTHCARE_COMPANIES)} healthcare companies!")
    
    with col2:
        if st.button("➕ Add Finance Companies", help="Add major financial companies"):
            st.success(f"Added {len(FINANCE_COMPANIES)} finance companies!")
        
        if st.button("➕ Add Startup Companies", help="Add popular startup companies"):
            st.success(f"Added {len(STARTUP_COMPANIES)} startup companies!")


def _show_company_analytics():
    """Show company analytics and insights"""
    st.subheader("Company Analytics")
    
    # Mock analytics data
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Companies", "127", delta="12")
    
    with col2:
        st.metric("Industries", "8", delta="2")
    
    with col3:
        st.metric("Applications", "45", delta="7")
    
    with col4:
        st.metric("Response Rate", "23%", delta="5%")
    
    st.divider()
    
    # Industry distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Industry Distribution**")
        industry_data = {
            "Technology": 45,
            "Finance": 23,
            "Healthcare": 18,
            "Manufacturing": 12,
            "Retail": 8,
            "Other": 21
        }
        st.bar_chart(industry_data)
    
    with col2:
        st.write("**Company Size Distribution**")
        size_data = {
            "Large": 34,
            "Medium": 28,
            "Small": 25,
            "Startup": 40
        }
        st.bar_chart(size_data)
    
    # Recent activity
    st.write("**Recent Activity**")
    recent_activity = [
        {"Date": "2024-01-15", "Company": "OpenAI", "Action": "Added to database"},
        {"Date": "2024-01-14", "Company": "Stripe", "Action": "Updated information"},
        {"Date": "2024-01-13", "Company": "Google", "Action": "Application submitted"},
        {"Date": "2024-01-12", "Company": "Microsoft", "Action": "Career page updated"},
    ]
    
    st.dataframe(recent_activity, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    show_company_management()