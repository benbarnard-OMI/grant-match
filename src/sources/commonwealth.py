"""
Commonwealth Fund Grant Scraper.

The Commonwealth Fund is a private foundation focused on improving 
health care quality and access, especially for vulnerable populations.

URL: https://www.commonwealthfund.org/grants-and-fellowships
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


class CommonwealthFundSource(GrantSource):
    """
    Scraper for Commonwealth Fund grants and fellowships.
    
    Focus areas:
    - Health policy analysis
    - Health system performance
    - Insurance coverage and access
    - Vulnerable populations
    - Health care delivery system
    - State health policy
    """
    
    FUNDING_URL = "https://www.commonwealthfund.org/grants-and-fellowships"
    
    RELEVANT_AREAS = [
        'health policy',
        'health insurance',
        'medicaid',
        'state policy',
        'health system',
        'vulnerable populations',
        'health equity',
        'health care delivery'
    ]
    
    def __init__(self):
        super().__init__(
            name="Commonwealth Fund",
            base_url="https://www.commonwealthfund.org/"
        )
    
    def discover(self, filters: Optional[Dict[str, Any]] = None) -> List[GrantOpportunity]:
        """Discover Commonwealth Fund opportunities."""
        logger.info("Discovering Commonwealth Fund opportunities...")
        
        opportunities = self._scrape_web()
        
        # Filter for relevance
        if filters and filters.get('require_relevance', True):
            opportunities = self._filter_relevant(opportunities)
        
        logger.info(f"Found {len(opportunities)} Commonwealth Fund opportunities")
        return opportunities
    
    def _scrape_web(self) -> List[GrantOpportunity]:
        """Scrape Commonwealth Fund website."""
        try:
            from playwright.sync_api import sync_playwright
            
            opportunities = []
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                page.goto(self.FUNDING_URL, wait_until="networkidle")
                
                # Look for grant/fellowship items
                # Selectors based on typical Drupal/Foundation site structure
                items = page.query_selector_all('.view-content .views-row, .grant-item, article')
                
                for item in items:
                    try:
                        title_elem = item.query_selector('h2 a, h3 a, .title a')
                        if not title_elem:
                            continue
                        
                        title = title_elem.inner_text()
                        url = title_elem.get_attribute('href')
                        
                        desc_elem = item.query_selector('.field--name-body, .description, p')
                        description = desc_elem.inner_text() if desc_elem else ''
                        
                        # Look for deadline
                        deadline_elem = item.query_selector('.deadline, .date-display-single')
                        deadline_text = deadline_elem.inner_text() if deadline_elem else None
                        deadline = self._parse_date(deadline_text)
                        
                        grant = GrantOpportunity(
                            id=f"CWF-{len(opportunities)+1:03d}",
                            title=title,
                            agency="Commonwealth Fund",
                            description=description,
                            eligibility="See opportunity for eligibility requirements",
                            deadline=deadline,
                            url=url if url and url.startswith('http') else f"https://www.commonwealthfund.org{url}",
                            funding_source=FundingSource.OTHER,
                            raw_text=f"{title} {description} Commonwealth Fund health policy"
                        )
                        opportunities.append(grant)
                        
                    except Exception as e:
                        logger.debug(f"Error parsing Commonwealth item: {e}")
                
                browser.close()
            
            return opportunities
            
        except ImportError:
            logger.warning("Playwright not available for Commonwealth scraping")
            return []
        except Exception as e:
            logger.error(f"Commonwealth scraping error: {e}")
            return []
    
    def _filter_relevant(self, opportunities: List[GrantOpportunity]) -> List[GrantOpportunity]:
        """Filter for MPART-relevant opportunities."""
        relevant = []
        
        for opp in opportunities:
            text = f"{opp.title} {opp.description}".lower()
            
            if any(keyword in text for keyword in [
                'medicaid', 'policy', 'state', 'insurance', 'coverage',
                'health system', 'delivery', 'vulnerable', 'equity',
                'health services research'
            ]):
                relevant.append(opp)
        
        return relevant
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date from various formats."""
        if not date_str:
            return None
        
        try:
            # Try common formats
            for fmt in ['%B %d, %Y', '%m/%d/%Y', '%Y-%m-%d']:
                try:
                    return datetime.strptime(date_str.strip(), fmt)
                except ValueError:
                    continue
        except:
            pass
        
        return None


if __name__ == '__main__':
    source = CommonwealthFundSource()
    opportunities = source.discover()
    
    print(f"\nFound {len(opportunities)} Commonwealth Fund opportunities\n")
    print("="*60)
    
    for opp in opportunities[:5]:
        print(f"\nTitle: {opp.title}")
        print(f"URL: {opp.url}")
        print("-"*60)
