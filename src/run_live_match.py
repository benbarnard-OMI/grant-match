#!/usr/bin/env python3
"""
Live Match Pipeline for MPART @ UIS

Runs the complete end-to-end pipeline:
1. Discovers grants from live sources (GATA + SAM + optional foundations)
2. Matches against MPART profile
3. Saves results to mpart_matches.json with provenance metadata

Usage:
    python src/run_live_match.py [--foundations] [--output PATH]

Environment Variables:
    DATA_GOV_API_KEY - Required for SAM.gov access
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from scout_il import SAMSource, create_mpart_pipeline
from mpart_adapter import create_adapter


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_live_match_pipeline(
    include_foundations: bool = False,
    output_path: str = "data/mpart_matches.json",
    enable_deep_research: bool = False
) -> dict:
    """
    Run the complete live match pipeline.
    
    Args:
        include_foundations: Whether to include foundation sources (RWJF, etc.)
        output_path: Where to save mpart_matches.json
        enable_deep_research: Whether to enable AI deep research
        
    Returns:
        Dict with pipeline results and metadata
    """
    print("\n" + "="*80)
    print("🚀 MPART @ UIS LIVE MATCH PIPELINE")
    print("="*80 + "\n")
    
    # Step 1: Create pipeline with live sources
    logger.info("Initializing grant discovery pipeline...")
    pipeline = create_mpart_pipeline(include_foundations=include_foundations)
    
    # Check SAM.gov availability
    sam_source = SAMSource()
    if not sam_source.api_key:
        logger.warning("DATA_GOV_API_KEY not set - SAM.gov source skipped")
    
    # Step 2: Run discovery
    logger.info("Running grant discovery...")
    discovery_results = pipeline.discover_all(apply_prefilter=False)
    
    # Collect all grants
    all_grants = []
    for source_name, grants in discovery_results.items():
        all_grants.extend(grants)
    
    sources_used = list(discovery_results.keys())
    
    logger.info(f"Discovery complete: {len(all_grants)} total from {len(sources_used)} sources")
    
    # Step 3: Run matching
    logger.info("Initializing MPART matching adapter...")
    adapter = create_adapter(enable_deep_research=enable_deep_research)
    adapter.initialize()
    
    logger.info(f"Matching {len(all_grants)} grants against MPART profile...")
    matches = adapter.match_grants(all_grants)
    
    logger.info(f"Matching complete: {len(matches)} results")
    
    # Step 4: Save with provenance metadata
    logger.info(f"Saving results to {output_path}...")
    
    # Ensure output directory exists
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    adapter.save_matches(
        matches,
        output_path,
        mode="live",
        sources=sources_used
    )
    
    logger.info(f"✅ Results saved to {output_path}")
    
    # Return summary
    return {
        'success': True,
        'output_path': output_path,
        'sources_used': sources_used,
        'total_discovered': len(all_grants),
        'total_matches': len(matches),
        'high_priority': sum(1 for m in matches if m.match_score >= 80),
        'metadata': {
            'mode': 'live',
            'sources': sources_used
        }
    }


def validate_output(output_path: str) -> bool:
    """
    Validate that the output file exists and is valid.
    
    Args:
        output_path: Path to mpart_matches.json
        
    Returns:
        True if valid, raises exception otherwise
    """
    path = Path(output_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Output file not found: {output_path}")
    
    with open(path) as f:
        data = json.load(f)
    
    if not data.get('matches'):
        logger.warning("Output file has no matches")
    
    if data.get('metadata', {}).get('mode') != 'live':
        logger.warning("Output file is not marked as 'live' mode")
    
    logger.info(f"✅ Output validation passed: {len(data['matches'])} matches")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Run live match pipeline for MPART @ UIS'
    )
    parser.add_argument(
        '--foundations', 
        action='store_true',
        help='Include foundation sources (RWJF, Commonwealth, AcademyHealth)'
    )
    parser.add_argument(
        '--output',
        default='data/mpart_matches.json',
        help='Output path for matches JSON (default: data/mpart_matches.json)'
    )
    parser.add_argument(
        '--deep-research',
        action='store_true',
        help='Enable AI deep research (slower, more expensive)'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate output after generation'
    )
    
    args = parser.parse_args()
    
    # Check for API key
    if not os.getenv('DATA_GOV_API_KEY'):
        logger.warning("DATA_GOV_API_KEY not set - SAM.gov source will be skipped")
    
    try:
        # Run pipeline
        result = run_live_match_pipeline(
            include_foundations=args.foundations,
            output_path=args.output,
            enable_deep_research=args.deep_research
        )
        
        # Print summary
        print("\n" + "="*80)
        print("📊 PIPELINE SUMMARY")
        print("="*80)
        print(f"Sources used:     {', '.join(result['sources_used'])}")
        print(f"Grants discovered: {result['total_discovered']}")
        print(f"Total matches:    {result['total_matches']}")
        print(f"High priority:    {result['high_priority']}")
        print(f"Output file:      {result['output_path']}")
        print(f"Mode:             {result['metadata']['mode']}")
        print("="*80 + "\n")
        
        # Validate if requested
        if args.validate:
            validate_output(args.output)
            print("✅ Validation passed\n")
        
        return 0
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        print(f"\n❌ ERROR: {e}\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
