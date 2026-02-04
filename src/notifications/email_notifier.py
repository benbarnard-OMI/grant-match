"""
Email notification system for MPART grant matches.

Supports SMTP, SendGrid, and console output (for testing).
"""

import os
import json
import logging
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class NotificationConfig:
    """Configuration for email notifications."""
    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True
    from_address: str = "mpart-grants@uis.edu"
    to_addresses: List[str] = None
    cc_addresses: List[str] = None
    high_priority_threshold: int = 80
    send_daily_digest: bool = True
    send_immediate_alerts: bool = False  # For score > 95
    
    def __post_init__(self):
        if self.to_addresses is None:
            self.to_addresses = []
        if self.cc_addresses is None:
            self.cc_addresses = []


class EmailNotifier:
    """
    Sends email notifications for grant matches.
    
    Supports multiple backends:
    - SMTP (institutional email)
    - SendGrid (cloud)
    - Console (testing)
    """
    
    def __init__(self, config: Optional[NotificationConfig] = None):
        self.config = config or self._load_config_from_env()
        self.backend = self._detect_backend()
        
    def _load_config_from_env(self) -> NotificationConfig:
        """Load configuration from environment variables."""
        return NotificationConfig(
            smtp_host=os.getenv('SMTP_HOST', 'localhost'),
            smtp_port=int(os.getenv('SMTP_PORT', '587')),
            smtp_username=os.getenv('SMTP_USERNAME', ''),
            smtp_password=os.getenv('SMTP_PASSWORD', ''),
            smtp_use_tls=os.getenv('SMTP_USE_TLS', 'true').lower() == 'true',
            from_address=os.getenv('FROM_ADDRESS', 'mpart-grants@uis.edu'),
            to_addresses=os.getenv('TO_ADDRESSES', '').split(',') if os.getenv('TO_ADDRESSES') else [],
            cc_addresses=os.getenv('CC_ADDRESSES', '').split(',') if os.getenv('CC_ADDRESSES') else [],
            high_priority_threshold=int(os.getenv('HIGH_PRIORITY_THRESHOLD', '80')),
            send_daily_digest=os.getenv('SEND_DAILY_DIGEST', 'true').lower() == 'true',
            send_immediate_alerts=os.getenv('SEND_IMMEDIATE_ALERTS', 'false').lower() == 'true'
        )
    
    def _detect_backend(self) -> str:
        """Detect which email backend to use."""
        if os.getenv('SENDGRID_API_KEY'):
            return 'sendgrid'
        elif os.getenv('CONSOLE_EMAIL', 'false').lower() == 'true':
            return 'console'
        else:
            return 'smtp'
    
    def send_digest(self, matches: List[Dict], 
                   stats: Dict[str, Any],
                   recipient_override: Optional[str] = None) -> bool:
        """
        Send daily digest email with grant matches.
        
        Args:
            matches: List of match results
            stats: Summary statistics
            recipient_override: Send to specific address (for testing)
            
        Returns:
            True if sent successfully
        """
        if not self.config.send_daily_digest:
            logger.info("Daily digest disabled in configuration")
            return False
            
        to_addresses = [recipient_override] if recipient_override else self.config.to_addresses
        
        if not to_addresses:
            logger.warning("No recipients configured for digest")
            return False
        
        subject = f"MPART Grant Digest: {stats.get('high_priority', 0)} High-Priority Matches"
        
        html_body = self._generate_digest_html(matches, stats)
        text_body = self._generate_digest_text(matches, stats)
        
        return self._send_email(to_addresses, subject, text_body, html_body)
    
    def send_immediate_alert(self, match: Dict, 
                            recipient_override: Optional[str] = None) -> bool:
        """
        Send immediate alert for very high-priority match (score > 95).
        
        Args:
            match: Single high-priority match
            recipient_override: Send to specific address (for testing)
            
        Returns:
            True if sent successfully
        """
        if not self.config.send_immediate_alerts:
            return False
            
        to_addresses = [recipient_override] if recipient_override else self.config.to_addresses
        
        if not to_addresses:
            return False
        
        subject = f"🚨 HIGH PRIORITY: {match.get('grant_title', 'Grant Opportunity')[:50]}"
        
        html_body = self._generate_alert_html(match)
        text_body = self._generate_alert_text(match)
        
        return self._send_email(to_addresses, subject, text_body, html_body)
    
    def _generate_digest_html(self, matches: List[Dict], 
                             stats: Dict[str, Any]) -> str:
        """Generate HTML email body for daily digest."""
        high_priority = [m for m in matches if m.get('match_score', 0) >= self.config.high_priority_threshold]
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background: #003366; color: white; padding: 20px; text-align: center; }}
                .summary {{ background: #f5f5f5; padding: 15px; margin: 20px 0; }}
                .match {{ border: 1px solid #ddd; margin: 15px 0; padding: 15px; border-radius: 5px; }}
                .high-priority {{ border-left: 5px solid #e74c3c; }}
                .medium-priority {{ border-left: 5px solid #f39c12; }}
                .low-priority {{ border-left: 5px solid #95a5a6; }}
                .score {{ font-size: 24px; font-weight: bold; color: #003366; }}
                .score-bar {{ background: #ecf0f1; height: 20px; border-radius: 10px; overflow: hidden; margin: 10px 0; }}
                .score-fill {{ background: linear-gradient(90deg, #e74c3c 0%, #f39c12 50%, #27ae60 100%); height: 100%; }}
                .lead-badge {{ display: inline-block; padding: 5px 10px; border-radius: 15px; font-size: 12px; margin: 5px 0; }}
                .lead-policy {{ background: #3498db; color: white; }}
                .lead-data {{ background: #9b59b6; color: white; }}
                .lead-eval {{ background: #27ae60; color: white; }}
                .deadline {{ color: #e74c3c; font-weight: bold; }}
                .footer {{ text-align: center; padding: 20px; color: #7f8c8d; font-size: 12px; }}
                .button {{ display: inline-block; padding: 10px 20px; background: #003366; color: white; 
                          text-decoration: none; border-radius: 5px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 MPART @ UIS Grant Digest</h1>
                <p>Daily Grant Opportunities - {datetime.now().strftime('%B %d, %Y')}</p>
            </div>
            
            <div class="summary">
                <h2>📈 Summary</h2>
                <ul>
                    <li><strong>Total Matches:</strong> {stats.get('total_matches', 0)}</li>
                    <li><strong>High Priority (>{self.config.high_priority_threshold}):</strong> {stats.get('high_priority', 0)}</li>
                    <li><strong>Medium Priority:</strong> {stats.get('medium_priority', 0)}</li>
                </ul>
            </div>
            
            <h2>🎯 High-Priority Matches</h2>
        """
        
        for match in high_priority[:5]:  # Top 5
            score = match.get('match_score', 0)
            score_class = 'high-priority' if score >= 80 else 'medium-priority' if score >= 50 else 'low-priority'
            lead = match.get('recommended_lead', '')
            lead_class = f"lead-{lead.replace('mercenary_', '')}" if lead else ''
            lead_name = {
                'mercenary_policy': '📋 Policy Expert',
                'mercenary_data': '🔬 Data/AI Expert',
                'mercenary_eval': '🏥 Rural/Eval Expert'
            }.get(lead, 'Not assigned')
            
            html += f"""
            <div class="match {score_class}">
                <div class="score">{score}/100</div>
                <div class="score-bar">
                    <div class="score-fill" style="width: {score}%"></div>
                </div>
                <h3>{match.get('grant_title', 'Untitled')}</h3>
                <p><strong>Agency:</strong> {match.get('agency', 'Unknown')}</p>
                <p class="deadline">⏰ Deadline: {match.get('deadline', 'Not specified')}</p>
                <span class="lead-badge {lead_class}">{lead_name}</span>
                <p><strong>Why this matches:</strong> {match.get('rationale', 'No rationale provided')[:150]}...</p>
            </div>
            """
        
        html += f"""
            <div class="footer">
                <p>MPART @ UIS Grant Match System</p>
                <p>Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><a href="https://github.com/your-org/grant-match">View on GitHub</a></p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _generate_digest_text(self, matches: List[Dict], 
                             stats: Dict[str, Any]) -> str:
        """Generate plain text email body for daily digest."""
        text = f"""MPART @ UIS Grant Digest
{'='*60}
Date: {datetime.now().strftime('%B %d, %Y')}

SUMMARY
- Total Matches: {stats.get('total_matches', 0)}
- High Priority (>{self.config.high_priority_threshold}): {stats.get('high_priority', 0)}
- Medium Priority: {stats.get('medium_priority', 0)}

HIGH-PRIORITY MATCHES
{'='*60}
"""
        
        high_priority = [m for m in matches if m.get('match_score', 0) >= self.config.high_priority_threshold]
        
        for i, match in enumerate(high_priority[:5], 1):
            text += f"""
{i}. {match.get('grant_title', 'Untitled')}
   Score: {match.get('match_score', 0)}/100
   Agency: {match.get('agency', 'Unknown')}
   Deadline: {match.get('deadline', 'Not specified')}
   Lead: {match.get('recommended_lead', 'Not assigned')}
   
   Why: {match.get('rationale', 'No rationale provided')[:200]}...

"""
        
        return text
    
    def _generate_alert_html(self, match: Dict) -> str:
        """Generate HTML for immediate high-priority alert."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .alert {{ background: #e74c3c; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .score {{ font-size: 48px; color: #e74c3c; }}
            </style>
        </head>
        <body>
            <div class="alert">
                <h1>🚨 HIGH PRIORITY GRANT ALERT</h1>
            </div>
            <div class="content">
                <div class="score">{match.get('match_score', 0)}/100</div>
                <h2>{match.get('grant_title', 'Untitled')}</h2>
                <p><strong>Agency:</strong> {match.get('agency', 'Unknown')}</p>
                <p><strong>Deadline:</strong> {match.get('deadline', 'Not specified')}</p>
                <p><strong>Recommended Lead:</strong> {match.get('recommended_lead', 'Not assigned')}</p>
                <p>{match.get('rationale', '')}</p>
            </div>
        </body>
        </html>
        """
    
    def _generate_alert_text(self, match: Dict) -> str:
        """Generate plain text for immediate alert."""
        return f"""🚨 HIGH PRIORITY GRANT ALERT

Score: {match.get('match_score', 0)}/100

{match.get('grant_title', 'Untitled')}

Agency: {match.get('agency', 'Unknown')}
Deadline: {match.get('deadline', 'Not specified')}
Recommended Lead: {match.get('recommended_lead', 'Not assigned')}

{match.get('rationale', '')}
"""
    
    def _send_email(self, to_addresses: List[str], subject: str, 
                   text_body: str, html_body: str) -> bool:
        """Send email using configured backend."""
        if self.backend == 'sendgrid':
            return self._send_sendgrid(to_addresses, subject, text_body, html_body)
        elif self.backend == 'console':
            return self._send_console(to_addresses, subject, text_body)
        else:
            return self._send_smtp(to_addresses, subject, text_body, html_body)
    
    def _send_smtp(self, to_addresses: List[str], subject: str,
                  text_body: str, html_body: str) -> bool:
        """Send via SMTP."""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.config.from_address
            msg['To'] = ', '.join(to_addresses)
            
            if self.config.cc_addresses:
                msg['Cc'] = ', '.join(self.config.cc_addresses)
            
            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))
            
            with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
                if self.config.smtp_use_tls:
                    server.starttls()
                if self.config.smtp_username:
                    server.login(self.config.smtp_username, self.config.smtp_password)
                
                all_recipients = to_addresses + self.config.cc_addresses
                server.sendmail(self.config.from_address, all_recipients, msg.as_string())
            
            logger.info(f"Email sent successfully to {', '.join(to_addresses)}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def _send_sendgrid(self, to_addresses: List[str], subject: str,
                      text_body: str, html_body: str) -> bool:
        """Send via SendGrid API."""
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail
            
            sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
            
            message = Mail(
                from_email=self.config.from_address,
                to_emails=to_addresses,
                subject=subject,
                html_content=html_body,
                plain_text_content=text_body
            )
            
            response = sg.send(message)
            logger.info(f"SendGrid email sent: {response.status_code}")
            return response.status_code in [200, 202]
            
        except Exception as e:
            logger.error(f"SendGrid error: {e}")
            return False
    
    def _send_console(self, to_addresses: List[str], subject: str,
                     text_body: str) -> bool:
        """Print to console (for testing)."""
        print("\n" + "="*60)
        print("EMAIL NOTIFICATION (Console Mode)")
        print("="*60)
        print(f"To: {', '.join(to_addresses)}")
        print(f"Subject: {subject}")
        print("-"*60)
        print(text_body)
        print("="*60 + "\n")
        return True


class NotificationManager:
    """
    Manages all notifications for the MPART system.
    
    Coordinates email alerts, digests, and other notification channels.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or 'config/notifications.json'
        self.notifier = EmailNotifier()
        self.notification_history = []
        
    def process_matches(self, matches: List[Dict], 
                       source: str = "unknown") -> Dict[str, Any]:
        """
        Process new matches and send appropriate notifications.
        
        Args:
            matches: List of match results
            source: Source of matches (e.g., "gata", "sam")
            
        Returns:
            Summary of notifications sent
        """
        stats = {
            'total_matches': len(matches),
            'high_priority': 0,
            'immediate_alerts': 0,
            'digest_sent': False,
            'errors': []
        }
        
        # Count high priority
        for match in matches:
            score = match.get('match_score', 0)
            if score >= self.notifier.config.high_priority_threshold:
                stats['high_priority'] += 1
            
            # Send immediate alert for very high scores
            if score >= 95 and self.notifier.config.send_immediate_alerts:
                success = self.notifier.send_immediate_alert(match)
                if success:
                    stats['immediate_alerts'] += 1
                else:
                    stats['errors'].append(f"Failed to send alert for {match.get('grant_id')}")
        
        # Send daily digest
        if self.notifier.config.send_daily_digest:
            success = self.notifier.send_digest(matches, stats)
            stats['digest_sent'] = success
        
        # Log notification
        self._log_notification(stats, source)
        
        return stats
    
    def _log_notification(self, stats: Dict, source: str):
        """Log notification to history file."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'source': source,
            'stats': stats
        }
        
        self.notification_history.append(entry)
        
        # Save to file
        history_file = Path('data/notification_history.json')
        history_file.parent.mkdir(parents=True, exist_ok=True)
        
        existing_history = []
        if history_file.exists():
            with open(history_file) as f:
                existing_history = json.load(f)
        
        existing_history.append(entry)
        
        with open(history_file, 'w') as f:
            json.dump(existing_history, f, indent=2)


if __name__ == '__main__':
    # Test the notification system
    import sys
    
    # Set console mode for testing
    os.environ['CONSOLE_EMAIL'] = 'true'
    
    notifier = EmailNotifier()
    
    test_matches = [
        {
            'grant_id': 'TEST-001',
            'grant_title': 'Illinois Medicaid PolicyDelta Analysis',
            'agency': 'Illinois HFS',
            'match_score': 92,
            'deadline': '2026-03-15',
            'recommended_lead': 'mercenary_policy',
            'rationale': 'Strong alignment with state Medicaid policy expertise and 1115 Waiver experience.'
        },
        {
            'grant_id': 'TEST-002',
            'grant_title': 'National Policy Tracker Implementation',
            'agency': 'Illinois DHS',
            'match_score': 85,
            'deadline': '2026-04-30',
            'recommended_lead': 'mercenary_data',
            'rationale': 'Matches AI-assisted regulatory monitoring capabilities.'
        }
    ]
    
    test_stats = {
        'total_matches': 2,
        'high_priority': 2,
        'medium_priority': 0
    }
    
    print("Testing email digest...")
    notifier.send_digest(test_matches, test_stats)
    
    print("\nTesting immediate alert...")
    notifier.send_immediate_alert(test_matches[0])
