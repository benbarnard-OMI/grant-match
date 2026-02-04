#!/usr/bin/env python3
"""
MPART @ UIS Live Ingestion Demo

This script demonstrates the live web-scraping and API ingestion pipeline
with mock data when actual API keys are not available.
"""

import sys
import os
import json
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime, timedelta
from scout_il import (
    GrantOpportunity, GrantDiscoveryPipeline, HeuristicScorer,
    FundingSource, GrantStatus, GATAWebScraper, SAMSource
)


class MockGATAScraper(GATAWebScraper):
    """Mock GATA scraper for demo purposes."""
    
    def discover(self, filters=None):
        """Return mock Illinois GATA opportunities."""
        self.logger.info("MOCK MODE: Returning simulated GATA opportunities")
        
        return [
            GrantOpportunity(
                id="GATA-001",
                title="Illinois Medicaid Policy Monitoring Initiative",
                agency="Illinois Department of Healthcare and Family Services",
                description="Multi-year initiative for Medicaid policy monitoring and regulatory analysis across Illinois healthcare infrastructure.",
                eligibility="Public Universities in Illinois, Higher Education Institutions",
                deadline=datetime.now() + timedelta(days=90),
                funding_source=FundingSource.ILLINOIS_GATA,
                url="https://omb.illinois.gov/public/gata/csfa/OpportunityList.aspx",
                raw_text="Illinois Medicaid policy monitoring regulatory analysis healthcare infrastructure higher education"
            ),
            GrantOpportunity(
                id="GATA-002",
                title="State Policy Variations Research Program",
                agency="Illinois Governor's Office of Management and Budget",
                description="Research on state-level policy variations and multi-jurisdictional tracking for government evaluation.",
                eligibility="Illinois Public Universities, Research Institutions",
                deadline=datetime.now() + timedelta(days=120),
                funding_source=FundingSource.ILLINOIS_GATA,
                url="https://omb.illinois.gov/public/gata/csfa/ProgramList.aspx",
                raw_text="Illinois state policy variations multi-jurisdictional tracking government evaluation research"
            ),
            GrantOpportunity(
                id="GATA-003",
                title="Rural Health Infrastructure Assessment",
                agency="Illinois Department of Public Health",
                description="Evaluation of rural health infrastructure and healthcare access in underserved Illinois communities.",
                eligibility="Higher Education Institutions, Public Health Organizations",
                deadline=datetime.now() + timedelta(days=60),
                funding_source=FundingSource.ILLINOIS_GATA,
                url="https://omb.illinois.gov/public/gata/csfa/OpportunityList.aspx",
                raw_text="Illinois rural health infrastructure assessment healthcare access higher education"
            ),
            GrantOpportunity(
                id="GATA-004",
                title="Community Services Block Grant (Filtered)",
                agency="Illinois Department of Commerce",
                description="Community development grants for local organizations.",
                eligibility="Community Organizations, Nonprofits",
                deadline=datetime.now() + timedelta(days=45),
                funding_source=FundingSource.ILLINOIS_GATA,
                url="https://omb.illinois.gov/public/gata/csfa/ProgramList.aspx",
                raw_text="Illinois community services local organizations"  # No higher ed - should be filtered
            ),
        ]


class MockSAMSource(SAMSource):
    """Mock SAM.gov source for demo purposes."""
    
    def discover(self, filters=None):
        """Return mock federal opportunities."""
        self.logger.info("MOCK MODE: Returning simulated SAM.gov opportunities")
        
        return [
            GrantOpportunity(
                id="SAM-2024-001",
                title="CMS Medicaid Innovation Accelerator Program",
                agency="Centers for Medicare & Medicaid Services",
                description="Federal initiative supporting state Medicaid innovation in policy monitoring and regulatory analysis.",
                eligibility="State Agencies, Higher Education Institutions, Research Organizations",
                deadline=datetime.now() + timedelta(days=180),
                funding_source=FundingSource.FEDERAL_SAM_GOV,
                url="https://sam.gov/opp/abc123/view",
                raw_text="Federal CMS Medicaid innovation policy monitoring regulatory analysis higher education research"
            ),
            GrantOpportunity(
                id="SAM-2024-002",
                title="HRSA Rural Health Policy Analysis",
                agency="Health Resources and Services Administration",
                description="Rural health policy research and healthcare infrastructure evaluation.",
                eligibility="Public and Nonprofit Institutions of Higher Education",
                deadline=datetime.now() + timedelta(days=150),
                funding_source=FundingSource.FEDERAL_SAM_GOV,
                url="https://sam.gov/opp/def456/view",
                raw_text="Federal HRSA rural health policy healthcare infrastructure higher education"
            ),
            GrantOpportunity(
                id="SAM-2024-003",
                title="Defense Advanced Research Projects (Filtered)",
                agency="Department of Defense",
                description="Advanced technology research for defense applications.",
                eligibility="Defense Contractors, Research Labs",
                deadline=datetime.now() + timedelta(days=200),
                funding_source=FundingSource.FEDERAL_SAM_GOV,
                url="https://sam.gov/opp/ghi789/view",
                raw_text="Federal defense technology research contractors"  # No higher ed ref - should be filtered
            ),
        ]


def run_demo_ingestion():
    """Run the complete live ingestion pipeline with demo data."""
    print("\n" + "="*80)
    print("MPART @ UIS LIVE GRANT INGESTION PIPELINE (DEMO MODE)")
    print("="*80)
    print("\nNote: Using mock data for demonstration.")
    print("Set DATA_GOV_API_KEY environment variable for live SAM.gov queries.\n")
    
    # Initialize pipeline
    pipeline = GrantDiscoveryPipeline()
    
    # Register mock sources
    pipeline.register_source(MockGATAScraper())
    pipeline.register_source(MockSAMSource())
    
    # Run discovery with DeepResearch trigger at >80
    print("Starting live data collection...\n")
    results = pipeline.discover_all(trigger_deep_research_at=80)
    
    # Aggregate results
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
    
    # Sort by score descending
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
    
    # Display Top Matches
    print("\n" + "="*80)
    print("TOP MATCHES FOR MPART @ UIS")
    print("="*80)
    print(f"{'Rank':<6} {'Source':<20} {'Score':>6} {'DeepResearch':>12} {'Title':<40}")
    print("-"*80)
    
    top_grants = [g for g in all_grants if g.passes_prefilter][:10]
    
    for i, grant in enumerate(top_grants, 1):
        source_short = grant.funding_source.value.replace("_", " ").title()[:18]
        dr_status = "✓ TRIGGERED" if grant.deep_research_triggered else "-"
        title_short = (grant.title[:37] + "...") if len(grant.title) > 37 else grant.title
        print(f"{i:<6} {source_short:<20} {grant.keyword_score:>6} {dr_status:>12} {title_short:<40}")
    
    # Display Mercenary Recommendations for Triggered Grants
    triggered_grants = [g for g in all_grants if g.deep_research_triggered]
    
    if triggered_grants:
        print("\n" + "="*80)
        print("DEEPRESEARCH TRIGGERED - MERCENARY ASSIGNMENTS")
        print("="*80)
        print(f"{'Grant ID':<15} {'Score':>6} {'Recommended Lead':<30} {'Keywords Matched':<30}")
        print("-"*80)
        
        for grant in triggered_grants:
            # Simulate Mercenary matching based on content
            text = f"{grant.title} {grant.description}".lower()
            
            if "policy" in text and ("state" in text or "variation" in text or "jurisdiction" in text):
                lead = "mercenary_policy (State Policy Expert)"
                keywords = "state policy, medicaid variations"
            elif "monitoring" in text or "data" in text or "automation" in text:
                lead = "mercenary_data (AI/Data Expert)"
                keywords = "policy monitoring, regulatory tracking"
            elif "rural" in text or "infrastructure" in text or "evaluation" in text:
                lead = "mercenary_eval (Rural/Govt Eval)"
                keywords = "rural health, infrastructure"
            else:
                lead = "mercenary_policy (Default)"
                keywords = "general policy alignment"
            
            grant.recommended_lead = lead
            print(f"{grant.id:<15} {grant.keyword_score:>6} {lead:<30} {keywords:<30}")
    
    # Save ingestion results
    output_file = "data/live_ingestion_results.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    output_data = {
        "metadata": {
            "ingestion_timestamp": datetime.now().isoformat(),
            "pipeline_version": "2.0-live-demo",
            "deep_research_threshold": 80,
            "mode": "demo"
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
    
    # Also generate mpart_matches.json in demo mode
    print("Generating mpart_matches.json (demo mode)...")
    sys.path.insert(0, os.path.dirname(__file__))
    from mpart_adapter import create_adapter
    
    adapter = create_adapter(enable_deep_research=False)
    adapter.initialize()
    
    # Match the grants
    matches = adapter.match_grants([g for g in all_grants if g.passes_prefilter])
    
    adapter.save_matches(
        matches,
        "data/mpart_matches.json",
        mode="demo",
        sources=["Mock GATA Scraper", "Mock SAM Source"]
    )
    
    print(f"✅ mpart_matches.json saved (demo mode)")
    print(f"   File: data/mpart_matches.json")
    print(f"   Matches: {len(matches)}")
    
    # Summary
    print("\n📊 INGESTION COMPLETE")
    print(f"   • Total opportunities collected: {total_stats['total']}")
    print(f"   • Passed MPART pre-filter: {total_stats['passed']}")
    print(f"   • High-score matches (>80): {total_stats['high_score']}")
    print(f"   • DeepResearch triggered: {total_stats['triggered']}")
    
    return results


if __name__ == "__main__":
    run_demo_ingestion()
