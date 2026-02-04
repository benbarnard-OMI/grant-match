"""
Digest generation for various formats (email, Slack, Teams, etc.)
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class DigestGenerator:
    """
    Generates grant match digests in multiple formats.
    
    Supports:
    - HTML email
    - Plain text
    - Slack/Teams markdown
    - PDF (optional)
    """
    
    def __init__(self, organization: str = "MPART @ UIS"):
        self.organization = organization
    
    def generate_html(self, matches: List[Dict], 
                     stats: Dict[str, Any],
                     include_css: bool = True) -> str:
        """Generate HTML digest."""
        high_priority = [m for m in matches if m.get('match_score', 0) >= 80]
        
        css = """
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                   line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }
            .header { background: linear-gradient(135deg, #003366 0%, #004080 100%); 
                     color: white; padding: 30px; border-radius: 8px; text-align: center; }
            .summary { background: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 8px; }
            .stat-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-top: 15px; }
            .stat-box { background: white; padding: 15px; border-radius: 5px; text-align: center; 
                       box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .stat-number { font-size: 32px; font-weight: bold; color: #003366; }
            .stat-label { color: #666; font-size: 14px; }
            .match { background: white; border: 1px solid #e0e0e0; margin: 15px 0; padding: 20px; 
                    border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
            .match-header { display: flex; justify-content: space-between; align-items: center; 
                           margin-bottom: 15px; }
            .score-pill { background: #003366; color: white; padding: 8px 16px; border-radius: 20px; 
                         font-weight: bold; font-size: 18px; }
            .score-high { background: #e74c3c; }
            .score-medium { background: #f39c12; }
            .score-low { background: #95a5a6; }
            .lead-badge { display: inline-flex; align-items: center; gap: 5px; 
                         padding: 6px 12px; border-radius: 15px; font-size: 13px; font-weight: 500; }
            .lead-policy { background: #e3f2fd; color: #1565c0; }
            .lead-data { background: #f3e5f5; color: #7b1fa2; }
            .lead-eval { background: #e8f5e9; color: #2e7d32; }
            .deadline { color: #d32f2f; font-weight: 600; }
            .rationale { color: #666; font-style: italic; margin-top: 10px; }
            .footer { text-align: center; padding: 30px; color: #999; font-size: 13px; 
                     border-top: 1px solid #eee; margin-top: 30px; }
        </style>
        """ if include_css else ""
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Grant Digest - {self.organization}</title>
    {css}
</head>
<body>
    <div class="header">
        <h1>📊 Grant Opportunity Digest</h1>
        <p>{self.organization} • {datetime.now().strftime('%B %d, %Y')}</p>
    </div>
    
    <div class="summary">
        <h2>📈 Today's Summary</h2>
        <div class="stat-grid">
            <div class="stat-box">
                <div class="stat-number">{stats.get('total_matches', 0)}</div>
                <div class="stat-label">Total Matches</div>
            </div>
            <div class="stat-box">
                <div class="stat-number" style="color: #e74c3c;">{stats.get('high_priority', 0)}</div>
                <div class="stat-label">High Priority</div>
            </div>
            <div class="stat-box">
                <div class="stat-number" style="color: #f39c12;">{stats.get('medium_priority', 0)}</div>
                <div class="stat-label">Medium Priority</div>
            </div>
        </div>
    </div>
    
    <h2>🎯 Top Opportunities</h2>
"""
        
        for match in high_priority[:10]:
            score = match.get('match_score', 0)
            score_class = 'score-high' if score >= 80 else 'score-medium' if score >= 50 else 'score-low'
            lead = match.get('recommended_lead', '')
            lead_class = f"lead-{lead.replace('mercenary_', '')}" if lead else ''
            lead_icon = {'mercenary_policy': '📋', 'mercenary_data': '🔬', 'mercenary_eval': '🏥'}.get(lead, '👤')
            lead_name = {'mercenary_policy': 'Policy Expert', 'mercenary_data': 'Data/AI Expert', 
                        'mercenary_eval': 'Rural/Eval Expert'}.get(lead, 'Not assigned')
            
            html += f"""
    <div class="match">
        <div class="match-header">
            <h3 style="margin: 0; color: #003366;">{match.get('grant_title', 'Untitled')}</h3>
            <span class="score-pill {score_class}">{score}/100</span>
        </div>
        <p><strong>Agency:</strong> {match.get('agency', 'Unknown')}</p>
        <p class="deadline">⏰ Deadline: {match.get('deadline', 'Not specified')}</p>
        <span class="lead-badge {lead_class}">{lead_icon} {lead_name}</span>
        <p class="rationale">💡 {match.get('rationale', 'No rationale provided')}</p>
    </div>
"""
        
        html += f"""
    <div class="footer">
        <p>Generated by {self.organization} Grant Match System</p>
        <p>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</body>
</html>"""
        
        return html
    
    def generate_markdown(self, matches: List[Dict], 
                         stats: Dict[str, Any]) -> str:
        """Generate Markdown digest (for Slack, Teams, etc.)."""
        high_priority = [m for m in matches if m.get('match_score', 0) >= 80]
        
        md = f"""# 📊 Grant Opportunity Digest
**{self.organization}** • {datetime.now().strftime('%B %d, %Y')}

## 📈 Summary
- **Total Matches:** {stats.get('total_matches', 0)}
- **🔴 High Priority:** {stats.get('high_priority', 0)}
- **🟡 Medium Priority:** {stats.get('medium_priority', 0)}

## 🎯 Top Opportunities

"""
        
        for i, match in enumerate(high_priority[:5], 1):
            score = match.get('match_score', 0)
            lead = match.get('recommended_lead', '')
            lead_name = {'mercenary_policy': '📋 Policy', 'mercenary_data': '🔬 Data', 
                        'mercenary_eval': '🏥 Rural/Eval'}.get(lead, '👤 Unassigned')
            
            emoji = '🔴' if score >= 80 else '🟡' if score >= 50 else '⚪'
            
            md += f"""### {emoji} {match.get('grant_title', 'Untitled')}
**Score:** {score}/100 • **Lead:** {lead_name}

**Agency:** {match.get('agency', 'Unknown')}  
**⏰ Deadline:** {match.get('deadline', 'Not specified')}  
**💡 Why:** {match.get('rationale', 'No rationale')[:150]}...

---

"""
        
        return md
    
    def generate_excel_data(self, matches: List[Dict]) -> List[Dict]:
        """Generate data structure for Excel export."""
        rows = []
        for match in matches:
            rows.append({
                'Score': match.get('match_score', 0),
                'Priority': 'High' if match.get('match_score', 0) >= 80 else 
                           'Medium' if match.get('match_score', 0) >= 50 else 'Low',
                'Title': match.get('grant_title', ''),
                'Agency': match.get('agency', ''),
                'Deadline': match.get('deadline', ''),
                'Lead': match.get('recommended_lead', ''),
                'Rationale': match.get('rationale', ''),
                'Research Depth': match.get('research_depth', ''),
                'Recommended Action': match.get('recommended_action', '')
            })
        return rows
