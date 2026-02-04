#!/usr/bin/env python3
"""
Student Briefing Script for MPART @ UIS Grant Matches

This script provides a student-friendly view of the latest grant matches,
showing priority opportunities and recommended Mercenary leads.

Usage:
    python src/student_briefing.py
"""

import json
import sys
from datetime import datetime
from pathlib import Path


def load_matches():
    """Load the latest matches from the data file."""
    matches_file = Path(__file__).parent.parent / "data" / "mpart_matches.json"
    
    if not matches_file.exists():
        print("❌ No matches file found. Run the scout first:")
        print("   python src/scout_il.py --live")
        sys.exit(1)
    
    with open(matches_file) as f:
        return json.load(f)


def load_live_results():
    """Load the live ingestion results if available."""
    results_file = Path(__file__).parent.parent / "data" / "live_ingestion_results.json"
    
    if results_file.exists():
        with open(results_file) as f:
            return json.load(f)
    return None


def get_mercenary_icon(mercenary_id):
    """Get a visual icon for each Mercenary type."""
    icons = {
        "mercenary_policy": "📋",  # Clipboard for policy
        "mercenary_data": "🔬",     # Microscope for data/research
        "mercenary_eval": "🏥",     # Hospital for health eval
        "": "❓"
    }
    return icons.get(mercenary_id, "❓")


def get_mercenary_name(mercenary_id):
    """Get human-readable name for Mercenary ID."""
    names = {
        "mercenary_policy": "Policy Expert",
        "mercenary_data": "Data/AI Expert", 
        "mercenary_eval": "Rural/Eval Expert",
        "": "Not assigned"
    }
    return names.get(mercenary_id, "Unknown")


def format_date(date_str):
    """Format ISO date string for display."""
    if not date_str:
        return "No deadline"
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%b %d, %Y")
    except:
        return date_str[:10] if date_str else "Unknown"


def print_header():
    """Print the briefing header."""
    print("\n" + "="*80)
    print("📊 MPART @ UIS STUDENT BRIEFING".center(80))
    print("Latest Grant Opportunities for Medical Policy Applied Research Team".center(80))
    print("="*80 + "\n")


def print_summary(data, live_results):
    """Print summary statistics."""
    print("📈 SUMMARY")
    print("-"*80)
    
    if live_results:
        meta = live_results.get("metadata", {})
        summary = live_results.get("summary", {})
        
        print(f"  Last Updated:     {meta.get('ingestion_timestamp', 'Unknown')[:19]}")
        print(f"  Total Leads:      {summary.get('total', 0)}")
        print(f"  Passed Filter:    {summary.get('passed', 0)}")
        print(f"  High Priority:    {summary.get('high_score', 0)} (Score > 80)")
        print(f"  DeepResearch:     {summary.get('triggered', 0)} triggered")
    
    # Count by Mercenary
    matches = data.get("matches", [])
    mercenary_counts = {}
    for match in matches:
        lead = match.get("recommended_lead", "")
        mercenary_counts[lead] = mercenary_counts.get(lead, 0) + 1
    
    print(f"\n  📋 Lead Assignments:")
    for merc_id, count in sorted(mercenary_counts.items(), key=lambda x: x[1], reverse=True):
        if merc_id:
            icon = get_mercenary_icon(merc_id)
            name = get_mercenary_name(merc_id)
            print(f"     {icon} {name}: {count} leads")
    
    print()


def print_high_priority_matches(data):
    """Print high priority matches (score > 80 or DeepResearch triggered)."""
    matches = data.get("matches", [])
    
    # Filter to high priority
    high_priority = [
        m for m in matches 
        if m.get("match_score", 0) > 80 or m.get("deep_research_triggered", False)
    ]
    
    if not high_priority:
        print("⚠️  No high-priority matches found today.")
        return
    
    print("🎯 HIGH PRIORITY MATCHES (Score > 80)")
    print("-"*80)
    
    for i, match in enumerate(high_priority[:5], 1):
        score = match.get("match_score", 0)
        title = match.get("grant_title", "Untitled")
        agency = match.get("agency", "Unknown Agency")
        deadline = format_date(match.get("deadline"))
        lead = match.get("recommended_lead", "")
        
        icon = get_mercenary_icon(lead)
        lead_name = get_mercenary_name(lead)
        
        # Score bar
        score_bar = "█" * (score // 10) + "░" * (10 - (score // 10))
        
        print(f"\n  #{i} [{score_bar}] {score}/100")
        print(f"     📌 {title[:65]}{'...' if len(title) > 65 else ''}")
        print(f"     🏢 {agency[:60]}")
        print(f"     ⏰ Deadline: {deadline}")
        print(f"     {icon} Recommended Lead: {lead_name}")
        
        # Show alignment points if available
        alignment = match.get("alignment_points", [])
        if alignment:
            print(f"     ✓ Key Alignment:")
            for point in alignment[:2]:
                print(f"       • {point[:55]}{'...' if len(point) > 55 else ''}")
    
    print()


def print_all_matches(data):
    """Print all matches in a compact table format."""
    matches = data.get("matches", [])
    
    if not matches:
        print("No matches found.")
        return
    
    print("📋 ALL MATCHES")
    print("-"*80)
    print(f"{'#':<4} {'Score':>6} {'Lead':<12} {'Deadline':<12} {'Title':<35}")
    print("-"*80)
    
    for i, match in enumerate(matches[:20], 1):  # Show top 20
        score = match.get("match_score", 0)
        title = match.get("grant_title", "Untitled")
        deadline = format_date(match.get("deadline"))
        lead = match.get("recommended_lead", "")
        
        # Short lead name
        lead_short = {
            "mercenary_policy": "POLICY",
            "mercenary_data": "DATA",
            "mercenary_eval": "EVAL",
            "": "NONE"
        }.get(lead, "?")
        
        # Truncate title
        title_short = title[:32] + "..." if len(title) > 32 else title
        
        print(f"{i:<4} {score:>6} {lead_short:<12} {deadline:<12} {title_short:<35}")
    
    if len(matches) > 20:
        print(f"\n... and {len(matches) - 20} more matches")
    
    print()


def print_next_steps():
    """Print recommended next steps for students."""
    print("📝 NEXT STEPS FOR STUDENTS")
    print("-"*80)
    print("""
  1. Review HIGH PRIORITY matches above (Score > 80)
  
  2. Check your assigned Mercenary lead:
     📋 Policy Expert → State variations, 1115 Waivers, regulatory analysis
     🔬 Data Expert   → AI monitoring, document collection, automation
     🏥 Eval Expert   → Rural health, infrastructure impact, government eval
  
  3. For each high-priority match:
     • Click the grant URL to read full details
     • Check eligibility requirements carefully
     • Note the deadline and required documents
  
  4. Prepare briefing for MPART team:
     • Summarize top 3 opportunities
     • Highlight alignment with MPART pillars
     • Recommend which Mercenary should lead
  
  5. Questions? Check the full data:
     cat data/mpart_matches.json | python3 -m json.tool | less
""")


def main():
    """Main briefing function."""
    print_header()
    
    # Load data
    try:
        data = load_matches()
        live_results = load_live_results()
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        sys.exit(1)
    
    # Print sections
    print_summary(data, live_results)
    print_high_priority_matches(data)
    print_all_matches(data)
    print_next_steps()
    
    print("="*80)
    print("End of briefing. Run this script anytime with: python src/student_briefing.py")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
