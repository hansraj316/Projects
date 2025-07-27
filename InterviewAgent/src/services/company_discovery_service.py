"""
Company Career Page Discovery Service
Builds a database of companies and their career pages for direct job discovery
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from urllib.parse import urlparse, urljoin
import uuid
import re

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.operations import DatabaseOperations
from database.models import Company
from config import Config


class CompanyDiscoveryService:
    """
    Service to discover and manage company career pages
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        if config is None:
            config_obj = Config()
            self.config = config_obj.__dict__
        else:
            self.config = config
        self.logger = logging.getLogger("company_discovery_service")
        self.db_ops = DatabaseOperations()
        
        # Well-known company career page patterns
        self.career_page_patterns = [
            "/careers",
            "/jobs",
            "/opportunities",
            "/work-with-us",
            "/join-us",
            "/hiring",
            "/job-openings",
            "/employment"
        ]
        
        # Common career page subdomains
        self.career_subdomains = [
            "careers",
            "jobs",
            "apply",
            "hiring",
            "work",
            "join"
        ]
    
    async def discover_company_career_pages(self, company_list: List[str]) -> Dict[str, Any]:
        """
        Discover career pages for a list of companies
        
        Args:
            company_list: List of company names to discover
            
        Returns:
            Discovery results with saved companies
        """
        try:
            discovered_companies = []
            failed_discoveries = []
            
            for company_name in company_list:
                try:
                    company = await self._discover_single_company(company_name)
                    if company:
                        discovered_companies.append(company)
                        self.logger.info(f"Discovered career page for {company_name}")
                    else:
                        failed_discoveries.append(company_name)
                        self.logger.warning(f"Failed to discover career page for {company_name}")
                        
                except Exception as e:
                    self.logger.error(f"Error discovering {company_name}: {e}")
                    failed_discoveries.append(company_name)
            
            return {
                "success": True,
                "companies_discovered": len(discovered_companies),
                "companies_failed": len(failed_discoveries),
                "discovered_companies": [self._company_to_dict(c) for c in discovered_companies],
                "failed_companies": failed_discoveries,
                "message": f"Discovered {len(discovered_companies)} companies, {len(failed_discoveries)} failed"
            }
            
        except Exception as e:
            self.logger.error(f"Company discovery failed: {e}")
            return {
                "success": False,
                "message": f"Company discovery failed: {str(e)}",
                "companies_discovered": 0,
                "companies_failed": len(company_list)
            }
    
    async def _discover_single_company(self, company_name: str) -> Optional[Company]:
        """
        Discover career page for a single company
        
        Args:
            company_name: Name of the company
            
        Returns:
            Company object if discovered successfully
        """
        try:
            # Check if company already exists
            existing_company = await self.db_ops.get_company_by_name(company_name)
            if existing_company:
                self.logger.info(f"Company {company_name} already exists in database")
                return existing_company
            
            # Generate potential domains and career page URLs
            potential_domains = self._generate_potential_domains(company_name)
            career_page_url = None
            working_domain = None
            
            for domain in potential_domains:
                career_url = await self._find_career_page(domain)
                if career_url:
                    career_page_url = career_url
                    working_domain = domain
                    break
            
            if not career_page_url:
                # Use fallback approach
                working_domain = self._generate_primary_domain(company_name)
                career_page_url = f"https://careers.{working_domain}"
            
            # Create company record
            company = Company(
                id=str(uuid.uuid4()),
                name=company_name.strip(),
                domain=working_domain,
                career_page_url=career_page_url,
                industry=self._guess_industry(company_name),
                website_url=f"https://{working_domain}",
                is_active=True,
                last_scraped=None,
                jobs_found_count=0,
                scraping_difficulty=self._assess_scraping_difficulty(company_name),
                scraping_notes=f"Auto-discovered career page for {company_name}",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Save to database
            success = await self.db_ops.insert_company(company)
            if success:
                return company
            else:
                self.logger.error(f"Failed to save company {company_name} to database")
                return None
                
        except Exception as e:
            self.logger.error(f"Error discovering company {company_name}: {e}")
            return None
    
    def _generate_potential_domains(self, company_name: str) -> List[str]:
        """Generate potential domain names for a company"""
        # Clean company name
        clean_name = self._clean_company_name(company_name)
        
        domains = []
        
        # Common domain patterns
        domains.extend([
            f"{clean_name}.com",
            f"{clean_name}.io",
            f"{clean_name}.org",
            f"{clean_name}.net"
        ])
        
        # Handle multi-word companies
        words = clean_name.split()
        if len(words) > 1:
            # First word only
            domains.append(f"{words[0]}.com")
            # Abbreviation
            abbrev = "".join(word[0] for word in words)
            domains.append(f"{abbrev}.com")
            # With hyphens
            domains.append(f"{'-'.join(words)}.com")
        
        # Handle special company name patterns
        if "technologies" in company_name.lower():
            tech_name = clean_name.replace("technologies", "tech")
            domains.append(f"{tech_name}.com")
        
        if "corporation" in company_name.lower() or "corp" in company_name.lower():
            corp_name = clean_name.replace("corporation", "").replace("corp", "").strip()
            domains.append(f"{corp_name}.com")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_domains = []
        for domain in domains:
            if domain not in seen:
                seen.add(domain)
                unique_domains.append(domain)
        
        return unique_domains
    
    def _clean_company_name(self, company_name: str) -> str:
        """Clean company name for domain generation"""
        # Convert to lowercase
        clean = company_name.lower()
        
        # Remove common company suffixes
        suffixes = [
            "inc", "inc.", "incorporated", "corporation", "corp", "corp.", 
            "llc", "ltd", "ltd.", "limited", "company", "co", "co.",
            "technologies", "tech", "systems", "solutions", "group",
            "international", "intl", "global", "worldwide"
        ]
        
        for suffix in suffixes:
            clean = re.sub(rf'\b{suffix}\b', '', clean)
        
        # Remove special characters and extra spaces
        clean = re.sub(r'[^a-z0-9\s]', '', clean)
        clean = re.sub(r'\s+', '', clean)
        
        return clean.strip()
    
    def _generate_primary_domain(self, company_name: str) -> str:
        """Generate the most likely primary domain for a company"""
        clean_name = self._clean_company_name(company_name)
        return f"{clean_name}.com"
    
    async def _find_career_page(self, domain: str) -> Optional[str]:
        """
        Find the career page URL for a domain
        
        Args:
            domain: Domain to check
            
        Returns:
            Career page URL if found
        """
        # In a real implementation, this would make HTTP requests
        # For now, we'll use pattern-based URL generation
        
        try:
            # Try common career page patterns
            base_url = f"https://{domain}"
            
            # Check subdomain approach first
            for subdomain in self.career_subdomains:
                career_url = f"https://{subdomain}.{domain}"
                # In real implementation: if await self._url_exists(career_url):
                #     return career_url
            
            # Check path-based approach
            for pattern in self.career_page_patterns:
                career_url = urljoin(base_url, pattern)
                # In real implementation: if await self._url_exists(career_url):
                #     return career_url
            
            # Return most common pattern as fallback
            return f"https://careers.{domain}"
            
        except Exception as e:
            self.logger.error(f"Error finding career page for {domain}: {e}")
            return None
    
    def _guess_industry(self, company_name: str) -> str:
        """Guess industry from company name"""
        name_lower = company_name.lower()
        
        # Technology keywords
        tech_keywords = [
            "tech", "software", "systems", "solutions", "data", "cloud", "ai",
            "microsoft", "google", "amazon", "apple", "meta", "netflix", "uber",
            "startup", "platform", "digital", "cyber", "automation"
        ]
        
        # Financial keywords
        finance_keywords = [
            "bank", "financial", "capital", "investment", "trading", "fintech",
            "insurance", "credit", "fund", "securities", "advisor"
        ]
        
        # Healthcare keywords
        health_keywords = [
            "health", "medical", "pharma", "biotech", "hospital", "clinic",
            "healthcare", "medicine", "therapy", "diagnostic"
        ]
        
        # Manufacturing keywords
        manufacturing_keywords = [
            "manufacturing", "industrial", "automotive", "aerospace", "energy",
            "construction", "materials", "chemical", "oil", "gas"
        ]
        
        # Retail/Consumer keywords
        retail_keywords = [
            "retail", "consumer", "fashion", "food", "beverage", "restaurant",
            "store", "shop", "brand", "merchandise"
        ]
        
        if any(keyword in name_lower for keyword in tech_keywords):
            return "Technology"
        elif any(keyword in name_lower for keyword in finance_keywords):
            return "Financial Services"
        elif any(keyword in name_lower for keyword in health_keywords):
            return "Healthcare"
        elif any(keyword in name_lower for keyword in manufacturing_keywords):
            return "Manufacturing"
        elif any(keyword in name_lower for keyword in retail_keywords):
            return "Retail"
        else:
            return "Other"
    
    def _assess_scraping_difficulty(self, company_name: str) -> str:
        """Assess likely scraping difficulty for the company"""
        name_lower = company_name.lower()
        
        # Large tech companies typically have more sophisticated anti-scraping
        difficult_companies = [
            "google", "amazon", "microsoft", "apple", "meta", "facebook",
            "netflix", "uber", "airbnb", "tesla", "salesforce"
        ]
        
        # Financial companies often have strict security
        financial_companies = [
            "bank", "goldman", "morgan", "jpmorgan", "wells fargo", "citi"
        ]
        
        if any(company in name_lower for company in difficult_companies):
            return "hard"
        elif any(company in name_lower for company in financial_companies):
            return "hard"
        elif any(keyword in name_lower for keyword in ["startup", "small", "local"]):
            return "easy"
        else:
            return "medium"
    
    def _company_to_dict(self, company: Company) -> Dict[str, Any]:
        """Convert Company object to dictionary"""
        return {
            "id": company.id,
            "name": company.name,
            "domain": company.domain,
            "career_page_url": company.career_page_url,
            "industry": company.industry,
            "website_url": company.website_url,
            "scraping_difficulty": company.scraping_difficulty,
            "created_at": company.created_at.isoformat() if company.created_at else None
        }
    
    async def get_companies_by_industry(self, industry: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get companies filtered by industry
        
        Args:
            industry: Industry to filter by
            limit: Maximum number of companies to return
            
        Returns:
            List of companies in the industry
        """
        try:
            # In a real implementation, this would query the database
            # For now, return empty list
            return []
        except Exception as e:
            self.logger.error(f"Error getting companies by industry: {e}")
            return []
    
    async def search_companies_by_domain(self, domain_pattern: str) -> List[Dict[str, Any]]:
        """
        Search companies by domain pattern
        
        Args:
            domain_pattern: Pattern to search for in domains
            
        Returns:
            List of matching companies
        """
        try:
            # In a real implementation, this would query the database
            # For now, return empty list
            return []
        except Exception as e:
            self.logger.error(f"Error searching companies by domain: {e}")
            return []


# Pre-defined lists of companies for quick discovery
TECH_COMPANIES = [
    "Microsoft", "Google", "Amazon", "Apple", "Meta", "Netflix", "Uber",
    "Airbnb", "Stripe", "Salesforce", "Adobe", "Tesla", "SpaceX", "OpenAI",
    "Anthropic", "Databricks", "Snowflake", "Palantir", "Coinbase", "Robinhood"
]

FINANCE_COMPANIES = [
    "JPMorgan Chase", "Goldman Sachs", "Morgan Stanley", "Bank of America",
    "Wells Fargo", "Citigroup", "American Express", "BlackRock", "Vanguard",
    "Fidelity", "Charles Schwab", "Capital One", "Visa", "Mastercard"
]

HEALTHCARE_COMPANIES = [
    "Johnson & Johnson", "Pfizer", "Roche", "Novartis", "Merck", "AbbVie",
    "Bristol Myers Squibb", "Eli Lilly", "Amgen", "Gilead Sciences",
    "Moderna", "Regeneron", "Biogen", "Vertex Pharmaceuticals"
]

STARTUP_COMPANIES = [
    "Figma", "Notion", "Discord", "Slack", "Zoom", "Canva", "Miro",
    "Linear", "Vercel", "Supabase", "PlanetScale", "Railway", "Render"
]


async def discover_predefined_companies(service: CompanyDiscoveryService) -> Dict[str, Any]:
    """
    Discover career pages for predefined company lists
    
    Args:
        service: CompanyDiscoveryService instance
        
    Returns:
        Discovery results
    """
    all_companies = TECH_COMPANIES + FINANCE_COMPANIES + HEALTHCARE_COMPANIES + STARTUP_COMPANIES
    
    # Discover companies in batches to avoid overwhelming
    batch_size = 10
    total_discovered = 0
    total_failed = 0
    
    for i in range(0, len(all_companies), batch_size):
        batch = all_companies[i:i + batch_size]
        result = await service.discover_company_career_pages(batch)
        
        total_discovered += result.get("companies_discovered", 0)
        total_failed += result.get("companies_failed", 0)
        
        # Add delay between batches to be respectful
        await asyncio.sleep(1)
    
    return {
        "success": True,
        "total_companies": len(all_companies),
        "companies_discovered": total_discovered,
        "companies_failed": total_failed,
        "message": f"Batch discovery complete: {total_discovered} discovered, {total_failed} failed"
    }