#!/usr/bin/env python3
"""
Enhanced Student Briefing Script for MPART @ UIS Grant Matches

New features:
- Email notifications
- Excel/CSV export
- Decision tracking integration
- Deadline calendar generation
- Multi-source aggregation

Usage:
    python src/student_briefing_v2.py [options]

Options:
    --email           Send digest via email
    --excel           Export to Excel
    --csv             Export to CSV
    --calendar        Generate calendar file
    --min-score N     Filter by minimum score
    --status STATUS   Filter by decision status
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def load_data():
    """Load matches and decisions data."""
    matches_file = Path("data/mpart_matches.json")
    decisions_file = Path("data/grant_decisions.json")
    
    matches = []
    decisions = {}
    
    if matches_file.exists():
        with open(matches_file) as f:
            data = json.load(f)
            matches = data.get('matches', [])
    
    if decisions_file.exists():
        with open(decisions_file) as f:
            data = json.load(f)
            for d in data.get('decisions', []):
                decisions[d['grant_id']] = d
    
    return matches, decisions


def filter_matches(matches, decisions, min_score=0, status_filter=None):
    """Filter matches based on criteria."""
    filtered = matches
    
    if min_score > 0:
        filtered = [m for m in filtered if m.get('match_score', 0) >= min_score]
    
    if status_filter:
        filtered = [
            m for m in filtered 
            if decisions.get(m['grant_id'], {}).get('status') in status_filter
        ]
    
    return filtered


def print_header():
    """Print formatted header."""
    print("\n" + "="*80)
    print("📊 MPART @ UIS GRANT BRIEFING v2.0".center(80))
    print("Medical Policy Applied Research Team".center(80))
    print("="*80 + "\n")


def print_summary(matches, decisions):
    """Print summary statistics."""
    total = len(matches)
    high = len([m for m in matches if m.get('match_score', 0) >= 80])
    medium = len([m for m in matches if 50 <= m.get('match_score', 0) < 80])
    
    # Count by status
    status_counts = {}
    for m in matches:
        status = decisions.get(m['grant_id'], {}).get('status', 'new')
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print("📈 SUMMARY")
    print("-"*80)
    print(f"  Total Matches:     {total}")
    print(f"  🔴 High Priority:   {high}")
    print(f"  🟡 Medium Priority: {medium}")
    print()
    
    if status_counts:
        print("  Status Breakdown:")
        for status, count in sorted(status_counts.items()):
            print(f"    • {status.replace('_', ' ').title()}: {count}")
    print()


def print_high_priority(matches, decisions, limit=10):
    """Print high priority matches."""
    high_priority = [m for m in matches if m.get('match_score', 0) >= 80]
    high_priority.sort(key=lambda x: x.get('match_score', 0), reverse=True)
    
    if not high_priority:
        print("⚠️  No high-priority matches found.\n")
        return
    
    print(f"🎯 TOP {min(limit, len(high_priority))} HIGH-PRIORITY MATCHES")
    print("-"*80)
    
    for i, match in enumerate(high_priority[:limit], 1):
        score = match.get('match_score', 0)
        title = match.get('grant_title', 'Untitled')
        agency = match.get('agency', 'Unknown')
        lead = match.get('recommended_lead', 'Unassigned')
        deadline = match.get('deadline', 'Not specified')
        
        lead_display = {
            'mercenary_policy': '📋 Policy',
            'mercenary_data': '🔬 Data',
            'mercenary_eval': '🏥 Rural/Eval'
        }.get(lead, '❓ Unassigned')
        
        status = decisions.get(match['grant_id'], {}).get('status', 'new')
        status_icon = {
            'new': '○',
            'under_review': '◐',
            'pursuing': '●',
            'not_pursuing': '✗',
            'submitted': '✓',
            'awarded': '★'
        }.get(status, '○')
        
        print(f"\n{i}. [{status_icon}] {title[:60]}{'...' if len(title) > 60 else ''}")
        print(f"   Score: {score}/100 | {lead_display}")
        print(f"   Agency: {agency}")
        print(f"   Deadline: {deadline}")
        
        rationale = match.get('rationale', '')
        if rationale:
            print(f"   Why: {rationale[:100]}...")
    
    print("\n")


def print_actions():
    """Print available actions."""
    print("📝 AVAILABLE ACTIONS")
    print("-"*80)
    print("""
  1. View details:    python src/student_briefing_v2.py --details GRANT_ID
  2. Update status:   python src/tracking/decision_tracker.py --update GRANT_ID --status STATUS
  3. Export Excel:    python src/export/excel_exporter.py
  4. Send email:      python src/notifications/email_notifier.py --digest
  5. View calendar:   python src/integrations/calendar.py
  6. Run dashboard:   streamlit run src/dashboard/app.py
""")


def send_email_digest(matches, args):
    """Send email digest."""
    try:
        from notifications import EmailNotifier
        
        notifier = EmailNotifier()
        
        stats = {
            'total_matches': len(matches),
            'high_priority': len([m for m in matches if m.get('match_score', 0) >= 80]),
            'medium_priority': len([m for m in matches if 50 <= m.get('match_score', 0) < 80])
        }
        
        success = notifier.send_digest(matches, stats)
        
        if success:
            print("✅ Email digest sent successfully")
        else:
            print("❌ Failed to send email digest")
            
    except ImportError as e:
        logger.error(f"Email module not available: {e}")


def export_excel(matches):
    """Export to Excel."""
    try:
        from export import ExcelExporter
        
        exporter = ExcelExporter()
        filepath = exporter.export(matches)
        print(f"✅ Excel exported to: {filepath}")
        
    except ImportError as e:
        logger.error(f"Export module not available: {e}")


def export_csv(matches):
    """Export to CSV."""
    try:
        from export import CSVExporter
        
        exporter = CSVExporter()
        filepath = exporter.export(matches)
        print(f"✅ CSV exported to: {filepath}")
        
    except ImportError as e:
        logger.error(f"Export module not available: {e}")


def generate_calendar(matches):
    """Generate calendar file."""
    try:
        from integrations import CalendarIntegration
        
        # Only include high-priority matches with deadlines
        decisions = [
            {
                'grant_id': m['grant_id'],
                'grant_title': m['grant_title'],
                'application_deadline': m.get('deadline'),
                'agency': m.get('agency'),
                'assigned_lead': m.get('recommended_lead')
            }
            for m in matches
            if m.get('match_score', 0) >= 50 and m.get('deadline')
        ]
        
        calendar = CalendarIntegration()
        filepath = calendar.generate_ics(decisions)
        print(f"✅ Calendar exported to: {filepath}")
        
    except ImportError as e:
        logger.error(f"Calendar module not available: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='MPART Grant Briefing System v2.0'
    )
    parser.add_argument('--email', action='store_true', 
                       help='Send email digest')
    parser.add_argument('--excel', action='store_true',
                       help='Export to Excel')
    parser.add_argument('--csv', action='store_true',
                       help='Export to CSV')
    parser.add_argument('--calendar', action='store_true',
                       help='Generate calendar file')
    parser.add_argument('--min-score', type=int, default=0,
                       help='Minimum match score filter')
    parser.add_argument('--status', nargs='+',
                       help='Filter by status (new, pursuing, submitted, etc.)')
    parser.add_argument('--limit', type=int, default=10,
                       help='Limit number of high-priority matches shown')
    
    args = parser.parse_args()
    
    # Load data
    matches, decisions = load_data()
    
    if not matches:
        print("❌ No matches found. Run discovery first:")
        print("   python src/scout_il.py --live")
        sys.exit(1)
    
    # Filter matches
    filtered = filter_matches(matches, decisions, args.min_score, args.status)
    
    # Execute requested actions
    if args.email:
        send_email_digest(filtered, args)
        return
    
    if args.excel:
        export_excel(filtered)
        return
    
    if args.csv:
        export_csv(filtered)
        return
    
    if args.calendar:
        generate_calendar(filtered)
        return
    
    # Default: print briefing
    print_header()
    print_summary(filtered, decisions)
    print_high_priority(filtered, decisions, args.limit)
    print_actions()


if __name__ == '__main__':
    main()
