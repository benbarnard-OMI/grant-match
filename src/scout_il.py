"""
Illinois GATA (Grant Accountability and Transparency Act) Portal Scouter

This module provides live web-data ingestion for MPART @ UIS grant monitoring.
Features:
- Playwright-based scraping of Illinois GATA portal
- SAM.gov API integration for federal opportunities
- Deterministic pipeline with automated DeepResearchEngine triggers

"""

import json
import logging
import os
import re
import requests
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GrantStatus(Enum):
    """Enumeration of possible grant statuses."""
    OPEN = "open"
    CLOSED = "closed"
    UPCOMING = "upcoming"
    ARCHIVED = "archived"


class FundingSource(Enum):
    """Enumeration of funding sources."""
    ILLINOIS_GATA = "illinois_gata"
    FEDERAL_SAM_GOV = "federal_sam_gov"
    FEDERAL_GRANTS_GOV = "federal_grants_gov"
    MEDICAID_INNOVATION = "medicaid_innovation"
    NSF = "nsf"
    NIH = "nih"
    OTHER = "other"


@dataclass
class GrantOpportunity:
    """Data class representing a grant opportunity."""
    id: str
    title: str
    agency: str
    description: str
    eligibility: str
    award_amount: Optional[str] = None
    deadline: Optional[datetime] = None
    status: GrantStatus = GrantStatus.OPEN
    funding_source: FundingSource = FundingSource.OTHER
    url: str = ""
    posted_date: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    raw_text: str = ""
    keyword_score: int = 0
    passes_prefilter: bool = False
    recommended_lead: str = ""  # mercenary_policy, mercenary_data, mercenary_eval
    deep_research_triggered: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert GrantOpportunity to dictionary."""
        result = asdict(self)
        result['status'] = self.status.value
        result['funding_source'] = self.funding_source.value
        if self.deadline:
            result['deadline'] = self.deadline.isoformat()
        if self.posted_date:
            result['posted_date'] = self.posted_date.isoformat()
        return result


class GrantSource(ABC):
    """Abstract base class for grant sources."""
    
    def __init__(self, name: str, base_url: str):
        self.name = name
        self.base_url = base_url
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    @abstractmethod
    def discover(self, filters: Optional[Dict[str, Any]] = None) -> List[GrantOpportunity]:
        """Discover grant opportunities from this source."""
        pass


class GATAWebScraper(GrantSource):
    """
    Illinois GATA Web Scraper using Playwright.
    
    Scrapes live data from:
    - Program List: https://omb.illinois.gov/public/gata/csfa/ProgramList.aspx
    - Opportunity List: https://omb.illinois.gov/public/gata/csfa/OpportunityList.aspx
    """
    
    PROGRAM_LIST_URL = "https://omb.illinois.gov/public/gata/csfa/ProgramList.aspx"
    OPPORTUNITY_LIST_URL = "https://omb.illinois.gov/public/gata/csfa/OpportunityList.aspx"
    
    def __init__(self):
        super().__init__(
            name="Illinois GATA Live Scraper",
            base_url="https://omb.illinois.gov/public/gata/csfa/"
        )
        self.output_file = "data/gata_live_capture.json"
    
    def discover(self, filters: Optional[Dict[str, Any]] = None) -> List[GrantOpportunity]:
        """
        Scrape Illinois GATA portal using Playwright.
        
        Returns:
            List of GrantOpportunity objects from scraped data
        """
        self.logger.info("Starting Illinois GATA live web scraping...")
        
        try:
            from playwright.sync_api import sync_playwright
            
            opportunities = []
            scraped_data = {
                "metadata": {
                    "scraped_at": datetime.now().isoformat(),
                    "source": "Illinois GATA Portal",
                    "urls": [self.PROGRAM_LIST_URL, self.OPPORTUNITY_LIST_URL]
                },
                "programs": [],
                "opportunities": []
            }
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(user_agent="MPART-UIS-GrantBot/1.0")
                page = context.new_page()
                
                # Scrape Program List
                self.logger.info(f"Navigating to Program List: {self.PROGRAM_LIST_URL}")
                page.goto(self.PROGRAM_LIST_URL, wait_until="networkidle")
                page.wait_for_load_state("domcontentloaded")
                
                # Extract program table data
                programs = self._extract_table_data(page, "program")
                scraped_data["programs"] = programs
                self.logger.info(f"Extracted {len(programs)} programs")
                
                # Scrape Opportunity List
                self.logger.info(f"Navigating to Opportunity List: {self.OPPORTUNITY_LIST_URL}")
                page.goto(self.OPPORTUNITY_LIST_URL, wait_until="networkidle")
                page.wait_for_load_state("domcontentloaded")
                
                # Extract opportunity table data
                opportunities_data = self._extract_table_data(page, "opportunity")
                scraped_data["opportunities"] = opportunities_data
                self.logger.info(f"Extracted {len(opportunities_data)} opportunities")
                
                browser.close()
            
            # Save scraped data
            os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
            with open(self.output_file, 'w') as f:
                json.dump(scraped_data, f, indent=2)
            self.logger.info(f"Saved scraped data to {self.output_file}")
            
            # Convert to GrantOpportunity objects
            opportunities = self._convert_to_grants(scraped_data)
            return opportunities
            
        except ImportError:
            self.logger.error("Playwright not installed. Run: pip install playwright && playwright install")
            return []
        except Exception as e:
            self.logger.error(f"Error during scraping: {e}")
            return []
    
    def _extract_table_data(self, page, list_type: str) -> List[Dict]:
        """Extract table data from GATA pages."""
        data = []
        
        try:
            # Wait for table to load
            page.wait_for_selector("table", timeout=10000)
            
            # Extract rows - GATA tables typically have these columns:
            # Program Title, Agency, Application Date Range, Status, etc.
            rows = page.query_selector_all("table tr")
            
            headers = []
            for i, row in enumerate(rows):
                cells = row.query_selector_all("td, th")
                
                if i == 0:
                    # Header row
                    headers = [cell.inner_text().strip() for cell in cells]
                else:
                    # Data row
                    row_data = {}
                    for j, cell in enumerate(cells):
                        if j < len(headers):
                            row_data[headers[j]] = cell.inner_text().strip()
                    
                    if row_data:
                        # Map common column names
                        mapped = self._map_columns(row_data, list_type)
                        if mapped.get("title"):  # Only add if has title
                            data.append(mapped)
            
        except Exception as e:
            self.logger.warning(f"Error extracting {list_type} table: {e}")
        
        return data
    
    def _map_columns(self, row_data: Dict, list_type: str) -> Dict:
        """Map GATA column names to standard fields."""
        mapped = {
            "source_type": list_type,
            "raw_data": row_data
        }
        
        # Map common column variations
        for key, value in row_data.items():
            key_lower = key.lower()
            
            if any(term in key_lower for term in ["program", "title", "name", "opportunity"]):
                mapped["title"] = value
            elif any(term in key_lower for term in ["agency", "department", "sponsor"]):
                mapped["agency"] = value
            elif any(term in key_lower for term in ["date", "deadline", "application", "range"]):
                mapped["date_range"] = value
                # Try to parse deadline
                mapped["deadline"] = self._parse_date(value)
            elif any(term in key_lower for term in ["status", "state"]):
                mapped["status"] = value
            elif any(term in key_lower for term in ["description", "summary", "details"]):
                mapped["description"] = value
            elif any(term in key_lower for term in ["eligibility", "eligible", "who can apply"]):
                mapped["eligibility"] = value
            elif any(term in key_lower for term in ["amount", "funding", "award"]):
                mapped["award_amount"] = value
        
        # Set defaults
        mapped.setdefault("title", "")
        mapped.setdefault("agency", "Illinois State Agency")
        mapped.setdefault("description", "Illinois GATA opportunity")
        mapped.setdefault("eligibility", "See opportunity details")
        
        return mapped
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse date from various formats."""
        if not date_str:
            return None
        
        # Common date patterns
        patterns = [
            r'(\d{1,2}/\d{1,2}/\d{4})',  # MM/DD/YYYY
            r'(\d{1,2}-\d{1,2}-\d{4})',  # MM-DD-YYYY
            r'(\w+ \d{1,2},? \d{4})',    # Month DD, YYYY
        ]
        
        for pattern in patterns:
            match = re.search(pattern, date_str)
            if match:
                return match.group(1)
        return None
    
    def _convert_to_grants(self, scraped_data: Dict) -> List[GrantOpportunity]:
        """Convert scraped data to GrantOpportunity objects."""
        grants = []
        
        for opp in scraped_data.get("opportunities", []):
            grant = GrantOpportunity(
                id=f"GATA-OPP-{len(grants)+1:03d}",
                title=opp.get("title", "Untitled Opportunity"),
                agency=opp.get("agency", "Illinois GATA"),
                description=opp.get("description", opp.get("raw_data", {})),
                eligibility=opp.get("eligibility", "See opportunity for eligibility requirements"),
                award_amount=opp.get("award_amount"),
                url=self.OPPORTUNITY_LIST_URL,
                funding_source=FundingSource.ILLINOIS_GATA,
                raw_text=f"{opp.get('title', '')} {opp.get('agency', '')} {opp.get('description', '')} Illinois".strip()
            )
            grants.append(grant)
        
        for prog in scraped_data.get("programs", []):
            grant = GrantOpportunity(
                id=f"GATA-PROG-{len(grants)+1:03d}",
                title=prog.get("title", "Untitled Program"),
                agency=prog.get("agency", "Illinois GATA"),
                description=prog.get("description", prog.get("raw_data", {})),
                eligibility=prog.get("eligibility", "See program for eligibility requirements"),
                award_amount=prog.get("award_amount"),
                url=self.PROGRAM_LIST_URL,
                funding_source=FundingSource.ILLINOIS_GATA,
                raw_text=f"{prog.get('title', '')} {prog.get('agency', '')} {prog.get('description', '')} Illinois".strip()
            )
            grants.append(grant)
        
        self.logger.info(f"Converted {len(grants)} scraped items to GrantOpportunity objects")
        return grants


class SAMSource(GrantSource):
    """
    SAM.gov (System for Award Management) API Source.
    
    Uses DATA_GOV_API_KEY from environment for authentication.
    Searches for federal opportunities matching MPART pillars.
    """
    
    API_BASE_URL = "https://api.sam.gov/opportunities/v1/search"
    
    # MPART Research Pillars for SAM search
    MPART_KEYWORDS = [
        "Medicaid",
        "State Policy",
        "Regulatory Monitoring",
        "Healthcare Infrastructure",
        "1115 Waiver",
        "Health Policy",
        "Rural Health"
    ]
    
    def __init__(self):
        super().__init__(
            name="SAM.gov API",
            base_url="https://sam.gov/"
        )
        self.api_key = os.getenv("DATA_GOV_API_KEY")
        if not self.api_key:
            self.logger.warning("DATA_GOV_API_KEY not set in environment!")
    
    def discover(self, filters: Optional[Dict[str, Any]] = None) -> List[GrantOpportunity]:
        """
        Discover federal opportunities from SAM.gov API.
        
        Returns:
            List of GrantOpportunity objects from SAM API
        """
        if not self.api_key:
            self.logger.error("Cannot query SAM.gov: DATA_GOV_API_KEY not set")
            return []
        
        self.logger.info("Querying SAM.gov API for MPART-relevant opportunities...")
        
        opportunities = []
        
        # Search for each MPART keyword
        for keyword in self.MPART_KEYWORDS:
            try:
                params = {
                    "api_key": self.api_key,
                    "q": keyword,
                    "limit": 25,
                    "sort": "relevance",
                    "order": "desc"
                }
                
                self.logger.info(f"Searching SAM.gov for: '{keyword}'")
                response = requests.get(self.API_BASE_URL, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    hits = data.get("opportunitiesData", [])
                    self.logger.info(f"Found {len(hits)} results for '{keyword}'")
                    
                    for hit in hits:
                        grant = self._convert_sam_hit(hit)
                        if grant:
                            opportunities.append(grant)
                else:
                    self.logger.warning(f"SAM API returned status {response.status_code}: {response.text[:200]}")
                    
            except Exception as e:
                self.logger.error(f"Error querying SAM.gov for '{keyword}': {e}")
        
        # Deduplicate by notice ID
        seen_ids = set()
        unique_opps = []
        for opp in opportunities:
            if opp.id not in seen_ids:
                seen_ids.add(opp.id)
                unique_opps.append(opp)
        
        self.logger.info(f"Returning {len(unique_opps)} unique opportunities from SAM.gov")
        return unique_opps
    
    def _convert_sam_hit(self, hit: Dict) -> Optional[GrantOpportunity]:
        """Convert SAM API hit to GrantOpportunity."""
        try:
            notice_id = hit.get("noticeId", "")
            title = hit.get("title", "Untitled")
            
            # Parse dates
            deadline_str = hit.get("responseDeadLine", "")
            deadline = None
            if deadline_str:
                try:
                    deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
                except:
                    pass
            
            # Build description
            description_parts = [
                hit.get("description", ""),
                hit.get("uiLink", ""),
            ]
            description = " ".join(filter(None, description_parts))
            
            # Determine eligibility from type
            opp_type = hit.get("type", "").lower()
            eligibility = "Federal contractors, educational institutions, nonprofits"
            if "grant" in opp_type:
                eligibility = "Higher Education Institutions, Nonprofits, Research Organizations"
            
            return GrantOpportunity(
                id=f"SAM-{notice_id}",
                title=title,
                agency=hit.get("department", "Federal Agency"),
                description=description or "Federal opportunity from SAM.gov",
                eligibility=eligibility,
                deadline=deadline,
                award_amount=hit.get("estimatedTotalValue"),
                url=hit.get("uiLink", "https://sam.gov"),
                funding_source=FundingSource.FEDERAL_SAM_GOV,
                raw_text=f"{title} {hit.get('department', '')} {description} Federal".strip()
            )
            
        except Exception as e:
            self.logger.warning(f"Error converting SAM hit: {e}")
            return None


class HeuristicScorer:
    """Deterministic keyword-based scorer for grant opportunities."""
    
    KEYWORD_WEIGHTS = {
        'medicaid': 35,
        'policy monitoring': 25,
        'regulatory analysis': 25,
        'rural health': 15,
        'policydelta': 20,
        'national policy tracker': 18,
        'healthcare infrastructure': 16,
        'regulatory monitoring': 15,
        '1115 waiver': 12,
        'state policy': 12,
        'multi-state': 10,
        'government evaluation': 10,
        'illinois': 8,
        'higher education': 8,
    }
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.HeuristicScorer")
    
    def score(self, grant: GrantOpportunity) -> int:
        """Calculate keyword score (0-100) for a grant opportunity."""
        text_to_analyze = " ".join([
            grant.title or "",
            grant.description or "",
            grant.eligibility or "",
            " ".join(grant.tags),
            grant.raw_text or ""
        ]).lower()
        
        score = 0
        for keyword, weight in self.KEYWORD_WEIGHTS.items():
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            matches = len(re.findall(pattern, text_to_analyze))
            if matches > 0:
                score += min(matches * weight, weight * 2)
        
        return min(int(score), 100)


class GrantDiscoveryPipeline:
    """Pipeline for discovering grants from multiple sources."""
    
    def __init__(self):
        self.sources: List[GrantSource] = []
        self.scorer = HeuristicScorer()
        self.logger = logging.getLogger(f"{__name__}.Pipeline")
    
    def register_source(self, source: GrantSource) -> None:
        """Register a new grant source."""
        self.sources.append(source)
        self.logger.info(f"Registered source: {source.name}")
    
    def pre_filter(self, grant: GrantOpportunity, reference_date: Optional[datetime] = None) -> Tuple[bool, str]:
        """Deterministic pre-filter to discard irrelevant grants."""
        if reference_date is None:
            reference_date = datetime.now()
        
        # Check 1: Close Date is in the past
        if grant.deadline and grant.deadline < reference_date:
            return False, f"Deadline in past"
        
        all_text = " ".join([
            grant.title or "",
            grant.description or "",
            grant.eligibility or "",
            grant.raw_text or ""
        ]).lower()
        
        # Check 2: Must contain 'Illinois' or be federal with IL relevance
        if "illinois" not in all_text and "il" not in all_text:
            # Federal opportunities may not mention Illinois explicitly
            if grant.funding_source != FundingSource.FEDERAL_SAM_GOV:
                return False, "No Illinois reference"
        
        # Check 3: Must be eligible for Higher Education
        eligible_terms = ['higher education', 'public universit', 'college', 
                         'academic institution', 'research institution', 
                         'university', 'education', 'institution of higher']
        
        if not any(term in all_text for term in eligible_terms):
            return False, "Not Higher Ed eligible"
        
        return True, "Passed all pre-filter checks"
    
    def process_grant(self, grant: GrantOpportunity, 
                     reference_date: Optional[datetime] = None,
                     trigger_deep_research_at: int = 80) -> GrantOpportunity:
        """Process a single grant through the pipeline."""
        # Apply pre-filter
        passes, reason = self.pre_filter(grant, reference_date)
        grant.passes_prefilter = passes
        
        if passes:
            # Calculate heuristic score
            grant.keyword_score = self.scorer.score(grant)
            
            # Trigger DeepResearchEngine if score > threshold
            if grant.keyword_score > trigger_deep_research_at:
                grant.deep_research_triggered = True
                self.logger.info(f"Grant '{grant.id}' score {grant.keyword_score} > {trigger_deep_research_at}: DeepResearch triggered")
        else:
            grant.keyword_score = 0
        
        return grant
    
    def discover_all(self, filters: Optional[Dict[str, Any]] = None,
                     apply_prefilter: bool = True,
                     trigger_deep_research_at: int = 80) -> Dict[str, List[GrantOpportunity]]:
        """Discover grants from all registered sources."""
        results = {}
        
        for source in self.sources:
            try:
                opportunities = source.discover(filters)
                
                if apply_prefilter:
                    opportunities = [
                        self.process_grant(opp, trigger_deep_research_at=trigger_deep_research_at)
                        for opp in opportunities
                    ]
                
                results[source.name] = opportunities
                passed = sum(1 for opp in opportunities if opp.passes_prefilter)
                triggered = sum(1 for opp in opportunities if opp.deep_research_triggered)
                
                self.logger.info(f"{source.name}: {len(opportunities)} found, {passed} passed, {triggered} triggered DeepResearch")
                
            except Exception as e:
                self.logger.error(f"Error from {source.name}: {e}")
                results[source.name] = []
        
        return results


def run_live_ingestion():
    """
    Run complete live ingestion pipeline:
    1. Scrape Illinois GATA portal
    2. Query SAM.gov API
    3. Apply pre_filter
    4. Trigger DeepResearchEngine for scores > 80
    5. Output summary table
    """
    print("\n" + "="*80)
    print("MPART @ UIS LIVE GRANT INGESTION PIPELINE")
    print("="*80 + "\n")
    
    # Initialize pipeline
    pipeline = GrantDiscoveryPipeline()
    
    # Register live sources
    pipeline.register_source(GATAWebScraper())
    pipeline.register_source(SAMSource())
    
    # Run discovery with DeepResearch trigger at >80
    print("Starting live data collection...\n")
    results = pipeline.discover_all(trigger_deep_research_at=80)
    
    # Aggregate and analyze results
    all_grants = []
    source_stats = {}
    
    for source_name, grants in results.items():
        total = len(grants)
        passed = sum(1 for g in grants if g.passes_prefilter)
        high_score = sum(1 for g in grants if g.keyword_score > 80)
        triggered = sum(1 for g in grants if g.deep_research_triggered)
        
        source_stats[source_name] = {
            'total': total,
            'passed': passed,
            'high_score': high_score,
            'triggered': triggered
        }
        
        all_grants.extend(grants)
    
    # Sort by score
    all_grants.sort(key=lambda x: x.keyword_score, reverse=True)
    
    # Display Summary Table
    print("\n" + "="*80)
    print("INGESTION SUMMARY TABLE")
    print("="*80)
    print(f"{'Source':<30} {'Live Leads':>12} {'Passed Filter':>14} {'High Score (>80)':>18} {'DeepResearch':>14}")
    print("-"*80)
    
    for source_name, stats in source_stats.items():
        print(f"{source_name:<30} {stats['total']:>12} {stats['passed']:>14} {stats['high_score']:>18} {stats['triggered']:>14}")
    
    print("-"*80)
    total_stats = {
        'total': sum(s['total'] for s in source_stats.values()),
        'passed': sum(s['passed'] for s in source_stats.values()),
        'high_score': sum(s['high_score'] for s in source_stats.values()),
        'triggered': sum(s['triggered'] for s in source_stats.values())
    }
    print(f"{'TOTAL':<30} {total_stats['total']:>12} {total_stats['passed']:>14} {total_stats['high_score']:>18} {total_stats['triggered']:>14}")
    
    # Display Top Matches for MPART
    print("\n" + "="*80)
    print("TOP MATCHES FOR MPART @ UIS")
    print("="*80)
    print(f"{'Rank':<6} {'Source':<20} {'Score':>6} {'DeepResearch':>12} {'Title':<40}")
    print("-"*80)
    
    top_grants = [g for g in all_grants if g.passes_prefilter][:10]
    
    for i, grant in enumerate(top_grants, 1):
        source_short = grant.funding_source.value.replace("_", " ").title()[:18]
        dr_status = "TRIGGERED" if grant.deep_research_triggered else "-"
        title_short = grant.title[:38] + "..." if len(grant.title) > 38 else grant.title
        print(f"{i:<6} {source_short:<20} {grant.keyword_score:>6} {dr_status:>12} {title_short:<40}")
    
    # Save results
    output_file = "data/live_ingestion_results.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    output_data = {
        "metadata": {
            "ingestion_timestamp": datetime.now().isoformat(),
            "pipeline_version": "2.0-live",
            "deep_research_threshold": 80
        },
        "summary": total_stats,
        "source_breakdown": source_stats,
        "all_grants": [g.to_dict() for g in all_grants]
    }
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"Results saved to: {output_file}")
    print("="*80 + "\n")
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="MPART @ UIS Live Grant Ingestion")
    parser.add_argument("--live", action="store_true", help="Run live ingestion (GATA + SAM)")
    parser.add_argument("--test-prefilter", action="store_true", help="Test pre-filter logic")
    
    args = parser.parse_args()
    
    if args.live:
        run_live_ingestion()
    elif args.test_prefilter:
        # Test pre-filter with sample data
        print("Pre-filter test mode - implement test cases here")
    else:
        print("Usage:")
        print("  python scout_il.py --live          # Run live ingestion")
        print("  python scout_il.py --test-prefilter # Test filters")
