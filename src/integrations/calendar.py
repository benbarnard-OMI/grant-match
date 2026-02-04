"""
Calendar integration for grant deadlines.

Supports:
- iCalendar (.ics) export
- Google Calendar API
- Outlook/Exchange
- Deadline reminders
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional


logger = logging.getLogger(__name__)


class DeadlineManager:
    """
    Manages grant deadlines and reminders.
    
    Tracks upcoming deadlines and generates reminder schedules.
    """
    
    def __init__(self):
        self.reminder_days = [30, 14, 7, 3, 1]  # Days before deadline to remind
    
    def get_upcoming_deadlines(self, decisions: List[Dict], 
                               days_ahead: int = 90) -> List[Dict]:
        """
        Get deadlines coming up within specified days.
        
        Args:
            decisions: List of grant decisions
            days_ahead: How many days ahead to look
            
        Returns:
            List of deadlines with urgency info
        """
        upcoming = []
        now = datetime.now()
        cutoff = now + timedelta(days=days_ahead)
        
        for decision in decisions:
            deadline_str = decision.get('application_deadline')
            if not deadline_str:
                continue
            
            try:
                deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
                
                if now <= deadline <= cutoff:
                    days_until = (deadline - now).days
                    
                    urgency = 'normal'
                    if days_until <= 7:
                        urgency = 'critical'
                    elif days_until <= 14:
                        urgency = 'high'
                    elif days_until <= 30:
                        urgency = 'medium'
                    
                    upcoming.append({
                        'grant_id': decision.get('grant_id'),
                        'title': decision.get('grant_title'),
                        'deadline': deadline.isoformat(),
                        'days_until': days_until,
                        'urgency': urgency,
                        'status': decision.get('status'),
                        'lead': decision.get('assigned_lead', 'Unassigned')
                    })
                    
            except Exception as e:
                logger.debug(f"Error parsing deadline: {e}")
        
        return sorted(upcoming, key=lambda x: x['days_until'])
    
    def get_reminders_for_today(self, decisions: List[Dict]) -> List[Dict]:
        """Get reminders that should be sent today."""
        reminders = []
        
        for decision in decisions:
            deadline_str = decision.get('application_deadline')
            if not deadline_str:
                continue
            
            try:
                deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
                days_until = (deadline - datetime.now()).days
                
                if days_until in self.reminder_days:
                    reminders.append({
                        'grant_id': decision.get('grant_id'),
                        'title': decision.get('grant_title'),
                        'deadline': deadline.isoformat(),
                        'days_until': days_until,
                        'message': self._generate_reminder_message(decision, days_until)
                    })
            except:
                continue
        
        return reminders
    
    def _generate_reminder_message(self, decision: Dict, days_until: int) -> str:
        """Generate reminder message text."""
        urgency_word = "URGENT" if days_until <= 7 else "Reminder"
        
        return (f"{urgency_word}: '{decision.get('grant_title')}' "
                f"deadline is in {days_until} day{'s' if days_until != 1 else ''} "
                f"({decision.get('application_deadline', 'unknown date')})")


class CalendarIntegration:
    """
    Integration with calendar systems for deadline management.
    
    Supports iCalendar export and direct API integration.
    """
    
    def __init__(self):
        self.deadline_manager = DeadlineManager()
    
    def generate_ics(self, decisions: List[Dict], 
                    output_path: Optional[str] = None) -> str:
        """
        Generate iCalendar (.ics) file for deadlines.
        
        Args:
            decisions: List of grant decisions with deadlines
            output_path: Where to save the .ics file
            
        Returns:
            Path to generated file
        """
        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d')
            output_path = f"data/mpart_deadlines_{timestamp}.ics"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        ics_content = self._build_ics_content(decisions)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(ics_content)
        
        logger.info(f"Generated ICS file: {output_path}")
        return str(output_path)
    
    def _build_ics_content(self, decisions: List[Dict]) -> str:
        """Build iCalendar format content."""
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//MPART@UIS//Grant Deadlines//EN",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
            "X-WR-CALNAME:MPART Grant Deadlines",
            "X-WR-TIMEZONE:America/Chicago"
        ]
        
        for decision in decisions:
            deadline_str = decision.get('application_deadline')
            if not deadline_str:
                continue
            
            try:
                deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
                
                # Create event
                uid = f"{decision.get('grant_id')}@mpart-uis"
                dtstamp = datetime.now().strftime('%Y%m%dT%H%M%SZ')
                dtstart = deadline.strftime('%Y%m%d')
                
                summary = f"DEADLINE: {decision.get('grant_title', 'Grant')[:50]}"
                description = f"Grant Deadline\\nAgency: {decision.get('agency', 'Unknown')}\\nLead: {decision.get('assigned_lead', 'Unassigned')}"
                
                lines.extend([
                    "BEGIN:VEVENT",
                    f"UID:{uid}",
                    f"DTSTAMP:{dtstamp}",
                    f"DTSTART;VALUE=DATE:{dtstart}",
                    f"SUMMARY:{summary}",
                    f"DESCRIPTION:{description}",
                    "STATUS:CONFIRMED",
                    "TRANSP:TRANSPARENT",
                    "BEGIN:VALARM",
                    "ACTION:DISPLAY",
                    "DESCRIPTION:Reminder",
                    "TRIGGER:-P7D",  # 7 days before
                    "END:VALARM",
                    "END:VEVENT"
                ])
            except:
                continue
        
        lines.append("END:VCALENDAR")
        
        return "\r\n".join(lines)
    
    def generate_google_calendar_link(self, decision: Dict) -> str:
        """
        Generate Google Calendar 'Add to Calendar' link.
        
        Args:
            decision: Grant decision with deadline
            
        Returns:
            Google Calendar URL
        """
        from urllib.parse import quote
        
        deadline_str = decision.get('application_deadline')
        if not deadline_str:
            return ""
        
        try:
            deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
            
            title = quote(f"DEADLINE: {decision.get('grant_title', 'Grant')}")
            details = quote(f"Grant Application Deadline\\nAgency: {decision.get('agency', 'Unknown')}")
            
            # Format dates for Google Calendar
            dates = deadline.strftime('%Y%m%d') + "/" + deadline.strftime('%Y%m%d')
            
            return f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={title}&details={details}&dates={dates}"
        except:
            return ""
    
    def sync_to_google_calendar(self, decisions: List[Dict],
                               calendar_id: str = "primary") -> bool:
        """
        Sync deadlines to Google Calendar via API.

        Requires GOOGLE_CREDENTIALS environment variable.

        Args:
            decisions: List of decisions to sync
            calendar_id: Google Calendar ID

        Returns:
            True if successful
        """
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build

            # This would need proper setup with credentials
            # Placeholder for the implementation
            logger.info("Google Calendar sync would require API credentials setup")
            return False

        except ImportError:
            logger.warning("Google Calendar API not available. Install: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
            return False


def generate_deadline_calendar(matches_file: str = "data/mpart_matches.json",
                               output_path: Optional[str] = None,
                               min_score: int = 50) -> str:
    """
    Convenience function to generate calendar from matches.

    Args:
        matches_file: Path to matches JSON
        output_path: Output ICS file path
        min_score: Minimum match score to include

    Returns:
        Path to generated ICS file
    """
    matches_path = Path(matches_file)
    if not matches_path.exists():
        raise FileNotFoundError(f"Matches file not found: {matches_file}")

    with open(matches_path) as f:
        data = json.load(f)

    # Convert matches to decision format
    decisions = []
    for match in data.get('matches', []):
        if match.get('match_score', 0) >= min_score and match.get('deadline'):
            decisions.append({
                'grant_id': match.get('grant_id'),
                'grant_title': match.get('grant_title'),
                'application_deadline': match.get('deadline'),
                'agency': match.get('agency'),
                'assigned_lead': match.get('recommended_lead'),
                'status': 'new'
            })

    calendar = CalendarIntegration()
    return calendar.generate_ics(decisions, output_path=output_path)


if __name__ == '__main__':
    # Test calendar generation
    try:
        output = generate_deadline_calendar()
        print(f"✓ Calendar generated: {output}")
    except FileNotFoundError:
        print("❌ No matches file found.")
