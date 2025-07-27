"""
Company Management page for InterviewAgent Streamlit app
Manages company career page discovery and database
"""

import streamlit as st
import asyncio
from typing import List
from datetime import datetime

# Note: Path is already set by streamlit_app.py, so direct imports should work
from services.company_discovery_service import (
    CompanyDiscoveryService, 
    discover_predefined_companies,
    TECH_COMPANIES, FINANCE_COMPANIES, HEALTHCARE_COMPANIES, STARTUP_COMPANIES
)

from config import Config
from database.operations import get_db_operations


def show_company_management():
    """Display the company management interface"""
    
    st.header("🏢 Company Career Page Management")
    st.write("Build and manage a database of companies and their career pages for direct job discovery.")
    
    # Initialize session state
    if 'company_discovery_results' not in st.session_state:
        st.session_state.company_discovery_results = None
    if 'discovered_companies' not in st.session_state:
        st.session_state.discovered_companies = []
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Discover Companies", "📋 Manage Companies", "📊 Industry Analysis", "⚙️ Bulk Operations"])
    
    with tab1:
        _show_company_discovery_section()
    
    with tab2:
        _show_company_management_section()
    
    with tab3:
        _show_industry_analysis_section()
    
    with tab4:
        _show_bulk_operations_section()


def _show_company_discovery_section():
    """Show company discovery interface"""
    st.subheader("🔍 Discover Company Career Pages")
    
    # Discovery options
    discovery_option = st.radio(
        "Choose discovery method:",
        ["Single Company", "Multiple Companies", "Predefined Lists"],
        horizontal=True
    )
    
    if discovery_option == "Single Company":
        _show_single_company_discovery()
    elif discovery_option == "Multiple Companies":
        _show_multiple_company_discovery()
    elif discovery_option == "Predefined Lists":
        _show_predefined_list_discovery()


def _show_single_company_discovery():
    """Show single company discovery interface"""
    st.write("### Discover Single Company")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        company_name = st.text_input(
            "Company Name", 
            placeholder="e.g., Microsoft, Google, Stripe"
        )
    
    with col2:
        if st.button("🔍 Discover", type="primary"):
            if not company_name:
                st.error("Please enter a company name")
                return
            
            with st.spinner(f"Discovering career page for {company_name}..."):
                try:
                    result = asyncio.run(_discover_companies([company_name]))
                    
                    if result.get("success"):
                        st.success(f"✅ Successfully discovered career page for {company_name}!")
                        
                        discovered = result.get("discovered_companies", [])
                        if discovered:
                            company = discovered[0]
                            
                            # Show company details
                            with st.expander("📋 Company Details", expanded=True):
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.write(f"**Name:** {company['name']}")
                                    st.write(f"**Domain:** {company['domain']}")
                                    st.write(f"**Industry:** {company['industry']}")
                                
                                with col2:
                                    st.write(f"**Career Page:** [{company['career_page_url']}]({company['career_page_url']})")
                                    st.write(f"**Website:** [{company['website_url']}]({company['website_url']})")
                                    st.write(f"**Scraping Difficulty:** {company['scraping_difficulty']}")
                    else:
                        st.error(f"❌ Failed to discover career page for {company_name}")
                        st.write(f"Error: {result.get('message', 'Unknown error')}")
                
                except Exception as e:
                    st.error(f"Discovery error: {str(e)}")


def _show_multiple_company_discovery():
    """Show multiple company discovery interface"""
    st.write("### Discover Multiple Companies")
    
    company_list = st.text_area(
        "Company Names (one per line)",
        placeholder="Microsoft\nGoogle\nAmazon\nApple\nMeta",
        height=150
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Discover All", type="primary"):
            if not company_list.strip():
                st.error("Please enter at least one company name")
                return
            
            companies = [name.strip() for name in company_list.split('\n') if name.strip()]
            
            with st.spinner(f"Discovering career pages for {len(companies)} companies..."):
                try:
                    result = asyncio.run(_discover_companies(companies))
                    _display_discovery_results(result)
                
                except Exception as e:
                    st.error(f"Discovery error: {str(e)}")
    
    with col2:
        sample_companies = st.selectbox(
            "Load Sample List:",
            ["Tech Companies", "Finance Companies", "Healthcare Companies", "Startup Companies"]
        )
        
        if st.button("📝 Load Sample"):
            if sample_companies == "Tech Companies":
                sample_list = "\n".join(TECH_COMPANIES[:10])
            elif sample_companies == "Finance Companies":
                sample_list = "\n".join(FINANCE_COMPANIES[:10])
            elif sample_companies == "Healthcare Companies":
                sample_list = "\n".join(HEALTHCARE_COMPANIES[:10])
            else:
                sample_list = "\n".join(STARTUP_COMPANIES[:10])
            
            st.text_area("Sample loaded:", value=sample_list, height=100, key="sample_display")
    
    with col3:
        if st.button("🧹 Clear List"):
            st.rerun()


def _show_predefined_list_discovery():
    """Show predefined list discovery interface"""
    st.write("### Discover Predefined Company Lists")
    st.info("Use curated lists of companies by industry for bulk discovery.")
    
    # Show available lists
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Available Lists:**")
        st.write(f"• **Tech Companies:** {len(TECH_COMPANIES)} companies")
        st.write(f"• **Finance Companies:** {len(FINANCE_COMPANIES)} companies")
        st.write(f"• **Healthcare Companies:** {len(HEALTHCARE_COMPANIES)} companies")
        st.write(f"• **Startup Companies:** {len(STARTUP_COMPANIES)} companies")
        
        total_companies = len(TECH_COMPANIES) + len(FINANCE_COMPANIES) + len(HEALTHCARE_COMPANIES) + len(STARTUP_COMPANIES)
        st.write(f"**Total:** {total_companies} companies")
    
    with col2:
        selected_lists = st.multiselect(
            "Select Lists to Discover:",
            ["Tech Companies", "Finance Companies", "Healthcare Companies", "Startup Companies"],
            default=["Tech Companies"]
        )
        
        if st.button("🎯 Discover Selected Lists", type="primary"):
            if not selected_lists:
                st.error("Please select at least one list")
                return
            
            # Combine selected lists
            companies_to_discover = []
            for list_name in selected_lists:
                if list_name == "Tech Companies":
                    companies_to_discover.extend(TECH_COMPANIES)
                elif list_name == "Finance Companies":
                    companies_to_discover.extend(FINANCE_COMPANIES)
                elif list_name == "Healthcare Companies":
                    companies_to_discover.extend(HEALTHCARE_COMPANIES)
                elif list_name == "Startup Companies":
                    companies_to_discover.extend(STARTUP_COMPANIES)
            
            with st.spinner(f"Discovering {len(companies_to_discover)} companies from selected lists..."):
                try:
                    config = Config()
                    service = CompanyDiscoveryService(config=config.__dict__)
                    result = asyncio.run(discover_predefined_companies(service))
                    
                    _display_discovery_results(result)
                
                except Exception as e:
                    st.error(f"Discovery error: {str(e)}")


def _show_company_management_section():
    """Show company management interface"""
    st.subheader("📋 Company Database Management")
    st.info("View and manage discovered companies in the database.")
    
    # Load companies from database
    if st.button("🔄 Refresh Companies"):
        st.info("Company refresh functionality will be implemented with database queries")
    
    # Mock company data for demo
    st.write("### Recently Discovered Companies")
    if st.session_state.discovered_companies:
        for i, company in enumerate(st.session_state.discovered_companies):
            with st.expander(f"🏢 {company['name']} ({company['industry']})"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Domain:** {company['domain']}")
                    st.write(f"**Industry:** {company['industry']}")
                
                with col2:
                    st.write(f"**Career Page:** [{company['career_page_url']}]({company['career_page_url']})")
                    st.write(f"**Difficulty:** {company['scraping_difficulty']}")
                
                with col3:
                    if st.button("🗑️ Remove", key=f"remove_company_{i}"):
                        st.success("Company removal functionality will be implemented")
                    if st.button("✏️ Edit", key=f"edit_company_{i}"):
                        st.info("Company editing functionality will be implemented")
    else:
        st.info("No companies discovered yet. Use the Discovery tab to add companies.")


def _show_industry_analysis_section():
    """Show industry analysis interface"""
    st.subheader("📊 Industry Analysis")
    
    # Industry breakdown
    if st.session_state.discovered_companies:
        industries = {}
        for company in st.session_state.discovered_companies:
            industry = company.get('industry', 'Unknown')
            industries[industry] = industries.get(industry, 0) + 1
        
        st.write("### Industry Distribution")
        for industry, count in industries.items():
            st.write(f"**{industry}:** {count} companies")
    else:
        st.info("No companies available for analysis. Discover companies first.")


def _show_bulk_operations_section():
    """Show bulk operations interface"""
    st.subheader("⚙️ Bulk Operations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### Export Operations")
        if st.button("📊 Export to CSV"):
            st.info("CSV export functionality will be implemented")
        
        if st.button("📋 Export to JSON"):
            st.info("JSON export functionality will be implemented")
    
    with col2:
        st.write("### Maintenance Operations")
        if st.button("🔄 Update All Career Pages"):
            st.info("Bulk update functionality will be implemented")
        
        if st.button("🧹 Clean Invalid Entries"):
            st.info("Cleanup functionality will be implemented")


async def _discover_companies(company_list: List[str]) -> dict:
    """Discover companies using the discovery service"""
    try:
        config = Config()
        service = CompanyDiscoveryService(config=config.__dict__)
        
        result = await service.discover_company_career_pages(company_list)
        
        # Add discovered companies to session state
        if result.get("success") and result.get("discovered_companies"):
            st.session_state.discovered_companies.extend(result["discovered_companies"])
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Discovery failed: {str(e)}",
            "companies_discovered": 0,
            "companies_failed": len(company_list)
        }


def _display_discovery_results(result: dict):
    """Display discovery results in a nice format"""
    if result.get("success"):
        discovered_count = result.get("companies_discovered", 0)
        failed_count = result.get("companies_failed", 0)
        
        st.success(f"🎉 **Discovery Complete!** {discovered_count} companies discovered, {failed_count} failed")
        
        # Show metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("✅ Discovered", discovered_count)
        
        with col2:
            st.metric("❌ Failed", failed_count)
        
        with col3:
            total = discovered_count + failed_count
            success_rate = (discovered_count / total * 100) if total > 0 else 0
            st.metric("📊 Success Rate", f"{success_rate:.1f}%")
        
        # Show discovered companies
        discovered_companies = result.get("discovered_companies", [])
        if discovered_companies:
            with st.expander("📋 Discovered Companies", expanded=True):
                for company in discovered_companies:
                    st.write(f"• **{company['name']}** ({company['industry']}) - [{company['career_page_url']}]({company['career_page_url']})")
        
        # Show failed companies
        failed_companies = result.get("failed_companies", [])
        if failed_companies:
            with st.expander("❌ Failed Companies"):
                for company in failed_companies:
                    st.write(f"• {company}")
    else:
        st.error(f"❌ Discovery failed: {result.get('message', 'Unknown error')}")


if __name__ == "__main__":
    show_company_management()