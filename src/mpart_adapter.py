"""
MPART @ UIS Grant Matching Adapter

This module provides specialized matching logic for MPART @ UIS
(Medical Policy Applied Research Team at University of Illinois Springfield),
separating it from the Vanderbilt upstream codebase.

The adapter implements a tiered matching approach:
1. Deterministic pre-filtering (pure Python, no AI)
2. Heuristic keyword scoring (pure Python, no AI)
3. Deep Research AI call (only if keyword_score > 50)
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

# Import from scout_il module
from scout_il import (
    GrantOpportunity,
    GrantDiscoveryPipeline,
    HeuristicScorer,
    create_mpart_pipeline,
    FundingSource,
    GrantStatus
)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResearchDepth(Enum):
    """Enumeration of research depth levels."""
    PREFILTER_ONLY = "prefilter_only"           # Did not pass pre-filter
    HEURISTIC_ONLY = "heuristic_only"           # Passed pre-filter, score <= 50
    DEEP_RESEARCH = "deep_research"             # Passed pre-filter, score > 50


@dataclass
class MatchResult:
    """
    Data class representing a match result between a grant and MPART @ UIS.
    
    Attributes:
        grant_id: Unique identifier for the grant
        grant_title: Title of the grant
        faculty_match: Name of the matched faculty/team
        recommended_lead: Mercenary ID best suited for this lead (policy/data/rural)
        match_score: Overall match score (0-100)
        keyword_score: Heuristic keyword score (0-100)
        research_depth: Level of research performed
        rationale: Explanation of why this is a match
        alignment_points: Specific alignment points between grant and MPART
        recommended_action: Suggested next step
        deep_research_data: Results from AI deep research (if performed)
        timestamp: When the match was generated
    """
    grant_id: str
    grant_title: str
    faculty_match: str = "MPART @ UIS Research Team"
    recommended_lead: str = ""  # mercenary_policy, mercenary_data, mercenary_eval, or ""
    match_score: int = 0
    keyword_score: int = 0
    research_depth: ResearchDepth = ResearchDepth.PREFILTER_ONLY
    rationale: str = ""
    alignment_points: List[str] = field(default_factory=list)
    recommended_action: str = ""
    deep_research_data: Optional[Dict[str, Any]] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert MatchResult to dictionary."""
        return {
            'grant_id': self.grant_id,
            'grant_title': self.grant_title,
            'faculty_match': self.faculty_match,
            'recommended_lead': self.recommended_lead,
            'match_score': self.match_score,
            'keyword_score': self.keyword_score,
            'research_depth': self.research_depth.value,
            'rationale': self.rationale,
            'alignment_points': self.alignment_points,
            'recommended_action': self.recommended_action,
            'deep_research_data': self.deep_research_data,
            'timestamp': self.timestamp
        }


class MPARTProfileLoader:
    """
    Loads and manages MPART @ UIS faculty profile data.
    
    Decouples profile loading from the matching logic.
    Loads both primary team profile and Mercenary roster.
    """
    
    DEFAULT_PROFILE_PATH = 'data/faculty_from_fis.json'
    
    # Mercenary profile definitions
    MERCENARY_PROFILES = {
        'mercenary_policy': {
            'id': 'mercenary_policy',
            'name': 'Policy Mercenary',
            'bio': 'Expert in state-level Medicaid variations and 1115 Waiver regulatory analysis. Specialized in tracking 54 jurisdictions for policy trends.',
            'specialization_tags': ['policy', 'regulatory', 'waivers', 'state_analysis'],
            'research_interests': [
                'State-level Medicaid variations',
                '1115 Waiver regulatory analysis',
                'Multi-jurisdictional policy tracking',
                'Regulatory compliance frameworks'
            ]
        },
        'mercenary_data': {
            'id': 'mercenary_data',
            'name': 'Data Mercenary',
            'bio': 'Data Scientist focused on AI-assisted tools for medical policy document collection and automated regulatory monitoring.',
            'specialization_tags': ['data', 'ai', 'automation', 'monitoring', 'nlp'],
            'research_interests': [
                'AI-assisted policy document collection',
                'Automated regulatory monitoring',
                'Natural language processing for policy',
                'Machine learning for document classification'
            ]
        },
        'mercenary_eval': {
            'id': 'mercenary_eval',
            'name': 'Rural Health Mercenary',
            'bio': 'Public health evaluator specializing in the impact of state medical policy changes on rural health infrastructure.',
            'specialization_tags': ['rural', 'health_equity', 'infrastructure', 'evaluation', 'impact'],
            'research_interests': [
                'Rural health infrastructure impact',
                'State policy effects on rural populations',
                'Rural health disparities',
                'Healthcare access in underserved areas'
            ]
        }
    }
    
    def __init__(self, profile_path: Optional[str] = None):
        self.profile_path = profile_path or self.DEFAULT_PROFILE_PATH
        self.profile_data: Optional[Dict[str, Any]] = None
        self.faculty_entry: Optional[Dict[str, Any]] = None
        self.mercenary_entries: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(f"{__name__}.MPARTProfileLoader")
    
    def load(self) -> Dict[str, Any]:
        """
        Load MPART @ UIS profile from JSON file.
        
        Returns:
            Primary faculty entry dictionary
        """
        try:
            with open(self.profile_path, 'r') as f:
                self.profile_data = json.load(f)
            
            if not self.profile_data.get('faculty'):
                raise ValueError("No faculty entries found in profile")
            
            self.faculty_entry = self.profile_data['faculty'][0]
            
            # Load mercenary entries (profiles with id starting with 'mercenary_')
            self.mercenary_entries = [
                f for f in self.profile_data.get('faculty', [])
                if f.get('id', '').startswith('mercenary_')
            ]
            
            self.logger.info(
                f"Loaded MPART @ UIS profile: {self.faculty_entry.get('name')}"
            )
            self.logger.info(
                f"Loaded {len(self.mercenary_entries)} Mercenary profiles"
            )
            
            return self.faculty_entry
            
        except FileNotFoundError:
            self.logger.error(f"Profile file not found: {self.profile_path}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in profile file: {e}")
            raise
    
    def get_research_interests(self) -> List[str]:
        """Get research interests from profile."""
        if not self.faculty_entry:
            self.load()
        return self.faculty_entry.get('research_interests', [])
    
    def get_bio(self) -> str:
        """Get bio from profile."""
        if not self.faculty_entry:
            self.load()
        return self.faculty_entry.get('bio', '')
    
    def get_research_areas(self) -> List[str]:
        """Get research areas from profile."""
        if not self.faculty_entry:
            self.load()
        return self.faculty_entry.get('research_areas', [])
    
    def get_mercenary_profiles(self) -> List[Dict[str, Any]]:
        """Get all Mercenary profiles."""
        if not self.mercenary_entries:
            self.load()
        return self.mercenary_entries
    
    def get_mercenary_by_id(self, mercenary_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific Mercenary profile by ID."""
        if not self.mercenary_entries:
            self.load()
        for m in self.mercenary_entries:
            if m.get('id') == mercenary_id:
                return m
        return None


class MercenaryMatcher:
    """
    Determines which Mercenary profile is the best fit for a grant opportunity.
    
    Uses keyword matching against each Mercenary's specialization tags
    and research interests to recommend the optimal lead.
    """
    
    # Mercenary-specific keyword mappings for matching
    MERCENARY_KEYWORDS = {
        'mercenary_policy': [
            'state policy', 'medicaid variations', '1115 waiver', 'regulatory analysis',
            'jurisdictional', 'multi-state', 'interstate', 'state-federal',
            'waiver negotiation', 'state plan', 'spa', 'state plan amendment',
            'cms approval', 'federal match', 'fmap', 'state legislature'
        ],
        'mercenary_data': [
            'policy monitoring', 'regulatory monitoring', 'automated monitoring',
            'ai-assisted', 'document collection', 'nlp', 'natural language',
            'machine learning', 'data pipeline', 'automated', 'classification',
            'document intelligence', 'scraping', 'api', 'data science'
        ],
        'mercenary_eval': [
            'rural health', 'rural infrastructure', 'government evaluation', 'health disparities',
            'rural hospital', 'critical access', 'underserved', 'telehealth',
            'government service', 'rural population', 'policy effectiveness',
            'rural access', 'health equity', 'evaluation', 'impact assessment'
        ]
    }
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.MercenaryMatcher")
    
    def match_grant_to_mercenary(self, grant: GrantOpportunity) -> Tuple[str, Dict[str, int]]:
        """
        Match a grant to the best Mercenary profile.
        
        Args:
            grant: The grant opportunity to match
            
        Returns:
            Tuple of (best_mercenary_id, score_dict)
            score_dict contains scores for each mercenary type
        """
        # Combine all grant text
        grant_text = " ".join([
            grant.title or "",
            grant.description or "",
            grant.eligibility or "",
            " ".join(grant.tags),
            grant.raw_text or ""
        ]).lower()
        
        scores = {}
        
        for mercenary_id, keywords in self.MERCENARY_KEYWORDS.items():
            score = 0
            matched_terms = []
            
            for keyword in keywords:
                if keyword in grant_text:
                    score += 1
                    matched_terms.append(keyword)
            
            scores[mercenary_id] = {
                'score': score,
                'matched_terms': matched_terms
            }
            
            self.logger.debug(
                f"{mercenary_id}: score={score}, matches={matched_terms[:3]}"
            )
        
        # Find best match
        best_id = max(scores.keys(), key=lambda k: scores[k]['score'])
        
        # If no matches, return empty
        if scores[best_id]['score'] == 0:
            return "", scores
        
        return best_id, scores
    
    def get_mercenary_name(self, mercenary_id: str) -> str:
        """Get human-readable name for a Mercenary ID."""
        names = {
            'mercenary_policy': 'Policy Mercenary (State/Regulatory Expert)',
            'mercenary_data': 'Data Mercenary (AI/Automation Expert)',
            'mercenary_eval': 'Evaluation Mercenary (Rural/Govt Services Expert)',
            '': 'No specific Mercenary match'
        }
        return names.get(mercenary_id, f"Unknown ({mercenary_id})")


class DeepResearchEngine:
    """
    AI-powered deep research engine for high-potential grant matches.
    
    This engine is ONLY triggered when keyword_score > 50.
    Separates expensive AI calls from deterministic filtering.
    
    Includes Mercenary lead tagging functionality.
    
    NOTE: This is a skeleton implementation. Actual AI integration
    would use an LLM API (Claude, GPT-4, etc.) for analysis.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.DeepResearchEngine")
        self.mercenary_matcher = MercenaryMatcher()
    
    def analyze(self, grant: GrantOpportunity, profile: Dict[str, Any], 
                mercenary_profiles: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform deep research analysis on a grant opportunity.
        
        This method would call an LLM API to:
        1. Analyze grant requirements in detail
        2. Compare against MPART capabilities and research areas
        3. Identify specific alignment points
        4. Tag the best Mercenary lead for this opportunity
        5. Generate strategic recommendations
        
        Args:
            grant: The grant opportunity to analyze
            profile: MPART @ UIS primary faculty profile
            mercenary_profiles: List of Mercenary profile dictionaries
            
        Returns:
            Dictionary with deep research results including recommended_lead
        """
        self.logger.info(
            f"Performing deep research on grant '{grant.id}' "
            f"(keyword_score: {grant.keyword_score})"
        )
        
        # Step 1: Tag the best Mercenary lead
        recommended_lead, mercenary_scores = self.mercenary_matcher.match_grant_to_mercenary(grant)
        
        self.logger.info(
            f"Tagged grant '{grant.id}' to Mercenary: {recommended_lead} "
            f"(score: {mercenary_scores.get(recommended_lead, {}).get('score', 0)})"
        )
        
        # SKELETON: This would be replaced with actual LLM API call
        # Example prompt structure:
        prompt = f"""
        Analyze this grant opportunity for MPART @ UIS:
        
        GRANT:
        Title: {grant.title}
        Agency: {grant.agency}
        Description: {grant.description}
        Eligibility: {grant.eligibility}
        
        MPART @ UIS PROFILE:
        Bio: {profile.get('bio', '')}
        Research Interests: {profile.get('research_interests', [])}
        Research Areas: {profile.get('research_areas', [])}
        
        MERCENARY TAG: {recommended_lead}
        Mercenary Scores: {mercenary_scores}
        
        KEYWORD SCORE: {grant.keyword_score}/100
        
        Provide:
        1. Detailed match rationale
        2. Specific alignment points (3-5 bullet points)
        3. Why the tagged Mercenary is the best fit
        4. Recommended action (apply, monitor, skip)
        5. Strategic considerations
        """
        
        self.logger.debug(f"Generated prompt (not sent): {prompt[:200]}...")
        
        # SKELETON: Return simulated results
        # In production, this would call an LLM API
        return {
            'analysis_performed': True,
            'prompt_preview': prompt[:100] + "...",
            'note': 'This is a skeleton implementation. Actual AI call would go here.',
            'recommended_lead': recommended_lead,
            'mercenary_scores': mercenary_scores,
            'lead_name': self.mercenary_matcher.get_mercenary_name(recommended_lead),
            'simulated_rationale': self._generate_simulated_rationale(grant, profile),
            'simulated_alignment': self._generate_simulated_alignment(grant),
            'simulated_recommendation': self._generate_simulated_recommendation(grant)
        }
    
    def _generate_simulated_rationale(self, grant: GrantOpportunity, profile: Dict[str, Any]) -> str:
        """Generate a simulated rationale (for skeleton implementation)."""
        keywords = []
        if 'medicaid' in grant.title.lower() or 'medicaid' in grant.description.lower():
            keywords.append("Medicaid policy expertise")
        if '1115' in grant.title or 'waiver' in grant.description.lower():
            keywords.append("1115 Waiver experience")
        if 'policy monitoring' in grant.description.lower() or 'regulatory monitoring' in grant.description.lower():
            keywords.append("Policy monitoring capability")
        if 'state policy' in grant.description.lower():
            keywords.append("State policy expertise")
        
        if keywords:
            return f"Strong alignment due to: {', '.join(keywords)}."
        return "General alignment with MPART research areas."
    
    def _generate_simulated_alignment(self, grant: GrantOpportunity) -> List[str]:
        """Generate simulated alignment points."""
        points = []
        desc_lower = grant.description.lower()
        
        if 'medicaid' in desc_lower:
            points.append("Direct experience with Medicaid policy implementation")
        if '1115' in grant.description:
            points.append("Specialized expertise in 1115 Waiver technical assistance")
        if 'policy monitoring' in desc_lower or 'regulatory monitoring' in desc_lower:
            points.append("Policy monitoring and regulatory analysis capabilities")
        if 'state policy' in desc_lower:
            points.append("State-level policy variation expertise")
        if 'applied research' in desc_lower:
            points.append("Implementation-focused applied research approach")
        if 'rural' in desc_lower:
            points.append("Rural health impact evaluation expertise")
        
        return points if points else ["General research capability alignment"]
    
    def _generate_simulated_recommendation(self, grant: GrantOpportunity) -> str:
        """Generate simulated recommendation."""
        if grant.keyword_score >= 75:
            return "HIGH PRIORITY: Apply - Strong alignment with core competencies"
        elif grant.keyword_score >= 50:
            return "MEDIUM PRIORITY: Consider - Moderate alignment, review details"
        else:
            return "LOW PRIORITY: Monitor - Weak alignment, skip for now"


class MPARTMatchingAdapter:
    """
    Main adapter class for MPART @ UIS grant matching.
    
    Orchestrates the tiered matching workflow:
    1. Load MPART profile (primary + Mercenary roster)
    2. Run grant discovery pipeline
    3. Apply deterministic pre-filtering
    4. Calculate heuristic keyword scores
    5. Trigger deep research AI only for high-scoring grants (score > 50)
    6. Tag the best Mercenary lead for the opportunity
    7. Generate structured match results
    """
    
    # Score threshold for triggering deep research
    DEEP_RESEARCH_THRESHOLD = 50
    
    def __init__(self, 
                 profile_path: Optional[str] = None,
                 enable_deep_research: bool = True):
        """
        Initialize the MPART matching adapter.
        
        Args:
            profile_path: Path to faculty profile JSON (default: data/faculty_from_fis.json)
            enable_deep_research: Whether to enable AI deep research for high-scoring grants
        """
        self.profile_loader = MPARTProfileLoader(profile_path)
        self.discovery_pipeline = create_mpart_pipeline()
        self.deep_research = DeepResearchEngine() if enable_deep_research else None
        self.mercenary_matcher = MercenaryMatcher()
        self.enable_deep_research = enable_deep_research
        
        self.profile: Optional[Dict[str, Any]] = None
        self.mercenary_profiles: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(f"{__name__}.MPARTMatchingAdapter")
    
    def initialize(self) -> None:
        """Load profile and prepare for matching."""
        self.logger.info("Initializing MPART @ UIS Matching Adapter")
        self.profile = self.profile_loader.load()
        self.mercenary_profiles = self.profile_loader.get_mercenary_profiles()
        self.logger.info(f"Adapter ready for {self.profile.get('name')}")
        self.logger.info(f"Loaded {len(self.mercenary_profiles)} Mercenary profiles for lead tagging")
    
    def match_grant(self, grant: GrantOpportunity) -> MatchResult:
        """
        Match a single grant against MPART @ UIS profile.
        
        Args:
            grant: GrantOpportunity to evaluate
            
        Returns:
            MatchResult with scoring and recommendations
        """
        if not self.profile:
            self.initialize()
        
        # Step 1: Apply deterministic pre-filtering
        passes_prefilter, filter_reason = self.discovery_pipeline.pre_filter(grant)
        grant.passes_prefilter = passes_prefilter
        
        if not passes_prefilter:
            self.logger.debug(f"Grant '{grant.id}' rejected by pre-filter: {filter_reason}")
            return MatchResult(
                grant_id=grant.id,
                grant_title=grant.title,
                match_score=0,
                keyword_score=0,
                research_depth=ResearchDepth.PREFILTER_ONLY,
                rationale=f"Did not pass pre-filter: {filter_reason}",
                recommended_action="Skip - does not meet basic criteria"
            )
        
        # Step 2: Calculate heuristic keyword score
        keyword_score = self.discovery_pipeline.scorer.score(grant)
        grant.keyword_score = keyword_score
        
        # Step 3: Determine research depth and generate result
        if keyword_score > self.DEEP_RESEARCH_THRESHOLD and self.enable_deep_research:
            # Trigger deep research AI
            return self._perform_deep_match(grant, keyword_score)
        else:
            # Heuristic-only match
            return self._perform_heuristic_match(grant, keyword_score)
    
    def _perform_heuristic_match(self, grant: GrantOpportunity, keyword_score: int) -> MatchResult:
        """Generate match result based on heuristic scoring only."""
        scorer = self.discovery_pipeline.scorer
        details = scorer.get_match_details(grant)
        
        # Generate simple rationale from matched keywords
        matched = details['matched_keywords']
        if matched:
            keyword_list = ", ".join([f"{k}({v['contribution']})" for k, v in list(matched.items())[:3]])
            rationale = f"Keyword matches: {keyword_list}. Score: {keyword_score}/100"
        else:
            rationale = f"No high-value keywords matched. Score: {keyword_score}/100"
        
        # Tag best Mercenary lead (even for heuristic-only matches)
        recommended_lead, _ = self.mercenary_matcher.match_grant_to_mercenary(grant)
        
        return MatchResult(
            grant_id=grant.id,
            grant_title=grant.title,
            recommended_lead=recommended_lead,
            match_score=keyword_score,  # Use keyword score as overall score
            keyword_score=keyword_score,
            research_depth=ResearchDepth.HEURISTIC_ONLY,
            rationale=rationale,
            alignment_points=list(matched.keys())[:5] if matched else [],
            recommended_action="Review - Consider for deeper analysis if resources allow"
        )
    
    def _perform_deep_match(self, grant: GrantOpportunity, keyword_score: int) -> MatchResult:
        """Generate match result with AI deep research."""
        if not self.deep_research:
            # Fallback to heuristic if deep research disabled
            return self._perform_heuristic_match(grant, keyword_score)
        
        # Perform AI deep research (includes Mercenary tagging)
        deep_data = self.deep_research.analyze(
            grant, self.profile, self.mercenary_profiles
        )
        
        # Extract recommended lead from deep research results
        recommended_lead = deep_data.get('recommended_lead', '')
        
        # Calculate final score (blend keyword score with AI assessment)
        # In production, this could be more sophisticated
        ai_boost = min(15, keyword_score // 10)  # Small boost for AI-validated matches
        final_score = min(keyword_score + ai_boost, 100)
        
        return MatchResult(
            grant_id=grant.id,
            grant_title=grant.title,
            recommended_lead=recommended_lead,
            match_score=final_score,
            keyword_score=keyword_score,
            research_depth=ResearchDepth.DEEP_RESEARCH,
            rationale=deep_data.get('simulated_rationale', 'AI analysis performed'),
            alignment_points=deep_data.get('simulated_alignment', []),
            recommended_action=deep_data.get('simulated_recommendation', 'Review AI analysis'),
            deep_research_data=deep_data
        )
    
    def match_grants(self, grants: List[GrantOpportunity]) -> List[MatchResult]:
        """
        Match multiple grants against MPART @ UIS profile.
        
        Args:
            grants: List of GrantOpportunity objects
            
        Returns:
            List of MatchResult objects, sorted by match_score descending
        """
        if not self.profile:
            self.initialize()
        
        self.logger.info(f"Matching {len(grants)} grants against MPART @ UIS profile")
        
        results = []
        for grant in grants:
            result = self.match_grant(grant)
            results.append(result)
        
        # Sort by match score descending
        results.sort(key=lambda x: x.match_score, reverse=True)
        
        # Log summary
        deep_research_count = sum(1 for r in results if r.research_depth == ResearchDepth.DEEP_RESEARCH)
        heuristic_count = sum(1 for r in results if r.research_depth == ResearchDepth.HEURISTIC_ONLY)
        filtered_count = sum(1 for r in results if r.research_depth == ResearchDepth.PREFILTER_ONLY)
        
        self.logger.info(
            f"Matching complete: {deep_research_count} deep research, "
            f"{heuristic_count} heuristic, {filtered_count} filtered out"
        )
        
        return results
    
    def discover_and_match(self, 
                          filters: Optional[Dict[str, Any]] = None) -> List[MatchResult]:
        """
        Full workflow: discover grants from all sources and match against MPART.
        
        Args:
            filters: Optional filters for discovery
            
        Returns:
            List of MatchResult objects
        """
        if not self.profile:
            self.initialize()
        
        # Discover grants with pre-filtering and scoring
        self.logger.info("Starting grant discovery and matching workflow")
        
        all_grants = []
        discovery_results = self.discovery_pipeline.discover_all(
            filters=filters,
            apply_prefilter=True
        )
        
        for source_grants in discovery_results.values():
            all_grants.extend(source_grants)
        
        self.logger.info(f"Discovered {len(all_grants)} grants from all sources")
        
        # Match all grants
        return self.match_grants(all_grants)
    
    def save_matches(self, matches: List[MatchResult], filepath: str) -> None:
        """
        Save match results to a JSON file.
        
        Args:
            matches: List of MatchResult objects
            filepath: Path to save the JSON file
        """
        # Calculate Mercenary lead distribution
        mercenary_leads = {
            'mercenary_policy': sum(1 for m in matches if m.recommended_lead == 'mercenary_policy'),
            'mercenary_data': sum(1 for m in matches if m.recommended_lead == 'mercenary_data'),
            'mercenary_eval': sum(1 for m in matches if m.recommended_lead == 'mercenary_eval'),
            'none': sum(1 for m in matches if m.recommended_lead == '')
        }
        
        output = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'organization': 'MPART @ UIS',
                'faculty_matched': self.profile.get('name') if self.profile else 'Unknown',
                'total_matches': len(matches),
                'deep_research_threshold': self.DEEP_RESEARCH_THRESHOLD,
                'deep_research_enabled': self.enable_deep_research
            },
            'summary': {
                'high_priority': sum(1 for m in matches if m.match_score >= 75),
                'medium_priority': sum(1 for m in matches if 50 <= m.match_score < 75),
                'low_priority': sum(1 for m in matches if 0 < m.match_score < 50),
                'filtered_out': sum(1 for m in matches if m.match_score == 0)
            },
            'mercenary_lead_distribution': mercenary_leads,
            'matches': [m.to_dict() for m in matches]
        }
        
        with open(filepath, 'w') as f:
            json.dump(output, f, indent=2)
        
        self.logger.info(f"Saved {len(matches)} matches to {filepath}")


def create_adapter(enable_deep_research: bool = True) -> MPARTMatchingAdapter:
    """
    Factory function to create a configured MPART @ UIS matching adapter.
    
    Args:
        enable_deep_research: Whether to enable AI deep research
        
    Returns:
        Configured MPARTMatchingAdapter instance
    """
    return MPARTMatchingAdapter(enable_deep_research=enable_deep_research)


# CLI Interface
if __name__ == "__main__":
    """
    Command-line interface for MPART @ UIS grant matching.
    
    Usage:
        python mpart_adapter.py --test
        python mpart_adapter.py --match-file grants.json --output matches.json
        python mpart_adapter.py --discover-and-match --output matches.json
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="MPART @ UIS Grant Matching Adapter"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run test with sample grants"
    )
    parser.add_argument(
        "--match-file",
        help="Path to JSON file with grants to match"
    )
    parser.add_argument(
        "--discover-and-match",
        action="store_true",
        help="Run discovery and match workflow"
    )
    parser.add_argument(
        "--output",
        default="data/mpart_matches.json",
        help="Output file path"
    )
    parser.add_argument(
        "--no-deep-research",
        action="store_true",
        help="Disable AI deep research (heuristic only)"
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("MPART @ UIS Grant Matching Adapter")
    print("Medical Policy Applied Research Team at University of Illinois Springfield")
    print("=" * 70)
    
    if args.test:
        print("\n[RUNNING TEST MATCHES WITH MERCENARY LEAD TAGGING]")
        
        # Create adapter
        adapter = create_adapter(enable_deep_research=not args.no_deep_research)
        adapter.initialize()
        
        # Create test grants with different Mercenary targeting profiles
        # Focus on new research pillars: PolicyDelta, National Policy Tracker,
        # Regulatory Monitoring, and Healthcare Infrastructure (NO LCNC REFERENCES)
        test_grants = [
            GrantOpportunity(
                id="IL-TRUTH-001",
                title="Multi-State Medical Policy Monitoring Infrastructure",
                agency="Illinois HFS",
                description="Comprehensive infrastructure for monitoring medical policy variations across multiple states. Implementation of National Policy Tracker system with PolicyDelta analysis for Medicaid regulatory monitoring and healthcare infrastructure assessment. Focus on regulatory analysis and state variations tracking.",
                eligibility="Higher Education Institutions, Public Universities in Illinois",
                deadline=datetime(2026, 6, 30),
                status=GrantStatus.OPEN,
                funding_source=FundingSource.ILLINOIS_GATA,
                url="https://example.com/il-truth-001",
                raw_text="Multi-State Medical Policy Monitoring Infrastructure National Policy Tracker PolicyDelta regulatory monitoring healthcare infrastructure state variations"
            ),
            GrantOpportunity(
                id="IL-POLICY-002",
                title="Illinois Medicaid PolicyDelta Analysis Initiative",
                agency="Illinois HFS",
                description="Research on state-level Medicaid variations using PolicyDelta methodology. Focus on 1115 Waiver regulatory analysis and multi-jurisdictional policy tracking for Illinois public universities.",
                eligibility="Higher Education Institutions, Public Universities in Illinois",
                deadline=datetime(2026, 7, 15),
                status=GrantStatus.OPEN,
                funding_source=FundingSource.ILLINOIS_GATA,
                url="https://example.com/il-policy-002",
                raw_text="Medicaid PolicyDelta state policy 1115 Waiver regulatory analysis multi-jurisdictional state variations"
            ),
            GrantOpportunity(
                id="IL-DATA-003",
                title="National Policy Tracker Implementation",
                agency="Illinois DHS",
                description="Development of automated policy monitoring infrastructure using National Policy Tracker framework. AI-assisted regulatory monitoring for medical policy document collection and healthcare infrastructure data systems.",
                eligibility="Higher Education Institutions, Public Universities in Illinois",
                deadline=datetime(2026, 8, 15),
                status=GrantStatus.OPEN,
                funding_source=FundingSource.ILLINOIS_GATA,
                url="https://example.com/il-data-003",
                raw_text="National Policy Tracker policy monitoring regulatory monitoring automated healthcare infrastructure"
            ),
            GrantOpportunity(
                id="IL-EVAL-004",
                title="Rural Healthcare Infrastructure Government Evaluation",
                agency="Illinois DPH",
                description="Government service evaluation of state medical policy impact on rural healthcare infrastructure. Assessment of health disparities and policy effectiveness in underserved Illinois communities.",
                eligibility="Public Universities in Illinois, Research Institutions",
                deadline=datetime(2026, 5, 15),
                status=GrantStatus.OPEN,
                funding_source=FundingSource.ILLINOIS_GATA,
                url="https://example.com/il-eval-004",
                raw_text="rural health infrastructure government evaluation policy impact health disparities underserved"
            ),
            GrantOpportunity(
                id="IL-REJECTED-005",
                title="Illinois Community Health Grant",
                agency="Illinois DPH",
                description="Community health programs for Illinois residents.",
                eligibility="Nonprofit Organizations, Community Health Centers",
                deadline=datetime(2026, 8, 15),
                status=GrantStatus.OPEN,
                funding_source=FundingSource.ILLINOIS_GATA,
                url="https://example.com/il-rejected-005"
            ),
            GrantOpportunity(
                id="FED-REJECTED-006",
                title="Federal Medicaid Innovation Award",
                agency="CMS",
                description="National Medicaid innovation funding for applied research projects.",
                eligibility="Higher Education Institutions",
                deadline=datetime(2026, 9, 30),
                status=GrantStatus.OPEN,
                funding_source=FundingSource.MEDICAID_INNOVATION,
                url="https://example.com/fed-rejected-006"
            )
        ]
        
        # Run matches
        results = adapter.match_grants(test_grants)
        
        # Display results
        print(f"\n{'='*70}")
        print("MATCH RESULTS WITH MERCENARY LEAD TAGGING")
        print(f"{'='*70}\n")
        
        mercenary_icons = {
            'mercenary_policy': '[POLICY]',
            'mercenary_data': '[DATA]  ',
            'mercenary_eval': '[EVAL]  ',
            '': '[NONE]  '
        }
        
        for result in results:
            depth_emoji = {
                "prefilter_only": "✗",
                "heuristic_only": "○",
                "deep_research": "●"
            }.get(result.research_depth.value, "?")
            
            lead_icon = mercenary_icons.get(result.recommended_lead, '[?]')
            
            print(f"{depth_emoji} {result.grant_id} | {lead_icon} | Score: {result.match_score}/100")
            print(f"   Title: {result.grant_title[:55]}...")
            print(f"   Lead: {adapter.mercenary_matcher.get_mercenary_name(result.recommended_lead)}")
            print(f"   Action: {result.recommended_action}")
            if result.alignment_points:
                print(f"   Alignment: {', '.join(result.alignment_points[:2])}")
            print()
        
        # Summary
        deep = sum(1 for r in results if r.research_depth.value == "deep_research")
        heuristic = sum(1 for r in results if r.research_depth.value == "heuristic_only")
        filtered = sum(1 for r in results if r.research_depth.value == "prefilter_only")
        
        print(f"{'='*70}")
        print("SUMMARY")
        print(f"{'='*70}")
        print(f"Matches: {deep} deep research, {heuristic} heuristic, {filtered} filtered")
        
        # Mercenary lead distribution
        policy_leads = sum(1 for r in results if r.recommended_lead == 'mercenary_policy')
        data_leads = sum(1 for r in results if r.recommended_lead == 'mercenary_data')
        eval_leads = sum(1 for r in results if r.recommended_lead == 'mercenary_eval')
        
        print(f"\nMercenary Lead Distribution:")
        print(f"  Policy Mercenary:    {policy_leads} leads")
        print(f"  Data Mercenary:      {data_leads} leads")
        print(f"  Evaluation Mercenary: {eval_leads} leads")
        
        print(f"\nResults saved to: {args.output}")
        
        adapter.save_matches(results, args.output)
        
    elif args.match_file:
        print(f"\n[LOADING GRANTS FROM {args.match_file}]")
        # TODO: Implement file loading and matching
        print("Feature not yet implemented in skeleton")
        
    elif args.discover_and_match:
        print("\n[DISCOVER AND MATCH WORKFLOW]")
        adapter = create_adapter(enable_deep_research=not args.no_deep_research)
        matches = adapter.discover_and_match()
        adapter.save_matches(matches, args.output)
        print(f"\nSaved {len(matches)} matches to {args.output}")
        
    else:
        print("\nNo action specified. Use --test to run sample matches.")
        print("Usage: python mpart_adapter.py --test")
