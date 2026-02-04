"""
Multi-state grant source expansion.

Adds monitoring for additional states beyond Illinois:
- Missouri
- Indiana
- Wisconsin
- Iowa
- Federal health agencies (CMS, HRSA)
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


class MissouriGrantsSource(GrantSource):
    """Missouri state grant opportunities."""
    
    URL = "https://oa.mo.gov/mogans/state-grant-notices"
    
    def __init__(self):
        super().__init__(name="Missouri State Grants", base_url=self.URL)
    
    def discover(self, filters=None):
        """Discover Missouri state grants."""
        # Implementation would scrape Missouri grant portal
        logger.info("Missouri grants - stub implementation")
        return []


class IndianaGrantsSource(GrantSource):
    """Indiana state grant opportunities."""
    
    URL = "https://www.in.gov/grants/"
    
    def __init__(self):
        super().__init__(name="Indiana State Grants", base_url=self.URL)
    
    def discover(self, filters=None):
        """Discover Indiana state grants."""
        logger.info("Indiana grants - stub implementation")
        return []


class CMSInnovationSource(GrantSource):
    """
    CMS Innovation Center funding opportunities.
    
    Highly relevant for Medicaid and health policy work.
    """
    
    URL = "https://innovation.cms.gov/innovation-models"
    
    def __init__(self):
        super().__init__(name="CMS Innovation Center", base_url=self.URL)
    
    def discover(self, filters=None):
        """Discover CMS Innovation Center opportunities."""
        try:
            from playwright.sync_api import sync_playwright
            
            opportunities = []
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                page.goto(self.URL, wait_until="networkidle")
                
                # Look for innovation model cards
                items = page.query_selector_all('.model-card, .innovation-item')
                
                for item in items:
                    try:
                        title_elem = item.query_selector('h2, h3, .model-title')
                        if not title_elem:
                            continue
                        
                        title = title_elem.inner_text().strip()
                        
                        # Filter for Medicaid/Medicare policy relevant items
                        text = item.inner_text().lower()
                        if not any(kw in text for kw in ['medicaid', 'state', 'policy', 'innovation']):
                            continue
                        
                        link_elem = item.query_selector('a')
                        url = link_elem.get_attribute('href') if link_elem else self.URL
                        
                        desc_elem = item.query_selector('.description, p')
                        description = desc_elem.inner_text().strip() if desc_elem else ''
                        
                        grant = GrantOpportunity(
                            id=f"CMS-{len(opportunities)+1:03d}",
                            title=title,
                            agency="CMS Innovation Center",
                            description=description,
                            eligibility="See opportunity for eligibility",
                            url=url if url.startswith('http') else f"https://innovation.cms.gov{url}",
                            funding_source=FundingSource.OTHER,
                            raw_text=f"{title} {description} CMS Medicaid Medicare"
                        )
                        opportunities.append(grant)
                        
                    except Exception as e:
                        logger.debug(f"Error parsing CMS item: {e}")
                
                browser.close()
            
            return opportunities
            
        except Exception as e:
            logger.error(f"CMS Innovation scraping error: {e}")
            return []


class HRSASource(GrantSource):
    """
    HRSA (Health Resources and Services Administration) grants.
    
    Focus on rural health, health equity, and underserved populations.
    """
    
    URL = "https://www.hrsa.gov/grants"
    
    def __init__(self):
        super().__init__(name="HRSA Grants", base_url=self.URL)
    
    def discover(self, filters=None):
        """Discover HRSA grant opportunities."""
        try:
            from playwright.sync_api import sync_playwright
            
            opportunities = []
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                page.goto(self.URL, wait_until="networkidle")
                
                # Look for grant announcements
                items = page.query_selector_all('.grant-opportunity, .announcement')
                
                for item in items:
                    try:
                        title_elem = item.query_selector('h3 a, .title a')
                        if not title_elem:
                            continue
                        
                        title = title_elem.inner_text().strip()
                        
                        # Filter for relevant programs
                        text = item.inner_text().lower()
                        if not any(kw in text for kw in ['rural', 'health equity', 'medicaid', 
                                                         'underserved', 'primary care']):
                            continue
                        
                        url = title_elem.get_attribute('href')
                        
                        grant = GrantOpportunity(
                            id=f"HRSA-{len(opportunities)+1:03d}",
                            title=title,
                            agency="HRSA",
                            description="HRSA grant opportunity - see URL for details",
                            eligibility="See opportunity for eligibility",
                            url=url if url and url.startswith('http') else f"https://www.hrsa.gov{url}",
                            funding_source=FundingSource.OTHER,
                            raw_text=f"{title} HRSA rural health equity"
                        )
                        opportunities.append(grant)
                        
                    except Exception as e:
                        logger.debug(f"Error parsing HRSA item: {e}")
                
                browser.close()
            
            return opportunities
            
        except Exception as e:
            logger.error(f"HRSA scraping error: {e}")
            return []


def get_all_multistate_sources() -> List[GrantSource]:
    """Get all multi-state and federal health sources."""
    return [
        MissouriGrantsSource(),
        IndianaGrantsSource(),
        CMSInnovationSource(),
        HRSASource()
    ]


if __name__ == '__main__':
    # Test multi-state sources
    sources = get_all_multistate_sources()
    
    for source in sources:
        try:
            opportunities = source.discover()
            print(f"\n{source.name}: {len(opportunities)} opportunities")
        except Exception as e:
            print(f"\n{source.name}: Error - {e}")
