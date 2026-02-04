"""
AcademyHealth Grant and Funding Opportunity Scraper.

AcademyHealth is a leading professional organization for health services
researchers, offering various funding opportunities and fellowships.

URL: https://www.academyhealth.org/career/funding-opportunities
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


class AcademyHealthSource(GrantSource):
    """
    Scraper for AcademyHealth funding opportunities.
    
    Relevant program areas:
    - Health services research
    - Health policy
    - Dissemination and implementation research
    - Health equity
    - Medicaid/CHIP research
    - State health policy
    """
    
    FUNDING_URL = "https://www.academyhealth.org/career/funding-opportunities"
    
    RELEVANT_PROGRAMS = [
        'health services research',
        'health policy',
        'implementation research',
        'medicaid',
        'state health policy',
        'health equity',
        'dissemination'
    ]
    
    def __init__(self):
        super().__init__(
            name="AcademyHealth",
            base_url="https://www.academyhealth.org/"
        )
    
    def discover(self, filters: Optional[Dict[str, Any]] = None) -> List[GrantOpportunity]:
        """Discover AcademyHealth opportunities."""
        logger.info("Discovering AcademyHealth opportunities...")
        
        opportunities = self._scrape_web()
        
        if filters and filters.get('require_relevance', True):
            opportunities = self._filter_relevant(opportunities)
        
        logger.info(f"Found {len(opportunities)} AcademyHealth opportunities")
        return opportunities
    
    def _scrape_web(self) -> List[GrantOpportunity]:
        """Scrape AcademyHealth funding page."""
        try:
            from playwright.sync_api import sync_playwright
            
            opportunities = []
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                page.goto(self.FUNDING_URL, wait_until="networkidle")
                
                # AcademyHealth uses specific content types for funding opportunities
                items = page.query_selector_all('.funding-opportunity, .grant-item, .view-funding .views-row')
                
                for item in items:
                    try:
                        title_elem = item.query_selector('h2 a, h3 a, .title')
                        if not title_elem:
                            continue
                        
                        title = title_elem.inner_text().strip()
                        url = title_elem.get_attribute('href') or self.FUNDING_URL
                        
                        # Get description
                        desc_elem = item.query_selector('.description, .field--name-body, .summary')
                        description = desc_elem.inner_text().strip() if desc_elem else ''
                        
                        # Look for deadline information
                        deadline_elem = item.query_selector('.deadline, .field--name-field-deadline, .date')
                        deadline_text = deadline_elem.inner_text() if deadline_elem else None
                        deadline = self._parse_date(deadline_text)
                        
                        # Look for award amount
                        award_elem = item.query_selector('.award-amount, .funding-amount')
                        award_amount = award_elem.inner_text() if award_elem else None
                        
                        grant = GrantOpportunity(
                            id=f"AH-{len(opportunities)+1:03d}",
                            title=title,
                            agency="AcademyHealth",
                            description=description,
                            eligibility="See opportunity for eligibility",
                            award_amount=award_amount,
                            deadline=deadline,
                            url=url if url.startswith('http') else f"https://www.academyhealth.org{url}",
                            funding_source=FundingSource.OTHER,
                            raw_text=f"{title} {description} AcademyHealth health services research"
                        )
                        opportunities.append(grant)
                        
                    except Exception as e:
                        logger.debug(f"Error parsing AcademyHealth item: {e}")
                
                browser.close()
            
            return opportunities
            
        except ImportError:
            logger.warning("Playwright not available for AcademyHealth scraping")
            return []
        except Exception as e:
            logger.error(f"AcademyHealth scraping error: {e}")
            return []
    
    def _filter_relevant(self, opportunities: List[GrantOpportunity]) -> List[GrantOpportunity]:
        """Filter for health policy and services research."""
        relevant = []
        
        for opp in opportunities:
            text = f"{opp.title} {opp.description}".lower()
            
            if any(keyword in text for keyword in [
                'medicaid', 'policy', 'state', 'health services',
                'health policy', 'implementation', 'dissemination',
                'health equity', 'health systems'
            ]):
                relevant.append(opp)
        
        return relevant
    
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
    source = AcademyHealthSource()
    opportunities = source.discover()
    
    print(f"\nFound {len(opportunities)} AcademyHealth opportunities\n")
    print("="*60)
    
    for opp in opportunities[:5]:
        print(f"\nTitle: {opp.title}")
        print(f"Agency: {opp.agency}")
        print(f"URL: {opp.url}")
        print("-"*60)
