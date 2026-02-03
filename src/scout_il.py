"""
Illinois GATA (Grant Accountability and Transparency Act) Portal Scouter

This module provides functionality to discover and monitor grant opportunities
from the Illinois GATA portal and related state/federal sources relevant to
MPART @ UIS (Medical Policy Applied Research Team at University of Illinois Springfield).

Reference: https://grants.illinois.gov/
"""

import json
import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum


# Configure logging
logging.basicConfig(level=logging.INFO)
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
    FEDERAL_GRANTS_GOV = "federal_grants_gov"
    MEDICAID_INNOVATION = "medicaid_innovation"
    NSF = "nsf"
    NIH = "nih"
    OTHER = "other"


@dataclass
class GrantOpportunity:
    """
    Data class representing a grant opportunity.
    
    Attributes:
        id: Unique identifier for the grant
        title: Title of the grant opportunity
        agency: Funding agency/organization
        description: Full description of the grant
        eligibility: Eligibility requirements
        award_amount: Estimated award amount range
        deadline: Application deadline (close date)
        status: Current status of the grant
        funding_source: Source of the funding
        url: URL to the grant announcement
        posted_date: Date the grant was posted
        tags: Relevant keywords/tags for matching
        raw_text: Raw text content for NLP processing
        keyword_score: Heuristic score from keyword matching (0-100)
        passes_prefilter: Whether the grant passed deterministic pre-filtering
    """
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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert GrantOpportunity to dictionary."""
        result = asdict(self)
        # Convert enums to strings
        result['status'] = self.status.value
        result['funding_source'] = self.funding_source.value
        # Convert datetime to ISO format
        if self.deadline:
            result['deadline'] = self.deadline.isoformat()
        if self.posted_date:
            result['posted_date'] = self.posted_date.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GrantOpportunity':
        """Create GrantOpportunity from dictionary."""
        # Convert string enums back to enums
        data['status'] = GrantStatus(data['status'])
        data['funding_source'] = FundingSource(data['funding_source'])
        # Convert ISO format back to datetime
        if data.get('deadline'):
            data['deadline'] = datetime.fromisoformat(data['deadline'])
        if data.get('posted_date'):
            data['posted_date'] = datetime.fromisoformat(data['posted_date'])
        return cls(**data)


class GrantSource(ABC):
    """
    Abstract base class for grant sources.
    
    All grant source implementations must inherit from this class
    and implement the discover() method.
    """
    
    def __init__(self, name: str, base_url: str):
        self.name = name
        self.base_url = base_url
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    @abstractmethod
    def discover(self, filters: Optional[Dict[str, Any]] = None) -> List[GrantOpportunity]:
        """
        Discover grant opportunities from this source.
        
        Args:
            filters: Optional filters to narrow down results
            
        Returns:
            List of GrantOpportunity objects
        """
        pass
    
    @abstractmethod
    def get_grant_details(self, grant_id: str) -> Optional[GrantOpportunity]:
        """
        Get detailed information about a specific grant.
        
        Args:
            grant_id: Unique identifier for the grant
            
        Returns:
            GrantOpportunity if found, None otherwise
        """
        pass


class IllinoisGATASource(GrantSource):
    """
    Illinois GATA (Grant Accountability and Transparency Act) Portal source.
    
    Reference: https://grants.illinois.gov/
    
    TODO: Implement actual scraping/ API integration when available.
    For now, this is a skeleton implementation.
    """
    
    def __init__(self):
        super().__init__(
            name="Illinois GATA Portal",
            base_url="https://grants.illinois.gov/"
        )
        self.search_url = f"{self.base_url}search"
    
    def discover(self, filters: Optional[Dict[str, Any]] = None) -> List[GrantOpportunity]:
        """
        Discover grants from Illinois GATA portal.
        
        TODO: Implement actual discovery logic:
        1. Navigate to GATA portal search page
        2. Apply filters (healthcare, Medicaid, innovation, etc.)
        3. Extract grant listings
        4. Parse individual grant pages
        5. Return structured GrantOpportunity objects
        
        For now, returns an empty list as a skeleton.
        """
        self.logger.info(f"Discovering grants from {self.name}")
        self.logger.info("NOTE: This is a skeleton implementation.")
        self.logger.info(f"Would search: {self.search_url}")
        
        if filters:
            self.logger.info(f"With filters: {filters}")
        
        # TODO: Implement actual scraping/API calls here
        return []
    
    def get_grant_details(self, grant_id: str) -> Optional[GrantOpportunity]:
        """
        Get detailed information about a specific GATA grant.
        
        TODO: Implement actual detail retrieval from GATA portal.
        """
        self.logger.info(f"Fetching grant details for ID: {grant_id}")
        return None
    
    def search_by_category(self, category: str) -> List[GrantOpportunity]:
        """
        Search GATA grants by category.
        
        Useful categories for MPART @ UIS:
        - Healthcare
        - Medicaid
        - Innovation
        - Technology
        - Social Services
        """
        return self.discover(filters={"category": category})


class FederalGrantsGovSource(GrantSource):
    """
    Federal Grants.gov source for federal funding opportunities.
    
    Reference: https://www.grants.gov/
    
    Grants.gov provides a SOAP API for searching opportunities.
    """
    
    def __init__(self):
        super().__init__(
            name="Grants.gov",
            base_url="https://www.grants.gov/"
        )
        self.api_url = "https://apply07.grants.gov/apply/opportunities/search"
    
    def discover(self, filters: Optional[Dict[str, Any]] = None) -> List[GrantOpportunity]:
        """
        Discover federal grants from Grants.gov.
        
        TODO: Implement Grants.gov API integration:
        1. Use Grants.gov SOAP API
        2. Search by CFDA numbers, agencies, keywords
        3. Filter by MPART @ UIS-relevant criteria
        4. Parse XML responses
        """
        self.logger.info(f"Discovering grants from {self.name}")
        
        # MPART @ UIS-relevant search terms
        mpart_keywords = [
            "Medicaid",
            "healthcare innovation",
            "health policy",
            "1115 waiver",
            "health information technology",
            "CMS innovation",
            "social determinants of health"
        ]
        
        self.logger.info(f"Would search with keywords: {mpart_keywords}")
        return []
    
    def get_grant_details(self, grant_id: str) -> Optional[GrantOpportunity]:
        """Get detailed information about a specific federal grant."""
        self.logger.info(f"Fetching federal grant details for ID: {grant_id}")
        return None


class MedicaidInnovationSource(GrantSource):
    """
    CMS Medicaid Innovation source.
    
    Reference: https://www.medicaid.gov/medicaid/innovation/index.html
    
    For 1115 Waivers and other Medicaid innovation opportunities.
    """
    
    def __init__(self):
        super().__init__(
            name="CMS Medicaid Innovation",
            base_url="https://www.medicaid.gov/medicaid/innovation/"
        )
    
    def discover(self, filters: Optional[Dict[str, Any]] = None) -> List[GrantOpportunity]:
        """
        Discover Medicaid innovation opportunities.
        
        Specifically monitors:
        - 1115 Waiver demonstration opportunities
        - Delivery System Reform Incentive Payment (DSRIP) programs
        - Medicaid Innovation Accelerator Program
        """
        self.logger.info(f"Discovering opportunities from {self.name}")
        return []
    
    def get_grant_details(self, grant_id: str) -> Optional[GrantOpportunity]:
        """Get details about a specific Medicaid innovation opportunity."""
        self.logger.info(f"Fetching Medicaid innovation details for ID: {grant_id}")
        return None


class HeuristicScorer:
    """
    Deterministic keyword-based scorer for grant opportunities.
    
    This is pure Python logic (no AI) that calculates a keyword_score
    based on direct string matches for MPART @ UIS priority terms.
    
    Research Pillars (from MPART @ UIS website):
    - Medicaid (35): Core focus area
    - Policy Monitoring (25): Regulatory tracking and automation
    - Regulatory Analysis (25): Compliance and variation analysis
    - Rural Health (15): Rural health infrastructure and impact
    
    Additional Pillars:
    - PolicyDelta: State policy variation tracking
    - National Policy Tracker: Multi-jurisdictional monitoring
    - Healthcare Infrastructure: System evaluation and assessment
    """
    
    # Keyword weights for scoring (must sum to 100)
    KEYWORD_WEIGHTS = {
        # Core Research Pillars (100 total)
        'medicaid': 35,
        'policy monitoring': 25,
        'regulatory analysis': 25,
        'rural health': 15,
        # Research Infrastructure Terms (bonus scoring)
        'policydelta': 20,
        'policy delta': 18,
        'national policy tracker': 18,
        'healthcare infrastructure': 16,
        'regulatory monitoring': 15,
        '1115 waiver': 12,
        '1115': 10,
        'waiver': 8,
        'state variations': 10,
        'jurisdictional': 8,
        'multi-state': 10,
        'cross-state': 8,
        'rural infrastructure': 8,
        'health disparities': 8,
        'government evaluation': 10,
        'policy evaluation': 8,
        'health policy': 8,
        'technical assistance': 5,
        'cms': 5,
    }
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.HeuristicScorer")
    
    def score(self, grant: GrantOpportunity) -> int:
        """
        Calculate keyword score (0-100) for a grant opportunity.
        
        Args:
            grant: GrantOpportunity to score
            
        Returns:
            Integer score from 0 to 100
        """
        # Combine all text fields for analysis
        text_to_analyze = " ".join([
            grant.title or "",
            grant.description or "",
            grant.eligibility or "",
            " ".join(grant.tags),
            grant.raw_text or ""
        ]).lower()
        
        score = 0
        matched_keywords = []
        
        for keyword, weight in self.KEYWORD_WEIGHTS.items():
            # Use word boundary regex for precise matching
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            matches = len(re.findall(pattern, text_to_analyze))
            
            if matches > 0:
                # Cap the score contribution per keyword to prevent over-weighting
                contribution = min(matches * weight, weight * 2)
                score += contribution
                matched_keywords.append(f"{keyword}({contribution})")
        
        # Cap at 100
        final_score = min(int(score), 100)
        
        self.logger.debug(
            f"Scored grant '{grant.id}': {final_score}/100 "
            f"matches: {matched_keywords}"
        )
        
        return final_score
    
    def get_match_details(self, grant: GrantOpportunity) -> Dict[str, Any]:
        """
        Get detailed scoring breakdown for a grant.
        
        Returns:
            Dictionary with score and matched keywords
        """
        text_to_analyze = " ".join([
            grant.title or "",
            grant.description or "",
            grant.eligibility or "",
            " ".join(grant.tags),
            grant.raw_text or ""
        ]).lower()
        
        matches = {}
        for keyword, weight in self.KEYWORD_WEIGHTS.items():
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            count = len(re.findall(pattern, text_to_analyze))
            if count > 0:
                matches[keyword] = {
                    'count': count,
                    'weight': weight,
                    'contribution': min(count * weight, weight * 2)
                }
        
        return {
            'total_score': self.score(grant),
            'matched_keywords': matches,
            'analyzed_text_length': len(text_to_analyze)
        }


class GrantDiscoveryPipeline:
    """
    Pipeline for discovering grants from multiple sources.
    
    Orchestrates the discovery process across all configured sources,
    applies deterministic pre-filtering, and calculates heuristic scores.
    """
    
    def __init__(self):
        self.sources: List[GrantSource] = []
        self.scorer = HeuristicScorer()
        self.logger = logging.getLogger(f"{__name__}.Pipeline")
    
    def register_source(self, source: GrantSource) -> None:
        """Register a new grant source."""
        self.sources.append(source)
        self.logger.info(f"Registered source: {source.name}")
    
    def pre_filter(self, grant: GrantOpportunity, reference_date: Optional[datetime] = None) -> Tuple[bool, str]:
        """
        Deterministic pre-filter to discard irrelevant grants.
        
        PURE PYTHON LOGIC - NO AI.
        
        Discards grants if:
        1. Close Date is in the past
        2. Text does not contain 'Illinois' or 'IL'
        3. Not eligible for 'Higher Education' or 'Public Universities'
        
        Args:
            grant: GrantOpportunity to evaluate
            reference_date: Date to use for deadline comparison (defaults to now)
            
        Returns:
            Tuple of (passes_filter: bool, reason: str)
        """
        if reference_date is None:
            reference_date = datetime.now()
        
        # Check 1: Close Date is in the past
        if grant.deadline and grant.deadline < reference_date:
            return False, f"Deadline {grant.deadline.isoformat()} is in the past"
        
        # Combine all text for analysis
        all_text = " ".join([
            grant.title or "",
            grant.description or "",
            grant.eligibility or "",
            grant.agency or "",
            " ".join(grant.tags),
            grant.raw_text or ""
        ]).lower()
        
        # Check 2: Must contain 'Illinois' or 'IL' (Illinois-specific relevance)
        illinois_pattern = r'\b(illinois|il)\b'
        if not re.search(illinois_pattern, all_text):
            return False, "Does not contain 'Illinois' or 'IL'"
        
        # Check 3: Must be eligible for 'Higher Education' or 'Public Universities'
        eligible_entities = [
            'higher education',
            'public universit',
            'college',
            'academic institution',
            'research institution',
            'university of illinois',
            'uis',
            'u of i',
            'state university'
        ]
        
        has_eligible_audience = any(
            entity in all_text for entity in eligible_entities
        )
        
        if not has_eligible_audience:
            return False, "Not eligible for Higher Education or Public Universities"
        
        return True, "Passed all pre-filter checks"
    
    def process_grant(self, grant: GrantOpportunity, reference_date: Optional[datetime] = None) -> GrantOpportunity:
        """
        Process a single grant through the pipeline.
        
        Applies pre-filtering and heuristic scoring.
        
        Args:
            grant: GrantOpportunity to process
            reference_date: Date for deadline comparison
            
        Returns:
            Processed GrantOpportunity with scores and flags
        """
        # Apply pre-filter
        passes, reason = self.pre_filter(grant, reference_date)
        grant.passes_prefilter = passes
        
        if passes:
            # Calculate heuristic score
            grant.keyword_score = self.scorer.score(grant)
            self.logger.info(
                f"Grant '{grant.id}' passed pre-filter with score {grant.keyword_score}/100"
            )
        else:
            grant.keyword_score = 0
            self.logger.info(f"Grant '{grant.id}' rejected: {reason}")
        
        return grant
    
    def discover_all(self, filters: Optional[Dict[str, Any]] = None, 
                     apply_prefilter: bool = True,
                     reference_date: Optional[datetime] = None) -> Dict[str, List[GrantOpportunity]]:
        """
        Discover grants from all registered sources.
        
        Args:
            filters: Optional filters to apply to all sources
            apply_prefilter: Whether to apply deterministic pre-filtering
            reference_date: Date to use for deadline comparison
            
        Returns:
            Dictionary mapping source names to lists of opportunities
        """
        results = {}
        
        for source in self.sources:
            try:
                opportunities = source.discover(filters)
                
                if apply_prefilter:
                    # Process each grant through the pipeline
                    opportunities = [
                        self.process_grant(opp, reference_date)
                        for opp in opportunities
                    ]
                
                results[source.name] = opportunities
                passed = sum(1 for opp in opportunities if opp.passes_prefilter)
                self.logger.info(
                    f"{source.name}: {len(opportunities)} found, {passed} passed pre-filter"
                )
            except Exception as e:
                self.logger.error(f"Error discovering from {source.name}: {e}")
                results[source.name] = []
        
        return results
    
    def get_qualified_opportunities(self, min_score: int = 50,
                                   filters: Optional[Dict[str, Any]] = None) -> List[GrantOpportunity]:
        """
        Get all opportunities that passed pre-filter and meet minimum score.
        
        Args:
            min_score: Minimum keyword_score to include (default 50)
            filters: Optional filters to apply
            
        Returns:
            List of qualified GrantOpportunity objects
        """
        all_results = self.discover_all(filters, apply_prefilter=True)
        qualified = []
        
        for source_opps in all_results.values():
            for opp in source_opps:
                if opp.passes_prefilter and opp.keyword_score >= min_score:
                    qualified.append(opp)
        
        # Sort by score descending
        qualified.sort(key=lambda x: x.keyword_score, reverse=True)
        
        return qualified
    
    def get_all_opportunities(self, filters: Optional[Dict[str, Any]] = None) -> List[GrantOpportunity]:
        """
        Get all opportunities from all sources as a flat list.
        
        Args:
            filters: Optional filters to apply
            
        Returns:
            Combined list of all GrantOpportunity objects
        """
        all_results = self.discover_all(filters, apply_prefilter=False)
        combined = []
        for opportunities in all_results.values():
            combined.extend(opportunities)
        return combined
    
    def save_results(self, results: Dict[str, List[GrantOpportunity]], filepath: str) -> None:
        """
        Save discovery results to a JSON file.
        
        Args:
            results: Results from discover_all()
            filepath: Path to save the JSON file
        """
        serializable = {
            source: [opp.to_dict() for opp in opportunities]
            for source, opportunities in results.items()
        }
        
        # Calculate summary stats
        total = sum(len(opps) for opps in results.values())
        passed = sum(
            sum(1 for opp in opps if opp.passes_prefilter)
            for opps in results.values()
        )
        high_score = sum(
            sum(1 for opp in opps if opp.passes_prefilter and opp.keyword_score >= 50)
            for opps in results.values()
        )
        
        serializable['metadata'] = {
            'discovered_at': datetime.now().isoformat(),
            'sources_checked': len(self.sources),
            'total_opportunities': total,
            'passed_prefilter': passed,
            'high_score_50plus': high_score
        }
        
        with open(filepath, 'w') as f:
            json.dump(serializable, f, indent=2)
        
        self.logger.info(f"Saved results to {filepath}")


def create_mpart_pipeline() -> GrantDiscoveryPipeline:
    """
    Factory function to create a pre-configured pipeline for MPART @ UIS.
    
    Returns:
        GrantDiscoveryPipeline with all MPART @ UIS-relevant sources registered
    """
    pipeline = GrantDiscoveryPipeline()
    
    # Register Illinois-specific sources
    pipeline.register_source(IllinoisGATASource())
    
    # Register federal sources
    pipeline.register_source(FederalGrantsGovSource())
    pipeline.register_source(MedicaidInnovationSource())
    
    return pipeline


# CLI Interface for testing
if __name__ == "__main__":
    """
    Command-line interface for testing the grant discovery pipeline.
    
    Usage:
        python scout_il.py --dry-run
        python scout_il.py --source gata --output grants.json
        python scout_il.py --search "healthcare innovation"
        python scout_il.py --test-prefilter
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Illinois GATA Grant Discovery Tool for MPART @ UIS"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in dry-run mode (no actual API calls)"
    )
    parser.add_argument(
        "--source",
        choices=["gata", "federal", "medicaid", "all"],
        default="all",
        help="Source to search"
    )
    parser.add_argument(
        "--output",
        default="data/grants_discovered.json",
        help="Output file path"
    )
    parser.add_argument(
        "--search",
        help="Search keywords"
    )
    parser.add_argument(
        "--test-prefilter",
        action="store_true",
        help="Test pre-filter logic with sample grants"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Illinois GATA Grant Discovery Tool for MPART @ UIS")
    print("Medical Policy Applied Research Team at UIS")
    print("=" * 60)
    
    if args.test_prefilter:
        print("\n[TESTING PRE-FILTER LOGIC]")
        pipeline = GrantDiscoveryPipeline()
        
        # Test case 1: Valid Illinois grant for higher ed
        grant1 = GrantOpportunity(
            id="TEST-001",
            title="Illinois Medicaid Innovation Grant for Universities",
            agency="Illinois HFS",
            description="Grant for Illinois public universities to implement Medicaid innovation.",
            eligibility="Higher Education Institutions, Public Universities",
            deadline=datetime(2026, 12, 31),
            status=GrantStatus.OPEN,
            funding_source=FundingSource.ILLINOIS_GATA,
            url="https://example.com/1"
        )
        
        # Test case 2: Past deadline
        grant2 = GrantOpportunity(
            id="TEST-002",
            title="Old Illinois Grant",
            agency="Illinois DHS",
            description="Past opportunity for higher education.",
            eligibility="Public Universities",
            deadline=datetime(2020, 1, 1),
            status=GrantStatus.CLOSED,
            funding_source=FundingSource.ILLINOIS_GATA,
            url="https://example.com/2"
        )
        
        # Test case 3: Not Illinois
        grant3 = GrantOpportunity(
            id="TEST-003",
            title="Federal Medicaid Grant",
            agency="CMS",
            description="Federal opportunity for higher education institutions nationwide.",
            eligibility="Higher Education Institutions",
            deadline=datetime(2026, 6, 30),
            status=GrantStatus.OPEN,
            funding_source=FundingSource.FEDERAL_GRANTS_GOV,
            url="https://example.com/3"
        )
        
        # Test case 4: Not eligible for higher ed
        grant4 = GrantOpportunity(
            id="TEST-004",
            title="Illinois Community Grant",
            agency="Illinois DHS",
            description="Grant for Illinois community organizations.",
            eligibility="Nonprofit Organizations, Community Groups",
            deadline=datetime(2026, 8, 15),
            status=GrantStatus.OPEN,
            funding_source=FundingSource.ILLINOIS_GATA,
            url="https://example.com/4"
        )
        
        test_grants = [grant1, grant2, grant3, grant4]
        
        for grant in test_grants:
            passes, reason = pipeline.pre_filter(grant)
            status = "✓ PASS" if passes else "✗ FAIL"
            print(f"\n{status} | {grant.id}: {grant.title}")
            print(f"       Reason: {reason}")
    
    elif args.dry_run:
        print("\n[DRY RUN MODE]")
        pipeline = create_mpart_pipeline()
        print("Pipeline configured with sources:")
        for source in pipeline.sources:
            print(f"  - {source.name}: {source.base_url}")
        print("\nNo actual API calls will be made.")
        print("This is a skeleton implementation ready for full development.")
    else:
        print(f"\nSearching for grants...")
        if args.search:
            print(f"Filters: {args.search}")
        
        pipeline = create_mpart_pipeline()
        results = pipeline.discover_all(apply_prefilter=True)
        pipeline.save_results(results, args.output)
        
        print(f"\nResults saved to: {args.output}")
        print("\nSummary:")
        for source, opportunities in results.items():
            passed = sum(1 for opp in opportunities if opp.passes_prefilter)
            high = sum(1 for opp in opportunities if opp.passes_prefilter and opp.keyword_score >= 50)
            print(f"  {source}: {len(opportunities)} total, {passed} passed pre-filter, {high} high score (50+)")
