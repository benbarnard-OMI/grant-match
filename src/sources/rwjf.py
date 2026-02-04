"""
Robert Wood Johnson Foundation (RWJF) Grant Scraper.

RWJF is one of the largest health philanthropy foundations in the US,
focusing on health equity, health systems, and public health research.

URL: https://www.rwjf.org/en/grants/funding-opportunities.html
"""

import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from scout_il import GrantSource, GrantOpportunity, FundingSource, GrantStatus


logger = logging.getLogger(__name__)


class RWJFSource(GrantSource):
    """
    Scraper for Robert Wood Johnson Foundation funding opportunities.
    
    Focus areas relevant to MPART:
    - Health equity and Medicaid
    - Health policy research
    - State health policy
    - Rural health
    - Health systems research
    """
    
    FUNDING_URL = "https://www.rwjf.org/en/grants/funding-opportunities.html"
    API_URL = "https://www.rwjf.org/content/dam/foundation/api/grants/funding-opportunities.json"
    
    # MPART-relevant RWJF program areas
    RELEVANT_PROGRAMS = [
        'health equity',
        'medicaid',
        'health policy',
        'state health policy',
        'rural health',
        'health systems',
        'public health',
        'health care quality',
        'social determinants of health'
    ]
    
    def __init__(self):
        super().__init__(
            name="Robert Wood Johnson Foundation",
            base_url="https://www.rwjf.org/"
        )
        self.cache_file = Path("data/rwjf_opportunities.json")
    
    def discover(self, filters: Optional[Dict[str, Any]] = None) -> List[GrantOpportunity]:
        """
        Discover RWJF funding opportunities.
        
        Strategy:
        1. Try API endpoint first (if available)
        2. Fall back to web scraping
        3. Cache results for performance
        """
        logger.info("Discovering RWJF opportunities...")
        
        opportunities = []
        
        # Try API first
        api_data = self._fetch_api()
        if api_data:
            opportunities = self._parse_api_response(api_data)
        else:
            # Fall back to web scraping
            opportunities = self._scrape_web()
        
        # Filter for relevance
        if filters and filters.get('require_relevance', True):
            opportunities = self._filter_relevant(opportunities)
        
        logger.info(f"Found {len(opportunities)} RWJF opportunities")
        return opportunities
    
    def _fetch_api(self) -> Optional[Dict]:
        """Try to fetch from RWJF API."""
        try:
            import requests
            response = requests.get(self.API_URL, timeout=30)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.debug(f"RWJF API fetch failed: {e}")
        return None
    
    def _parse_api_response(self, data: Dict) -> List[GrantOpportunity]:
        """Parse RWJF API response."""
        opportunities = []
        
        for item in data.get('opportunities', []):
            try:
                grant = GrantOpportunity(
                    id=f"RWJF-{item.get('id', 'unknown')}",
                    title=item.get('title', 'Untitled'),
                    agency="Robert Wood Johnson Foundation",
                    description=item.get('description', ''),
                    eligibility=item.get('eligibility', 'See opportunity for details'),
                    award_amount=item.get('awardAmount'),
                    deadline=self._parse_date(item.get('deadline')),
                    url=item.get('url', self.FUNDING_URL),
                    funding_source=FundingSource.OTHER,
                    raw_text=f"{item.get('title', '')} {item.get('description', '')} "
                            f"{item.get('programArea', '')} RWJF Robert Wood Johnson Foundation"
                )
                opportunities.append(grant)
            except Exception as e:
                logger.warning(f"Error parsing RWJF item: {e}")
        
        return opportunities
    
    def _scrape_web(self) -> List[GrantOpportunity]:
        """Scrape RWJF website for opportunities."""
        try:
            from playwright.sync_api import sync_playwright
            
            opportunities = []
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                page.goto(self.FUNDING_URL, wait_until="networkidle")
                
                # Look for opportunity cards/items
                # Note: This selector may need adjustment based on actual site structure
                items = page.query_selector_all('.opportunity-card, .grant-item, [data-opportunity]')
                
                for item in items:
                    try:
                        title = item.query_selector('h2, h3, .title')
                        title_text = title.inner_text() if title else 'Untitled'
                        
                        desc = item.query_selector('.description, p')
                        desc_text = desc.inner_text() if desc else ''
                        
                        link = item.query_selector('a')
                        url = link.get_attribute('href') if link else self.FUNDING_URL
                        
                        grant = GrantOpportunity(
                            id=f"RWJF-{len(opportunities)+1:03d}",
                            title=title_text,
                            agency="Robert Wood Johnson Foundation",
                            description=desc_text,
                            eligibility="See opportunity for eligibility",
                            url=url if url.startswith('http') else f"https://www.rwjf.org{url}",
                            funding_source=FundingSource.OTHER,
                            raw_text=f"{title_text} {desc_text} RWJF Robert Wood Johnson Foundation"
                        )
                        opportunities.append(grant)
                    except Exception as e:
                        logger.warning(f"Error parsing RWJF item: {e}")
                
                browser.close()
            
            return opportunities
            
        except ImportError:
            logger.warning("Playwright not available for RWJF scraping")
            return []
        except Exception as e:
            logger.error(f"RWJF scraping error: {e}")
            return []
    
    def _filter_relevant(self, opportunities: List[GrantOpportunity]) -> List[GrantOpportunity]:
        """Filter opportunities for MPART relevance."""
        relevant = []
        
        for opp in opportunities:
            text = f"{opp.title} {opp.description} {opp.raw_text}".lower()
            
            # Check for relevant keywords
            if any(keyword in text for keyword in [
                'medicaid', 'policy', 'state', 'rural', 'health equity',
                'health services research', 'health policy', 'public health',
                'health systems', 'social determinants'
            ]):
                relevant.append(opp)
        
        return relevant
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string."""
        if not date_str:
            return None
        
        formats = [
            '%Y-%m-%d',
            '%B %d, %Y',
            '%m/%d/%Y',
            '%Y-%m-%dT%H:%M:%S'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None


if __name__ == '__main__':
    # Test the RWJF source
    source = RWJFSource()
    opportunities = source.discover()
    
    print(f"\nFound {len(opportunities)} RWJF opportunities\n")
    print("="*60)
    
    for opp in opportunities[:5]:
        print(f"\nTitle: {opp.title}")
        print(f"URL: {opp.url}")
        print(f"Description: {opp.description[:150]}...")
        print("-"*60)
