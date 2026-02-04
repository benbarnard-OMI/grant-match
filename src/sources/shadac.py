"""
SHADAC (State Health Access Data Assistance Center) Scraper.

SHADAC is a multidisciplinary health policy research center at the 
University of Minnesota, focused on state health policy and data.

URL: https://www.shadac.org/about/employment-and-rfps
"""

import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from scout_il import GrantSource, GrantOpportunity, FundingSource


logger = logging.getLogger(__name__)


class SHADACSource(GrantSource):
    """
    Scraper for SHADAC RFPs and opportunities.
    
    SHADAC focus areas (highly aligned with MPART):
    - State health policy
    - Medicaid/CHIP research
    - Health insurance coverage
    - State health data
    - Health equity
    - Rural health
    """
    
    FUNDING_URL = "https://www.shadac.org/about/employment-and-rfps"
    
    RELEVANT_AREAS = [
        'state health policy',
        'medicaid',
        'health insurance',
        'health data',
        'rural health',
        'health equity',
        'CHIP'
    ]
    
    def __init__(self):
        super().__init__(
            name="SHADAC",
            base_url="https://www.shadac.org/"
        )
    
    def discover(self, filters: Optional[Dict[str, Any]] = None) -> List[GrantOpportunity]:
        """Discover SHADAC opportunities."""
        logger.info("Discovering SHADAC opportunities...")
        
        opportunities = self._scrape_web()
        
        if filters and filters.get('require_relevance', True):
            opportunities = self._filter_relevant(opportunities)
        
        logger.info(f"Found {len(opportunities)} SHADAC opportunities")
        return opportunities
    
    def _scrape_web(self) -> List[GrantOpportunity]:
        """Scrape SHADAC employment and RFPs page."""
        try:
            from playwright.sync_api import sync_playwright
            
            opportunities = []
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                page.goto(self.FUNDING_URL, wait_until="networkidle")
                
                # Look for RFP/opportunity items
                # SHADAC typically uses standard content blocks
                items = page.query_selector_all('.rfp-item, .opportunity, .node--type-rfp')
                
                for item in items:
                    try:
                        title_elem = item.query_selector('h2 a, h3 a, .title')
                        if not title_elem:
                            continue
                        
                        title = title_elem.inner_text().strip()
                        url = title_elem.get_attribute('href')
                        
                        # Get description/summary
                        desc_elem = item.query_selector('.description, .field--name-body, p')
                        description = desc_elem.inner_text().strip() if desc_elem else ''
                        
                        # Look for deadline
                        deadline_elem = item.query_selector('.deadline, .field--name-field-date, .date')
                        deadline_text = deadline_elem.inner_text() if deadline_elem else None
                        deadline = self._parse_date(deadline_text)
                        
                        grant = GrantOpportunity(
                            id=f"SHADAC-{len(opportunities)+1:03d}",
                            title=title,
                            agency="SHADAC (University of Minnesota)",
                            description=description,
                            eligibility="See RFP for eligibility requirements",
                            deadline=deadline,
                            url=url if url and url.startswith('http') else f"https://www.shadac.org{url}",
                            funding_source=FundingSource.OTHER,
                            raw_text=f"{title} {description} SHADAC state health policy"
                        )
                        opportunities.append(grant)
                        
                    except Exception as e:
                        logger.debug(f"Error parsing SHADAC item: {e}")
                
                browser.close()
            
            return opportunities
            
        except ImportError:
            logger.warning("Playwright not available for SHADAC scraping")
            return []
        except Exception as e:
            logger.error(f"SHADAC scraping error: {e}")
            return []
    
    def _filter_relevant(self, opportunities: List[GrantOpportunity]) -> List[GrantOpportunity]:
        """Filter for state health policy relevance."""
        # SHADAC is highly relevant to MPART's work, so most opportunities
        # are likely relevant. Still filter for specific keywords.
        relevant = []
        
        for opp in opportunities:
            text = f"{opp.title} {opp.description}".lower()
            
            if any(keyword in text for keyword in [
                'medicaid', 'state', 'policy', 'health insurance',
                'coverage', 'health data', 'rural', 'equity'
            ]):
                relevant.append(opp)
        
        # If filtering is too aggressive, return all
        return relevant if relevant else opportunities
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string."""
        if not date_str:
            return None
        
        try:
            for fmt in ['%B %d, %Y', '%m/%d/%Y', '%Y-%m-%d']:
                try:
                    return datetime.strptime(date_str.strip(), fmt)
                except ValueError:
                    continue
        except:
            pass
        
        return None


if __name__ == '__main__':
    source = SHADACSource()
    opportunities = source.discover()
    
    print(f"\nFound {len(opportunities)} SHADAC opportunities\n")
    print("="*60)
    
    for opp in opportunities[:5]:
        print(f"\nTitle: {opp.title}")
        print(f"Agency: {opp.agency}")
        print(f"URL: {opp.url}")
        print("-"*60)
